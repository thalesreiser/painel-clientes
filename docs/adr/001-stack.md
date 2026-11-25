# 001 - Stack

- **Status:** accepted
- **Date:** 2026-11-25
- **Decided by:** Thales Reiser
- **Reference:** DEC-01, EST-01.1

## Context

Each client gets a dashboard generated from a JSON configuration and the files they export. The MVP
must cost close to nothing per client (RNF-03), load in under 2 s on 4G (RNF-06) and allow office
branding later (RF-08). One developer builds it at about 20 h per week, and the development machine
has little RAM, so builds and tests run in CI.

## Options considered

1. **Astro + ECharts, one static site generated per client:** reuses the pattern and the deploy of
   `landing-servicos-template` (`CLIENTE=` like `NICHO=`), zero hosting cost, full control of the look
   for white label. Cost: the period filter runs in the browser, so marts must be pre-aggregated
   (RNF-08).
2. **Evidence.dev, pages in SQL and Markdown:** fast to build, but less control over the look and a
   new tool to learn.
3. **Nuxt 4 + FastAPI, dynamic:** as in `tax-reform-saas`; only worth it if the product becomes a SaaS
   with its own sign-up, which is out of scope.

## Decision

Option 1.

| Layer | Choice |
|---|---|
| Ingestion | Python 3.12 with uv, ruff and pytest; connectors for CSV and XLSX (Conta Azul later) |
| Transformation | dbt + DuckDB, staging/intermediate/marts, `dbt-dw-api` naming convention |
| Dashboard | Astro + Tailwind + ECharts, Node 24, one build per client selected by `CLIENTE=` |
| Configuration | One JSON Schema, validated with Pydantic in the pipeline and Zod in the site |
| Hosting | Cloudflare Pages, one project per client, deployed from GitHub Actions |
| Schedule | GitHub Actions cron, one matrix job per client |

## Consequences

- Marts are exported as pre-aggregated JSON and the dashboard never loads raw entries (RNF-08).
- A failing dbt test stops the deploy, so the previous version stays online (RNF-04).
- Moving to option 3 later means rewriting the site, not the pipeline or the dbt models.
