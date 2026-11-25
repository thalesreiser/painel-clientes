# Working on painel-clientes

Read this file before every task. It applies to every contributor, human or automated. If anything
here conflicts with another document, follow the stricter rule and point out the conflict on the task
card.

## Sources of truth

- **Development plan** (tracks, tasks, estimates, Definition of Ready and Done):
  `docs/development-plan.md`.
- **Vision and scope:** `docs/01-vision-and-scope.md`. **Requirements:** `docs/02-requirements.md`.
- **Decisions taken:** `docs/adr/`. **Decisions pending:** `docs/03-open-questions.md`.
- **Task board** (Trello, pt-BR): https://trello.com/b/GOH5bRnu. Card names carry the task ID, e.g.
  `[DAD-02.1]`.

## Business rules

- **RN-01:** result = revenue - expenses in the period. Cash or accrual basis depends on Q-02; do not
  pick one until it is answered.
- **RN-02:** a delivery is on time when the delivery date is on or before the promised date.
- **RN-03:** amounts are in BRL; dates are converted to UTC-3 only for presentation, as in
  `dbt-dw-api`.
- Business rules ship with dbt or pytest tests. Cases validated with a pilot office become tests that
  block the merge; never change an expected value to make a test pass: ask on the card.

## Who decides what

Contributors implement; Thales decides. Never decide the items below on your own:

- **Design, UI and UX:** visual identity, layout, navigation, interface copy, mobile behaviour.
- **Business rules:** any metric definition or calculation not already in RN-xx or an ADR.
- **Security and personal data:** login, permissions, authorised e-mails, secrets, LGPD retention.
- **Integrations, infrastructure and cost:** a new or replaced provider, a relevant new dependency, a
  paid plan, any change to CI/CD or repository settings.
- **Removing a feature** or changing behaviour a client can notice.

When you reach one of these:

1. Pause only the affected part; keep working on the rest of the task.
2. Ask on the task card and in the PR under "Questions for Thales": context, 2 or 3 options with pros
   and cons, impact and a recommendation.
3. Wait for Thales's answer on the card.
4. Record the decision as an ADR (`docs/adr/NNN-short-title.md`, see `000-template.md`), close the
   item in `docs/03-open-questions.md` and link the ADR from the PR.

Routine implementation choices (library versions inside the agreed stack, lint strictness, file
layout) do not need a decision: pick the most sensible option and list it under "Implementation
choices" in the PR description with the reason.

## Workflow for every task

1. **Pick** a card in "Pronto" and move it to "Em andamento".
2. **Check the Definition of Ready.** If an acceptance criterion or a decision is missing, comment
   what is missing and pick another card.
3. **Read** this file, the plan entry for the task, related ADRs and the surrounding code.
4. **Branch** from an up-to-date `develop`: `feat/<task-id>-<slug>`, `fix/<task-id>-<slug>` or
   `chore/<task-id>-<slug>`.
5. **Commit** in small steps (see Conventions).
6. **Verify in CI, never locally.** Push the branch and open the PR; lint, format, type checks, tests,
   `dbt build` and the site build run in CI. The development laptop has 7.7 GB of RAM, so installs,
   builds, test suites, dbt and dev servers are not run on it. Visual checks use the PR preview
   deployment. Locally, only lockfile updates are allowed
   (`npm install --package-lock-only --ignore-scripts`, `uv lock`).
7. **Open the PR** against `develop` with the template, then move the card to "Revisão".
8. **Address review** with new commits; never rewrite history that was already reviewed.
9. **Merge** is always done by Thales. The card goes to "Concluído" after the merge.

`main` and `develop` are protected by repository rulesets: changes arrive only through pull requests.

If you are stuck after two attempts, stop, describe what you tried on the card and ask for help. Never
work around it by disabling a test, a lint rule or a type check.

## Commands (run in CI)

| Command        | What it does                                |
| -------------- | ------------------------------------------- |
| `make install` | `uv sync` and `npm ci`                      |
| `make lint`    | Ruff, ESLint and Prettier checks            |
| `make test`    | pytest                                      |
| `make demo`    | `dbt build` on the demos and the site build |

## Conventions

- **Node.js** 24 with an npm workspace (`web`); **Python** with uv (`pyproject.toml`, `uv.lock`).
- **dbt naming** follows `dbt-dw-api` (RNF-05): columns use the prefixes `id_`, `dt_`, `vl_`, `nr_`,
  `tp_`, `fl_`, `nm_`.
- Follow existing patterns and reuse models and components before creating new ones.
- One task per branch and per PR, roughly 400 changed lines at most, not counting lockfiles and
  generated code; split bigger work.
- GitHub Actions are pinned to a full commit SHA with the version in a comment
  (`uses: owner/action@<sha> # v1.2.3`); Dependabot keeps them updated. Never use a floating tag.
- **Language:** code, commits, branches, PRs and repository docs in English; Trello cards and comments
  in Brazilian Portuguese; user-facing text in Brazilian Portuguese.
- **Commits:** Conventional Commits with the task ID, e.g. `feat(dbt): add dim_data (DAD-02.1)`.
  No co-author trailers or tool-generated footers in commits or PRs, and no mention of the tools used
  to write the code.

## What never goes into this repository

The repository is public ([ADR 003](docs/adr/003-public-code-private-config.md)).

- Secrets of any kind: API keys, tokens, passwords, `.env` files (only `.env.example`).
- **Real client data:** client names, CNPJs, authorised e-mails, raw files, revenue or any figure from
  an office or its clients, even in tests or fixtures. Real configurations live in the private
  repository; raw files live in R2.

**Fictional data only (RNF-01):** demos in `clientes/` and fixtures use invented companies, clearly
fake CNPJs and example e-mails (`@example.com`).

## Finishing a task

- Fill the PR template: Definition of Done, implementation choices, questions, what could not be
  tested.
- UI changes include desktop and mobile screenshots from the preview deployment.
- Merge and production deploys are always done by Thales.
