import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest
from openpyxl import Workbook

from pipeline.config import load_cliente
from pipeline.ingest import ArquivoInvalidoError, ConversaoError, carregar, converter, main

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize(
    ("coluna", "bruto", "esperado"),
    [
        ("dt_x", "05/01/2026", date(2026, 1, 5)),
        ("dt_x", "2026-01-05", date(2026, 1, 5)),
        ("dt_x", datetime(2026, 1, 5, 10, 0), date(2026, 1, 5)),
        ("vl_x", "R$ 1.234,56", Decimal("1234.56")),
        ("vl_x", "-89,9", Decimal("-89.90")),
        ("vl_x", "1234.5", Decimal("1234.50")),
        ("vl_x", "1.234,56", Decimal("1234.56")),
        ("vl_x", "1.500", Decimal("1500.00")),
        ("vl_x", "12.345.678", Decimal("12345678.00")),
        ("vl_x", "1.5", Decimal("1.50")),
        ("vl_x", "1234.56", Decimal("1234.56")),
        ("vl_x", 12.5, Decimal("12.50")),
        ("nr_x", " 7 ", 7),
        ("nr_x", 3.0, 3),
        ("nm_x", "  Rota Sul ", "Rota Sul"),
        ("id_x", 123.0, "123"),
        ("tp_x", "", None),
    ],
)
def test_converter(coluna: str, bruto: object, esperado: object) -> None:
    assert converter(coluna, bruto) == esperado


@pytest.mark.parametrize(
    ("coluna", "bruto"), [("dt_x", "31/02/2026"), ("vl_x", "abc"), ("nr_x", "2,5")]
)
def test_converter_invalido(coluna: str, bruto: str) -> None:
    with pytest.raises(ConversaoError):
        converter(coluna, bruto)


def test_csv_com_rejeitados(tmp_path: Path) -> None:
    cliente = load_cliente(FIXTURES / "cliente-financeiro.json")
    db = tmp_path / "painel.duckdb"
    carregar(cliente, FIXTURES, db)
    with duckdb.connect(str(db)) as con:
        linhas = con.execute(
            "SELECT id_lancamento, dt_vencimento, dt_pagamento, vl_lancamento, nm_categoria "
            "FROM raw_financeiro ORDER BY id_lancamento"
        ).fetchall()
        rejeitados = con.execute(
            "SELECT nr_linha, nm_coluna FROM raw_financeiro_rejeitados ORDER BY nr_linha"
        ).fetchall()
    assert linhas == [
        ("L1", date(2026, 1, 5), date(2026, 1, 6), Decimal("1234.56"), "Serviços"),
        ("L2", date(2026, 1, 10), None, Decimal("-89.90"), "Aluguel"),
    ]
    assert rejeitados == [(4, "dt_vencimento"), (5, "vl_lancamento"), (6, "nm_categoria")]
    relatorio = (tmp_path / "raw_financeiro_rejeitados.csv").read_text(encoding="utf-8")
    assert relatorio.splitlines()[0] == "arquivo;linha;coluna;valor;motivo"
    assert len(relatorio.splitlines()) == 4


def _cliente_entregas(tmp_path: Path) -> Path:
    dados = {
        "id": "teste-entregas",
        "nome": "Transportes Fictícios",
        "template": "entregas",
        "fonte": {
            "tipo": "xlsx",
            "arquivos": ["entregas.xlsx"],
            "aba": "Entregas",
            "mapeamento_colunas": {
                "id_entrega": "CT-e",
                "dt_prevista": "Previsão",
                "dt_entrega": "Entregue",
                "nm_cliente": "Destinatário",
                "tp_status": "Status",
                "nr_volumes": "Volumes",
            },
        },
        "kpis_ativos": ["entregas_por_dia"],
        "marca": {"nome": "Transportes Fictícios", "cor_primaria": "#654321"},
    }
    path = tmp_path / "cliente.json"
    path.write_text(json.dumps(dados), encoding="utf-8")
    return path


def test_xlsx_via_cli(tmp_path: Path) -> None:
    livro = Workbook()
    aba = livro.active
    aba.title = "Entregas"
    aba.append(["CT-e", "Previsão", "Entregue", "Destinatário", "Status", "Volumes"])
    aba.append([1001, datetime(2026, 3, 2), "03/03/2026", " Loja A ", "entregue", 4])
    aba.append([1002, "2026-03-05", None, "Loja B", "pendente", "dois"])
    livro.save(tmp_path / "entregas.xlsx")
    db = tmp_path / "out" / "painel.duckdb"
    cliente = str(_cliente_entregas(tmp_path))
    assert main(["--cliente", cliente, "--dados", str(tmp_path), "--db", str(db)]) == 0
    with duckdb.connect(str(db)) as con:
        linhas = con.execute("SELECT * FROM raw_entregas").fetchall()
        rejeitados = con.execute(
            "SELECT nr_linha, nm_coluna FROM raw_entregas_rejeitados ORDER BY nm_coluna"
        ).fetchall()
    assert linhas == [("1001", date(2026, 3, 2), date(2026, 3, 3), "Loja A", "entregue", 4)]
    assert rejeitados == [(3, "dt_entrega"), (3, "nr_volumes")]


def test_coluna_mapeada_ausente(tmp_path: Path) -> None:
    livro = Workbook()
    livro.active.title = "Entregas"
    livro.active.append(["CT-e"])
    livro.save(tmp_path / "entregas.xlsx")
    cliente = load_cliente(_cliente_entregas(tmp_path))
    with pytest.raises(ArquivoInvalidoError, match="ausentes"):
        carregar(cliente, tmp_path, tmp_path / "x.duckdb")
