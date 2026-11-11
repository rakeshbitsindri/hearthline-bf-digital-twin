# Database

PostgreSQL in Compose. Tests and the default local URL use SQLite with the same tables.

| Table | Purpose |
|---|---|
| furnace | id, name, origin, assumed volume and nameplate, citation |
| campaign | furnace, id, start, end |
| capability | furnace, feature, status, detail, data revision |
| run_manifest | hash, seed, model id, metrics JSON, created at |
| audit_event | append-only actor, action, target, payload, created at |

Hourly facts and cast analyses live in parquet under `data/cache/`, content-addressed by the source SHA-256. They are not updated in place. A new import writes a new cache directory.

Event fields stored on each cache row: `event_time`, `available_at`, `origin`, `quality`. EVRAZ timestamps have no confirmed timezone, so they are stored as naive local time and the API says so.
