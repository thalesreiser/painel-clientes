import json
from pathlib import Path

import pytest

from pipeline.config import SCHEMA_PATH, Cliente, ClienteInvalidoError, load_cliente

CLIENTES = Path(__file__).resolve().parents[2] / "clientes"
DEMOS = sorted(CLIENTES.glob("demo-*.json"))


def _demo_bpo() -> dict:
    return json.loads((CLIENTES / "demo-bpo.json").read_text(encoding="utf-8"))


def _gravar(tmp_path: Path, dados: dict) -> Path:
    path = tmp_path / "cliente.json"
    path.write_text(json.dumps(dados), encoding="utf-8")
    return path


def test_demos_exist() -> None:
    assert {p.name for p in DEMOS} == {"demo-bpo.json", "demo-transportadora.json"}


@pytest.mark.parametrize("path", DEMOS, ids=lambda p: p.stem)
def test_demo_is_valid(path: Path) -> None:
    assert load_cliente(path).id == path.stem


def test_fuso_defaults_to_sao_paulo() -> None:
    assert load_cliente(CLIENTES / "demo-transportadora.json").fuso == "America/Sao_Paulo"


def test_models_match_schema_fields() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    campos = {f.alias or n for n, f in Cliente.model_fields.items()}
    assert campos == set(schema["properties"])
    assert set(schema["required"]) == {
        f.alias or n for n, f in Cliente.model_fields.items() if f.is_required()
    }


@pytest.mark.parametrize(
    ("alterar", "campo"),
    [
        (lambda d: d.pop("nome"), "nome"),
        (lambda d: d.update(id="Demo BPO"), "id"),
        (lambda d: d.update(template="vendas"), "template"),
        (lambda d: d["fonte"].update(tipo="contaazul"), "fonte.tipo"),
        (lambda d: d["fonte"].update(arquivos=[]), "fonte.arquivos"),
        (lambda d: d["marca"].update(cor_primaria="azul"), "marca.cor_primaria"),
        (lambda d: d.update(emails=["a@exemplo.com"]), "emails"),
        (lambda d: d.update(kpis_ativos=["taxa_no_prazo"]), "kpis_ativos"),
        (lambda d: d["fonte"]["mapeamento_colunas"].pop("vl_lancamento"), "vl_lancamento"),
        (lambda d: d["fonte"]["mapeamento_colunas"].update(nm_rota="Rota"), "nm_rota"),
    ],
)
def test_invalid_config_names_the_field(tmp_path: Path, alterar, campo: str) -> None:
    dados = _demo_bpo()
    alterar(dados)
    with pytest.raises(ClienteInvalidoError, match=campo.replace(".", r"\.")):
        load_cliente(_gravar(tmp_path, dados))


def test_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "cliente.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(ClienteInvalidoError, match="JSON malformado"):
        load_cliente(path)
