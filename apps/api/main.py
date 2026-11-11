"""Read-only advisory API. No plant write route."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bf_twin.connector import connector_diagnostics, enforce_readonly_op, sse_shadow_stream
from bf_twin.db import (
    MODEL_VERSION,
    ROLES_PERMISSIONS,
    append_audit,
    list_audit,
    record_confirmed_execution,
    verify_audit_chain,
)
from bf_twin.engine import (
    diagnose,
    identity_summary,
    predict_silicon,
    pressure_at,
    scenario,
    sensitivity_matrix,
    train_card,
    twin_at,
    utilisation,
)
from bf_twin.knowledge_hub import (
    export_plant_slice_csv,
    industrial_plant_data_summary,
    list_knowledge_articles,
)
from bf_twin.simulator import (
    compute_golden_ranges,
    learn_from_dataset,
    modelops_status,
    optimize_for_target,
    scan_historical_shortfalls,
    simulate_coupled,
)
from bf_twin.store import (
    PARAMETER_CATALOG,
    active_dataset_id,
    active_dataset_meta,
    capability,
    hourly,
    labeled_regimes,
    list_datasets,
    parameter_catalog,
    playback,
    quality_report,
    set_active_dataset,
    silicon,
    slice_series,
    upload_user_dataset,
)

app = FastAPI(title="Blast furnace advisory twin", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class StrictModel(BaseModel):
    """Reject unknown fields. A silently dropped field returned a plausible but wrong hour."""

    model_config = ConfigDict(extra="forbid")


class AuditIn(StrictModel):
    actor: str = Field(min_length=1, max_length=80)
    action: str
    target: str = Field(min_length=1, max_length=120)
    payload: dict = Field(default_factory=dict)
    role: Optional[str] = None


class ConfirmExecutionIn(StrictModel):
    actor: str = Field(min_length=1, max_length=80)
    status: str
    notes: str = ""
    role: Optional[str] = None


class ProbeIn(StrictModel):
    op: str


class ScenarioIn(StrictModel):
    t: str
    blast_delta: float = 0
    hot_blast_delta: float = 0
    oxygen_delta: float = 0
    top_pressure_delta: float = 0
    ore_coke_delta: float = 0
    cold_blast_temp_delta: float = 0
    cold_blast_pressure_delta: float = 0
    extra_deltas: Dict[str, float] = Field(default_factory=dict)
    horizon_hours: int = 4
    mode: str = "hybrid"


class SimulateIn(StrictModel):
    t: Optional[str] = None
    overrides: dict = Field(default_factory=dict)
    deltas: dict = Field(default_factory=dict)
    switches: dict = Field(default_factory=dict)
    mode: str = "hybrid"
    horizon_hours: int = 24
    target_production: float = 4500.0


class OptimizeIn(StrictModel):
    t: Optional[str] = None
    target_production: float = 4650.0
    target_si: float = 0.46
    max_dp: float = 1.52
    min_raft: float = 2000.0
    max_raft: float = 2250.0
    objective_mode: str = "balanced"


class DatasetSelectIn(StrictModel):
    dataset_id: str


@app.get("/health")
def health() -> dict:
    ds = active_dataset_id()
    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    return {
        "status": "ok",
        "origin": ds_info["origin"],
        "dataset_id": ds,
        "plant_write": False,
    }


@app.get("/catalog")
def catalog_route() -> dict:
    return {"parameters": PARAMETER_CATALOG}


@app.get("/parameters")
def parameters_route() -> dict:
    ds = active_dataset_id()
    return {
        "dataset_id": ds,
        "parameters": parameter_catalog(ds),
        "regimes": labeled_regimes(),
    }


@app.get("/datasets")
def datasets_route() -> dict:
    return {"active": active_dataset_meta(), "active_id": active_dataset_id(), "datasets": list_datasets()}


@app.post("/datasets/select")
def select_dataset_route(body: DatasetSelectIn) -> dict:
    try:
        selected = set_active_dataset(body.dataset_id)
        learned = learn_from_dataset(force=True)
        return {"status": "ok", "active": selected, "dataset": selected, "rows_trained": learned["rows_trained"]}
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/datasets/upload")
async def upload_dataset_route(file: UploadFile = File(...), column_map: Optional[str] = Form(None)) -> dict:
    try:
        content = await file.read()
        meta = upload_user_dataset(file.filename or "uploaded.csv", content)
        learned = learn_from_dataset(force=True)
        return {
            "status": "ok",
            "dataset": meta,
            "learned_summary": {"rows_trained": learned["rows_trained"], "r2_scores": learned["r2_scores"]},
        }
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/sensitivity")
def sensitivity_route(horizon_hours: int = 4, retrain: bool = False) -> dict:
    learned = learn_from_dataset(force=retrain)
    mat = sensitivity_matrix(horizon_hours=horizon_hours)
    return {**mat, **learned}


@app.post("/simulate")
def simulate_route(body: SimulateIn) -> dict:
    hours = hourly()
    when = pd.Timestamp(body.t) if body.t else pd.Timestamp(hours["dt"].iloc[-1])
    return simulate_coupled(
        when=when,
        overrides=body.overrides,
        deltas=body.deltas,
        switches=body.switches,
        mode=body.mode,
        horizon_hours=min(max(body.horizon_hours, 4), 72),
        target_production=body.target_production,
    )


@app.get("/golden-ranges")
def golden_ranges_route(target_production: float = 4500.0) -> dict:
    return compute_golden_ranges(target_production=target_production)


@app.get("/shortfalls")
def shortfalls_route(target_production: float = 4500.0, limit: int = 16) -> dict:
    return scan_historical_shortfalls(target_production=target_production, limit=min(max(limit, 4), 40))


@app.post("/optimize")
def optimize_route(body: OptimizeIn) -> dict:
    hours = hourly()
    when = pd.Timestamp(body.t) if body.t else pd.Timestamp(hours["dt"].iloc[-1])
    return optimize_for_target(
        when=when,
        target_production=body.target_production,
        target_si=body.target_si,
        max_dp=body.max_dp,
        min_raft=body.min_raft,
        max_raft=body.max_raft,
        objective_mode=body.objective_mode,
    )


@app.get("/furnace")
def furnace() -> dict:
    ds = active_dataset_id()
    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    hours = hourly(ds)
    casts = silicon(ds)
    start = pd.Timestamp(hours["dt"].iloc[0])
    end = pd.Timestamp(hours["dt"].iloc[-1])
    return {
        "id": ds,
        "campaign": ds_info.get("campaign", "2013-2016-public"),
        "origin": ds_info["origin"],
        "name": ds_info["name"],
        "timezone": ds_info.get("timezone", "unconfirmed"),
        "live": False,
        "from": start.isoformat(sep=" "),
        "to": end.isoformat(sep=" "),
        "hours": int(len(hours)),
        "casts": int(len(casts)),
        "has_production": ds_info.get("has_production", False),
        "has_co": ds_info.get("has_co", False),
        "assumed_working_volume_m3": 2000,
        "assumed_nameplate_t_per_day": 4500,
        "assumption_citation": "Trofimov, Data in Brief 63:112159",
        "licence": "CC BY 4.0",
    }


@app.get("/capability")
def capability_route() -> dict:
    ds = active_dataset_id()
    return {"furnace": ds, "features": capability(ds)}


@app.get("/playback")
def playback_route(stride: int = 6) -> dict:
    return playback(stride)


@app.get("/series")
def series(tag: str, start: Optional[str] = None, end: Optional[str] = None, limit: int = 400) -> dict:
    try:
        return slice_series(tag, start, end, min(limit, 2000))
    except KeyError as exc:
        raise HTTPException(404, f"unknown tag {exc}") from exc


@app.get("/quality")
def quality() -> dict:
    return quality_report()


@app.get("/physics/pressure")
def pressure(t: str) -> dict:
    return pressure_at(pd.Timestamp(t))


@app.get("/physics/utilisation")
def gas_utilisation() -> dict:
    return utilisation()


@app.get("/physics/identity")
def identity() -> dict:
    return identity_summary()


@app.get("/predict/silicon")
def predict(t: str) -> dict:
    return predict_silicon(pd.Timestamp(t))


@app.get("/model-card")
def model_card(force: bool = False) -> dict:
    return train_card(force=force)


@app.get("/diagnose")
def diagnose_route() -> dict:
    return diagnose()


@app.get("/twin")
def twin(t: str) -> dict:
    return twin_at(pd.Timestamp(t))


@app.post("/scenario")
def scenario_route(body: ScenarioIn) -> dict:
    return scenario(
        pd.Timestamp(body.t),
        body.blast_delta,
        body.hot_blast_delta,
        body.oxygen_delta,
        body.top_pressure_delta,
        body.ore_coke_delta,
        body.cold_blast_temp_delta,
        body.cold_blast_pressure_delta,
        body.extra_deltas,
        body.horizon_hours,
        body.mode,
    )


@app.post("/audit")
def audit(body: AuditIn, x_hearthline_role: Optional[str] = Header(None)) -> dict:
    eff_role = body.role or x_hearthline_role or "operator"
    try:
        return append_audit(body.actor, body.action, body.target, body.payload, role=eff_role)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/audit/{event_id}/confirm-execution")
def confirm_execution_route(
    event_id: int,
    body: ConfirmExecutionIn,
    x_hearthline_role: Optional[str] = Header(None),
) -> dict:
    eff_role = body.role or x_hearthline_role or "operator"
    try:
        return record_confirmed_execution(event_id, body.actor, body.status, role=eff_role, notes=body.notes)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/audit")
def audit_list(limit: int = 100) -> dict:
    return {"model_version": MODEL_VERSION, "roles": {k: sorted(v) for k, v in ROLES_PERMISSIONS.items()}, "events": list_audit(limit)}


@app.get("/audit/verify")
def audit_verify_route() -> dict:
    return verify_audit_chain()


@app.post("/connector/probe")
def probe(body: ProbeIn) -> dict:
    try:
        return enforce_readonly_op(body.op)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc


@app.get("/connector/profiles")
def connector_profiles_route() -> dict:
    return connector_diagnostics()


@app.get("/stream/live")
async def stream_live_route(
    target_production: float = 4500.0,
    max_events: int = 6,
    interval_sec: float = 0.75,
) -> StreamingResponse:
    return StreamingResponse(
        sse_shadow_stream(target_production=target_production, max_events=max_events, interval_sec=interval_sec),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/modelops/status")
def modelops_status_route() -> dict:
    return modelops_status()


@app.get("/knowledge")
def knowledge_route(q: Optional[str] = None) -> dict:
    return list_knowledge_articles(query=q)


@app.get("/industrial-data/summary")
def industrial_data_summary_route(sample_limit: int = 24) -> dict:
    return industrial_plant_data_summary(sample_limit=sample_limit)


@app.get("/industrial-data/export.csv")
def industrial_data_export_route(limit: int = 500) -> PlainTextResponse:
    csv_text = export_plant_slice_csv(limit=limit)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="evraz_zsmk_plant_extract.csv"'},
    )
