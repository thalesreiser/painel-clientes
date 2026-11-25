# 01 - Vision and scope

One dashboard per client, built from a JSON configuration file and the data the client already has.
The first public demo, with fictional data, is due on 2026-12-18 for the prospecting meetings. The
pilot with real data goes live on 2027-01-08 (2027-01-15 if the validation session cannot be booked
by 2026-12-18), at about 20 hours per week.

## Model

The product repeats the `landing-servicos-template` model: each new client is a new JSON file in
`clientes/`, with no code change. A schema validates the JSON, and a typo fails the build with the
name of the field.

## Templates

| Template | For | Prospecting leads | What the dashboard shows |
|---|---|---|---|
| `financeiro` | Accounting offices with outsourced finance (BPO) that hand the dashboard to their own clients | Aliança, Detalhes, GRR, Ferreira e Ebling | Revenue, expenses, result, cash flow and overdue bills |
| `entregas` | Carriers and distributors | Modal Expresso | Deliveries per day, on-time rate, performance by customer and route |

## Scope

- **MVP:** CSV and XLSX ingestion of files exported from the client's system, dbt models per
  template, one static dashboard per client behind a login, scheduled daily refresh and public demos
  with fictional data.
- **Right after launch:** Conta Azul API integration, the office's own branding (white label) and a
  monthly e-mail summary.
- **Out of scope:** writing to the client's system, self-service sign-up (multi-tenant SaaS), a mobile
  app, forecasts and other ERP integrations without a client asking for them.
