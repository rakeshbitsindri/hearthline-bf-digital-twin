# 04 — Dynamic twin

Read `knowledge/14-dynamic-twin-model.md` and `knowledge/16-twin-commissioning-and-acceptance.md`. This phase steps state forward. It does not train the residual model. That is phase 5.

## Build

1. A DAE stepper in absolute kilograms, moles, and joules. Per-tonne numbers are outputs. Closures that are pending or missing return `not_run` for the dependent state and still advance the states that are determined.

2. Multirate, event-aware solver with a slower reference mode. Interactive mode is accepted only when trajectories, closure, and uncertainty match the reference within the tolerances written in the test. Positivity, simplex, and Fe, C, O, N, H, energy closure are checked every step.

3. Operating-mode state machine. Recommendations are not emitted here at all. Mode changes from blast-off on EVRAZ are labelled inferred.

4. Estimator interface with at least one implemented filter and a recorded comparison note if the second is not implemented yet. Bounds, cast resets, outlier rejection, and normalised innovation squared. States that fail the withholding test are `not_observable`.

5. Persist filtered and smoothed trajectories separately. Scenario branches and ghost comparison use the filtered state. `available_at` is honoured. A fixture inserts a future silicon result and shows the filtered state unchanged.

6. Checkpoints, rewind, and deterministic replay from the run manifest. Same hash, same trajectory.

7. Scenario contract: draft, run, immutable result. Edit creates a new id. Store assumptions and envelope status.

8. Independent perturbed generator in a separate module. Tests include bias, a missing tag, and an event the stepper does not model. A same-model round trip is marked as a software test, not a recovery claim.

9. UI slice: time scrubber, filtered-versus-measured ghost on tags that exist, and a banner. EVRAZ replay shows 2013–2016. Speed control does not relabel the run as live. Zone inventories that lack coke and Fe stay hidden.

## Exit tests

- Pressure-drop identity still holds after a step on EVRAZ inputs.
- A 24-hour EVRAZ slice replays from the manifest.
- Future silicon does not move the filtered state.
- Hearth level on EVRAZ is `not_estimable`.
- Reference-solver comparison is stored next to the timing number.
