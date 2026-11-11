# 00 — Architecture only

Read `CLAUDE.md`, `knowledge/README.md`, `knowledge/13-parameter-tiers.md`, `knowledge/14-dynamic-twin-model.md`, `knowledge/15-data-time-and-provenance.md`, and `knowledge/16-twin-commissioning-and-acceptance.md`. Also read `data/public/evraz-zsmk-2013-2016/PROFILE.md`.

Do not write application code. Produce design documents and stop.

## Documents

1. `ARCHITECTURE.md` — components, data flow, measured versus inferred, background jobs, read-only plant boundary.
2. `DATABASE_DESIGN.md` — effective-dated furnace, campaign, asset, instrument, tag alias, geometry, sensor position, event envelope, revisions, capability matrix, run manifests, recommendation audit.
3. `PHYSICS_MODEL_DESIGN.md` — which steady equations ship in phase 3, which stay pending, and the fixtures.
4. `TWIN_DESIGN.md` — the DAE state, closures, solver, estimator benchmark, filtered versus smoothed state, scenario contract, and the EVRAZ limits.
5. `ML_ARCHITECTURE.md` — persistence, LightGBM, two residuals, purged walk-forward, conformal intervals.
6. `OBSERVABILITY_DESIGN.md` — seven gates, capability-aware `not_testable`, twin finder.
7. `OPTIMIZATION_DESIGN.md` — identifiability, three estimators, density envelope, trial dossier, wording rules.
8. `PARAMETER_TIERS.md` — feature contracts copied from `knowledge/13-parameter-tiers.md` into the schema.
9. `CONNECTOR_DESIGN.md` — zones, DMZ replica, fixed read profiles, vault, capture-only versus advisory serving.
10. `DATA_TIME_PROVENANCE.md` — envelope, `available_at`, as-of replay.
11. `UX_DESIGN.md` — use the project's design skill. Four workspaces: Observe, Investigate, Decide, Govern. Role journeys for shift monitoring, shortfall investigation, replay, scenario review, accept/reject, handover, and data-quality remediation. Runtime states. 2D authority and progressive 3D. Control-room and laptop first. WCAG 2.2 AA.
12. `API_DESIGN.md` — ingest, map, capability, balances, twin step, predict, diagnose, optimise, model cards. Diagnosis returns a gate result.
13. `COMMISSIONING_PLAN.md` — maturity ladder and sign-offs.
14. `E2E_ACCEPTANCE.md` — the matrix in `knowledge/16-twin-commissioning-and-acceptance.md` plus the browser flows: fresh, stale, disconnected, replay not labelled live, inconclusive diagnosis, scenario branch, no plant write, role denial, no-WebGL.
15. `IMPLEMENTATION_ROADMAP.md` — phases 1–12 aligned with `prompts/README.md`.
16. `DATA_DICTIONARY_TEMPLATE.md` — consistent with `DATA_REQUEST.md`.
17. `RISK_REGISTER.md` — start from `knowledge/11-pending-validation.md` and the EVRAZ gaps.

## Constraints

- Stack from `CLAUDE.md`. Do not add Redis, TimescaleDB, or PyTorch in the design unless a measurement forces it.
- Deployment is on-prem or industrial DMZ, with backup, Parquet retention, and no required public internet path at runtime.
- The public series is origin `public_reference`. Later plant data is origin `plant`. They do not overwrite each other.

## Exit

Stop after the documents. List questions a process engineer must answer. Do not start phase 1.
