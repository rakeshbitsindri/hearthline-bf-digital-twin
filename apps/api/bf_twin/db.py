"""Tamper-evident append-only audit log, Phase-1 RBAC, and separate post-hoc execution ledger.

Per CLAUDE.md:
- Role-based access and an append-only audit log are built in phase 1.
- Model version is on every result.
- Operator accept or reject is recorded.
- Confirmed execution, when the plant later reports it, is a separate field.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "twin.sqlite"
MODEL_VERSION = "hearthline-hybrid-0.4.0"

ROLES_PERMISSIONS: dict[str, set[str]] = {
    "viewer": set(),
    "operator": {"accept", "reject", "note", "confirm_execution"},
    "metallurgist": {"accept", "reject", "note", "confirm_execution", "pv_signoff", "moc_dossier"},
    "ot_auditor": {"note"},
    "admin": {"accept", "reject", "note", "confirm_execution", "pv_signoff", "moc_dossier"},
}

ALLOWED_ACTIONS = {"accept", "reject", "note", "pv_signoff", "moc_dossier"}


def check_role_permission(role: str, action: str) -> None:
    norm = (role or "operator").strip().lower()
    if norm not in ROLES_PERMISSIONS:
        raise PermissionError(f"Unknown role '{role}'. Valid roles: {', '.join(sorted(ROLES_PERMISSIONS))}")
    if action not in ROLES_PERMISSIONS[norm]:
        raise PermissionError(f"Role '{norm}' is not permitted to perform action '{action}'.")


def _compute_hash(prev_hash: str, created_at: str, actor: str, role: str, action: str, target: str, payload_json: str, model_version: str) -> str:
    canonical = f"{prev_hash}|{created_at}|{actor}|{role}|{action}|{target}|{model_version}|{payload_json}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _connect() -> sqlite3.Connection:
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres"):
        try:
            import psycopg  # type: ignore  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "DATABASE_URL points to PostgreSQL; install psycopg[binary] in production or unset DATABASE_URL for SQLite."
            ) from exc
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            payload TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'operator',
            model_version TEXT NOT NULL DEFAULT 'hearthline-hybrid-0.4.0',
            prev_hash TEXT NOT NULL DEFAULT 'GENESIS',
            event_hash TEXT NOT NULL DEFAULT '',
            confirmed_execution TEXT DEFAULT NULL,
            confirmed_at TEXT DEFAULT NULL,
            confirmed_by TEXT DEFAULT NULL
        )
        """
    )
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(audit_event)").fetchall()}
    migrations = [
        ("role", "TEXT NOT NULL DEFAULT 'operator'"),
        ("model_version", f"TEXT NOT NULL DEFAULT '{MODEL_VERSION}'"),
        ("prev_hash", "TEXT NOT NULL DEFAULT 'GENESIS'"),
        ("event_hash", "TEXT NOT NULL DEFAULT ''"),
        ("confirmed_execution", "TEXT DEFAULT NULL"),
        ("confirmed_at", "TEXT DEFAULT NULL"),
        ("confirmed_by", "TEXT DEFAULT NULL"),
    ]
    for col_name, col_def in migrations:
        if col_name not in existing_cols:
            conn.execute(f"ALTER TABLE audit_event ADD COLUMN {col_name} {col_def}")

    # Backfill hash chain on any legacy pre-migration rows that have empty event_hash
    unhashed = conn.execute(
        "SELECT id, created_at, actor, role, action, target, payload, model_version FROM audit_event WHERE event_hash = '' ORDER BY id"
    ).fetchall()
    if unhashed:
        for r_id, c_at, actr, rl, actn, tgt, p_json, m_ver in unhashed:
            prev_row = conn.execute("SELECT event_hash FROM audit_event WHERE id < ? ORDER BY id DESC LIMIT 1", (r_id,)).fetchone()
            p_hash = prev_row[0] if prev_row and prev_row[0] else "GENESIS"
            e_hash = _compute_hash(p_hash, c_at, actr, rl, actn, tgt, p_json, m_ver)
            conn.execute("UPDATE audit_event SET prev_hash = ?, event_hash = ? WHERE id = ?", (p_hash, e_hash, r_id))
    conn.commit()
    return conn


def append_audit(
    actor: str,
    action: str,
    target: str,
    payload: dict,
    role: str = "operator",
    model_version: str = MODEL_VERSION,
) -> dict:
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"action must be one of {sorted(ALLOWED_ACTIONS)}")
    check_role_permission(role, action)
    created = datetime.now(timezone.utc).isoformat()
    payload_json = json.dumps(payload, sort_keys=True)
    norm_role = (role or "operator").strip().lower()

    with _connect() as conn:
        last_row = conn.execute("SELECT event_hash FROM audit_event ORDER BY id DESC LIMIT 1").fetchone()
        prev_hash = last_row[0] if last_row and last_row[0] else "GENESIS"
        event_hash = _compute_hash(prev_hash, created, actor, norm_role, action, target, payload_json, model_version)
        cur = conn.execute(
            """
            INSERT INTO audit_event
                (created_at, actor, role, action, target, payload, model_version, prev_hash, event_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (created, actor, norm_role, action, target, payload_json, model_version, prev_hash, event_hash),
        )
        event_id = cur.lastrowid

    return {
        "id": event_id,
        "created_at": created,
        "actor": actor,
        "role": norm_role,
        "action": action,
        "target": target,
        "model_version": model_version,
        "prev_hash": prev_hash,
        "event_hash": event_hash,
        "confirmed_execution": None,
    }


def record_confirmed_execution(event_id: int, actor: str, status: str, role: str = "operator", notes: str = "") -> dict:
    """
    Record whether the plant later executed an accepted recommendation.
    Stored in dedicated post-hoc columns without mutating the immutable recommendation payload or hash chain.
    """
    check_role_permission(role, "confirm_execution")
    if status not in {"executed_in_plant", "partially_executed", "not_executed"}:
        raise ValueError("status must be executed_in_plant, partially_executed, or not_executed")
    confirmed_at = datetime.now(timezone.utc).isoformat()
    detail = status if not notes else f"{status}: {notes}"
    with _connect() as conn:
        row = conn.execute("SELECT id FROM audit_event WHERE id = ?", (event_id,)).fetchone()
        if not row:
            raise KeyError(f"Audit event {event_id} not found")
        conn.execute(
            "UPDATE audit_event SET confirmed_execution = ?, confirmed_at = ?, confirmed_by = ? WHERE id = ?",
            (detail, confirmed_at, actor, event_id),
        )
        conn.commit()
    return {
        "id": event_id,
        "confirmed_execution": detail,
        "confirmed_at": confirmed_at,
        "confirmed_by": actor,
    }


def list_audit(limit: int = 100) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, actor, role, action, target, payload, model_version,
                   prev_hash, event_hash, confirmed_execution, confirmed_at, confirmed_by
            FROM audit_event
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [
        {
            "id": row[0],
            "created_at": row[1],
            "actor": row[2],
            "role": row[3],
            "action": row[4],
            "target": row[5],
            "payload": json.loads(row[6]),
            "model_version": row[7],
            "prev_hash": row[8],
            "event_hash": row[9],
            "confirmed_execution": row[10],
            "confirmed_at": row[11],
            "confirmed_by": row[12],
        }
        for row in reversed(rows)
    ]


def verify_audit_chain() -> dict:
    """Verify the cryptographic SHA-256 hash chain across all append-only audit rows."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, created_at, actor, role, action, target, payload, model_version, prev_hash, event_hash FROM audit_event ORDER BY id"
        ).fetchall()

    expected_prev = "GENESIS"
    broken_id: Optional[int] = None
    for r_id, c_at, actr, rl, actn, tgt, p_json, m_ver, p_hash, e_hash in rows:
        recomputed = _compute_hash(expected_prev, c_at, actr, rl, actn, tgt, p_json, m_ver)
        if p_hash != expected_prev or e_hash != recomputed:
            broken_id = int(r_id)
            break
        expected_prev = e_hash

    return {
        "intact": broken_id is None,
        "events_verified": len(rows),
        "head_hash": expected_prev,
        "broken_at_id": broken_id,
        "roles_configured": sorted(ROLES_PERMISSIONS.keys()),
    }
