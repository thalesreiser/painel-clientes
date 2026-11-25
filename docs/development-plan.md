# Development plan

The pilot needs every M task: 90 hours, about 4.5 weeks at 20 h per week (Q-06). S tasks add 23 hours
right after. INT-01 becomes M (+14 h before the pilot) if the pilot office can only send data through
the Conta Azul API (Q-03). Task board (Trello, pt-BR): https://trello.com/b/GOH5bRnu.

## Process

- **Definition of Ready:** requirement and acceptance criterion written, dependencies done (tasks,
  questions, decisions), estimate set.
- **Definition of Done:** PR template checklist and card sub-tasks ticked, CI green and, when there is
  data, `dbt build` passing on the demos.
- **Flow:** Backlog → Pronto → Em andamento → Revisão (PR open) → Concluído (merged).
- **Client validation:** tasks marked (validation) end in a session with the first pilot office; its
  cases become dbt tests that block the merge.
- **Who decides:** design, interface, business rules, security, infrastructure and cost go to Thales
  with options and a recommendation and end in an ADR. Routine implementation choices go in the PR.

## Milestones

| Milestone | Main tasks |
|---|---|
| Public `financeiro` demo (2026-12-18) | EST-01.1-01.2, DAD-01.1-01.3, DAD-02.1-02.2, DAD-02.4, WEB-01.1-01.2, WEB-02.1 |
| Deliveries, login and CI (2026-12-30) | DAD-02.3, WEB-02.2-02.3, WEB-01.3, WEB-03.1, EST-01.3, EST-02, EST-03.1, INT-01.1 (Conta Azul spike) |
| Pilot live (2027-01-08) | EST-03.2, EST-03.3, DAD-02.5, NEG-01.2-01.4 |
| S scope (2027-01-22) | INT-01.2-01.3, INT-02, WEB-02.4, NEG-01.5 |

**Calendar risk:** the pilot falls between Christmas and the first week of January, when accounting
offices close the year. Book the validation session (DAD-02.5) and send the data agreement (NEG-01.4)
in December. If nothing is booked by 2026-12-18, the pilot moves to 2027-01-15.

## Structural (EST)

| ID | Task | Req. | Prio. | Est. | Depends on |
|---|---|---|---|---|---|
| EST-01.1 | Vision, requirements, plan, ADRs 001-003 and Trello board | - | M | 3 h | DEC-01 |
| EST-01.2 | Repository structure and tooling | RNF-07 | M | 4 h | EST-01.1 |
| EST-01.3 | Contribution rules, templates and branch protection | RNF-01, RNF-07 | M | 2 h | EST-01.2 |
| EST-02.1 | CI pipeline | RNF-04, RNF-07 | M | 3 h | EST-01.2 |
| EST-02.2 | Security automation | RNF-02 | M | 2 h | EST-02.1 |
| EST-03.1 | Accounts and environments (manual, Thales) | RNF-03 | M | 2 h | DEC-02, DEC-03 |
| EST-03.2 | Scheduled build workflow per client | RF-07, RNF-04 | M | 3 h | EST-03.1, DAD-02.4, WEB-01.1 |
| EST-03.3 | Failure alert and new-client runbook | RF-07 | M | 2 h | EST-03.2 |

- **EST-01.2:** folders `pipeline/`, `dbt/`, `web/`, `clientes/`, `docs/` · Python 3.12 with uv, ruff
  and pytest · Node 24 pinned in `.nvmrc`, Astro, ESLint, Prettier · commitlint · Makefile
  (`make demo`, `make test`), as in `dbt-dw-api`.
- **EST-01.3:** `CLAUDE.md` · PR template · Dependabot · fictional-data rule · `main` and `develop`
  protected.
- **EST-02.1:** ruff, pytest, `dbt build` on the demos, `astro check`, validation of every JSON in
  `clientes/` and a build of each demo.
- **EST-02.2:** gitleaks · CodeQL · `SECURITY.md`.
- **EST-03.1:** Cloudflare Pages, Access and R2 · private configuration repository · R2 lifecycle rule
  deleting raw files after 90 days (RNF-02).
- **EST-03.2:** GitHub Actions daily cron with a matrix per client · downloads the files from R2, runs
  `dbt build`, builds the site and publishes it to the client's project · a failing test does not
  publish (RNF-04).

## Data (DAD)

| ID | Task | Req. | Prio. | Est. | Depends on |
|---|---|---|---|---|---|
| DAD-01.1 | Client JSON schema | RF-01 | M | 3 h | EST-01.2 |
| DAD-01.2 | CSV and XLSX connector with column mapping | RF-02 | M | 4 h | DAD-01.1 |
| DAD-01.3 | Fictional data generator | RNF-01 | M | 4 h | DAD-01.1 |
| DAD-02.1 | dbt project and conventions | RNF-05 | M | 2 h | EST-01.2 |
| DAD-02.2 | `financeiro` template: staging, intermediate and marts | RF-03, RN-01 | M | 7 h | DAD-02.1, DAD-01.2 |
| DAD-02.3 | `entregas` template: staging, intermediate and marts | RF-04, RN-02 | M | 5 h | DAD-02.1, DAD-01.2 |
| DAD-02.4 | Quality tests and mart export | RNF-04, RNF-08 | M | 3 h | DAD-02.2, DAD-02.3 |
| DAD-02.5 | Validation with the first office (validation) | RN-01 | M | 4 h | DAD-02.2, NEG-01.2, Q-02 |

- **DAD-01.1:** one JSON Schema, validated in the pipeline (Pydantic) and the site (Zod), like the
  landing template's `schema.ts` · source, template, column mapping, active KPIs and branding.
- **DAD-01.2:** load into DuckDB · types, dates and BRL amounts · a rejected row goes to a report, it
  never disappears.
- **DAD-01.3:** one BPO office with three clients and one carrier with three months of deliveries ·
  Faker pt_BR with a fixed seed.
- **DAD-02.1:** `docs/naming-conventions.md` and `dim_data` with national holidays, reused from
  `dbt-dw-api`.
- **DAD-02.2:** `fct_lancamento`, `fct_fluxo_caixa_diario`, `dim_categoria`, `dim_conta` · overdue
  payables and receivables.
- **DAD-02.3:** `fct_entrega`, `dim_cliente`, `dim_rota` · on-time rate per RN-02.
- **DAD-02.4:** `not_null`, `unique`, `relationships` and `accepted_values` tests · marts exported as
  pre-aggregated JSON for the site (RNF-08).
- **DAD-02.5:** the office's real cases become tests · review session · fixes.

## Dashboard (WEB)

| ID | Task | Req. | Prio. | Est. | Depends on |
|---|---|---|---|---|---|
| WEB-01.1 | Astro app with `CLIENTE=` | RF-01 | M | 4 h | EST-01.2, DAD-01.1 |
| WEB-01.2 | Chart and KPI components | RNF-06 | M | 4 h | WEB-01.1 |
| WEB-01.3 | Visual direction (decision, Thales) | RF-08 | M | 2 h | WEB-01.2 |
| WEB-02.1 | `financeiro` dashboard | RF-03, RF-05 | M | 6 h | WEB-01.2, DAD-02.4 |
| WEB-02.2 | `entregas` dashboard | RF-04, RF-05 | M | 5 h | WEB-01.2, DAD-02.4 |
| WEB-02.3 | Period filter and print version | RF-05 | M | 3 h | WEB-02.1 |
| WEB-02.4 | Office white label | RF-08 | S | 3 h | WEB-02.1 |
| WEB-03.1 | Per-client login with Cloudflare Access | RF-06 | M | 3 h | EST-03.1 |

- **WEB-01.1:** `CLIENTE=demo-bpo npm run build`, like the template's `NICHO=` · an unknown name or
  invalid JSON fails the build · theme per client.
- **WEB-01.2:** KPI card with change, line, bars and table · readable on a phone.
- **WEB-02.4:** office logo and colours in the JSON · "prepared by" footer.
- **WEB-03.1:** one Access policy per Pages project · authorised e-mails in the private JSON.

## Integrations (INT)

| ID | Task | Req. | Prio. | Est. | Depends on |
|---|---|---|---|---|---|
| INT-01.1 | Spike: OAuth 2.0 and financial endpoints of the Conta Azul API v2 | RF-09 | S | 4 h | Q-04 |
| INT-01.2 | Connector for entries, categories and balances | RF-09 | S | 6 h | INT-01.1, DAD-01.1 |
| INT-01.3 | Token refresh and credentials in secrets | RF-09, RNF-02 | S | 4 h | INT-01.2 |
| INT-02.1 | Monthly e-mail summary | RF-10 | S | 4 h | WEB-02.3 |

## Business (NEG)

| ID | Task | Req. | Prio. | Est. | Depends on |
|---|---|---|---|---|---|
| NEG-01.1 | Published demos (`financeiro` and `entregas`) | - | M | 2 h | WEB-02.1, WEB-02.2 |
| NEG-01.2 | First pilot with a prospecting office | - | M | 4 h | NEG-01.1 |
| NEG-01.3 | Proposal and pricing (manual, Thales) | - | M | 2 h | Q-01, Q-07 |
| NEG-01.4 | Data processing agreement for the client | RNF-02 | M | 2 h | - |
| NEG-01.5 | Portfolio README with demo links and a GIF | - | S | 2 h | NEG-01.1 |

## Effort

| Track | Tasks | Total | Needed for the pilot (M) |
|---|---|---|---|
| Structural | 8 | 21 h | 21 h |
| Data | 8 | 32 h | 32 h |
| Dashboard | 8 | 30 h | 27 h |
| Integrations | 4 | 18 h | 0 h |
| Business | 5 | 12 h | 10 h |
| **Total** | **33** | **113 h** | **90 h** |
