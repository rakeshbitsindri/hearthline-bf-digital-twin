# Time, identity, and provenance

## Who owns a number

| Source | Owns | Platform may store |
|---|---|---|
| Historian | Process measurements and their quality flags | A copy |
| LIMS and material systems | Analyses and certificates | A copy |
| MES, cast house, weighbridge | Production, casts, delays | A copy |
| Engineering master data | Geometry and sensor locations | A versioned copy |
| CMMS and calibration | Maintenance and calibration events | A copy |
| This platform | Derived, reconciled, estimated, and simulated values | The original |

The platform does not become the system of record for a plant measurement. A correction from the source appends a revision. It does not overwrite the bytes already stored.

## Event envelope

Every accepted record has:

- `event_time` and, for a bucket, `interval_start` and `interval_end`
- `source_time` and `server_time` when the source provides them
- timezone offset as recorded, plus `event_time_utc`
- `available_at`, the time the platform was allowed to use the value
- `ingested_at`
- `quality` and native status, preserved
- `sequence` from the source when one exists
- `source_revision`
- `dedup_key` of source, native point, event time, and revision
- measured clock skew for that source, when a monitor exists

A backdated assay is invisible to any prediction, filter, or recommendation whose as-of time is before `available_at`.

## Identity

Tag names are aliases. The durable ids are source system, native point, physical instrument, asset, and location. Aliases, units, position, calibration, and replacement have `valid_from` and `valid_to`. Furnace id and campaign id are required even when the source file leaves campaign blank. The public EVRAZ import uses furnace id `evraz-zsmk-bf` and campaign id `2013-2016-public`.

## Late data and connector health

Late records land in event-time order inside a reorder window. Beyond the window the platform keeps the record and marks affected checkpoints for an explicit replay. Filtered state is `provisional` until the watermark passes. An audited recommendation stores the revision hash it used. A later revision does not rewrite that recommendation.

Connector states: `healthy`, `degraded`, `stale`, `offline`, `catching_up`, `backfilling`. Each feature has a freshness limit in `13-parameter-tiers.md`. Last-known values keep their event time. They are not relabelled as now. After an outage, catch-up finishes and quality checks pass before the state returns to `healthy`.

## Replay

An as-of query returns the records whose `available_at` is at or before that instant, using the revision current at that instant. Deterministic replay is this query plus the run manifest. Minute archives and hourly facts share the envelope. The public series is replayed on this bus with its original timestamps. The UI clock shows 2013–2016. Speed-up is a display control. It is not a live feed.

## Connector boundary

The collector runs in a separate process from the web application. It talks only to an approved historian replica or export endpoint in the industrial DMZ. It does not sit on the control network. Allowed operations are a fixed PI read scope, OPC UA `Read`, `HistoryRead`, and subscriptions, or a fixed SQL `SELECT` against named views. No generic query, write, or method call is exposed. Transport is TLS or mTLS with certificate checks. Secrets live in the plant vault and rotate. Query windows are bounded. A circuit breaker stops a backfill that would load the historian. Phase 2 may capture only. Phase 11 may serve the advisory UI from that capture after the OT approval test has shown that writes fail.

## Deployment

Phase 00 records on-prem or DMZ placement, backup, restore, Parquet retention, migrations, health checks, and operation without a public internet path. The browser receives normalised events from this platform. It never receives a historian connection string.
