# 12 — Plant data and commissioning

Use this prompt when a plant extract or an approved connector is available. Read `DATA_REQUEST.md`, `knowledge/13-parameter-tiers.md`, and `knowledge/16-twin-commissioning-and-acceptance.md`. Write the profile before retuning models.

## Profile

`docs/data-capability.md` records furnaces, campaigns, span, missing hours, timezone, roles populated, within-hour statistics, per-tuyere and per-stave coverage, production routes and their residual, certificate join rate, delay codes, commanded-versus-forced, clock skew, and tags that are constant. State what gate 0, the twin, and the optimiser can and cannot do.

## Ingest

Run the phase 2 recipe. Do not drop range failures. Reconcile Fe, C, N, O, and H where inputs exist. Recompute the envelope, effective sample size, and embargo from this file. Do not reuse the EVRAZ embargo.

## Models and twin

Walk-forward on this furnace. Publish persistence, LightGBM, and the hybrid at 1, 4, and 8 hours. If the hybrid does not beat persistence, serve persistence. Rerun the identifiability audit. Expect `not_identified` entries. Rerun observability tests before showing zone states.

## Episodes

For dates the plant names, run phases 6 and 9. Record the gate, the evidence, and the tests that were blocked. Keep an `explained_external` result. Compare signature matches with `knowledge/06-plant-case-studies.md` and keep the evidence grade.

Build the incident casebook: two qualified people label cause, evidence, onset, and confidence; disagreements are adjudicated; labels stay out of training.

## Commission

Follow the maturity ladder. Shadow mode comes before actionable recommendations. The advisory pilot includes the usability check: if a user confuses public, plant, replay, and scenario data, release stops.

Sign-off lines for data owner, instrumentation, OT security, metallurgy, operations, and safety. Update `RISK_REGISTER.md`. Do not raise a claim above the walk-forward card.

## Exit

The capability table answers, for this extract: tonne reconciliation, sub-hourly behaviour, raw materials, response-versus-mean, slow accumulators, eight-hour forecast, identified setpoints, and counterfactuals. Each cell is yes, partial, or no, with the missing column named.
