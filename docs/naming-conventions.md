# Naming conventions (RNF-05)

Adapted from `dbt-dw-api`. Identifiers are lower-case `snake_case`; table and column names
follow the business domain in Portuguese (`cliente`, `fatura`, `entrega`), while code, comments
and repository docs are in English.

## Layers and models

| Layer | Folder | Materialization | Model name | Example |
|---|---|---|---|---|
| Staging | `dbt/models/staging/` | view | `stg_<source>__<table>` | `stg_erp__fatura` |
| Intermediate | `dbt/models/intermediate/` | view | `int_<entity>__<transformation>` | `int_fatura__agregada` |
| Marts | `dbt/models/marts/<template>/` | table | `dim_<entity>`, `fct_<process>` | `fct_faturamento` |
| Shared marts | `dbt/models/marts/comum/` | table | `dim_<entity>` | `dim_data` |
| Seeds | `dbt/seeds/` | seed (CSV) | `<entity in Portuguese, plural>` | `feriados_nacionais` |

- Staging is the only layer that reads `source()`: one model per source table, no joins and no
  business rules. It renames, casts and standardizes.
- Each template (`financeiro`, `entregas`) has its own folder under `marts/`; models used by
  more than one template live in `marts/comum/`.
- Every model has a YAML entry next to it (`_<folder>.yml`) describing the model, its **grain**
  and every column.
- Singular tests live in `dbt/tests/<layer>/` and are named `assert_<what_must_hold>.sql`.
- Tables use singular entity names (`dim_cliente`, not `dim_clientes`), except staging models,
  which keep the source table name.

## Column prefixes

| Prefix | Meaning | Type | Example |
|---|---|---|---|
| `id_` | Identifier (from the source, or a key built in the marts) | `varchar` | `id_cliente`, `id_fatura` |
| `dt_` | Calendar date | `date` | `dt_emissao`, `dt_data` |
| `vl_` | Monetary value in BRL | `decimal(18,2)` | `vl_fatura` |
| `nr_` | Count or number | `integer` | `nr_entregas`, `nr_mes` |
| `tp_` | Categorical type or status code | `varchar`, upper case, no accents | `tp_status` |
| `fl_` | Boolean flag | `boolean` | `fl_dia_util` |
| `nm_` | Name or free text | `varchar`, trimmed, accents kept | `nm_cliente` |

Rules:

- The date dimension is keyed by the date itself (`dim_data.dt_data`); facts join on their own
  `dt_` column.
- Timestamps, when a source has them, are stored in UTC. Conversion to UTC-3 (America/Sao_Paulo) happens
  only at presentation time, in the panel, never in the warehouse (RN-03).
- Amounts are always BRL with two decimal places and a point as decimal separator; formatting
  (`R$ 1.234,56`) is a presentation concern.
- Data in this repository is fictional (RNF-01); public reference data such as national
  holidays is the only exception.
