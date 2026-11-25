"""Client configuration (RF-01): Pydantic mirror of schemas/cliente.schema.json.

Enums and canonical columns are read from the JSON Schema, so the schema stays the single
source of truth; tests check that the structure of the models matches it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "cliente.schema.json"
_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
_DEFS = _SCHEMA["$defs"]

Template = Literal["financeiro", "entregas"]

KPIS: dict[str, frozenset[str]] = {
    t: frozenset(_DEFS[f"kpis_{t}"]["enum"]) for t in ("financeiro", "entregas")
}
COLUNAS: dict[str, frozenset[str]] = {
    t: frozenset(_DEFS[f"colunas_{t}"]["propertyNames"]["enum"]) for t in ("financeiro", "entregas")
}
COLUNAS_OBRIGATORIAS: dict[str, frozenset[str]] = {
    t: frozenset(_DEFS[f"colunas_{t}"]["required"]) for t in ("financeiro", "entregas")
}

Texto = Annotated[str, Field(min_length=1)]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Fonte(_Base):
    tipo: Literal["csv", "xlsx"]
    arquivos: list[Texto] = Field(min_length=1)
    mapeamento_colunas: dict[str, Texto]
    separador: Annotated[str, Field(min_length=1, max_length=1)] | None = None
    aba: Texto | None = None
    encoding: Texto | None = None


class Marca(_Base):
    nome: Texto
    logo: Texto | None = None
    cor_primaria: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
    preparado_por: Texto | None = None


class Cliente(_Base):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    schema_: str | None = Field(default=None, alias="$schema")
    id: Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
    nome: Texto
    template: Template
    fonte: Fonte
    kpis_ativos: list[str] = Field(min_length=1)
    marca: Marca
    fuso: Texto = "America/Sao_Paulo"

    @model_validator(mode="after")
    def _regras_do_template(self) -> Self:
        invalidos = [k for k in self.kpis_ativos if k not in KPIS[self.template]]
        if invalidos:
            raise ValueError(
                f"kpis_ativos: {invalidos} não existem no template '{self.template}' "
                f"(válidos: {sorted(KPIS[self.template])})"
            )
        if len(set(self.kpis_ativos)) != len(self.kpis_ativos):
            raise ValueError("kpis_ativos: há KPIs repetidos")
        mapa = self.fonte.mapeamento_colunas
        desconhecidas = sorted(set(mapa) - COLUNAS[self.template])
        if desconhecidas:
            raise ValueError(
                f"fonte.mapeamento_colunas: colunas {desconhecidas} não existem no template "
                f"'{self.template}' (válidas: {sorted(COLUNAS[self.template])})"
            )
        faltando = sorted(COLUNAS_OBRIGATORIAS[self.template] - set(mapa))
        if faltando:
            raise ValueError(f"fonte.mapeamento_colunas: faltam as colunas obrigatórias {faltando}")
        return self


class ClienteInvalidoError(ValueError):
    """A client JSON that does not follow the schema; the message names the field."""


def _campo(loc: tuple[int | str, ...]) -> str:
    return ".".join(str(p) for p in loc) or "(raiz)"


def load_cliente(path: str | Path) -> Cliente:
    """Read and validate a client JSON, raising ClienteInvalidoError naming each bad field."""
    path = Path(path)
    try:
        dados = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClienteInvalidoError(f"{path}: JSON malformado ({exc})") from exc
    try:
        return Cliente.model_validate(dados)
    except ValidationError as exc:
        erros = "; ".join(f"campo '{_campo(e['loc'])}': {e['msg']}" for e in exc.errors())
        raise ClienteInvalidoError(f"{path}: {erros}") from exc
