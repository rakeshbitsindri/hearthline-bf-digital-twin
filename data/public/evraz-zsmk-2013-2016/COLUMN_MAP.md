# Column map

Sheets in `1_blast_furnace_data_first_dataset.xlsx`: `symbols`, `data`, `Si`.

| Source column | Registry concept | Unit as published | Role | Capability note |
|---|---|---|---|---|
| `dt` | event time | timestamp, no zone stated | — | Treat as furnace local time until a zone is confirmed. Do not invent UTC. |
| `Fb` | Blast volume | m³/min | manipulated | Not stated as Nm³. |
| `Ph` | Hot blast pressure | kgf/cm² | state_response | |
| `Pc` | Cold blast pressure | kgf/cm² | state_response | |
| `Tc` | Cold blast temperature | °C | state_response | Instrument span 0–150 °C. |
| `Fo` | Oxygen flow | m³/h | manipulated | Not enrichment percent. |
| `dP` | Total pressure drop | kgf/cm² | state_response | Equals `dPu + dPl` in this file. |
| `dPu` | Upper pressure drop | kgf/cm² | state_response | |
| `dPl` | Lower pressure drop | kgf/cm² | state_response | |
| `Pt` | Top pressure | kgf/cm² | manipulated or response | The file does not say which. Map as state_response until an operator log says it is a setpoint. |
| `Th` | Hot blast temperature | °C | manipulated | |
| `CO2` | Top gas CO₂ | vol% | state_response | CO is absent, so ηCO is `not_run`. |
| `H2` | Top gas H₂ | vol% | state_response | |
| `Tt1`–`Tt4` | Top gas temperature by offtake | °C | state_response | Positions not in the file. |
| `Tp1`–`Tp10` | Peripheral gas temperature | °C | state_response | Angles not in the file. |
| `R` | Ore-to-coke ratio | t/t | derived_latent | Not a separate coke rate. |
| `Si` | Hot metal silicon | wt% | outcome | Separate sheet. Cast time, not the hour bucket. |

`2_blast_furnace_data_second_dataset.xlsx` repeats a 200-hour extract. Its `Si` sheet adds `State of blast furnace` with 127 labels. Those labels are a demonstration dictionary, not a training prior for rare events.

Furnace configuration, assumed from the paper and labelled assumed: working volume 2,000 m³, nameplate 4,500 t/day. There is no production column.
