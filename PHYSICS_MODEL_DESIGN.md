# Physics

Shipped now, each returning `not_run` when an input is absent:

- Pressure-drop identity: `dPu + dPl - dP`.
- Gas utilisation only when both CO and CO₂ exist. EVRAZ has CO₂ only, so ηCO is `not_run`.
- Ore-to-coke ratio is passed through. It is not converted into a coke rate.
- RAFT is `not_run` without blast moisture and enrichment percent. Oxygen flow is not rewritten as enrichment.
- Five production ceilings are `not_run` without a tonne series.

Pending coefficients PV-01 through PV-09 are not given numbers. The Geerdes and Bailera fixtures remain in `knowledge/03-physics-equations.md` for the later full balance module. This build does not invent those balances from the EVRAZ columns.
