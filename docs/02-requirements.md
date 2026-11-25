# 02 - Requirements

IDs follow the pattern of `tax-reform-saas` and `dbt-dw-api`: RF for functional requirements, RNF for
non-functional requirements and RN for business rules. Tasks in the
[development plan](development-plan.md) cite these IDs. Priority: M = must (needed for the pilot),
S = should (right after the pilot).

## Functional

| ID | Requirement | Prio. |
|---|---|---|
| RF-01 | Per-client JSON configuration (source, template, column mapping, active KPIs, branding), validated by a schema; an invalid JSON fails the build | M |
| RF-02 | Ingestion of CSV and XLSX exported from the ERP or from spreadsheets, using the column mapping in the JSON | M |
| RF-03 | `financeiro` template: revenue, expenses, result, realised and forecast cash flow, overdue payables and receivables, top categories, comparison with the previous month and year | M |
| RF-04 | `entregas` template: deliveries per day, on-time rate, incidents, performance by customer and route | M |
| RF-05 | Period filter and a print/PDF version of the month | M |
| RF-06 | Protected access: each client sees only their own dashboard | M |
| RF-07 | Scheduled daily refresh, with the date of the last refresh shown on the dashboard | M |
| RF-08 | Office branding on the dashboard (logo, colours, "prepared by") so the office can resell the service | S |
| RF-09 | Read-only Conta Azul API v2 integration (OAuth 2.0): financial entries, categories and balances | S |
| RF-10 | Monthly e-mail summary with the main figures and the dashboard link | S |

## Non-functional

| ID | Requirement | Prio. |
|---|---|---|
| RNF-01 | Demos and fixtures use fictional data only; no real data in the repository | M |
| RNF-02 | LGPD: each client's data isolated, credentials in secrets, minimum retention and a signed data processing agreement | M |
| RNF-03 | Recurring cost close to zero per client in the MVP, using free tiers | M |
| RNF-04 | dbt quality tests block publishing: a failing test keeps the previous version of the dashboard online, which shows a stale-data warning when the last refresh is older than 2 days | M |
| RNF-05 | `dbt-dw-api` naming convention (prefixes `id_`, `dt_`, `vl_`, `nr_`, `tp_`, `fl_`, `nm_`) | M |
| RNF-06 | Dashboard readable on a phone and loaded in under 2 s on a 4G connection | M |
| RNF-07 | CI on every PR and commits following Conventional Commits | M |
| RNF-08 | Marts exported already aggregated by day and month, so the period filter runs in the browser without downloading the entries; each dashboard's JSON under 500 KB (supports RNF-06) | M |

## Business rules

| ID | Rule | Prio. |
|---|---|---|
| RN-01 | Result = revenue - expenses in the period; cash or accrual basis depends on Q-02 | M |
| RN-02 | On-time delivery = delivery date on or before the promised date | M |
| RN-03 | Amounts in BRL; dates converted to UTC-3 only for presentation, as in `dbt-dw-api` | M |
