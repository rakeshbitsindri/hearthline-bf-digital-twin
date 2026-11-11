# Acquisition priority and capability contracts

Acquisition priority says what to ask the plant for first. It does not decide whether a feature runs. A feature runs only when its own contract is met for that furnace, campaign, time window, and use case.

## Statuses

| Status | Meaning |
|---|---|
| `ready` | Required inputs, quality, resolution, freshness, and, where relevant, observability and identifiability are met. |
| `degraded` | The feature can run. An optional or alternative input is missing, so uncertainty is wider and the screen says what is missing. |
| `blocked_missing` | A required input or an acceptable alternative group is absent. |
| `blocked_bad_quality` | The input exists and fails the quality rule for this feature. |
| `stale` | The newest accepted sample is older than the feature's freshness limit. Last-known values stay visible with their timestamp. |
| `backfilling` | History is still being loaded. Results that depend on a complete window wait. |
| `not_observable` | The state cannot be distinguished with this sensor set. Do not plot a number. |
| `not_identifiable` | An effect cannot be separated from operator policy or an unmeasured confounder. |
| `not_testable` | The comparison the feature needs was not recorded. |
| `pending_validation` | The equation or coefficient is in `11-pending-validation.md`. |
| `not_run` | The function refused to compute. The response names the missing inputs. |

## Acquisition priority

**Critical to request.** Without these, the base balance and playback stay blocked: furnace geometry, blast volume, hot blast temperature, oxygen enrichment or oxygen flow, injectant rates, coke rate, ferrous burden weights with Fe content, and at least one production route. Hot metal temperature and silicon are both requested. They are not substitutes. Silicon needs a site-fitted observation model before it can stand in for temperature.

**Important.** Missing these degrades specific features: top gas CO, CO₂, and H₂; shaft pressures; stave temperatures; slag chemistry; coke and sinter certificates; cooling-water flow and temperature rise; delay codes.

**Optional enrichment.** Per-tuyere flows, within-hour statistics, probe profiles, ambient conditions, alkali and zinc analyses, per-taphole chemistry, calibration events.

## Feature contracts

Each row is the minimum. A richer sensor set can only improve a `ready` feature. It cannot invent a state the contract says is `not_observable`.

| Feature | Required | Freshness while live | If missing |
|---|---|---|---|
| Hourly playback of measured tags | Timestamp, unit, and the tag itself | 2 hours for hourly tags; 5 minutes once minute capture exists | `blocked_missing` for that tag only |
| Provisional production display | One named production route | 6 hours | `blocked_missing` |
| Verified shortfall | At least two production routes, or one route plus the allocation rule and fleet-inventory note | The window under study | `not_testable` at gate 0 |
| Pressure-drop identity | `dP`, `dPu`, `dPl` in one unit | 2 hours | `not_run` |
| Gas utilisation | Dry CO and CO₂ | 2 hours | `not_run` |
| Circumferential gas view | At least four peripheral temperatures at known angles | 2 hours | `not_testable` for asymmetry |
| Silicon forecast | Cast silicon with sample time and `available_at` | Next cast | `blocked_missing` |
| Heat loss | Cooling-water flow and temperature rise on the circuit | 2 hours | `not_run` |
| Alkali ledger | Alkali input and slag or dust alkali | Certificate age under 14 days | Relative ledger only if one side exists; otherwise `not_testable` |
| Hearth level | Reconciled cast weights, taphole events, hearth geometry | Per cast | `not_estimable` |
| Inverse setpoint | Decision-model parents, site-approved limits, envelope, identifiability `identified` | Inputs fresher than their own limits | Blocked, not guessed |
| Public EVRAZ reference | The files in `data/public/evraz-zsmk-2013-2016/` | Not live | Production, PCI, coke rate, balances, and inverse stay `not_testable` |

Quality rules live on the parameter, not only on the feature: instrument range, frozen-value detection, and the reconciliation residual. A value outside the instrument range is `blocked_bad_quality` for any calculation that would treat it as a measurement. It remains visible in the quality view.

## Defaults

A missing measurement stays missing. The only defaults are configuration constants: thermal-reserve temperature, standard-coke carbon when the certificate is absent, and permeability variant. Each default is stored as `assumed`, with the citation and the person who accepted it. The public EVRAZ furnace may assume the paper's 2,000 m³ working volume and 4,500 t/day nameplate as configuration, labelled assumed from Trofimov 2025, and must not invent a production time series from the nameplate.

## Matrix

Recompute on every upload and every connector sync. Persist furnace id, campaign id, window start, window end, feature id, status, missing tags, and the data revision hash. The status page is the matrix. A feature call reads the matrix. It does not re-decide in the UI.
