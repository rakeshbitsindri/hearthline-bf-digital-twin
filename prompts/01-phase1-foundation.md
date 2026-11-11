# 01 — Foundation

Read `CLAUDE.md`, `knowledge/01-parameter-catalog.md`, `knowledge/13-parameter-tiers.md`, and `knowledge/15-data-time-and-provenance.md`. Implement only this phase.

## Build

1. Parameter registry with role, acquisition priority, canonical unit, physical range, and description. Seed it from the catalog and from `data/public/evraz-zsmk-2013-2016/COLUMN_MAP.md`. Adding a parameter is data.

2. Unit registry with tested conversions, including kgf/cm² to Pa and m³/min. Nm³ without reference conditions is a validation error.

3. Effective-dated tables: furnace, campaign, asset, physical instrument, native tag alias, geometry station, sensor position. Furnace `evraz-zsmk-bf` and campaign `2013-2016-public` exist. Working volume 2,000 m³ and nameplate 4,500 t/day are stored as assumed, with the Trofimov citation.

4. Event envelope columns from `knowledge/15-data-time-and-provenance.md`. Hourly facts and cast facts are separate. Dataset origin is `synthetic`, `public_reference`, or `plant`.

5. Capability-matrix table and a read API. Seed statuses for the public furnace from `knowledge/13-parameter-tiers.md`: silicon forecast can be `ready` once cast silicon is loaded; production, PCI, mass balance, and inverse are `not_testable`.

6. Immutable run-manifest table. A row can be written with hashes, seed, and code version even before a model exists.

7. SSO/OIDC boundary, roles, and an append-only audit table. Roles at least: viewer, furnace_engineer, metallurgist, model_admin, security_admin. Separation of duties: the person who promotes a model is recorded, and a viewer cannot accept a recommendation.

8. FastAPI and Next.js. Design tokens from `UX_DESIGN.md`. Persistent context shell: furnace, campaign, mode, timezone, selected time, data age, origin, capability, model version. Authoritative 2D geometry view from the configured profile. If the EVRAZ geometry is only a working volume, the 2D view says the profile is not dimensioned. A 3D wireframe is optional and not the quantitative view. Public-reference banner cannot be dismissed.

9. Docker Compose for API, web, and PostgreSQL. Background-job table. No Redis.

## Exit tests

- Unit conversions pass, including kgf/cm².
- A parameter without a role is rejected.
- Capability API returns `not_testable` for production on `evraz-zsmk-bf`.
- Audit rows cannot be updated through the API.
- README states how to boot, and that the bundled furnace is a 2013–2016 public reference.
