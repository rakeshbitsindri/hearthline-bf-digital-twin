# Prompt pack

Paste these into Claude Code one at a time. Stay in plan mode for `00`. Review the design documents before `01`. Do not paste the next prompt until the current phase's tests pass and the gaps are written down.

Each prompt assumes [../CLAUDE.md](../CLAUDE.md) is loaded.

## Order

| Prompt | Produces | Stop when |
|---|---|---|
| [00-kickoff-architecture.md](00-kickoff-architecture.md) | Design docs only | A person has accepted the phase cut |
| [01-phase1-foundation.md](01-phase1-foundation.md) | Registries, envelope, capability API, audit, 2D shell | EVRAZ production capability is `not_testable` |
| [02-phase2-ingestion.md](02-phase2-ingestion.md) | File import, quality, as-of reads | EVRAZ checksum and row counts match the profile |
| [03-phase3-physics.md](03-phase3-physics.md) | Steady balances with input contracts | EVRAZ does not grow a coke rate or a tonne series |
| [04-phase4-dynamic-twin.md](04-phase4-dynamic-twin.md) | Stepper, filter, replay, scenarios | Future silicon cannot move the filtered state |
| [05-phase5-lags-and-ml.md](05-phase5-lags-and-ml.md) | Lags, persistence, LightGBM, two residuals | EVRAZ silicon card shows a computed persistence RMSE |
| [06-phase6-observability-mystery.md](06-phase6-observability-mystery.md) | Seven gates | EVRAZ does not invent a tonne cause |
| [07-phase7-anomaly-sensitivity.md](07-phase7-anomaly-sensitivity.md) | Charts and alarms | Tennessee Eastman delay is written down |
| [08-phase8-inverse-optimizer.md](08-phase8-inverse-optimizer.md) | Audit and blocked setpoints | Flotation test passes and EVRAZ blast is not a silicon lever |
| [09-phase9-root-cause.md](09-phase9-root-cause.md) | Waterfall and signatures | Missing inputs return `inconclusive` |
| [10-phase10-experience.md](10-phase10-experience.md) | Workspaces, 2D authority, progressive 3D | No-WebGL path still decides |
| [11-phase11-live-connector-and-modelops.md](11-phase11-live-connector-and-modelops.md) | Read-only feed and model promotion | A write-shaped call is rejected |
| [12-phase12-real-data-handoff.md](12-phase12-real-data-handoff.md) | Plant capability report and commissioning | The report lists what this extract cannot support |

The public EVRAZ files are already in `data/public/evraz-zsmk-2013-2016/`. Phase 02 loads them. It does not re-download them unless the checksum fails.

## Review questions

After 00: Do geometry, campaigns, and the event envelope exist as tables, or only as furnace averages?

After 02: Does an as-of read ignore a late laboratory result?

After 04: Which states are `not_observable` on EVRAZ?

After 05: What is the effective sample size, and did the embargo match the decorrelation time?

After 08: Which variables are `not_identified`, and is that shown?

## Knowledge each phase reads

| Phase | Read first |
|---|---|
| 00, 01 | `knowledge/README.md`, `13-parameter-tiers.md`, `15-data-time-and-provenance.md` |
| 02 | `15-data-time-and-provenance.md`, `data/public/evraz-zsmk-2013-2016/PROFILE.md` |
| 03 | `02-derived-indices.md`, `03-physics-equations.md`, `11-pending-validation.md`, `13-parameter-tiers.md` |
| 04 | `14-dynamic-twin-model.md`, `16-twin-commissioning-and-acceptance.md` |
| 05 | `07-ml-literature.md`, `08-lag-reference.md`, EVRAZ `PROFILE.md` |
| 06 | `04-hidden-state-mechanisms.md`, `05-failure-mode-catalog.md`, `13-parameter-tiers.md` |
| 07 | `05-failure-mode-catalog.md`, `07-ml-literature.md`, `10-datasets-and-benchmarks.md` |
| 08 | `09-confounding-and-causality.md`, `03-physics-equations.md` |
| 09 | `04-hidden-state-mechanisms.md`, `05-failure-mode-catalog.md`, `06-plant-case-studies.md`, `09-confounding-and-causality.md` |
| 10 | `CLAUDE.md`, `16-twin-commissioning-and-acceptance.md` |
| 11 | `15-data-time-and-provenance.md` |
| 12 | `DATA_REQUEST.md`, `13-parameter-tiers.md`, `16-twin-commissioning-and-acceptance.md` |
