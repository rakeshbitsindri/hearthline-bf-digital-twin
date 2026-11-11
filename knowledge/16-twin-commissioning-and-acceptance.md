# Commissioning and acceptance

A phase can be coded and still not be an approved twin. Promotion is a separate, audited decision.

## Maturity

1. Offline balances and calibration on fixtures, including the EVRAZ pressure-drop identity.
2. Purged walk-forward holdout against persistence and LightGBM.
3. Sensor-withholding tests for every state that is shown.
4. Independent synthetic stress: structural mismatch, bias, missingness, and extra events.
5. Blind replay of the plant incident casebook, after two engineers have labelled cause, evidence, onset, and confidence and a third has adjudicated disagreements. Labels stay hidden from training.
6. Shadow operation on the live capture, with no recommendations shown as actionable.
7. Advisory pilot.
8. Approved use inside the limits named in `CLAUDE.md`.

No stage promotes itself. A campaign change, a sensor replacement, or a failed innovation test returns the affected states to the previous stage.

## Performance budgets

Name the device, browser, scene, and data window in the test report. Report p75 and p95.

| Budget | Target |
|---|---|
| Interactive 24-hour simulation | Under 1 second, after it matches the reference solver |
| Shell usable | Under 2 seconds |
| Full 3D | 60 frames per second |
| Reduced 3D | 30 frames per second |
| No WebGL | All decision views still work |
| Soak | 8–12 hours without unbounded memory growth |

Server-sent events detect a sequence gap and resync from a snapshot. Context loss on the 3D view falls back to 2D without discarding the selected time.

## Acceptance matrix

The twin is not called functioning until these pass on the named build:

- Equation fixtures, including Geerdes carbon split and Bailera ω at one temperature.
- Steady state recovered from a flat input.
- Per-step Fe, C, O, N, H, and energy closure, positivity, and simplex constraints.
- Timestep refinement against the reference solver.
- Charge, cast, and outage events.
- Lag step responses consistent with calibrated delays, not with a single global lag.
- Late and out-of-order measurements obey `available_at`.
- Bias, freeze, and dropout are rejected or down-weighted before assimilation.
- Observability failures suppress the state.
- Independent-truth recovery stays inside the stated error.
- Same manifest replays the same trajectory.
- Interval coverage meets the nominal level on the last walk-forward fold.
- Open-loop forecast beats persistence and is reported beside LightGBM.
- Missing inputs return the capability status instead of a filled value.
- Stale and disconnected screens keep timestamps.
- Role denial is tested.
- A non-production connector test shows plant writes are impossible.
- WCAG 2.2 AA checks that are automated, plus a keyboard pass.
- No-WebGL and a long session.

## Model promotion

Challengers run in shadow. A person promotes them. Rollback restores the previous manifest and reinitialises state when the manifest says to. Transfer to another furnace requires a local holdout on that furnace. It is never automatic.

## After a recommendation

Store disposition, whether execution was later confirmed, the observed outcome, confounders, and aborts. Do not treat accept as executed. This table is how value is judged later. It is not a control log.

## People

Phase 12 asks for sign-off from the data owner, instrumentation, OT security, metallurgy, operations, and safety. Confusion between measured, inferred, historical, and scenario values blocks release.
