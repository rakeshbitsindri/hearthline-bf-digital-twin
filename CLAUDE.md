# Blast furnace intelligence — constitution

This file is the law for every session in this repository. The knowledge base in `knowledge/` is the domain reference. The prompts in `prompts/` are the build order. If a prompt and this file disagree, this file wins.

## What this system is

A read-only advisory digital twin for iron blast furnaces. It is a near-real-time digital shadow for a metallurgist or furnace operator. It is not a safety instrumented system, an alarm system, a control HMI, or an emergency-response tool. DCS and SIS indications and the plant's approved procedures stay authoritative.

It learns from operating history, steps a reduced-order furnace model forward in time, checks recommendations against mass and heat balances, and explains production shortfalls. It does not write to a PLC, a DCS, a historian, or a furnace actuator. Recommendations are accepted or rejected by a person. Acceptance is not evidence that the action was executed.

The central question, from the plant: production falls while the operating sheet looks unchanged. Treat that as an observability problem. The protocol is in `knowledge/04-hidden-state-mechanisms.md` and `prompts/06-phase6-observability-mystery.md`. A confident wrong cause is worse than an inconclusive one.

Recommendations are suppressed during startup, shutdown, banking, blow-in, maintenance, calibration, severe instability, a stale source, or an unqualified regime.

## Data reality

- Plant history is often hourly, about 3–4 years, from more than one furnace. That is roughly 26,000–35,000 rows per furnace and, given an 8–12 hour thermal time constant, on the order of 2,500–4,000 independent blocks. See `knowledge/07-ml-literature.md`. Ask for the full historian retention. Do not cap the request at three years.
- The public stand-in is the EVRAZ ZSMK hourly series in `data/public/evraz-zsmk-2013-2016/`. It is a reference furnace from 2013–2016, not this plant. Its profile is in that folder. Screens say so.
- Hourly means hide slips, hangs, pressure spikes, tuyere events, and channeling precursors. Ask for within-hour standard deviation, minimum, maximum, and excursion counts. A read-only historian connector archives minute-level values from the day it is approved, so later shortfalls are not limited to hourly means. Until those values exist, the UI states that those phenomena are below the sampling interval.
- Hourly production is often an allocation of cast weight or an iron-balance estimate. Store the route. One route may be displayed as provisional. A verified shortfall requires the available routes to be reconciled. If they cannot, gate 0 is `not_testable`.
- Lags differ by variable. Blast is about an hour. PCI is 1.5–3 hours and bimodal. Charged coke is 5–8 hours. Hot metal temperature has a time constant above 8 hours. Literature lags are priors. Use active rates and plant-calibrated delays. See `knowledge/08-lag-reference.md`.
- Time, identity, and revisions follow `knowledge/15-data-time-and-provenance.md`. A laboratory result is usable only at or after its `available_at`. Raw records are append-only.

## Parameter roles and capability

Every column has exactly one role: `manipulated`, `disturbance`, `state_response`, `outcome`, or `derived_latent`. Definitions and examples are in `knowledge/README.md`. "All parameters are the same" almost always means all manipulated variables are the same. Compare the response variables and the disturbances before concluding the furnace was the same.

Acquisition priority is not the same as whether a feature can run. Priorities and per-feature contracts are in `knowledge/13-parameter-tiers.md`. A missing value is never replaced with a literature default and shown as measured. Configuration constants may be assumed only when labelled assumed, with the citation beside them.

Every feature declares required inputs, alternatives, quality, coverage, resolution, freshness, observability, and identifiability. The capability matrix is recomputed by furnace, campaign, window, and use case. Statuses include `ready`, `degraded`, `blocked_missing`, `blocked_bad_quality`, `stale`, `backfilling`, `not_observable`, `not_identifiable`, `not_testable`, and `pending_validation`.

Derived quantities are labelled inferred. Measured quantities are labelled measured. Evidence classes are `measured`, `reconciled`, `estimated`, `simulated`, `assumed`, and `unavailable`. A screen that mixes them without the label is a defect. Provenance sits on the value, not only on a separate panel.

## Models

- Physics mass, heat, carbon, oxygen, and alkali balances are the backbone. The dynamic twin in `knowledge/14-dynamic-twin-model.md` steps inventories in absolute SI units. Learned models correct bounded residuals. A pure neural net is not the digital twin.
- Forecast residuals and decision residuals are separate. What-if and the optimiser use the decision residual. See `knowledge/09-confounding-and-causality.md`.
- Report a persistence baseline beside every model: last cast's silicon, last hour's temperature, last shift's production. On the public EVRAZ file the silicon persistence RMSE is 0.120 wt%. A model that does not beat persistence does not ship.
- A regularised gradient-boosting model is the second baseline. A deeper model ships only when it beats that baseline on purged, embargoed, walk-forward validation.
- No random train/test split on this data. Embargo length comes from the measured decorrelation time of the target.
- Two model families. The predictive family may use any feature known at prediction time. The decision family, used for setpoints, uses only causal parents. Descendants of the outcome are leakage in the decision family even when they raise R².
- Every prediction shows a point, a conformal interval, coverage, an in-envelope flag, and the model version.
- Credible bands from the literature, not targets to overfit toward: silicon RMSE about 0.08–0.11 wt%, hot metal temperature MAE about 5–25 °C, closed-loop value of a few degrees and a few kg/t of reductant. See `knowledge/07-ml-literature.md` and `knowledge/06-plant-case-studies.md`.
- States that fail an observability test are `not_observable` and are not drawn. Slow inventories stay relative until a plant-specific observation model is validated.
- Replay used for validation and for scenario branches uses the causal filtered state. A retrospective smooth is stored separately and is not a substitute for what the twin knew at the time.
- The synthetic truth generator is independent of the estimator. Recovery on data made by the same simulator proves software consistency only.

## Recommendations

- Run the identifiability audit before showing a setpoint. Non-identifiable is an allowed answer. See `knowledge/09-confounding-and-causality.md`.
- Require agreement of backdoor adjustment, g-computation, and double machine learning, with block-bootstrap intervals.
- Stay inside a density-based operating envelope and a trust region around the current point. A box of historical min/max is not an envelope.
- Word recommendations as associations adjusted for measured disturbances, not as guaranteed effects, unless the audit says the effect is identified.
- If the target is infeasible, say so and return the binding ceiling among tuyere stoichiometry, permeability, flooding, top-gas temperature, and hearth drainage.
- Missing site-approved limits, stale or bad data, non-observability, non-identifiability, or an out-of-envelope point blocks a routine setpoint. An engineering trial is a dossier for the plant's own management-of-change process. This platform does not authorise the trial.
- Never invent a metallurgical coefficient. Items in `knowledge/11-pending-validation.md` stay `pending_validation` and render as "not validated".

## Numbers

- No hardcoded predictions, optimiser outputs, or fake history.
- Synthetic data is generated, labelled synthetic on every screen, and used to test software. It is not evidence of metallurgical accuracy.
- Public reference data is labelled public reference, with the furnace and the year range. It is not this plant and it is not live.
- Units live in a registry. Conversions have tests. Permeability variant, productivity denominator, kinetic-energy convention, and thermal-equivalence convention are configuration, printed next to every result that depends on them.
- Raw uploads and raw connector records are immutable. Corrections append a revision. Every transform is reproducible from an as-of view and a run manifest.

## Stack

Use what the data volume justifies. When designing screens, follow the project's design-pack rule and the design skill it names. Do not invent a generic admin theme.

- Web: Next.js, React, TypeScript, Tailwind, shadcn/ui, ECharts, React Flow. Quantitative authority is the 2D engineering views and tables. A progressive 3D cutaway, using react-three-fiber, loads after that 2D state and only from configured geometry. Zones are zones, not a continuous CFD field. A no-WebGL path keeps every decision. See `knowledge/16-twin-commissioning-and-acceptance.md` for the performance budgets.
- API: Python, FastAPI, Pydantic. Live updates use server-sent events with sequence numbers.
- Numbers: NumPy, pandas, SciPy, scikit-learn, LightGBM. Add PyTorch only after the gradient-boosting baseline has been beaten on walk-forward validation.
- Storage: PostgreSQL for configuration, runs, and hourly facts. Parquet plus DuckDB for large extracts and the minute archive. Redis, TimescaleDB, and a feature-store service are out of scope until a measurement shows they are needed.
- Jobs: a simple background worker with progress rows in Postgres. Training, simulation, and optimisation never block a request.
- Historian connector: read-only, least privilege, secret vault, industrial DMZ, fixed read profiles. Specified in `knowledge/15-data-time-and-provenance.md` and `prompts/11-phase11-live-connector-and-modelops.md`.

## How to build

One phase at a time, from `prompts/`. Do not start the next phase inside the same change. Each phase ships the screen for what it builds. At the end of a phase, run the tests, write what works, and list what does not. Do not mark a feature done with a mock chart.

Design documents come before application code. `prompts/00-kickoff-architecture.md` produces design docs only.

## Safety

- Read-only toward the plant. No write path to control, historian, or actuators, even behind a flag.
- The connector cannot issue SQL, OPC methods, or historian writes. Credentials are not stored in the repo.
- Role-based access and an append-only audit log are built in phase 1. Model version is on every result. Operator accept or reject is recorded. Confirmed execution, when the plant later reports it, is a separate field.
- A recommendation outside the validated envelope is blocked.
- Uncertainty is visible. Coverage failure is visible. Stale data is never shown as current.
