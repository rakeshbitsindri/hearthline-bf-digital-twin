import pandas as pd
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

DEFAULT_DATASET = "evraz-zsmk-bf"


@pytest.fixture(autouse=True)
def restore_default_dataset():
    """The selected dataset is persisted, so a failing test must not leave it switched."""
    yield
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})


def test_health_is_public_reference():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    body = client.get("/health").json()
    assert body["origin"] == "public_reference"
    assert body["plant_write"] is False


def test_production_is_not_testable():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    features = {row["feature"]: row["status"] for row in client.get("/capability").json()["features"]}
    assert features["verified_shortfall"] == "not_testable"
    assert features["inverse_setpoint"] == "not_identified"
    assert features["gas_utilisation"] == "not_run"
    assert features["coupled_simulation"] == "ready"


def test_pressure_identity_is_tight():
    body = client.get("/physics/identity").json()
    assert body["median_abs_residual"] < 1e-6


def test_utilisation_does_not_invent_co():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    assert client.get("/physics/utilisation").json()["status"] == "not_run"


def test_diagnosis_does_not_invent_tonnes():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    gates = client.get("/diagnose").json()["gates"]
    assert gates[0]["status"] == "not_testable"
    assert "tonne" in gates[0]["detail"]


def test_connector_rejects_write():
    response = client.post("/connector/probe", json={"op": "write"})
    assert response.status_code == 403


def test_audit_appends():
    created = client.post(
        "/audit",
        json={"actor": "tester", "action": "reject", "target": "setpoint", "payload": {"reason": "not identified"}},
    ).json()
    events = client.get("/audit").json()["events"]
    assert events[-1]["id"] == created["id"]
    assert events[-1]["action"] == "reject"


def test_series_has_points():
    body = client.get("/series", params={"tag": "Th", "limit": 5}).json()
    assert body["evidence"] == "measured"
    assert len(body["points"]) == 5


def test_model_card_lightgbm_beats_persistence():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    card = client.get("/model-card", params={"force": True}).json()
    assert card["served_model"] == "lightgbm"
    assert card["lightgbm_rmse"] < card["persistence_rmse"]


def test_scenario_and_simulate_coupled_parameters():
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})
    hour = client.get("/furnace").json()["from"]
    when = (pd.Timestamp(hour) + pd.Timedelta(days=30)).isoformat(sep=" ")
    body = client.post(
        "/scenario",
        json={
            "t": when,
            "blast_delta": 250,
            "hot_blast_delta": 60,
            "oxygen_delta": 1500,
            "top_pressure_delta": 0.1,
            "ore_coke_delta": 0.2,
            "horizon_hours": 4,
            "mode": "hybrid",
        },
    ).json()
    assert body["setpoint"]["status"] == "not_identified"
    assert body["status"] == "scenario"
    tonnes = next(row for row in body["outputs"] if row["name"] == "Hot-metal tonnes")
    assert tonnes["basis"] == "not_in_file"
    assert len(body["parameter_rows"]) >= 28
    sim = body["simulated"]
    assert abs(sim["dP"] - (sim["dPu"] + sim["dPl"])) < 1e-4

    # Also verify /simulate and /optimize endpoints used by the 3D workbench
    sim_res = client.post(
        "/simulate",
        json={
            "t": when,
            "deltas": {"Fb": 200, "Th": 50, "PCI": 15},
            "switches": {"switch_dehumidification": True, "switch_center_coke": True},
            "mode": "hybrid",
            "horizon_hours": 24,
        },
    ).json()
    assert sim_res["status"] == "ready"
    assert len(sim_res["parameters"]) >= 35
    assert len(sim_res["trajectory_24h"]) == 25
    assert len(sim_res["attributions"]) == 3

    opt_res = client.post(
        "/optimize",
        json={"t": when, "target_production": 4650, "target_si": 0.46, "max_dp": 1.52},
    ).json()
    assert "recommendations" in opt_res
    assert len(opt_res["recommendations"]) == 8


def test_sensitivity_and_user_dataset_simulation():
    sens = client.get("/sensitivity", params={"horizon_hours": 4}).json()
    assert "jacobian" in sens
    assert "correlations" in sens
    assert len(sens["controls"]) >= 7

    # Test switching to synthetic full-sensor dataset (with Production, PCI, CokeRate, CO, HMT)
    sel = client.post("/datasets/select", json={"dataset_id": "synthetic-plant-bf1"}).json()
    assert sel["status"] == "ok"
    furn = client.get("/furnace").json()
    assert furn["has_production"] is True

    sc = client.post(
        "/scenario",
        json={
            "t": furn["to"],
            "blast_delta": 200,
            "oxygen_delta": 1000,
            "extra_deltas": {"PCI": 15},
            "horizon_hours": 4,
        },
    ).json()
    tonnes = next(row for row in sc["outputs"] if row["name"] == "Hot-metal tonnes")
    assert tonnes["basis"] == "estimated"
    assert tonnes["scenario"] is not None

    # Restore default dataset
    client.post("/datasets/select", json={"dataset_id": "evraz-zsmk-bf"})


def test_oxygen_enrichment_is_above_air_not_o2_to_air_ratio():
    """Enrichment is (total O2 / total volume) - 21, not Fo/air. The ratio form inflated RAFT ~130 C."""
    from bf_twin.simulator import compute_physics_state

    phys = compute_physics_state({"Fb": 3837.0, "Fo": 20939.0, "Th": 1028.0})
    air_h = 3837.0 * 60.0
    expected_total = 100.0 * (0.21 * air_h + 20939.0) / (air_h + 20939.0)
    assert phys["O2TotalPct"] == pytest.approx(expected_total, abs=0.02)
    assert phys["O2EnrichmentPct"] == pytest.approx(expected_total - 21.0, abs=0.02)
    # The old ratio form gave 9.09 points of enrichment for this hour.
    assert phys["O2EnrichmentPct"] < 8.0


def test_soft_limit_keeps_downstream_response_alive_at_a_ceiling():
    """A hard clip zeroed every downstream effect once a quantity rested on its limit."""
    from bf_twin.simulator import compute_physics_state

    base = {"Fb": 3837.0, "Fo": 20939.0, "Th": 1028.0, "PCI": 115.0, "CokeRate": 375.0}
    hot = dict(base, Th=1068.0)
    a, b = compute_physics_state(base), compute_physics_state(hot)
    assert b["RAFT"] > a["RAFT"]
    # Blast temperature must still reach hot metal temperature and silicon.
    assert b["HMT"] > a["HMT"]
    assert b["Si"] > a["Si"]


def test_physics_is_reconciled_onto_measured_sensors():
    """Absolute values must agree with the instruments; only unmeasured quantities free-run."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    hour = client.get("/furnace").json()["from"]
    when = (pd.Timestamp(hour) + pd.Timedelta(days=30)).isoformat(sep=" ")
    body = client.post("/simulate", json={"t": when}).json()

    rec = body["reconciliation"]
    assert {"dP", "dPu", "dPl", "CO2"}.issubset(set(rec["anchored"]))
    # dP = dPu + dPl must survive the reconciliation.
    kpi = body["physics_kpis"]
    assert kpi["dP"] == pytest.approx(kpi["dPu"] + kpi["dPl"], abs=1e-3)
    # EVRAZ has no RAFT or HMT sensor, so neither may be presented as an absolute value.
    status = rec["kpi_status"]
    assert status["RAFT"]["show_absolute"] is False
    assert status["HMT"]["show_absolute"] is False
    assert status["dP"]["status"] == "measured_anchored"


def test_reconciliation_does_not_damp_the_simulated_response():
    """The bias is a constant, so a knob change must produce the same delta it did free-running."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    hour = client.get("/furnace").json()["from"]
    when = (pd.Timestamp(hour) + pd.Timedelta(days=30)).isoformat(sep=" ")
    base = client.post("/simulate", json={"t": when}).json()
    moved = client.post("/simulate", json={"t": when, "deltas": {"Th": 40.0}}).json()

    d_raft = moved["physics_kpis"]["RAFT"] - base["physics_kpis"]["RAFT"]
    assert d_raft == pytest.approx(0.82 * 40.0, abs=2.0)
    changed = [
        k
        for k in ("RAFT", "HMT", "Si", "CZHeight", "Tp1", "Tt1", "CO2")
        if abs(moved["simulated_state"].get(k, 0.0) - base["simulated_state"].get(k, 0.0)) > 1e-6
    ]
    assert len(changed) >= 4, f"blast temperature only moved {changed}"


def test_zero_change_identity_nothing_moves():
    """
    If no knob moved, no output may move. A phantom delta makes every real effect
    unreadable. This caught an absolute switch term and a clamp that rewrote measured values.
    """
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    hour = client.get("/furnace").json()["from"]
    for offset_days in (120, 400, 700):
        when = (pd.Timestamp(hour) + pd.Timedelta(days=offset_days)).isoformat(sep=" ")
        body = client.post("/simulate", json={"t": when}).json()
        base, sim = body["baseline_state"], body["simulated_state"]
        drift = {k: sim[k] - base[k] for k in set(base) & set(sim) if abs(sim[k] - base[k]) > 1e-6}
        assert drift == {}, f"{when} drifted with no input change: {drift}"


def test_measured_excursion_is_not_clipped_to_the_catalog_range():
    """A 2.94 wt% cast silicon is a real excursion and must not be rewritten as 1.62."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    body = client.post("/simulate", json={"t": "2014-07-12 18:00:00"}).json()
    assert body["baseline_state"]["Si"] == pytest.approx(2.94, abs=0.01)
    # One silicon on the screen: the ribbon and the physics panel must agree.
    assert body["simulated_state"]["Si"] == pytest.approx(body["physics_kpis"]["Si"], abs=1e-3)
    warning = next(w for w in body["reconciliation"]["warnings"] if w["quantity"] == "Si")
    assert warning["source"] == "measurement"


def test_unqualified_regime_suppresses_absolute_values():
    """Off wind the steady-state correlations do not hold, so nothing absolute is served."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    body = client.post("/simulate", json={"t": "2014-07-10 00:00:00"}).json()
    regime = body["operating_regime"]
    assert regime["qualified"] is False
    assert regime["regime"] in ("off_wind", "reduced_blast")
    status = body["reconciliation"]["kpi_status"]
    assert status["Production"]["show_absolute"] is False
    # A sensor reading still stands on its own even in an unqualified regime.
    assert status["dP"]["status"] == "measured_anchored"


def test_playback_frames_declare_operating_regime():
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    frames = client.get("/playback", params={"stride": 24}).json()["frames"]
    assert all("qualified" in f and "regime" in f for f in frames)
    assert any(f["qualified"] for f in frames)


def test_golden_ranges_scale_with_required_production_for_all_parameters():
    """Every parameter must have a Golden Range [golden_low, golden_high] that adapts to target_production."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    g_low_target = client.get("/golden-ranges", params={"target_production": 3900.0}).json()
    g_high_target = client.get("/golden-ranges", params={"target_production": 4850.0}).json()

    assert len(g_low_target["ranges"]) >= 41
    for tag, spec in g_low_target["ranges"].items():
        assert spec["golden_low"] < spec["golden_high"], f"{tag} has invalid golden bounds"
        assert spec["below_warning"] and spec["above_warning"], f"{tag} missing warning text"

    # Higher required production requires higher blast wind Fb and oxygen Fo golden ranges
    assert g_high_target["ranges"]["Fb"]["golden_center"] > g_low_target["ranges"]["Fb"]["golden_center"]
    assert g_high_target["ranges"]["Fo"]["golden_center"] > g_low_target["ranges"]["Fo"]["golden_center"]


def test_simulate_flags_below_and_above_golden_range_and_historical_shortfall_causes():
    """Moving a knob below or above its Golden Range warns the user; historical drops identify root-cause parameters."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    # 1. Check historical drop episode attribution (e.g. 2014-11-18 23:00:00 where wind and O2 dropped)
    hist = client.post("/simulate", json={"t": "2014-11-18 23:00:00", "target_production": 4500.0}).json()
    ga = hist["golden_analysis"]
    assert ga["shortfall_vs_target_t_d"] > 1000.0
    cause_tags = [c["tag"] for c in ga["historical_root_causes"]]
    assert "Fb" in cause_tags or "Fo" in cause_tags

    # 2. Check below_golden and above_golden warning when moving a knob on a normal hour
    low_fb = client.post(
        "/simulate",
        json={"t": "2014-07-15 12:00:00", "deltas": {"Fb": -700.0}, "target_production": 4500.0},
    ).json()
    fb_row = next(p for p in low_fb["parameters"] if p["tag"] == "Fb")
    assert fb_row["simulated_golden_status"] == "below_golden"
    assert fb_row["production_risk_t_d"] > 100.0
    assert "below the Golden Range" in fb_row["golden_warning"]

    high_sinter = client.post(
        "/simulate",
        json={"t": "2014-07-15 12:00:00", "deltas": {"SinterRDI": 9.0}, "target_production": 4500.0},
    ).json()
    rdi_row = next(p for p in high_sinter["parameters"] if p["tag"] == "SinterRDI")
    assert rdi_row["simulated_golden_status"] == "above_golden"
    assert rdi_row["production_risk_t_d"] > 20.0
    assert "exceeds the Golden Range" in rdi_row["golden_warning"]

    # 3. Verify /shortfalls endpoint scans history and returns categorized episodes with root causes
    sf = client.get("/shortfalls", params={"target_production": 4500.0, "limit": 10}).json()
    assert len(sf["episodes"]) >= 6
    assert all(len(ep["top_causes"]) >= 1 for ep in sf["episodes"])


def test_knowledge_hub_and_running_plant_industrial_data_endpoints():
    """Verify built-in knowledge chapters, running-plant EVRAZ data summary, and explicit exceptions."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    kb = client.get("/knowledge").json()
    assert kb["total_documents"] >= 27
    assert kb["total_words"] > 20000
    assert len(kb["exceptions"]) >= 6
    slugs = {d["slug"] for d in kb["documents"]}
    assert "04-hidden-state-mechanisms" in slugs

    ind = client.get("/industrial-data/summary", params={"sample_limit": 15}).json()
    pr = ind["plant_reference"]
    assert pr["hourly_rows"] == 29602
    assert pr["cast_silicon_analyses"] == 16589
    assert len(ind["tag_profiles"]) == 28
    assert len(ind["labeled_furnace_regimes"]) == 8
    assert len(ind["sample_plant_records"]) == 15

    csv_resp = client.get("/industrial-data/export.csv", params={"limit": 60})
    assert csv_resp.status_code == 200
    assert "Fb,Ph,Pc,Tc,Fo" in csv_resp.text


def test_trl7_harness_rbac_sha256_audit_sse_and_mahalanobis_envelope():
    """Verify RBAC enforcement, SHA-256 hash chain, post-hoc execution, SSE stream, and Mahalanobis MoC gate."""
    client.post("/datasets/select", json={"dataset_id": DEFAULT_DATASET})
    # Viewer role cannot accept setpoints (HTTP 403)
    denied = client.post(
        "/audit",
        json={"actor": "guest", "role": "viewer", "action": "accept", "target": "setpoint_test"},
    )
    assert denied.status_code == 403

    # Operator can accept, and post-hoc confirmed_execution is stored separately without breaking hash chain
    accepted = client.post(
        "/audit",
        json={"actor": "op1", "role": "operator", "action": "accept", "target": "setpoint_Fb_3680", "payload": {"Fb": 3680}},
    ).json()
    assert accepted["event_hash"]
    exec_rec = client.post(
        f"/audit/{accepted['id']}/confirm-execution",
        json={"actor": "shift_log", "role": "operator", "status": "executed_in_plant", "notes": "Verified"},
    ).json()
    assert "executed_in_plant" in exec_rec["confirmed_execution"]

    chain = client.get("/audit/verify").json()
    assert chain["intact"] is True

    # Out-of-envelope move triggers Mahalanobis MoC dossier
    extreme = client.post(
        "/simulate",
        json={"t": "2014-07-22 06:00:00", "deltas": {"Fb": 800.0, "Fo": 8000.0, "Th": 150.0}},
    ).json()
    assert extreme["envelope"]["in_envelope"] is False
    assert extreme["envelope"]["moc_dossier"]["status"] == "engineering_trial_required"

    # ModelOps & SSE live shadow stream
    mops = client.get("/modelops/status").json()
    assert len(mops["trl_ladder"]) == 7
    sse = client.get("/stream/live?max_events=2&interval_sec=0.05")
    assert sse.status_code == 200
    assert "event: twin_frame" in sse.text


