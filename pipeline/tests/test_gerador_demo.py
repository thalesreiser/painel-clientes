import csv
import hashlib
import io
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from pipeline import gerador_demo as g


def _hash_xlsx(path: Path) -> str:
    ws = load_workbook(path, read_only=True).active
    return hashlib.sha256(repr(list(ws.iter_rows(values_only=True))).encode()).hexdigest()


def test_csv_is_deterministic() -> None:
    a = hashlib.sha256(g.csv_lancamentos()).hexdigest()
    b = hashlib.sha256(g.csv_lancamentos()).hexdigest()
    assert a == b
    assert a != hashlib.sha256(g.csv_lancamentos(seed=1)).hexdigest()


def test_csv_columns_match_mapping() -> None:
    linhas = list(csv.reader(io.StringIO(g.csv_lancamentos().decode("utf-8")), delimiter=";"))
    assert linhas[0] == list(g.mapeamento("demo-bpo").values())
    assert len(linhas) > 300


def test_lancamentos_mix() -> None:
    linhas = g.gerar_lancamentos()
    assert {linha["tp_lancamento"] for linha in linhas} == {"Receita", "Despesa"}
    vencidos = [
        linha
        for linha in linhas
        if not linha["dt_pagamento"]
        and datetime.strptime(linha["dt_vencimento"], "%d/%m/%Y").date() <= g.DATA_REFERENCIA
    ]
    assert vencidos
    assert any("," in linha["vl_lancamento"] for linha in linhas)


def test_xlsx_deterministic_and_columns(tmp_path: Path) -> None:
    g.main(["--saida", str(tmp_path / "a")])
    g.main(["--saida", str(tmp_path / "b")])
    a = tmp_path / "a" / "demo-transportadora" / "entregas.xlsx"
    b = tmp_path / "b" / "demo-transportadora" / "entregas.xlsx"
    assert _hash_xlsx(a) == _hash_xlsx(b)
    wb = load_workbook(a, read_only=True)
    assert wb.sheetnames == ["Entregas"]
    cabecalho = next(wb.active.iter_rows(values_only=True))
    assert list(cabecalho) == list(g.mapeamento("demo-transportadora").values())
    assert (tmp_path / "a" / "demo-bpo" / "lancamentos.csv").exists()


def test_on_time_rate_in_band() -> None:
    entregues = [e for e in g.gerar_entregas() if e["tp_status"] == "Entregue"]
    no_prazo = sum(e["dt_entrega"].date() <= e["dt_prevista"] for e in entregues)
    assert 0.85 <= no_prazo / len(entregues) <= 0.92
    assert any(e["tp_ocorrencia"] for e in entregues)
