# Security policy

This public repository holds the code of a client dashboard for accounting offices: a Python data
pipeline, dbt models and a static Astro site. Real client configurations and raw files live outside
it. Please report any vulnerability privately so it can be fixed before it is exposed.

## Supported branches

| Branch    | Purpose            | Supported |
| --------- | ------------------ | --------- |
| `main`    | Production         | Yes       |
| `develop` | Integration branch | Yes       |

## Reporting a vulnerability

Use GitHub private vulnerability reporting:
[open a private report](https://github.com/thalesreiser/painel-clientes/security/advisories/new).

**Do not open a public issue, pull request or discussion about a vulnerability.**

Include, in English or Portuguese, the affected file or URL, the steps to reproduce it, the impact you
expect and the commit or date on which you observed it.

Never include real client data, CNPJs of real companies, e-mails, credentials or API keys in a
report. Describe them instead, for example by saying which field was exposed.

## Scope

In scope:

- **Pipeline:** `pipeline/` and how it reads raw files and client configurations.
- **dbt:** `dbt/` models and seeds.
- **Site:** `web/`, the published dashboards and client login.
- **Data exposure:** any way for one client to see another client's data, or for client data to
  reach this public repository.
- **Workflows:** `.github/workflows` and anything that could expose secrets or alter a deploy.

Out of scope: flaws in third-party services (report them to the provider), denial of service, spam,
social engineering and reports from automated tools with no demonstrated impact.

## No real client data in this repository

This repository contains fictional data only (RNF-01, ADR 003): invented companies, clearly fake
CNPJs and `@example.com` e-mails. CI runs Gitleaks on every pull request and push, with an extra rule
that flags CNPJ-like numbers outside the fictional demos and test fixtures. If you find real client
data or a secret here, report it privately as above.

## Response

Responses are **best effort**, with no guaranteed deadline. Reports are handled in the advisory
thread. There is no bug bounty programme.
