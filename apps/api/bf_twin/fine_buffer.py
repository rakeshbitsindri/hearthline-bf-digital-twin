"""One-second advisory runs with a fixed-size ring.

Autopilot and the production-goal test step the reduced-order model once per
simulated second. Samples stay in memory and in one overwrite file. The file
is rewritten from the ring and is not allowed to grow past a few megabytes.
Historical replay stays on the hourly archive and does not use this buffer.
"""

from __future__ import annotations

import json
import math
import threading
from collections import deque
from typing import Any

import pandas as pd

from bf_twin.simulator import compute_physics_state, furnace_class_for_demand
from bf_twin.store import CACHE, active_dataset_id, active_dataset_meta

RING_CAP = 4096
DISK_CAP_BYTES = 1_500_000
STEP_S = 1
KEEP_TAGS = (
    "Production",
    "Si",
    "dP",
    "HMT",
    "RAFT",
    "Fb",
    "Fo",
    "Th",
    "Pt",
    "PCI",
    "CokeRate",
    "BlastMoisture",
    "R",
)
STATE_KEYS = (
    "Fb",
    "Th",
    "Fo",
    "Pt",
    "R",
    "PCI",
    "CokeRate",
    "BlastMoisture",
    "BurdenFe",
    "CokeCSR",
    "SinterRDI",
    "AlkaliInput",
    "ZnInput",
)

MANIPULATED = ("Fb", "Th", "Fo", "Pt", "R", "PCI", "CokeRate", "BlastMoisture")
LIMITS = {
    "Fb": (2600.0, 4250.0),
    "Th": (980.0, 1240.0),
    "Fo": (5000.0, 30000.0),
    "Pt": (1.15, 1.72),
    "R": (3.30, 4.65),
    "PCI": (75.0, 195.0),
    "CokeRate": (285.0, 435.0),
    "BlastMoisture": (8.0, 32.0),
}
USUAL = {
    "Fb": 3650.0,
    "Th": 1100.0,
    "Fo": 18500.0,
    "Pt": 1.42,
    "R": 3.98,
    "PCI": 115.0,
    "CokeRate": 375.0,
    "BlastMoisture": 16.0,
    "BurdenFe": 58.5,
    "CokeCSR": 64.0,
    "SinterRDI": 26.5,
    "AlkaliInput": 2.1,
    "ZnInput": 115.0,
    "switch_dehumidification": False,
    "switch_center_coke": True,
    "switch_alkali_flush": False,
}

_LOCK = threading.Lock()
_RUN: dict[str, Any] = {
    "mode": None,
    "cursor_s": 0,
    "state": {},
    "holds": {},
    "scale": 1.0,
    "volume": 2000.0,
    "target": 4500.0,
    "samples": deque(maxlen=RING_CAP),
    "origin": "simulated_flow",
    "dataset_id": None,
}


def _disk_path():
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / "fine_ring.json"


def _frame_state(row: pd.Series) -> dict[str, float]:
    state = {
        "switch_dehumidification": False,
        "switch_center_coke": True,
        "switch_alkali_flush": False,
    }
    for key in STATE_KEYS:
        if key in row and pd.notna(row[key]):
            state[key] = float(row[key])
    return state


def _blend(a: dict[str, float], b: dict[str, float], frac: float, pin: dict[str, float]) -> dict[str, float]:
    out = dict(a)
    for key, aval in a.items():
        if not isinstance(aval, (int, float)):
            continue
        if key in pin:
            out[key] = pin[key]
            continue
        bval = b.get(key, aval)
        if isinstance(bval, (int, float)):
            out[key] = float(aval) + (float(bval) - float(aval)) * frac
    return out


def _slew(state: dict[str, float], pin: dict[str, float]) -> dict[str, float]:
    out = dict(state)
    for key, goal in pin.items():
        cur = float(out.get(key, goal))
        out[key] = cur + 0.08 * (float(goal) - cur)
    return out


def _own_state(scale: float) -> dict[str, Any]:
    state = dict(USUAL)
    state["Fb"] = USUAL["Fb"] * scale
    state["Fo"] = USUAL["Fo"] * scale
    return state


def _flow(state: dict[str, Any], cursor: int) -> None:
    """Slow usual variation of burden and coke quality. Not taken from the archive."""
    phase = cursor / 900.0
    state["BurdenFe"] = USUAL["BurdenFe"] + 0.35 * math.sin(phase)
    state["SinterRDI"] = USUAL["SinterRDI"] + 0.8 * math.sin(phase * 0.7 + 1.0)
    state["CokeCSR"] = USUAL["CokeCSR"] + 0.6 * math.sin(phase * 0.5 + 0.4)
    state["AlkaliInput"] = USUAL["AlkaliInput"] + 0.08 * math.sin(phase * 0.4)
    state["ZnInput"] = USUAL["ZnInput"] + 4.0 * math.sin(phase * 0.3 + 2.0)


def _recover(state: dict[str, Any], production: float, holds: dict[str, float]) -> None:
    err = float(_RUN["target"]) - float(production)
    ratio = err / max(800.0, float(_RUN["target"]))
    for tag in ("Fb", "Fo"):
        if tag in holds:
            state[tag] = holds[tag]
            continue
        state[tag] = float(state[tag]) * (1.0 + 0.04 * ratio)
    if "BlastMoisture" not in holds:
        state["BlastMoisture"] = float(state["BlastMoisture"]) - 0.15 * ratio
    if "PCI" not in holds:
        state["PCI"] = float(state["PCI"]) - 1.2 * ratio
    for tag, (lo, hi) in LIMITS.items():
        if tag in ("Fb", "Fo"):
            lo, hi = lo * _RUN["scale"], hi * _RUN["scale"]
        if tag in holds:
            state[tag] = holds[tag]
        elif tag in state and isinstance(state[tag], (int, float)):
            state[tag] = min(hi, max(lo, float(state[tag])))


def _sample(state: dict[str, float], sim_s: int, stamp: str) -> dict[str, Any]:
    phys = compute_physics_state(state, _RUN["volume"], _RUN["scale"])
    point = {"t": stamp, "sim_s": int(sim_s), "step_s": STEP_S}
    for tag in KEEP_TAGS:
        if tag in phys:
            point[tag] = round(float(phys[tag]), 3)
        elif tag in state:
            point[tag] = round(float(state[tag]), 3)
    return point


def _dump_disk() -> int:
    path = _disk_path()
    payload = {
        "dataset_id": _RUN["dataset_id"],
        "mode": _RUN["mode"],
        "step_s": STEP_S,
        "capacity": RING_CAP,
        "samples": list(_RUN["samples"]),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    if len(raw) > DISK_CAP_BYTES:
        payload["samples"] = list(_RUN["samples"])[-512:]
        raw = json.dumps(payload, separators=(",", ":")).encode()
    path.write_bytes(raw)
    return len(raw)


def start_fine(mode: str, target_production: float) -> dict[str, Any]:
    if mode not in {"autopilot", "goal"}:
        raise ValueError("fine run mode must be autopilot or goal")
    furnace = furnace_class_for_demand(target_production)
    scale = float(furnace["size_scale"])
    with _LOCK:
        _RUN["mode"] = mode
        _RUN["cursor_s"] = 0
        _RUN["state"] = _own_state(scale)
        _RUN["holds"] = {}
        _RUN["scale"] = scale
        _RUN["volume"] = float(furnace["working_volume_m3"])
        _RUN["furnace_class"] = furnace
        _RUN["target"] = float(target_production)
        _RUN["dataset_id"] = active_dataset_id()
        _RUN["origin"] = "simulated_flow"
        _RUN["samples"].clear()
        _dump_disk()
    return status_fine()


def hold_fine(tag: str, value: float | None) -> dict[str, Any]:
    if tag not in MANIPULATED:
        raise ValueError(f"{tag} is not an autopilot lever")
    with _LOCK:
        if _RUN["mode"] != "autopilot" or not _RUN["state"]:
            raise ValueError("holds apply only while autopilot is running")
        if value is None:
            _RUN["holds"].pop(tag, None)
        else:
            lo, hi = LIMITS[tag]
            if tag in ("Fb", "Fo"):
                lo, hi = lo * _RUN["scale"], hi * _RUN["scale"]
            held = min(hi, max(lo, float(value)))
            _RUN["holds"][tag] = held
            _RUN["state"][tag] = held
    return status_fine()


def tick_fine(steps: int = 1) -> dict[str, Any]:
    steps = max(1, min(int(steps), 60))
    with _LOCK:
        if _RUN["mode"] not in {"autopilot", "goal"} or not _RUN["state"]:
            raise ValueError("no fine run is active")
        for _ in range(steps):
            cursor = int(_RUN["cursor_s"])
            state = _RUN["state"]
            _flow(state, cursor)
            phys = compute_physics_state(state, _RUN["volume"], _RUN["scale"])
            _recover(state, phys["Production"], _RUN["holds"] if _RUN["mode"] == "autopilot" else {})
            stamp = str(pd.Timestamp("2026-01-01 00:00:00") + pd.Timedelta(seconds=cursor))
            _RUN["samples"].append(_sample(state, cursor, stamp))
            _RUN["cursor_s"] = cursor + STEP_S
        disk_bytes = _dump_disk() if _RUN["cursor_s"] % 30 == 0 else (_disk_path().stat().st_size if _disk_path().exists() else 0)
        tail = list(_RUN["samples"])[-120:]
        mode = _RUN["mode"]
        sim_s = _RUN["cursor_s"]
        count = len(_RUN["samples"])
        levers = []
        for tag in MANIPULATED:
            lo, hi = LIMITS[tag]
            if tag in ("Fb", "Fo"):
                lo, hi = lo * _RUN["scale"], hi * _RUN["scale"]
            levers.append(
                {
                    "tag": tag,
                    "value": round(float(_RUN["state"].get(tag, lo)), 3),
                    "min": round(lo, 3),
                    "max": round(hi, 3),
                    "held": tag in _RUN["holds"],
                }
            )
    spark = {tag: [row.get(tag) for row in tail] for tag in ("Production", "Si", "dP", "Fb")}
    return {
        "latest": tail[-1] if tail else None,
        "spark": spark,
        "count": count,
        "capacity": RING_CAP,
        "disk_bytes": disk_bytes,
        "disk_cap_bytes": DISK_CAP_BYTES,
        "step_s": STEP_S,
        "mode": mode,
        "sim_s": sim_s,
        "levers": levers,
        "source": "simulated_flow",
    }


def stop_fine() -> dict[str, Any]:
    with _LOCK:
        _RUN["mode"] = None
        _RUN["state"] = {}
        _RUN["holds"] = {}
    return status_fine()


def status_fine() -> dict[str, Any]:
    path = _disk_path()
    return {
        "mode": _RUN["mode"],
        "dataset_id": _RUN["dataset_id"],
        "origin": _RUN["origin"],
        "step_s": STEP_S,
        "count": len(_RUN["samples"]),
        "capacity": RING_CAP,
        "disk_bytes": path.stat().st_size if path.exists() else 0,
        "disk_cap_bytes": DISK_CAP_BYTES,
        "sim_s": _RUN["cursor_s"],
        "target_production": _RUN["target"],
    }
