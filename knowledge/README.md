# Blast furnace knowledge base

Compiled 8 November 2026 from published ironmaking literature, plant technical reports, and conference papers. This folder is the domain reference for the prompt pack in `../prompts/`.

These notes are a literature compilation, not a validated plant model. Coefficients marked pending in [11-pending-validation.md](11-pending-validation.md) must stay behind a documented interface until a metallurgist signs them off. Do not treat a number in these files as a setpoint.

## How to read the evidence grades

- **[P]** peer-reviewed paper, conference paper, or regulatory investigation.
- **[C]** company or vendor publication. Self-reported, usually unaudited.
- **[T]** trade press.
- **[I]** inference drawn from the sources, not a claim inside any one paper.

## Files

| File | What it holds |
|---|---|
| [01-parameter-catalog.md](01-parameter-catalog.md) | Measured parameters by furnace area: tag names, units, typical ranges for a 3000–5500 m³ furnace, instrument, and the role each parameter plays. |
| [02-derived-indices.md](02-derived-indices.md) | Productivity, fuel rate, gas utilisation, permeability variants, RAFT, raceway, slag, residence time. Conflicting conventions are flagged. |
| [03-physics-equations.md](03-physics-equations.md) | Implementable balances and correlations with symbols, units, assumptions, and sources. |
| [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) | Why production can fall while the blast sheet looks identical. Twelve mechanisms, signatures, and time scales. |
| [05-failure-mode-catalog.md](05-failure-mode-catalog.md) | Canonical failure modes with early-warning signatures and corrective actions. |
| [06-plant-case-studies.md](06-plant-case-studies.md) | Named plant cases, benchmark operating numbers, and commercial expert systems. |
| [07-ml-literature.md](07-ml-literature.md) | What data-driven BF models have actually achieved, and which published accuracies do not survive scrutiny. |
| [08-lag-reference.md](08-lag-reference.md) | Published input-to-output delays and how to estimate them. |
| [09-confounding-and-causality.md](09-confounding-and-causality.md) | Why a model trained on operator-controlled data recommends the operator's policy, and what to do about it. |
| [10-datasets-and-benchmarks.md](10-datasets-and-benchmarks.md) | Public datasets that can exercise the pipeline before plant data arrives. |
| [11-pending-validation.md](11-pending-validation.md) | Equations whose coefficients could not be established from open sources. |
| [12-references.md](12-references.md) | Authoritative books, journals, and open-access channels. |
| [13-parameter-tiers.md](13-parameter-tiers.md) | Acquisition priority versus per-feature capability contracts. |
| [14-dynamic-twin-model.md](14-dynamic-twin-model.md) | Reduced-order dynamic model, estimator, scenarios, and what the public furnace cannot identify. |
| [15-data-time-and-provenance.md](15-data-time-and-provenance.md) | Source authority, event time, revisions, late data, and the read-only connector boundary. |
| [16-twin-commissioning-and-acceptance.md](16-twin-commissioning-and-acceptance.md) | Maturity ladder, performance budgets, and the acceptance matrix. |

## Role classification used throughout

Every parameter belongs to exactly one role. The schema and the mystery protocol both depend on this.

| Role | Meaning | Examples |
|---|---|---|
| `manipulated` | Operator or control system sets it. | Blast volume, blast temperature, oxygen enrichment, PCI rate, coke rate, top pressure, charging program. |
| `disturbance` | Enters the furnace and is not chosen as a setpoint. | Coke CSR/CRI, sinter RDI and FeO, ore alumina, burden moisture, blast humidity, ambient conditions, alkali and zinc input. |
| `state_response` | The furnace answering. Often already logged, rarely read as a group. | Pressure-drop split, permeability indices, gas utilisation, stave temperature variance, heat loss, burden descent index, top gas temperature. |
| `outcome` | What the plant is trying to hit. | Hot metal production, hot metal temperature, silicon, sulphur, fuel rate. |
| `derived_latent` | Computed, not measured. Must be labelled as inferred. | RAFT, alkali inventory ledger, hearth liquid level, scaffold thickness estimate, direct reduction ratio, shaft efficiency. |
