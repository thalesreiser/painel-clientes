# clientes/

One JSON file per client. This public repository holds only the demos, with fictional data
(ADR 003). Real client configurations live in the private repository.

Each file follows `schemas/cliente.schema.json` (the single source of truth), checked by
`pipeline/config.py` (Pydantic, `load_cliente`) and `web/src/lib/schema.ts` (Zod).
Authorised e-mails never go here (ADR 003).

- `demo-bpo.json`: `financeiro` template, CSV source.
- `demo-transportadora.json`: `entregas` template, XLSX source.
