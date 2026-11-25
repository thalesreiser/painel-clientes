# 002 - Client login

- **Status:** accepted
- **Date:** 2026-11-25
- **Decided by:** Thales Reiser
- **Reference:** DEC-02, RF-06

## Context

Each client must see only their own dashboard (RF-06). The dashboards are static sites, so there is no
application server to check a session.

## Options considered

1. **Cloudflare Access in front of each Pages project, one-time code by e-mail:** no authentication
   code to write or maintain; authorised e-mails are a list per project. Cost: the free Zero Trust plan
   limits users across the whole account (about 50, to be confirmed in EST-03.1), not per project.
2. **Own authentication:** no user limit, but a login flow, sessions and password handling to build and
   secure, which a static site cannot do without adding a server.

## Decision

Option 1.

## Consequences

- One Access policy per Pages project; authorised e-mails live in the private configuration repository
  (ADR 003), never in this one.
- The account-wide user limit is enough for the pilot but caps resale. Q-07 measures the demand and
  feeds pricing (Q-01); passing the limit means a paid plan or revisiting this ADR.
