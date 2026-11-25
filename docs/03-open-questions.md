# 03 - Open questions

Questions that block or change a task. When one is answered, record the answer here (and an ADR when
it is a decision) and link it from the affected task.

## Decisions

| ID | Decision | Status |
|---|---|---|
| DEC-01 | Dashboard technology | Closed: [ADR 001](adr/001-stack.md) |
| DEC-02 | Client login | Closed: [ADR 002](adr/002-client-login.md) |
| DEC-03 | Where configurations and real data live | Closed: [ADR 003](adr/003-public-code-private-config.md) |

## Questions

| ID | Question | Where it is answered | Status |
|---|---|---|---|
| Q-01 | Pricing: setup fee plus a monthly fee per end client, or a package per office? | First prospecting meetings | Open |
| Q-02 | Does the `financeiro` template use cash or accrual basis (RN-01)? | First pilot office | Open |
| Q-03 | Which systems and exports do the offices use? Aliança, Detalhes, GRR and Ferreira e Ebling are listed in the [Conta Azul partner directory](https://contaazul.com/encontre-contador/contabilidade/rs/porto-alegre/) | Meetings; decides whether INT-01 becomes M | Open |
| Q-04 | The Conta Azul API [has no sandbox, only production](https://contaazul.com/blog/api-conta-azul-integracoes-para-o-seu-negocio/). How do we test without real data? | Spike INT-01.1: own test account and recorded responses as fictional fixtures | Open |
| Q-05 | Where does Modal Expresso's delivery data come from (transport system or spreadsheet)? | Meeting with Modal Expresso | Open |
| Q-06 | How many hours per week are available? The schedule assumes 20 h | Thales, before week 1 | Open |
| Q-07 | How many end clients does each office want on the dashboard? The free Cloudflare Access user limit applies to the whole account and decides whether pricing includes a paid plan (Q-01) | Prospecting meetings, with Q-01 | Open |
| Q-08 | How does the client's file reach R2, and how often? Upload page behind Access, synced shared folder or e-mail. If the export is manual and weekly, the daily refresh (RF-07) has no effect | First pilot office; the chosen path becomes an M task before the pilot | Open |
