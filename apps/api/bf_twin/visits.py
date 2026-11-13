"""Capped visit log. City and country only. Raw addresses are not stored."""

from __future__ import annotations

import json
import threading
import urllib.request
from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional

from bf_twin.store import CACHE

RING_CAP = 2000
DISK_CAP_BYTES = 800_000
_LOCK = threading.Lock()
_EVENTS: deque[dict[str, Any]] = deque(maxlen=RING_CAP)
_GEO: dict[str, tuple[str, str]] = {}


def _disk():
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / "visits_ring.json"


def _load() -> None:
    path = _disk()
    if not path.exists() or _EVENTS:
        return
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    for item in payload.get("events") or []:
        _EVENTS.append(item)


def _dump() -> int:
    path = _disk()
    raw = json.dumps({"events": list(_EVENTS)}, separators=(",", ":")).encode()
    if len(raw) > DISK_CAP_BYTES:
        raw = json.dumps({"events": list(_EVENTS)[-800:]}, separators=(",", ":")).encode()
    path.write_bytes(raw)
    return len(raw)


def _geo(ip: str) -> tuple[str, str]:
    if not ip or ip in {"127.0.0.1", "::1"} or ip.startswith(("10.", "192.168.", "172.")):
        return "local", "local"
    if ip in _GEO:
        return _GEO[ip]
    city, country = "unknown", "unknown"
    try:
        req = urllib.request.Request(f"https://ipwho.is/{ip}", headers={"User-Agent": "hearthline-visits"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode())
        if data.get("success"):
            city = str(data.get("city") or "unknown")[:80]
            country = str(data.get("country") or "unknown")[:80]
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    _GEO[ip] = (city, country)
    if len(_GEO) > 500:
        _GEO.pop(next(iter(_GEO)))
    return city, country


def client_ip(headers: dict[str, str], fallback: Optional[str]) -> str:
    for key in ("cf-connecting-ip", "x-forwarded-for", "x-real-ip"):
        value = headers.get(key) or ""
        if value:
            return value.split(",")[0].strip()
    return fallback or ""


def record_visit(ip: str, site: str, path: str, ref: str) -> dict[str, Any]:
    city, country = _geo(ip)
    event = {
        "t": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "site": (site or "unknown")[:120],
        "path": (path or "/")[:180],
        "city": city,
        "country": country,
        "ref": (ref or "")[:180],
    }
    with _LOCK:
        _load()
        _EVENTS.append(event)
        _dump()
    return {"ok": True, "city": city, "country": country}


def visit_summary() -> dict[str, Any]:
    with _LOCK:
        _load()
        events = list(_EVENTS)
    cities: dict[str, int] = {}
    sites: dict[str, int] = {}
    paths: dict[str, int] = {}
    for event in events:
        key = f"{event.get('city')}, {event.get('country')}"
        cities[key] = cities.get(key, 0) + 1
        site = str(event.get("site") or "unknown")
        sites[site] = sites.get(site, 0) + 1
        page = str(event.get("path") or "/")
        paths[page] = paths.get(page, 0) + 1
    return {
        "total": len(events),
        "capacity": RING_CAP,
        "note": "City and country only. Network addresses are not stored. The log keeps the latest 2,000 visits.",
        "cities": sorted(({"place": k, "visits": v} for k, v in cities.items()), key=lambda row: -row["visits"])[:40],
        "sites": sorted(({"site": k, "visits": v} for k, v in sites.items()), key=lambda row: -row["visits"])[:10],
        "paths": sorted(({"path": k, "visits": v} for k, v in paths.items()), key=lambda row: -row["visits"])[:20],
        "recent": list(reversed(events[-30:])),
    }
