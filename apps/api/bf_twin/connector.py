"""Phase-A / TRL-7 Read-Only Historian Connector Profiles & SSE Shadow-Mode Streamer.

Per CLAUDE.md:
- Read-only toward the plant. No write path to control, historian, or actuators, even behind a flag.
- The connector cannot issue SQL, OPC methods, or historian writes. Credentials are not stored in the repo.
- Live updates use server-sent events with sequence numbers.
- Hourly means hide slips, hangs, pressure spikes, tuyere events, and channeling precursors.
  Ask for within-hour __std, __min, __max, and __exc companions.
"""

from __future__ import annotations

import asyncio
import itertools
import json
import os
from datetime import datetime, timezone
from typing import AsyncIterator, Optional

import pandas as pd

from bf_twin.db import MODEL_VERSION
from bf_twin.simulator import simulate_coupled
from bf_twin.store import active_dataset_id, active_dataset_meta, clean_hourly, hourly

_SSE_SEQ = itertools.count(1)

FORBIDDEN_OPERATIONS = {
    "write",
    "put",
    "post",
    "delete",
    "update",
    "sql",
    "query",
    "method",
    "opc_call_method",
    "pi_update_value",
    "modbus_write_coil",
    "modbus_write_register",
    "setpoint_push",
}

READ_PROFILES = [
    {
        "profile_id": "pi_web_api_readonly",
        "protocol": "OSIsoft / AVEVA PI Web API (HTTPS GET only)",
        "direction": "OT DMZ Read Replica -> Hearthline Engine",
        "allowed_verbs": ["GET /piwebapi/streamsets/interpolated", "GET /piwebapi/streamsets/summary"],
        "blocked_verbs": ["POST", "PUT", "PATCH", "DELETE", "Batch-Write"],
        "env_secret_keys": ["BF_PI_BASE_URL", "BF_PI_READONLY_TOKEN_FILE"],
        "configured_in_env": bool(os.environ.get("BF_PI_BASE_URL")),
        "sub_hour_companions": ["__std", "__min", "__max", "__exc"],
        "status": "configured_ready" if os.environ.get("BF_PI_BASE_URL") else "adapter_ready_awaiting_dmz_url",
    },
    {
        "profile_id": "opcua_readonly_shadow",
        "protocol": "OPC-UA Binary / HTTPS (Read & HistoryRead service sets only)",
        "direction": "Industrial DMZ OPC-UA Aggregator -> Hearthline Engine",
        "allowed_verbs": ["Read", "HistoryRead"],
        "blocked_verbs": ["Write", "HistoryUpdate", "Call (OPC Methods)", "AddNodes", "DeleteNodes"],
        "env_secret_keys": ["BF_OPCUA_ENDPOINT", "BF_OPCUA_CERT_PATH"],
        "configured_in_env": bool(os.environ.get("BF_OPCUA_ENDPOINT")),
        "sub_hour_companions": ["__std", "__min", "__max", "__exc"],
        "status": "configured_ready" if os.environ.get("BF_OPCUA_ENDPOINT") else "adapter_ready_awaiting_dmz_endpoint",
    },
    {
        "profile_id": "dmz_dropzone_shadow",
        "protocol": "Immutable Parquet / CSV / XLSX Drop-Zone Watcher",
        "direction": "One-way Data Diode / SFTP Drop -> Hearthline Engine",
        "allowed_verbs": ["READ_FILE", "VERIFY_SHA256"],
        "blocked_verbs": ["WRITE_PLANT", "SQL_EXEC", "SOCKET_OUTBOUND_OT"],
        "env_secret_keys": ["BF_DROPZONE_DIR"],
        "configured_in_env": True,
        "sub_hour_companions": ["__std", "__min", "__max", "__exc"],
        "status": "active_on_reference_and_uploads",
    },
]


def advisory_autopilot(when, target_production: float = 4500.0) -> dict:
    """Propose constant-production moves. Shadow plugin commands are never dispatched."""
    sim = simulate_coupled(pd.Timestamp(when), target_production=float(target_production))
    steps = []
    for row in sim.get("parameters") or []:
        if row.get("role") != "manipulated":
            continue
        if row.get("simulated_golden_status", "in_golden") == "in_golden":
            continue
        if row.get("golden_center") is None:
            continue
        steps.append(
            {
                "tag": row["tag"],
                "label": row["label"],
                "unit": row["unit"],
                "now": row.get("simulated"),
                "golden_center": row.get("golden_center"),
                "status": row.get("simulated_golden_status"),
                "advisory": (
                    f"Hold {row['label']} at {row.get('golden_center')} {row.get('unit')} "
                    f"for the {target_production:g} t/d band."
                ),
                "shadow_plugins": [
                    {
                        "plugin": "pi_web_api_readonly",
                        "command": f"POST /piwebapi/streams/update {row['tag']}={row.get('golden_center')}",
                        "dispatched": False,
                        "blocked_because": "PI profile allows GET only",
                    },
                    {
                        "plugin": "opcua_readonly_shadow",
                        "command": f"Write {row['tag']} = {row.get('golden_center')}",
                        "dispatched": False,
                        "blocked_because": "OPC-UA profile allows Read and HistoryRead only",
                    },
                ],
            }
        )
    regime = (sim.get("operating_regime") or {}).get("regime", "unknown")
    compliance = (sim.get("golden_analysis") or {}).get("simulated_compliance_pct")
    situation = (
        f"Regime {regime}. Golden compliance {compliance}%. "
        f"{len(steps)} manipulated tags sit outside the band for {target_production:g} t/d."
    )
    return {
        "mode": "advisory_only",
        "plant_write_capable": False,
        "dataset_id": active_dataset_id(),
        "origin": active_dataset_meta().get("origin"),
        "t": sim.get("t"),
        "target_production": target_production,
        "situation": situation,
        "steps": steps,
        "dispatch": "not_sent",
    }


def enforce_readonly_op(op: str) -> dict:
    """Hard gate: reject every non-read operation with a PermissionError (mapped to HTTP 403)."""
    norm = (op or "").strip().lower()
    if norm != "read" or norm in FORBIDDEN_OPERATIONS:
        raise PermissionError(
            f"Operation '{op}' is hardware/architecture-blocked: Hearthline implements read-only profiles only; "
            "write, OPC method, SQL query, and setpoint-push paths do not exist."
        )
    return {
        "op": "read",
        "connected": bool(os.environ.get("BF_PI_BASE_URL") or os.environ.get("BF_OPCUA_ENDPOINT")),
        "active_profile": "dmz_dropzone_shadow",
        "plant_write_capable": False,
        "detail": "Read-only DMZ file & replay shadow adapter active; zero plant write sockets compiled.",
    }


def connector_diagnostics() -> dict:
    """Inspect active dataset freshness, staleness gate, and sub-hour companion availability."""
    ds = active_dataset_id()
    meta = active_dataset_meta()
    frame = hourly(ds)
    last_dt = pd.Timestamp(frame["dt"].iloc[-1])
    now_utc = datetime.now(timezone.utc)
    last_utc = last_dt.tz_localize("UTC") if last_dt.tzinfo is None else last_dt.tz_convert("UTC")
    age_hours = round(max(0.0, (now_utc - last_utc).total_seconds() / 3600.0), 1)

    companion_cols = [c for c in frame.columns if c.endswith(("__std", "__min", "__max", "__exc"))]
    is_live = bool(meta.get("live", False))
    stale_blocked = is_live and age_hours > 2.0

    return {
        "dataset_id": ds,
        "dataset_name": meta.get("name"),
        "origin": meta.get("origin"),
        "live_plant_socket_open": bool(os.environ.get("BF_PI_BASE_URL") or os.environ.get("BF_OPCUA_ENDPOINT")),
        "plant_write_path_exists": False,
        "last_record_timestamp": last_dt.isoformat(sep=" "),
        "archive_age_hours": age_hours,
        "stale_source_gate": "blocked_stale" if stale_blocked else ("historical_replay_mode" if not is_live else "fresh"),
        "within_hour_companions_present": len(companion_cols) > 0,
        "within_hour_companion_columns": companion_cols,
        "sub_sampling_blindness_notice": (
            "Within-hour __std/__min/__max/__exc companions detected."
            if companion_cols
            else "Hourly means only: slips, hangs, pressure spikes, tuyere events, and channeling precursors below the 1-hour sampling interval are not observable until the minute-level connector archive is active."
        ),
        "profiles": READ_PROFILES,
    }


async def sse_shadow_stream(
    target_production: float = 4500.0,
    max_events: int = 8,
    interval_sec: float = 0.85,
    start_offset: Optional[int] = None,
) -> AsyncIterator[str]:
    """
    Server-Sent Events (SSE) live shadow-mode stream with strictly monotonic sequence numbers.
    Steps forward through qualified operating frames so operators or pitch viewers can watch
    real-time telemetry, Golden Range drift, and root-cause detection in motion.
    """
    h = clean_hourly()
    on = h[h["Fb"] > 1500].reset_index(drop=True)
    if on.empty:
        on = h.reset_index(drop=True)

    n_rows = len(on)
    cursor = start_offset if start_offset is not None else max(0, int(n_rows * 0.62))
    count = max(1, min(int(max_events), 40))
    delay = max(0.05, min(float(interval_sec), 3.0))

    for step in range(count):
        row_idx = (cursor + step * 3) % n_rows
        ts = pd.Timestamp(on.iloc[row_idx]["dt"])
        sim = simulate_coupled(ts, target_production=target_production)
        ga = sim.get("golden_analysis", {})
        seq = next(_SSE_SEQ)
        payload = {
            "seq": seq,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
            "model_version": MODEL_VERSION,
            "stream_mode": "shadow_replay_readonly",
            "t": sim["t"],
            "regime": sim["operating_regime"]["regime"],
            "Fb": sim["simulated_state"].get("Fb"),
            "Th": sim["simulated_state"].get("Th"),
            "Fo": sim["simulated_state"].get("Fo"),
            "dP": sim["simulated_state"].get("dP"),
            "CO2": sim["simulated_state"].get("CO2"),
            "Si": sim["simulated_state"].get("Si"),
            "Production": sim["physics_kpis"].get("Production"),
            "binding_ceiling": sim["physics_kpis"].get("binding_ceiling"),
            "in_envelope": sim.get("envelope", {}).get("in_envelope", True),
            "golden_compliance_pct": ga.get("simulated_compliance_pct"),
            "out_of_golden_count": len(ga.get("out_of_golden_simulated", [])),
            "top_warning": (ga.get("out_of_golden_simulated") or [None])[0],
        }
        yield f"id: {seq}\nevent: twin_frame\ndata: {json.dumps(payload)}\n\n"
        if step + 1 < count:
            await asyncio.sleep(delay)
