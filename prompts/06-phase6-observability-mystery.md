# 06 — Observability and the production mystery

Read `knowledge/04-hidden-state-mechanisms.md`, `knowledge/05-failure-mode-catalog.md`, and `knowledge/13-parameter-tiers.md`. Implement gates as result objects.

## Protocol

Given a window below a stated baseline, run the gates in order. A gate that explains the gap stops the causal claim. Later gates may compute as context.

**Gate 0.** Compare production routes. If only one route exists, status is provisional, not verified. If blast reduction accounts for the tonnes and a reason code says the cut was commanded, return `explained_external`. If the reason code is absent, return `not_testable` for the commanded-versus-forced question and still show the blast cut. On EVRAZ there is no tonne series: gate 0 is `not_testable` for a production shortfall. Do not invent tonnes from the nameplate.

**Gate 1.** Compare lag-aligned active rates, then within-hour distribution and circumferential spread. EVRAZ has no within-hour statistics. Circumferential peripheral temperature is present. A mean match with a range mismatch can return `explained_input_distribution` for a temperature question. Say that production was not the target.

**Gate 2.** Coke, sinter, ore, moisture, humidity. Absent on EVRAZ: `not_testable`.

**Gate 3.** Pressure split, permeability if defined, gas utilisation if CO exists, heat loss, stave excursion, burden descent. EVRAZ can run the pressure identity and the peripheral spread. ηCO is `not_run`.

**Gate 4.** Alkali, zinc, char, liquid level, deadman. Without analyses and cast weights: `not_testable` or `not_estimable`. Do not fill a ledger with zeros.

**Gate 5.** Residual structure from the phase 5 model: multi-day autocorrelation, shift clustering, trend, sector pattern, calibration step. The class is the output.

**Gate 6.** Rank missing discriminators. `inconclusive` is a successful status.

## Twin finder

Distance on manipulated and disturbance variables that exist. Pairs need a production difference only when production exists. On EVRAZ, pairs may be defined on silicon or pressure drop, and the page says so.

## UI

Gate strip, evidence table, side-by-side windows. Public-reference banner. No sentence that the furnace caused a tonne loss on EVRAZ.

## Exit tests

- EVRAZ window does not return a tonne cause.
- A synthetic commanded-cut scenario, from the independent generator, returns `explained_external` when reason codes exist.
- A pair that matches on means and differs on peripheral range returns the distribution status.
- A window with no contrast returns `inconclusive`.
