# 09 — Root cause

Read `knowledge/04-hidden-state-mechanisms.md`, `knowledge/05-failure-mode-catalog.md`, `knowledge/06-plant-case-studies.md`, and `knowledge/09-confounding-and-causality.md`.

## Order

1. Call phase 6. If the status is `explained_external`, show the delay code and the tonne reconciliation. Do not add a furnace cause. If gate 0 is `not_testable`, the page says the shortfall is not established.

2. Physics attribution through the Rist line and the carbon and heat balances, in kilograms or tonnes, only for terms whose inputs exist. Each term names the convention. On EVRAZ this split is `not_run` for the missing coke, Fe, and production inputs. Do not fill the waterfall with silicon correlations.

3. SHAP on the predictive model, at the feature's lag, only as a secondary view. Caption: SHAP explains the fit. If the balance already accounts for the gap, SHAP is not the ranking.

4. Counterfactuals through the decision model only for variables phase 8 marked identified. Others are disabled. If identification fails, the answer is `not_identified`.

5. Signature match against `knowledge/05-failure-mode-catalog.md`. A match is a hypothesis with a citation. Missing signals are listed. The 127 EVRAZ labels may be opened as examples. They are not automatic verdicts for other hours.

## Fields

Rank, name, contribution when the balance ran, confidence, series, timing relative to the lag, an alternative that lost, a human check, and a suggestion. No action is sent to a plant system.

## Inconclusive

If every balance term is inside the reconciliation tolerance, or the inputs are absent, status is `inconclusive` and the body is the missing series.

## UI

Gate status, waterfall or the explicit `not_run`, signature hypothesis, counterfactual controls. Scenario watermark when the window is a branch.

## Exit tests

- EVRAZ does not receive a coke-rate tonne ranking.
- A synthetic oxygen-only change inside the identified set attributes the gap to the driving-rate term.
- High hydrogen plus a tuyere flow imbalance returns the water-leak hypothesis rather than the moisture hypothesis, when both signals exist.
- `inconclusive` is asserted when inputs are withheld.
