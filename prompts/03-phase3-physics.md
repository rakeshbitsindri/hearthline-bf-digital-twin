# 03 — Steady physics

Read `knowledge/02-derived-indices.md`, `knowledge/03-physics-equations.md`, `knowledge/11-pending-validation.md`, and `knowledge/13-parameter-tiers.md`. Pure functions. No optimiser and no learned model.

## Ship, each with a test

Iron, carbon, oxygen, nitrogen, sulphur, and alkali balances. Geerdes reference split is a fixture. Slag mass and iterative flux. Heat-balance terms with cited enthalpies. Cooling loss from water flow and temperature rise. PV-02 stays off.

Rist line with Bailera coefficients. The first test recomputes ω at one temperature and fails if the power-of-ten expansion is wrong.

RAFT, AIST/Geerdes form, labelled constant blast volume. Ergun and Nakamura when geometry exists. Permeability variants, each result carrying `variant_id` and `direction`. Gas utilisation only when CO and CO₂ both exist. Urbain, Riboud, and NPL viscosity. Sulphur partition, both cited forms. Geerdes replacement ratio. Five production ceilings. The feasible rate is the minimum, with the binding ceiling named.

Each function declares required inputs and returns `not_run` plus the missing names. It does not fill from a typical value.

On EVRAZ, CO₂ without CO yields `not_run` for ηCO. Ore-to-coke ratio is not converted into a coke rate. The pressure-drop identity is a fixture against the imported hours.

Pending ids PV-01 through PV-09 return `pending_validation`. Silicon has no default equation.

## Exit tests

- Fixtures pass from a cold import.
- An inconsistent balance returns the imbalance.
- EVRAZ rows do not produce a coke rate or a tonne figure.
- Convention flags appear on RAFT and permeability.
