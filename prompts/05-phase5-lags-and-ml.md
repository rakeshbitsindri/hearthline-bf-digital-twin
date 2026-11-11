# 05 — Lags and prediction

Read `knowledge/07-ml-literature.md`, `knowledge/08-lag-reference.md`, and `data/public/evraz-zsmk-2013-2016/PROFILE.md`. Forecasts and model cards. No setpoints.

## Features

Estimate a lag per manipulated variable against silicon and, when it exists, hot-metal temperature and production. Report method, significance, and production regime. Literature lags are priors. On EVRAZ, publish the flat level-correlation and the near-zero change-correlation. Do not invent a six-hour coke lag the file cannot show.

Active-rate features where the input exists. Two lags allowed for PCI when PCI exists. Cast silicon of the cast being predicted is a target, not an input. `available_at` cuts features that were not knowable.

## Models

Walk-forward, purged, embargo sized from the target autocorrelation:

1. Persistence. On EVRAZ silicon this RMSE is 0.120 wt%. The card must show that number from the run, not from this prompt.
2. LightGBM on lag and active-rate features.
3. Physics or twin output from phases 3 and 4, plus a LightGBM residual. Two residuals: forecast, and decision-compatible. The decision residual uses causal parents only, preserves balances, and is off outside the density envelope. Phase 4 may call the decision residual later. It is not trained on outcome descendants.

Serve a model only when it beats the previous bar on the same folds. No LSTM or PyTorch in this phase.

## Uncertainty and jobs

Rolling conformal intervals. If coverage on the last fold is below nominal, the card says so. Training is a background job.

## UI

Model card page: persistence, boosting, hybrid, effective sample size, embargo, coverage, origin. EVRAZ card states the series ends in 2016.

## Exit tests

- A future moving average or same-time silicon in the training frame fails the leak scan.
- `predict` returns point, interval, coverage, in-envelope, model version, origin.
- EVRAZ card includes persistence RMSE computed in the run.
- Decision residual training rejects a column that is a descendant of silicon.
