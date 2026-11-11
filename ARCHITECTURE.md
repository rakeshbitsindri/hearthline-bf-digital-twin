# Architecture

A read-only advisory twin. Plant systems are never written.

```
browser → Next.js (apps/web) → FastAPI (apps/api)
                              → parquet cache of immutable source files
                              → SQLite or PostgreSQL for audit, manifests, capability
```

Origins are `public_reference`, `plant`, and `synthetic`. They do not overwrite each other. The bundled origin is EVRAZ ZSMK, 2013–2016.

Measured tags are served from the hourly sheet. Cast silicon stays on cast time. Derived values carry `estimated` or `simulated`. Missing contracts return a status, not a filled number.

The dynamic step advances only states the sensors can support. On this file that is the measured gas and blast state. Hearth mass, alkali, and coke inventory stay `not_observable`.

Jobs that take longer than a request write a progress row. Training does not block the read API. The shipped silicon model is whichever of persistence and LightGBM wins the walk-forward comparison. If LightGBM does not win, persistence is served and the card shows both.

No Redis, TimescaleDB, or PyTorch. A historian connector is a separate process with a fixed read profile. This build ships the file adapter and rejects write-shaped calls.
