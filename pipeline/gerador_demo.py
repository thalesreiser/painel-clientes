"""Deterministic fictional data for the demo clients (RNF-01).

Usage: ``python -m pipeline.gerador_demo --saida dados/``

Writes ``<saida>/demo-bpo/lancamentos.csv`` and ``<saida>/demo-transportadora/entregas.xlsx``
using the CLIENT column names from ``mapeamento_colunas`` in ``clientes/demo-*.json``.
All names are fictional and carry a "Demo" marker; no CNPJs are generated.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

from faker import Faker

SEED = 20261125
DATA_REFERENCIA = date(2026, 11, 20)
CLIENTES_DIR = Path(__file__).resolve().parents[1] / "clientes"

# Monthly revenue multiplier (Jan..Dec): weak start of year, strong year end.
SAZONALIDADE = [0.80, 0.85, 0.95, 1.00, 1.00, 0.95, 0.95, 1.00, 1.05, 1.10, 1.15, 1.35]

CATEGORIAS_RECEITA = {
    "Venda de produtos": (800, 9000),
    "Prestação de serviços": (1500, 12000),
    "Receita financeira": (50, 600),
}
CATEGORIAS_DESPESA = {
    "Folha de pagamento": (8000, 22000),
    "Aluguel": (4500, 4500),
    "Fornecedores": (600, 7000),
    "Impostos": (1200, 6000),
    "Energia e água": (400, 1500),
    "Marketing": (300, 3000),
    "Tarifas bancárias": (30, 250),
}
CONTAS = ["Banco Demo 001 - CC", "Banco Exemplo 999 - CC"]

ROTAS = [
    "Petrópolis - Rio de Janeiro",
    "Teresópolis - Niterói",
    "Nova Friburgo - Duque de Caxias",
    "Petrópolis - Juiz de Fora",
    "Três Rios - Volta Redonda",
]
OCORRENCIAS = ["Destinatário ausente", "Endereço não localizado", "Avaria", "Atraso na coleta"]


def mapeamento(cliente_id: str, clientes_dir: Path = CLIENTES_DIR) -> dict[str, str]:
    dados = json.loads((clientes_dir / f"{cliente_id}.json").read_text(encoding="utf-8"))
    return dados["fonte"]["mapeamento_colunas"]


def _nomes(fake: Faker, modelo: str, n: int) -> list[str]:
    nomes: list[str] = []
    while len(nomes) < n:
        nome = modelo.format(fake.last_name())
        if nome not in nomes:
            nomes.append(nome)
    return nomes


def _brl(valor: float) -> str:
    inteiro, centavos = f"{valor:,.2f}".split(".")
    return f"{inteiro.replace(',', '.')},{centavos}"


def _data_br(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else ""


def _meses(inicio: date, fim: date) -> list[date]:
    meses, atual = [], inicio.replace(day=1)
    while atual <= fim:
        meses.append(atual)
        atual = (atual + timedelta(days=32)).replace(day=1)
    return meses


def gerar_lancamentos(seed: int = SEED) -> list[dict[str, str]]:
    """15 months of entries (Sep/2025..Nov/2026), keyed by dbt column names."""
    rng = random.Random(seed)
    fake = Faker("pt_BR")
    fake.seed_instance(seed)
    clientes = _nomes(fake, "Comércio {} Demo Ltda", 12)
    fornecedores = _nomes(fake, "Distribuidora {} Fictícia", 8)

    linhas: list[dict[str, str]] = []
    for mes in _meses(date(2025, 9, 1), date(2026, 11, 1)):
        fator = SAZONALIDADE[mes.month - 1]
        receitas = rng.choices(list(CATEGORIAS_RECEITA), k=rng.randint(14, 20))
        itens = [("Receita", c) for c in receitas]
        itens += [("Despesa", c) for c in CATEGORIAS_DESPESA]
        itens += [("Despesa", c) for c in rng.choices(["Fornecedores", "Marketing"], k=6)]
        for tipo, categoria in itens:
            faixa = (CATEGORIAS_RECEITA if tipo == "Receita" else CATEGORIAS_DESPESA)[categoria]
            valor = rng.uniform(*faixa) * (fator if tipo == "Receita" else 1.0)
            competencia = mes.replace(day=rng.randint(1, 28))
            vencimento = competencia + timedelta(days=rng.choice([0, 10, 15, 30]))
            pagamento: date | None = None
            if vencimento <= DATA_REFERENCIA:
                sorteio = rng.random()
                if sorteio > 0.08:  # ~8% stays overdue and unpaid
                    atraso = rng.randint(1, 12) if sorteio < 0.25 else -rng.randint(0, 3)
                    pagamento = min(vencimento + timedelta(days=atraso), DATA_REFERENCIA)
            if tipo == "Receita":
                contraparte = rng.choice(clientes)
            elif categoria in ("Fornecedores", "Marketing", "Energia e água"):
                contraparte = rng.choice(fornecedores)
            else:
                contraparte = "Imobiliária Exemplo Demo" if categoria == "Aluguel" else "-"
            linhas.append(
                {
                    "dt_competencia": _data_br(competencia),
                    "dt_vencimento": _data_br(vencimento),
                    "dt_pagamento": _data_br(pagamento),
                    "vl_lancamento": _brl(round(valor, 2)),
                    "tp_lancamento": tipo,
                    "nm_categoria": categoria,
                    "nm_conta": rng.choice(CONTAS),
                    "nm_contraparte": contraparte,
                }
            )
    for i, linha in enumerate(linhas, start=1):
        linha["id_lancamento"] = f"L{i:05d}"
    return linhas


def gerar_entregas(seed: int = SEED) -> list[dict[str, object]]:
    """~3 months of deliveries (Aug..Nov/2026), keyed by dbt column names."""
    rng = random.Random(seed)
    fake = Faker("pt_BR")
    fake.seed_instance(seed + 1)
    destinatarios = _nomes(fake, "Mercado {} Demo", 15)

    linhas: list[dict[str, object]] = []
    dia, numero = date(2026, 8, 24), 100000
    while dia <= DATA_REFERENCIA:
        if dia.weekday() < 6:  # Mon..Sat
            for _ in range(rng.randint(25, 45)):
                numero += 1
                coleta = datetime.combine(dia, time(rng.randint(6, 16), rng.choice([0, 15, 30])))
                prazo = rng.choice([1, 1, 2, 3])
                prevista = dia + timedelta(days=prazo)
                sorteio = rng.random()
                ocorrencia = ""
                if sorteio < 0.03:
                    status, entrega = "Devolvida", None
                    ocorrencia = rng.choice(OCORRENCIAS[:2])
                else:
                    atraso = rng.randint(1, 3) if sorteio < 0.14 else -rng.randint(0, prazo - 1)
                    dt = prevista + timedelta(days=atraso)
                    if dt > DATA_REFERENCIA:
                        status, entrega = "Em trânsito", None
                    else:
                        status = "Entregue"
                        entrega = datetime.combine(dt, time(rng.randint(8, 19), rng.randint(0, 59)))
                    if atraso > 0:
                        ocorrencia = rng.choice(OCORRENCIAS)
                linhas.append(
                    {
                        "id_entrega": str(numero),
                        "dt_coleta": coleta,
                        "dt_prevista": prevista,
                        "dt_entrega": entrega,
                        "nm_cliente": rng.choice(destinatarios),
                        "nm_rota": rng.choice(ROTAS),
                        "tp_status": status,
                        "tp_ocorrencia": ocorrencia,
                        "nr_volumes": rng.randint(1, 30),
                    }
                )
        dia += timedelta(days=1)
    return linhas


def csv_lancamentos(seed: int = SEED, clientes_dir: Path = CLIENTES_DIR) -> bytes:
    cols = mapeamento("demo-bpo", clientes_dir)
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", lineterminator="\n")
    writer.writerow(cols.values())
    for linha in gerar_lancamentos(seed):
        writer.writerow(linha[k] for k in cols)
    return buf.getvalue().encode("utf-8")


def escrever_entregas(destino: Path, seed: int = SEED, clientes_dir: Path = CLIENTES_DIR) -> None:
    from openpyxl import Workbook

    config = json.loads((clientes_dir / "demo-transportadora.json").read_text(encoding="utf-8"))
    cols = config["fonte"]["mapeamento_colunas"]
    wb = Workbook()
    ws = wb.active
    ws.title = config["fonte"]["aba"]
    ws.append(list(cols.values()))
    for linha in gerar_entregas(seed):
        ws.append([linha[k] for k in cols])
    fixo = datetime(2026, 11, 1)
    wb.properties.created = fixo
    wb.properties.modified = fixo
    wb.save(destino)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Gera dados fictícios dos clientes demo.")
    parser.add_argument("--saida", type=Path, default=Path("dados"))
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)

    bpo = args.saida / "demo-bpo"
    bpo.mkdir(parents=True, exist_ok=True)
    (bpo / "lancamentos.csv").write_bytes(csv_lancamentos(args.seed))
    transp = args.saida / "demo-transportadora"
    transp.mkdir(parents=True, exist_ok=True)
    escrever_entregas(transp / "entregas.xlsx", args.seed)
    print(f"Dados demo gravados em {args.saida}")


if __name__ == "__main__":
    main()
