# Build plan

Session rules are in `CLAUDE.md`. Domain notes are in `knowledge/`. Implementation order is in `prompts/`. This file is the map. It does not override `CLAUDE.md`.

## Product

A read-only advisory twin. A reduced-order multi-zone model steps inventories in absolute units. A state estimator updates only states that are observable with the sensors on hand. Two-dimensional engineering views are the numbers. A 3D cutaway is a situational view drawn from the same state, loaded afterward, and omitted entirely when WebGL is unavailable.

The plant question is a production drop at unchanged setpoints. The diagnosis runs seven gates, cheapest first, and may end at `not_testable` or `inconclusive`. Inverse setpoints require an identifiability audit. Missing site limits or a failed audit block the recommendation. An engineering trial is a dossier for the plant's own change process.

## Data

No major US, Chinese, or Indian producer has published a furnace historian. The bundled series is EVRAZ ZSMK, hourly, 1 January 2013 through 18 May 2016, CC BY 4.0, profiled in `data/public/evraz-zsmk-2013-2016/PROFILE.md`.

Use it for ingestion, bad-value handling, the pressure-drop identity, circumferential temperatures, and a silicon forecast that must beat a persistence RMSE of about 0.120 wt%. Do not use it for tonnes, PCI, a separate coke rate, hearth level, or a blast setpoint. Those stay `not_testable` or `not_observable`.

Plant history, when it arrives, is appended through the same event envelope. A read-only connector in the industrial DMZ can backfill whatever the historian still holds and then keep the tail. Replay of 2013–2016 is never labelled live.

## Phases

| Phase | Prompt | Result |
|---|---|---|
| 0 | `prompts/00-kickoff-architecture.md` | Design documents only |
| 1 | `01` | Registries, audit, capability API, 2D shell |
| 2 | `02` | Import EVRAZ, quality, as-of reads |
| 3 | `03` | Steady physics with explicit missing inputs |
| 4 | `04` | Dynamic stepper, filter, replay |
| 5 | `05` | Lags and residuals |
| 6 | `06` | Mystery gates |
| 7 | `07` | Alarms and sensitivity |
| 8 | `08` | Optimiser, blocked when not identified |
| 9 | `09` | Root cause |
| 10 | `10` | Workspaces and progressive 3D |
| 11 | `11` | Read-only connector and model promotion |
| 12 | `12` | Plant extract, shadow mode, sign-off |

## Out of scope

Writes to a PLC, DCS, or historian. Invented metallurgical coefficients. Treating the public series or the synthetic generator as a calibrated plant. A CFD furnace. Redis and TimescaleDB unless a measurement shows they are needed.
