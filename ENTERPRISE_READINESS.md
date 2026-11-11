# Enterprise readiness assessment

Honest maturity review of the Hearthline blast furnace advisory digital twin, written against the standard a large iron and steel producer would actually apply before a plant trial. The project constitution in `CLAUDE.md` requires that a confident wrong claim is treated as worse than an honest inconclusive one, so this document is deliberately blunt.

## One line answer

Hearthline is a credible, unusually honest working prototype with real reduced order physics, a learned response layer, production conditioned Golden Ranges, and backward compatible shortfall attribution. It is not yet an enterprise grade plant system. It sits at roughly Technology Readiness Level 4 to 5 (validated on public reference data in a lab setting), and reaching a production deployment on a customer furnace is a Technology Readiness Level 7 to 9 activity that needs plant data, security hardening, operations engineering, and on furnace validation that no public dataset can stand in for.

The right way to pitch it is as a de risked starting point with a working engine and a validation discipline already built in, not as a finished product. That honesty is itself the competitive advantage, because most vendor demos hide exactly the gaps listed below.

## What is genuinely built today

These are real and verifiable in the repository, not slideware.

- Reduced order physics backbone: RAFT (AIST and Geerdes form), Rist carbon and oxygen balance, Ergun pressure drop, bosh gas, alkali and zinc recirculation, five productivity ceilings.
- Sensor reconciliation: physics is anchored onto the furnace's own instruments, so absolute values match the plant and only the response to a change is pure model. The pressure identity dP = dPu + dPl is held exactly.
- Evidence and capability discipline: every value carries an evidence class (measured, reconciled, estimated, simulated, assumed, unavailable) and every feature carries a capability status (ready, degraded, blocked, stale, not observable, not identifiable, not testable, pending validation).
- Learned layer: walk forward, purged, embargoed LightGBM silicon forecast that must beat a last cast persistence baseline before it is served, plus a lag aligned cross parameter response matrix learned from the active dataset.
- Coupled interactive simulator: 41 parameters, soft limited so a knob change never silently dies at a clip, with a 24 hour lag aware trajectory and cross parameter attribution.
- Production conditioned Golden Ranges for every parameter, with below and above warnings expressed as production risk in tonnes per day, and a backward compatible historical shortfall root cause explorer across the whole record.
- Inverse optimiser that returns a binding ceiling and refuses to invent an unidentified setpoint.
- Operating regime gate that suppresses absolute values off wind, during banking, and during blow in.
- Read only posture: the connector rejects any non read operation, there is no write path to any actuator, and an append only audit log records operator accept and reject.
- A five theme operator interface, a 3D cutaway, zone health triage, and fast sensor issue tracking.
- A test suite (21 tests) and a documented pending validation register (PV-01 to PV-10).

## What is missing for enterprise grade

Grouped by the gate a plant IT, OT, and metallurgy review would run. Status is honest.

### 1. Live plant data integration (the biggest gap)
- The historian connector is specified and the read only contract is enforced in code, but no live adapter to a real historian (OSIsoft PI, AVEVA, Wonderware, Aspen IP21, OPC UA, Modbus) is implemented. Today the system reads files.
- No minute level or sub minute ingestion. The public file is hourly, which hides slips, hangs, pressure spikes, tuyere events, and channeling precursors.
- No streaming path proven end to end against a real source. Server sent events are designed, not demonstrated against a plant feed.
- Scale: the model handles roughly 41 tags. A real furnace instrument list is hundreds to low thousands of tags.

### 2. Model validation on the target furnace
- Everything is validated on the EVRAZ ZSMK public reference (2013 to 2016), which is explicitly not this plant and not live.
- Several metallurgical coefficients remain pending validation (PV-01 to PV-10). RAFT and hot metal temperature cannot be served as absolute values on EVRAZ because the file lacks injectant, moisture, and hot metal temperature columns.
- No shadow mode track record, no incident casebook, no closed loop value measured against a persistence baseline on a real furnace.

### 3. Security, identity, and compliance
- No authentication or authorisation on the API today. Every route is open. Role based access and SSO (SAML, OIDC, LDAP) are not built.
- CORS is wide open and TLS termination is left to the host. Fine for a public demo, not for a plant.
- No secret vault integration, no network segmentation between the IT application tier and the OT read tier, no formal data classification.
- No SOC 2 or ISO 27001 posture, no penetration test, no formal threat model sign off.

### 4. Operations and reliability
- Single instance. No high availability, failover, horizontal scale, or load testing.
- Audit log is SQLite, which is correct for a prototype and wrong for multi user production. Configuration, runs, and facts belong in PostgreSQL, large extracts in Parquet and DuckDB.
- No application observability (metrics, tracing, structured logs, alerting), no CI and CD pipeline, no backup and disaster recovery, no infrastructure as code.

### 5. ModelOps
- Model cards exist but there is no model registry, no automated retraining, no production drift detection, no champion and challenger framework.

### 6. Enterprise product surface
- No multi tenancy for multiple furnaces, plants, and user roles.
- No alerting and notification (email, SMS, Teams) when a sensor leaves its Golden Range.
- No scheduled management report export (PDF), no mobile and tablet layout, no configuration UI for the unit registry and site approved limits.

### 7. Domain depth beyond the current scope
- No stave cooling water model, detailed burden distribution model, hearth erosion and wear model, tuyere thermography, or gas cleaning, stove, and PCI plant integration. These are where a multi year roadmap earns its keep.

## Readiness scorecard

| Dimension | Status | Grade |
|---|---|---|
| Core physics and ML engine | Built, validated on public data | Strong prototype |
| Honesty, provenance, governance discipline | Built and enforced | Ahead of most commercial tools |
| Interactive twin and visualization | Built, five themes, 3D | Strong prototype |
| Golden Range tracking and shortfall attribution | Built | Strong prototype |
| Live historian integration | Specified, not built | Missing |
| Validation on the target furnace | Not started (needs plant data) | Missing |
| Security, identity, compliance | Not built | Missing |
| Operations, HA, observability, CI and CD | Not built | Missing |
| ModelOps (registry, retraining, drift) | Partial (cards only) | Early |
| Enterprise product surface (SSO, multi tenant, alerting, reports) | Not built | Missing |

## How to proceed: phased path to a plant

The sequence is deliberate. Each phase ends with something the customer can verify.

**Phase A, data handshake (weeks 1 to 4).** Sign a read only data sharing agreement. Pull the full historian retention, not three years capped. Stand up the historian connector against a read replica or export. Recompute the capability matrix on the real tag list. Deliverable: the twin runs on the customer's own history with an honest capability report.

**Phase B, calibration and validation (weeks 4 to 12).** Fit the plant specific coefficients, flip pending validation items only where a metallurgist signs them off, run purged walk forward validation on the customer furnace at 1, 4, and 8 hours, and publish persistence, LightGBM, and hybrid side by side. Deliverable: a validation card the plant's own data science team can reproduce.

**Phase C, shadow mode (weeks 12 to 24).** Run live, read only, alongside the control room. Log every recommendation and every Golden Range excursion. Build the incident casebook. Measure closed loop value against persistence. Deliverable: an evidence pack that the twin would have helped on real events.

**Phase D, hardening and rollout (parallel from week 8).** Authentication and SSO, RBAC, PostgreSQL, observability, CI and CD, HA, OT and IT segmentation, a formal threat model, and a management of change dossier. Deliverable: a system the plant IT and OT functions will accept.

Phases A, B, and C are the ones that de risk the purchase. Phase D is standard enterprise engineering and is well understood.

## The honest framing for the pitch

Lead with the engine and the discipline, show the validation status truthfully, and sell the phased path. The differentiator against incumbents is not a bigger neural network. It is that this system refuses to show a number it cannot defend, labels every value with its evidence, and turns a vague production shortfall into a ranked, lag aware, physically explained root cause. A plant that has been burned by black box optimisers will recognise the difference immediately.
