# 08 — Inverse optimisation

Read `knowledge/09-confounding-and-causality.md` and section 9 of `knowledge/03-physics-equations.md`. Run the flotation acceptance test in `knowledge/10-datasets-and-benchmarks.md` before any setpoint endpoint is enabled.

## Decision model

Separate from the forecast. Features are causal parents only. The phase 5 decision residual may adjust a source term inside the envelope. Descendants of the target are excluded.

## Audit

For each manipulated variable, estimate the effect with backdoor adjustment, g-computation, and double machine learning. Block-bootstrap. Block length at least the decorrelation time. Status `identified` only if all three agree in sign and the interval excludes zero. Otherwise `not_identified`, with the suspected confounder named.

On EVRAZ, the audit must be allowed to return `not_identified` for blast versus silicon. The flat change-correlation in `PROFILE.md` is the expected direction. Do not ship a setpoint that lowers blast to raise silicon.

## Flotation gate

The three estimators on the public flotation record, hourly. The test asserts a negative interventional pH effect, a near-zero partial dependence, amine not identified, and the concentrate iron assay flagged as leakage. If this fails, the optimiser returns 503.

## Search

Decision variables are the identified ones only. Others stay at the current value. Objectives: production when it exists, fuel rate when coke and injectants exist, stability penalty. Constraints: site-approved limits, quality bands, five physics ceilings, pathwise check through the phase 4 simulator. Envelope is a density in the joint manipulated space, plus a trust region. Infeasible targets return the binding ceiling. Missing limits, stale data, `not_observable`, or `not_identified` block a routine recommendation. An engineering-trial response is a dossier: rationale, uncertainty, bounds, monitoring, abort criteria. It does not authorise the change.

Wording follows `knowledge/09-confounding-and-causality.md`. `claim_level` is `association` or `identified_effect`.

## UI

Current, recommended, delta, held variables, claim level, interval, ceiling, path from the simulator. EVRAZ page explains that setpoints are blocked and why.

## Exit tests

- Flotation assertions.
- EVRAZ blast is not recommended as a silicon lever.
- A target above all ceilings returns infeasible.
- A point outside the density envelope is rejected.
- Same seed, same result.
- The job is asynchronous.
