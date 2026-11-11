# Dynamic twin model

This is a reduced-order, multi-zone, differential-algebraic model. It is not a CFD furnace. Per-tonne indexes are reports. Integration uses absolute SI inventories and rates.

## Zones and coordinates

Zones, top to bottom: stockline, upper shaft, lower shaft, cohesive zone, raceway, hearth. Gas flows up. Solids and liquids flow down. Geometry is the configured profile: height and diameter at each station, tuyere count, elevation, and angle, stave layout, and taphole elevation. If geometry is missing, playback of measured tags can still run. Zone positions stay `blocked_missing`.

## State vector

Integrate these when their observation contract in `13-parameter-tiers.md` and the observability test both allow it.

| Symbol | State | Unit |
|---|---|---|
| `M_fe,z` | Iron inventory by zone | kg |
| `M_c,z` | Coke carbon inventory by zone | kg |
| `A_b` | Burden age distribution, FIFO from the stockline | h |
| `U_z` | Thermal energy of zone solids and liquids | J |
| `n_g,z` | Gas component amounts, CO, CO₂, H₂, H₂O, N₂ | mol |
| `L_hm`, `L_slag` | Hearth hot-metal and slag mass | kg |
| `I_alk`, `I_zn` | Relative alkali and zinc ledger | kg |
| `mode` | Discrete operating mode | enum |

Algebraic variables, solved inside a step or held from the last valid measurement: pressure drop split, gas utilisation, raceway flame temperature, slag basicity. Raceway flame temperature uses the AIST form in `03-physics-equations.md` when the inputs exist, otherwise `not_run`.

Do not integrate an absolute scaffold thickness, deadman voidage, unburnt-char inventory, or cohesive-zone height until a plant observation model passes the commissioning gate. Until then those quantities are relative indicators with status `not_observable` for the absolute value.

## Inputs

`u` manipulated: blast volume, hot-blast temperature, oxygen flow, injectant flows, coke and ferrous batch weights, top-pressure setpoint, charging program. `d` disturbances: moisture, coke and sinter analyses, ore Fe, ambient humidity, barometric pressure. Missing members stay missing. Literature lags from `08-lag-reference.md` are priors on transport delay, not the plant's time constants. PCI has two delay paths. Burden age is the FIFO, so residence time changes when production rate changes.

## Closures

Every closure used in a step has a row: equation id, source, validity range, calibration method, and behaviour when pending. Pending ids in `11-pending-validation.md` do not receive a guessed coefficient. The step skips the dependent output and returns `pending_validation`.

| Closure | Source | If unavailable |
|---|---|---|
| Element balances Fe, C, O, N, H | `03-physics-equations.md` | Step rejected if a required flow exists and the balance cannot close |
| Zone heat balance | Same, enthalpies pinned in tests | `not_run` for zone temperature |
| Ergun or measured pressure drop | Ergun when voidage is configured; otherwise the measured drop is an input | Do not invent voidage |
| Gas utilisation | Measured CO and CO₂, else `not_run` | Do not fill from equilibrium alone and call it measured |
| Rist line | Bailera coefficients after the fixture passes | Reporting only |
| Liquid drainage | Event-driven cast weights | Hearth level `not_estimable` without weights and geometry |
| Residual correction | Phase 5, bounded | Off outside the validated density |

The forecast residual and the decision residual are different functions. What-if applies only the decision residual, and only inside the envelope. A correction may change a named source term or a named parameter. It may not add mass or energy.

## Solver

Gas residence is seconds, burden residence is hours, thermal memory is longer than 8 hours, and alkali memory is weeks. Use a multirate, event-aware solver. Fast gas composition may be algebraic when the sample interval cannot see it. Events are charges, casts, stove changes, and mode changes.

Each accepted step enforces non-negative inventories, gas mole fractions on the simplex, and closure of Fe, C, O, N, H, and energy within a stated tolerance. The interactive mode must reproduce a slower reference mode within declared trajectory, closure, and uncertainty tolerances on a named machine before the one-second-per-simulated-day budget counts. See `16-twin-commissioning-and-acceptance.md`.

## Operating modes

`normal`, `startup`, `shutdown`, `banked`, `blow_in`, `maintenance`, `recovery`. Mode is an input from delay codes when those codes exist, otherwise it is inferred only from blast flow and labelled inferred. Recommendations are off outside `normal`. A campaign boundary reinitialises slow states. A failed step keeps the last good checkpoint and surfaces `error`.

## Estimator

Benchmark a constrained extended Kalman filter and a moving-horizon estimator. Pick with a written comparison, not by default. Specify the observation map, process covariance, measurement covariance, bounds, charge and cast resets, outlier rejection, and divergence rules. Report normalised innovation squared on a holdout.

Before a state is shown, it passes a structural observability check for this sensor set and an empirical withholding test: hide the sensor, see whether the state is still determined. Failure yields `not_observable`. A missing sensor widens covariance only when the state remains observable through other measurements.

Store two trajectories. The filtered state uses only measurements with `available_at` at or before the timestamp. The smoothed state may use later measurements and is labelled retrospective. Validation, ghost comparison against what was knowable, and scenario branches start from the filtered state.

## Scenarios and manifests

A scenario is immutable once run. It records the filtered snapshot, future charge and cast schedule, disturbance assumptions, ramps, model version, seed, and envelope result. Editing creates a new id. The same scenario id and manifest hash rerun to the same trajectory.

The run manifest, written from phase 1, records raw-data hashes, as-of time, transforms, geometry version, tag map, conventions, parameters, solver tolerances, estimator covariance, artifact ids, container digest, and seed.

## Independent truth

The perturbed generator used in tests is a separate implementation. It adds structural mismatch, correlated noise, bias, missingness, and events the twin does not contain. Matching that generator is the state-recovery test. Matching the twin to itself is only a regression test.

## Public furnace

On EVRAZ ZSMK the measurable twin is blast, oxygen, pressures, pressure-drop split, top-gas CO₂ and H₂, top and peripheral temperatures, ore-to-coke ratio, and cast silicon. Zone inventories that need coke rate, Fe content, or cast weight stay `not_observable`. Do not back-calculate tonnes from the 4,500 t/day nameplate.
