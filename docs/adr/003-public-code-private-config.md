# 003 - Public code, private configuration

- **Status:** accepted
- **Date:** 2026-11-25
- **Decided by:** Thales Reiser
- **Reference:** DEC-03, RNF-01, RNF-02

## Context

The code is meant to stay in Thales's public portfolio, like the other projects, but client
configurations, authorised e-mails and raw files are personal and business data under LGPD.

## Options considered

1. **Public code with the demos; real configurations in a private repository; raw files in one R2
   bucket per client:** the code stays public and no real data enters this repository.
2. **Everything in one private repository:** simpler, but the project leaves the portfolio.

## Decision

Option 1.

## Consequences

- This repository holds only demo configurations in `clientes/` and fictional fixtures (RNF-01).
- The scheduled build workflow, which uses the secrets, runs in the private repository; this one runs
  only CI and the demos.
- Raw files in R2 are deleted by a lifecycle rule after 90 days (minimum retention, RNF-02).
- gitleaks and the fictional-data rule in `CLAUDE.md` guard against real data reaching this repository.
