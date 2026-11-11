# 02 — Ingestion

Read `CLAUDE.md`, `knowledge/15-data-time-and-provenance.md`, and `data/public/evraz-zsmk-2013-2016/PROFILE.md`. Implement the file path and the capture-only connector boundary. Do not serve live recommendations.

## Build

1. Upload CSV, Excel, and Parquet. Store bytes, checksum, and origin. The EVRAZ workbooks load through this path. Sheets `data` and `Si` stay distinct. Silicon is not copied onto the hour as if it were sampled then.

2. Mapping recipe, versioned. Timezone unknown stays unknown. Do not assign UTC to EVRAZ timestamps.

3. Quality functions: missing, duplicate time, dropout, flatline, spike, instrument-range violation, impossible value. Classes: `process_event`, `sensor_fault`, `noise`, `unknown`. The 3,311 °C sentinel and negative CO₂ are `sensor_fault`. Rows remain queryable.

4. Event envelope on every row. `available_at` for a file import is the import time unless the file has a laboratory availability column. Dedup key rejects a silent double load.

5. Late and out-of-order fixture: inserting a cast with an earlier event time and a later `available_at` does not change an as-of read taken between them.

6. Production routes and Fe, C, N, O, H reconciliation when columns exist. On EVRAZ they do not. Persist `not_run` and the missing list. Do not invent analyses.

7. Recompute the capability matrix after each import.

8. Connector process, separate from the web process, with a file adapter only in this phase. Health states `healthy`, `degraded`, `stale`, `offline`, `catching_up`, `backfilling`. Document the OT read-only interface. Do not ship a default host, token, or SQL string. A test double proves the web process has no historian client.

9. UI: file list, mapping, quality marks, route residual when present, banner for public reference. Stale and empty states use the shared runtime vocabulary.

## Exit tests

- EVRAZ checksum matches `SHA256SUMS` after import, and the raw file is unchanged.
- 29,602 hourly rows and 16,589 silicon rows. No hour invented between casts.
- Pressure-drop residual is stored and is about zero.
- As-of test for late silicon passes.
- Unmapped columns are listed.
