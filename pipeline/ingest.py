"""CSV/XLSX connector (RF-02): read a client's files, map columns and load raw_<template>.

Every column is converted by its prefix (RNF-05). A row that fails any conversion goes to
raw_<template>_rejeitados and to a CSV report, with line number, column and reason; it never
disappears silently.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import duckdb
from openpyxl import load_workbook

from pipeline.config import COLUNAS_OBRIGATORIAS, Cliente, load_cliente

TIPOS_SQL = {"dt_": "DATE", "vl_": "DECIMAL(18, 2)", "nr_": "BIGINT"}
_NUMERO_BR = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$|^-?\d+(,\d+)?$")
_NUMERO_ISO = re.compile(r"^-?\d+(\.\d+)?$")


class ConversaoError(ValueError):
    """A value that cannot be converted to the type its column prefix requires."""


class ArquivoInvalidoError(ValueError):
    """A client file that is missing or lacks a mapped column."""


def tipo_sql(coluna: str) -> str:
    return TIPOS_SQL.get(coluna[:3], "VARCHAR")


def _texto(valor: Any) -> str:
    return str(valor).strip()


def converter_data(valor: Any) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = _texto(valor)
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ConversaoError(f"data inválida '{texto}' (use dd/mm/aaaa ou aaaa-mm-dd)")


def converter_valor(valor: Any) -> Decimal:
    if isinstance(valor, int | float | Decimal) and not isinstance(valor, bool):
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    texto = _texto(valor).replace("R$", "").replace(" ", "").replace(" ", "")
    if _NUMERO_BR.match(texto) and ("," in texto or not _NUMERO_ISO.match(texto)):
        texto = texto.replace(".", "").replace(",", ".")
    elif not _NUMERO_ISO.match(texto):
        raise ConversaoError(f"valor inválido '{_texto(valor)}' (use 1.234,56)")
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise ConversaoError(f"valor inválido '{_texto(valor)}'") from exc


def converter_inteiro(valor: Any) -> int:
    if isinstance(valor, int) and not isinstance(valor, bool):
        return valor
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    texto = _texto(valor)
    if not re.fullmatch(r"-?\d+", texto):
        raise ConversaoError(f"número inteiro inválido '{texto}'")
    return int(texto)


def converter(coluna: str, valor: Any) -> Any:
    """Convert one cell by its column prefix; blank cells become None."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    prefixo = coluna[:3]
    if prefixo == "dt_":
        return converter_data(valor)
    if prefixo == "vl_":
        return converter_valor(valor)
    if prefixo == "nr_":
        return converter_inteiro(valor)
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return _texto(valor)


@dataclass
class Resultado:
    colunas: list[str]
    linhas: list[tuple[Any, ...]] = field(default_factory=list)
    rejeitados: list[tuple[str, int, str, str, str]] = field(default_factory=list)


def _ler_csv(path: Path, cliente: Cliente) -> Iterator[tuple[int, dict[str, Any]]]:
    encoding = cliente.fonte.encoding or "utf-8-sig"
    with path.open(encoding=encoding, newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=cliente.fonte.separador or ",")
        _checar_cabecalho(path, leitor.fieldnames or [], cliente)
        for linha in leitor:
            yield leitor.line_num, linha


def _ler_xlsx(path: Path, cliente: Cliente) -> Iterator[tuple[int, dict[str, Any]]]:
    livro = load_workbook(path, read_only=True, data_only=True)
    try:
        aba = livro[cliente.fonte.aba] if cliente.fonte.aba else livro.worksheets[0]
        linhas = aba.iter_rows(values_only=True)
        cabecalho = [_texto(c) if c is not None else "" for c in next(linhas, ())]
        _checar_cabecalho(path, cabecalho, cliente)
        for numero, valores in enumerate(linhas, start=2):
            if all(v is None for v in valores):
                continue
            yield numero, dict(zip(cabecalho, valores, strict=False))
    finally:
        livro.close()


def _checar_cabecalho(path: Path, cabecalho: list[str], cliente: Cliente) -> None:
    faltando = sorted(set(cliente.fonte.mapeamento_colunas.values()) - set(cabecalho))
    if faltando:
        raise ArquivoInvalidoError(f"{path}: colunas mapeadas ausentes no arquivo: {faltando}")


def ler_cliente(cliente: Cliente, dados: Path) -> Resultado:
    """Read all client files, returning converted rows and rejections."""
    mapa = cliente.fonte.mapeamento_colunas
    obrigatorias = COLUNAS_OBRIGATORIAS[cliente.template]
    resultado = Resultado(colunas=list(mapa))
    leitor = _ler_xlsx if cliente.fonte.tipo == "xlsx" else _ler_csv
    for nome in cliente.fonte.arquivos:
        path = dados / nome
        if not path.exists():
            path = dados / Path(nome).name
        if not path.exists():
            raise ArquivoInvalidoError(f"arquivo não encontrado: {dados / nome}")
        for numero, bruta in leitor(path, cliente):
            convertida: list[Any] = []
            erros: list[tuple[str, int, str, str, str]] = []
            for canonica, original in mapa.items():
                valor = bruta.get(original)
                try:
                    novo = converter(canonica, valor)
                    if novo is None and canonica in obrigatorias:
                        raise ConversaoError("valor obrigatório vazio")
                except ConversaoError as exc:
                    erros.append((path.name, numero, canonica, _texto(valor or ""), str(exc)))
                    continue
                convertida.append(novo)
            if erros:
                resultado.rejeitados.extend(erros)
            else:
                resultado.linhas.append(tuple(convertida))
    return resultado


def carregar(cliente: Cliente, dados: Path, db: Path, relatorio: Path | None = None) -> Resultado:
    """Load raw_<template> and raw_<template>_rejeitados into DuckDB; write the CSV report."""
    resultado = ler_cliente(cliente, dados)
    tabela = f"raw_{cliente.template}"
    colunas_sql = ", ".join(f"{c} {tipo_sql(c)}" for c in resultado.colunas)
    db.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db)) as con:
        con.execute(f"CREATE OR REPLACE TABLE {tabela} ({colunas_sql})")
        if resultado.linhas:
            marcadores = ", ".join("?" for _ in resultado.colunas)
            con.executemany(f"INSERT INTO {tabela} VALUES ({marcadores})", resultado.linhas)
        con.execute(
            f"CREATE OR REPLACE TABLE {tabela}_rejeitados (nm_arquivo VARCHAR, nr_linha BIGINT, "
            "nm_coluna VARCHAR, ds_valor VARCHAR, ds_motivo VARCHAR)"
        )
        if resultado.rejeitados:
            con.executemany(
                f"INSERT INTO {tabela}_rejeitados VALUES (?, ?, ?, ?, ?)", resultado.rejeitados
            )
    relatorio = relatorio or db.parent / f"{tabela}_rejeitados.csv"
    with relatorio.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["arquivo", "linha", "coluna", "valor", "motivo"])
        escritor.writerows(resultado.rejeitados)
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingere CSV/XLSX de um cliente no DuckDB.")
    parser.add_argument("--cliente", required=True, type=Path, help="JSON do cliente")
    parser.add_argument("--dados", required=True, type=Path, help="pasta com os arquivos")
    parser.add_argument("--db", type=Path, default=os.environ.get("PAINEL_DUCKDB"))
    parser.add_argument("--relatorio", type=Path, help="CSV de rejeitados")
    args = parser.parse_args(argv)
    if args.db is None:
        parser.error("informe --db ou a variável PAINEL_DUCKDB")
    cliente = load_cliente(args.cliente)
    try:
        resultado = carregar(cliente, args.dados, Path(args.db), args.relatorio)
    except ArquivoInvalidoError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    linhas_rejeitadas = len({(r[0], r[1]) for r in resultado.rejeitados})
    print(
        f"raw_{cliente.template}: {len(resultado.linhas)} linhas carregadas, "
        f"{linhas_rejeitadas} rejeitadas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
