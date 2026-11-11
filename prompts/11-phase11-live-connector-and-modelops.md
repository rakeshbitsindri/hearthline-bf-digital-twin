# 11 — Live connector and model operations

Read `knowledge/15-data-time-and-provenance.md` and `CONNECTOR_DESIGN.md`. Phase 2 captured files. This phase may serve the advisory UI from an approved read-only feed. It still does not write to the plant.

## Connector

Adapters for PI Web API, OPC UA, and SQL views. Each adapter's allowed calls are listed and tested. Anything else throws. Connection target is a replica or export endpoint in the industrial DMZ, supplied by configuration, with no default host in the repo. mTLS or TLS with certificate validation. Secret from the vault, not from a committed file. Bounded query windows, throttle, and circuit breaker.

Backfill uses historian retention as it stands. Do not stop at three years if more is available. Then append. Minute samples, when the point has them, go to Parquet. Hourly facts remain in PostgreSQL.

Sequence gaps resync. Health states from phase 2 drive the UI. Stale data cannot satisfy a freshness contract.

A non-production test points the adapter at a fixture and asserts that write, method-call, and ad hoc SQL helpers do not exist.

## Models

Registry of manifests. Drift checks on inputs, residuals, and coverage. A drift flag opens a review. It does not deploy a retrain. Challengers run in shadow. Promotion and rollback are audited. Campaign change and instrument replacement mark affected states for reinitialization. Cross-furnace transfer requires a holdout on the target furnace.

## UI

Source health, lag of the newest event, backfill progress, and the model registry. A viewer can see status. Only `model_admin` can promote. The promotion button is absent for other roles.

## Exit tests

- Fixture connector rejects a write-shaped call.
- A sequence gap is visible and then cleared by resync.
- Promoting a model writes an audit row and a second call with the same idempotency key does not create a second promotion.
- EVRAZ remains origin `public_reference` and is not overwritten by an empty live backfill.
