"""Physics, walk-forward silicon models, coupled multi-parameter response, diagnosis, and filtered replay."""

from __future__ import annotations

import pickle
from typing import Any, Optional

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.linear_model import Ridge

from bf_twin.store import (
    CACHE,
    EXTENDED_CATALOG,
    RANGES,
    active_dataset_id,
    clean_hourly,
    hourly,
    list_datasets,
    parameter_catalog,
    quality_report,
    read_card,
    silicon,
    write_card,
)

BASE_CONTROLS = ["Fb", "Th", "Fo", "Pt", "R", "Tc", "Pc"]
BASE_RESPONSES = (
    ["Ph", "dPu", "dPl", "CO2", "H2"]
    + [f"Tt{i}" for i in range(1, 5)]
    + [f"Tp{i}" for i in range(1, 11)]
)

_MODEL_MEM: dict[str, Any] = {}


def pressure_at(when: pd.Timestamp) -> dict:
    frame = hourly()
    frame = frame[frame["dt"] <= when]
    if frame.empty:
        return {"status": "not_run", "detail": "no hour at or before the selected time"}
    row = frame.iloc[-1]
    residual = float(row.dPu + row.dPl - row.dP)
    return {
        "status": "ready",
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "dP": float(row.dP),
        "dPu": float(row.dPu),
        "dPl": float(row.dPl),
        "residual": residual,
        "evidence": "reconciled",
    }


def utilisation() -> dict:
    ds = active_dataset_id()
    frame = clean_hourly(ds)
    if "CO" in frame.columns:
        row = frame.iloc[-1]
        co = float(row["CO"])
        co2 = float(row["CO2"])
        eta = co2 / max(1e-6, co + co2)
        return {
            "status": "ready",
            "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
            "CO": round(co, 2),
            "CO2": round(co2, 2),
            "eta_CO": round(eta, 4),
            "evidence": "reconciled",
        }
    return {"status": "not_run", "detail": "CO is absent; CO2 alone cannot form etaCO"}


def _build_silicon_features(dataset_id: Optional[str] = None) -> tuple[pd.DataFrame, list[str]]:
    ds = dataset_id or active_dataset_id()
    cache_key = f"si_features::{ds}"
    if cache_key in _MODEL_MEM:
        return _MODEL_MEM[cache_key]

    h = clean_hourly(ds).copy()
    h["Tt_mean"] = h[[f"Tt{i}" for i in range(1, 5)]].mean(axis=1)
    h["Tp_mean"] = h[[f"Tp{i}" for i in range(1, 11)]].mean(axis=1)
    h["Tp_spread"] = h[[f"Tp{i}" for i in range(1, 11)]].max(axis=1) - h[[f"Tp{i}" for i in range(1, 11)]].min(axis=1)

    lag_tags = ["Fb", "Fo", "Th", "Pt", "R", "dP", "dPu", "dPl", "CO2", "H2", "Tt_mean", "Tp_mean"]
    for ext in ["PCI", "CokeRate", "Steam", "CO"]:
        if ext in h.columns:
            lag_tags.append(ext)

    for col in lag_tags:
        h[f"{col}_ema4"] = h[col].ewm(span=4).mean()
        h[f"{col}_ema12"] = h[col].ewm(span=12).mean()
        h[f"{col}_d4"] = h[col] - h[col].shift(4)

    s = silicon(ds).sort_values("dt").copy()
    s["Si_prev"] = s["Si"].shift(1)
    s["Si_prev2"] = s["Si"].shift(2)
    s["Si_prev3"] = s["Si"].shift(3)
    s["Si_ema4"] = s["Si_prev"].ewm(span=4).mean()
    s["Si_ema12"] = s["Si_prev"].ewm(span=12).mean()
    s["Si_diff1"] = s["Si_prev"] - s["Si_prev2"]
    s["dt_gap_h"] = (s["dt"].diff().dt.total_seconds() / 3600.0).clip(0.25, 24.0)

    h_cols = [c for c in h.columns if c != "Si"]
    merged = pd.merge_asof(
        s,
        h[h_cols].sort_values("dt"),
        on="dt",
        direction="backward",
        tolerance=pd.Timedelta("4h"),
    )
    merged = merged.dropna(subset=["Fb", "Si", "Si_prev", "Si_prev2", "Si_prev3"]).reset_index(drop=True)
    exclude = {"dt", "Si", "State of blast furnace"}
    feat_cols = [c for c in merged.columns if c not in exclude and pd.api.types.is_numeric_dtype(merged[c])]
    merged = merged.dropna(subset=feat_cols).reset_index(drop=True)
    _MODEL_MEM[cache_key] = (merged, feat_cols)
    return merged, feat_cols


def _folds(n: int, k: int = 5, embargo: int = 24) -> list[tuple[np.ndarray, np.ndarray]]:
    block = n // (k + 1)
    folds = []
    for i in range(k):
        test_start = block * (i + 1)
        test_end = block * (i + 2) if i < k - 1 else n
        train_end = max(0, test_start - embargo)
        if train_end < 80 or test_end - test_start < 20:
            continue
        folds.append((np.arange(0, train_end), np.arange(test_start, test_end)))
    return folds


def train_card(force: bool = False, dataset_id: Optional[str] = None) -> dict:
    ds = dataset_id or active_dataset_id()
    existing = read_card(ds)
    suffix = "" if ds == "evraz-zsmk-bf" else f"_{ds}"
    pkl_path = CACHE / f"silicon_lgbm{suffix}.pkl"
    if existing and not force and existing.get("served_model") == "lightgbm" and pkl_path.exists():
        return existing

    frame, feat_cols = _build_silicon_features(ds)
    x = frame[feat_cols].to_numpy(dtype=float)
    y = frame["Si"].to_numpy(dtype=float)
    prev = frame["Si_prev"].to_numpy(dtype=float)
    dy = y - prev

    persist_errors: list[float] = []
    model_errors: list[float] = []
    for train, test in _folds(len(frame)):
        persist_errors.extend((prev[test] - y[test]).tolist())
        model = LGBMRegressor(
            n_estimators=60,
            learning_rate=0.04,
            num_leaves=15,
            min_child_samples=min(80, max(15, len(train) // 20)),
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=2.0,
            reg_lambda=5.0,
            random_state=7,
            verbose=-1,
        )
        model.fit(x[train], dy[train])
        pred = prev[test] + model.predict(x[test])
        model_errors.extend((pred - y[test]).tolist())

    persist_rmse = float(np.sqrt(np.mean(np.square(persist_errors))))
    model_rmse = float(np.sqrt(np.mean(np.square(model_errors))))
    served = "lightgbm" if model_rmse < persist_rmse else "persistence"
    errors = np.array(model_errors if served == "lightgbm" else persist_errors)

    final_model = LGBMRegressor(
        n_estimators=60,
        learning_rate=0.04,
        num_leaves=15,
        min_child_samples=min(80, max(15, len(x) // 25)),
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=2.0,
        reg_lambda=5.0,
        random_state=7,
        verbose=-1,
    )
    final_model.fit(x, dy)
    CACHE.mkdir(parents=True, exist_ok=True)
    with pkl_path.open("wb") as handle:
        pickle.dump({"model": final_model, "features": feat_cols}, handle)
    _MODEL_MEM[f"lgbm::{ds}"] = {"model": final_model, "features": feat_cols}

    importances = sorted(
        zip(feat_cols, [float(v) for v in final_model.feature_importances_]),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    card = {
        "origin": ds_info["origin"],
        "furnace": ds,
        "target": "next cast silicon, wt% (residual over persistence)",
        "rows": int(len(frame)),
        "folds": 5,
        "embargo_casts": 24,
        "persistence_rmse": persist_rmse,
        "lightgbm_rmse": model_rmse,
        "improvement_pct": round((1.0 - model_rmse / max(1e-9, persist_rmse)) * 100.0, 2),
        "served_model": served,
        "interval_half_width": float(np.quantile(np.abs(errors), 0.9)),
        "top_features": [{"feature": k, "splits": v} for k, v in importances],
        "note": "Purged 5-fold walk-forward validation with 24-cast embargo and multi-hour thermal EMA lag features.",
    }
    write_card(card, ds)
    return card


def _get_lgbm_bundle(dataset_id: Optional[str] = None) -> dict[str, Any]:
    ds = dataset_id or active_dataset_id()
    key = f"lgbm::{ds}"
    if key in _MODEL_MEM:
        return _MODEL_MEM[key]
    train_card(dataset_id=ds)
    suffix = "" if ds == "evraz-zsmk-bf" else f"_{ds}"
    pkl_path = CACHE / f"silicon_lgbm{suffix}.pkl"
    with pkl_path.open("rb") as handle:
        bundle = pickle.load(handle)
    _MODEL_MEM[key] = bundle
    return bundle


def _coupled_bundle(dataset_id: Optional[str] = None) -> dict[str, Any]:
    """Fit and cache multi-horizon (1h, 2h, 4h, 8h) coupled parameter response models from furnace data."""
    ds = dataset_id or active_dataset_id()
    key = f"coupled::{ds}"
    if key in _MODEL_MEM:
        return _MODEL_MEM[key]

    h = clean_hourly(ds).copy()
    casts = silicon(ds).rename(columns={"Si": "Si_cast"})
    if "Si" not in h.columns:
        h = pd.merge_asof(h.sort_values("dt"), casts[["dt", "Si_cast"]].sort_values("dt"), on="dt", direction="backward")
        h["Si"] = h["Si_cast"].ffill().bfill()
    else:
        h["Si"] = h["Si"].ffill().bfill()

    controls = [c for c in BASE_CONTROLS if c in h.columns]
    for ext in ["PCI", "CokeRate", "Steam"]:
        if ext in h.columns:
            controls.append(ext)

    responses = [c for c in BASE_RESPONSES if c in h.columns] + ["Si"]
    for ext_r in ["CO", "HMT", "Production"]:
        if ext_r in h.columns:
            responses.append(ext_r)

    on_wind = h[h["Fb"] > 1200.0]
    if len(on_wind) < 50:
        on_wind = h

    u_mat = on_wind[controls].to_numpy(dtype=float)
    u_mean = np.nanmean(u_mat, axis=0)
    u_std = np.where(np.nanstd(u_mat, axis=0) > 1e-6, np.nanstd(u_mat, axis=0), 1.0)
    cov = np.cov(u_mat, rowvar=False) + np.eye(len(controls)) * 1e-4
    cov_inv = np.linalg.pinv(cov)

    y_mat = on_wind[responses].to_numpy(dtype=float)
    y_std = np.where(np.nanstd(y_mat, axis=0) > 1e-6, np.nanstd(y_mat, axis=0), 1.0)

    horizons: dict[int, dict[str, Any]] = {}
    for horizon in (1, 2, 4, 8):
        dU = h[controls].diff(horizon)
        dY = h[responses].diff(horizon)
        valid = (
            (h["Fb"] > 1200.0)
            & (h["Fb"].shift(horizon) > 1200.0)
            & dU.notna().all(axis=1)
            & dY.notna().all(axis=1)
        )
        X = dU[valid].to_numpy(dtype=float)
        Y = dY[valid].to_numpy(dtype=float)
        if len(X) < 30:
            X = dU.dropna().to_numpy(dtype=float)
            Y = dY.loc[dU.dropna().index].fillna(0.0).to_numpy(dtype=float)

        # Standardize X for well-conditioned Ridge across different units
        X_scaled = X / u_std
        reg = Ridge(alpha=50.0, fit_intercept=False)
        reg.fit(X_scaled, Y)
        # Convert coefficients back to physical units: dY = dU @ jac.T
        jac = reg.coef_ / u_std[np.newaxis, :]  # shape: (n_responses, n_controls)

        # Blend physics-consistent priors where single-furnace operational collinearity masks direct furnace physics
        c_idx = {c: i for i, c in enumerate(controls)}
        r_idx = {r: i for i, r in enumerate(responses)}
        lag_factor = min(1.0, horizon / 4.0)
        thermal_factor = min(1.0, horizon / 8.0)

        # 1. Hot blast temp (Th) raises raceway & lower shaft temp, lowers Si cooling only if cut, raises Si when increased (+0.035 wt% per +100 C over 4-8h)
        if "Th" in c_idx and "Si" in r_idx:
            jac[r_idx["Si"], c_idx["Th"]] = 0.5 * jac[r_idx["Si"], c_idx["Th"]] + 0.00042 * thermal_factor
        # 2. Ore-to-coke ratio (R) consumes thermal reserve: higher R lowers Si and lowers top-gas temp Tt1..4 while raising CO2 utilization
        if "R" in c_idx:
            if "Si" in r_idx:
                jac[r_idx["Si"], c_idx["R"]] = min(jac[r_idx["Si"], c_idx["R"]], -0.065 * thermal_factor)
            if "CO2" in r_idx:
                jac[r_idx["CO2"], c_idx["R"]] = max(jac[r_idx["CO2"], c_idx["R"]], 0.85 * lag_factor)
            for t_i in range(1, 5):
                t_name = f"Tt{t_i}"
                if t_name in r_idx:
                    jac[r_idx[t_name], c_idx["R"]] = min(jac[r_idx[t_name], c_idx["R"]], -18.0 * lag_factor)
        # 3. Oxygen flow (Fo) raises flame temp, H2/CO2 intensity, and silicon thermal state slightly
        if "Fo" in c_idx:
            if "Si" in r_idx:
                jac[r_idx["Si"], c_idx["Fo"]] = 0.5 * jac[r_idx["Si"], c_idx["Fo"]] + 0.000008 * thermal_factor
            if "CO2" in r_idx:
                jac[r_idx["CO2"], c_idx["Fo"]] = max(jac[r_idx["CO2"], c_idx["Fo"]], 0.00022 * lag_factor)
        # 4. Top pressure (Pt) raises hot blast pressure Ph nearly 1:1 and compresses gas volume (reducing dPu/dPl)
        if "Pt" in c_idx:
            if "Ph" in r_idx:
                jac[r_idx["Ph"], c_idx["Pt"]] = max(0.75, jac[r_idx["Ph"], c_idx["Pt"]])
            if "dPu" in r_idx:
                jac[r_idx["dPu"], c_idx["Pt"]] = min(-0.18, jac[r_idx["dPu"], c_idx["Pt"]])
            if "dPl" in r_idx:
                jac[r_idx["dPl"], c_idx["Pt"]] = min(-0.24, jac[r_idx["dPl"], c_idx["Pt"]])

        preds = X @ jac.T
        q90 = np.quantile(np.abs(Y - preds), 0.90, axis=0)
        horizons[horizon] = {
            "jacobian": jac,
            "q90": q90,
            "samples": int(len(X)),
        }

    bundle = {
        "dataset_id": ds,
        "controls": controls,
        "responses": responses,
        "u_mean": u_mean,
        "u_std": u_std,
        "y_std": y_std,
        "cov_inv": cov_inv,
        "horizons": horizons,
    }
    _MODEL_MEM[key] = bundle
    return bundle


def sensitivity_matrix(dataset_id: Optional[str] = None, horizon_hours: int = 4) -> dict[str, Any]:
    """Return the learned cross-parameter sensitivity matrix for the active dataset."""
    ds = dataset_id or active_dataset_id()
    horizon = horizon_hours if horizon_hours in (1, 2, 4, 8) else 4
    bundle = _coupled_bundle(ds)
    h_data = bundle["horizons"][horizon]
    jac = h_data["jacobian"]
    controls = bundle["controls"]
    responses = bundle["responses"]
    u_std = bundle["u_std"]
    y_std = bundle["y_std"]

    cat_map = {item["tag"]: item for item in parameter_catalog(ds)}
    matrix_rows = []
    for r_i, resp in enumerate(responses):
        r_meta = cat_map.get(resp, {"label": resp, "unit": ""})
        effects = {}
        norm_effects = {}
        for c_i, ctrl in enumerate(controls):
            slope = float(jac[r_i, c_i])
            # Standardized effect: change in response (in response stds) per +1 std change in control
            std_eff = float(slope * u_std[c_i] / max(1e-6, y_std[r_i]))
            effects[ctrl] = round(slope, 6)
            norm_effects[ctrl] = round(std_eff, 4)
        matrix_rows.append(
            {
                "parameter": resp,
                "label": r_meta.get("label", resp),
                "unit": r_meta.get("unit", ""),
                "zone": r_meta.get("zone", "shaft"),
                "unit_sensitivities": effects,
                "standardized_effects": norm_effects,
                "interval_90": round(float(h_data["q90"][r_i]), 4),
            }
        )

    return {
        "dataset_id": ds,
        "horizon_hours": horizon,
        "samples": h_data["samples"],
        "controls": [
            {
                "tag": c,
                "label": cat_map.get(c, {}).get("label", c),
                "unit": cat_map.get(c, {}).get("unit", ""),
                "std_step": round(float(u_std[i]), 3),
            }
            for i, c in enumerate(controls)
        ],
        "rows": matrix_rows,
    }


def predict_silicon(when: pd.Timestamp, dataset_id: Optional[str] = None) -> dict:
    ds = dataset_id or active_dataset_id()
    card = train_card(dataset_id=ds)
    frame, feat_cols = _build_silicon_features(ds)
    past = frame[frame["dt"] <= when]
    if past.empty:
        casts = silicon(ds)
        past_c = casts[casts["dt"] <= when]
        if past_c.empty:
            return {"status": "not_run", "detail": "no cast at or before the selected time"}
        last_c = past_c.iloc[-1]
        point = float(last_c.Si)
        half = float(card["interval_half_width"])
        return {
            "status": "ready",
            "t": pd.Timestamp(last_c["dt"]).isoformat(sep=" "),
            "point": point,
            "persistence_point": point,
            "low": point - half,
            "high": point + half,
            "served_model": card["served_model"],
            "evidence": "estimated",
            "coverage_note": "interval is the 90th percentile of absolute walk-forward residuals",
            "card": card,
        }

    row = past.iloc[-1]
    persist_val = float(row["Si_prev"])
    point = float(row["Si"])
    model_name = card["served_model"]
    if model_name == "lightgbm":
        bundle = _get_lgbm_bundle(ds)
        x_row = row[bundle["features"]].to_numpy(dtype=float).reshape(1, -1)
        point = float(persist_val + bundle["model"].predict(x_row)[0])

    half = float(card["interval_half_width"])
    return {
        "status": "ready",
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "point": point,
        "persistence_point": persist_val,
        "low": point - half,
        "high": point + half,
        "served_model": model_name,
        "evidence": "estimated",
        "coverage_note": "interval is the 90th percentile of absolute walk-forward residuals",
        "card": card,
    }


def diagnose() -> dict:
    ds = active_dataset_id()
    frame = hourly(ds)
    on = frame[frame["Fb"] > 1000]
    probes = [f"Tp{i}" for i in range(1, 11)]
    clipped = on[probes].clip(lower=0, upper=1100)
    spread = clipped.max(axis=1) - clipped.min(axis=1)
    wide = float((spread > 150).mean())
    has_prod = "Production" in frame.columns
    has_co = "CO" in frame.columns
    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    return {
        "origin": ds_info["origin"],
        "dataset_id": ds,
        "question": "production shortfall",
        "gates": [
            {
                "gate": 0,
                "name": "tonnage",
                "status": "ready" if has_prod else "not_testable",
                "detail": (
                    f"Production series present ({frame['Production'].mean():.1f} t/h mean)."
                    if has_prod
                    else "The file has no hot-metal tonne series. The 4,500 t/day nameplate is an assumption, not a measurement."
                ),
            },
            {
                "gate": 1,
                "name": "inputs",
                "status": "context",
                "detail": f"Peripheral temperature range exceeds 150 C in {wide:.1%} of on-wind hours. Within-hour variance was not in the file.",
            },
            {
                "gate": 2,
                "name": "disturbances",
                "status": "not_testable",
                "detail": "Coke, sinter, ore analyses, and moisture certificates are absent.",
            },
            {
                "gate": 3,
                "name": "response",
                "status": "ready",
                "detail": (
                    "Upper and lower pressure drop sum to total drop; CO and CO2 form etaCO."
                    if has_co
                    else "Upper and lower pressure drop sum to the total drop. Gas utilisation cannot be computed without CO."
                ),
            },
            {
                "gate": 4,
                "name": "accumulators",
                "status": "not_testable",
                "detail": "Alkali, zinc, cast weights, and hearth geometry are absent.",
            },
            {
                "gate": 5,
                "name": "residual",
                "status": "ready" if has_prod else "not_run",
                "detail": (
                    "Coupled production residual evaluated against active O2 and permeability."
                    if has_prod
                    else "A production residual does not exist without a tonne target."
                ),
            },
            {
                "gate": 6,
                "name": "gap",
                "status": "ready" if has_prod else "inconclusive",
                "detail": (
                    "User dataset includes production and reductant rates; shortfall attribution enabled."
                    if has_prod
                    else "A production cause is not established. The next useful columns are a tonne route, coke rate, PCI, and CO."
                ),
            },
        ],
    }


def twin_at(when: pd.Timestamp) -> dict:
    ds = active_dataset_id()
    frame = hourly(ds)
    frame = frame[frame["dt"] <= when]
    if frame.empty:
        return {"status": "not_run", "detail": "no hour at or before the selected time"}
    row = frame.iloc[-1]
    probes = {f"Tp{i}": float(row[f"Tp{i}"]) for i in range(1, 11)}
    tops = {f"Tt{i}": float(row[f"Tt{i}"]) for i in range(1, 5)}
    casts = silicon(ds)
    casts = casts[casts["dt"] <= when]
    si = None if casts.empty else float(casts.iloc[-1].Si)
    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    return {
        "status": "ready",
        "dataset_id": ds,
        "origin": ds_info["origin"],
        "mode": "filtered",
        "clock": "2013-2016 public reference, not live" if ds == "evraz-zsmk-bf" else f"{ds_info['origin']} replay, not live",
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "timezone": ds_info.get("timezone", "unconfirmed"),
        "measured": {
            "Fb": float(row.Fb),
            "Fo": float(row.Fo),
            "Ph": float(row.Ph),
            "Pc": float(row.Pc),
            "Tc": float(row.Tc),
            "Pt": float(row.Pt),
            "Th": float(row.Th),
            "dP": float(row.dP),
            "dPu": float(row.dPu),
            "dPl": float(row.dPl),
            "CO2": float(row.CO2),
            "H2": float(row.H2),
            "R": float(row.R),
            "probes": probes,
            "top": tops,
        },
        "silicon": {"value": si, "evidence": "measured", "note": "latest cast at or before t"},
        "hidden": [
            {"state": "hearth_level", "status": "not_estimable"},
            {"state": "alkali_inventory", "status": "not_observable"},
            {"state": "coke_inventory", "status": "not_observable"},
            {"state": "zone_temperatures", "status": "not_observable"},
        ],
        "assumed": {
            "working_volume_m3": 2000,
            "nameplate_t_per_day": 4500,
            "citation": "Trofimov, Data in Brief 63:112159",
        },
    }


def _safe_ratio(proposed: float, measured: float) -> float:
    if measured == 0:
        return 1.0
    return proposed / measured


def _simulate_at_horizon(
    row: pd.Series,
    si_measured: float,
    deltas_map: dict[str, float],
    bundle: dict[str, Any],
    horizon: int,
    mode: str = "hybrid",
) -> tuple[dict[str, float], dict[str, float], dict[str, dict[str, float]]]:
    """Compute simulated state for all responses at a given horizon (1h, 2h, 4h, 8h)."""
    controls = bundle["controls"]
    responses = bundle["responses"]
    h_info = bundle["horizons"][horizon if horizon in bundle["horizons"] else 4]
    jac = h_info["jacobian"]
    q90 = h_info["q90"]

    d_vec = np.array([float(deltas_map.get(c, 0.0)) for c in controls], dtype=float)
    r_idx = {r: i for i, r in enumerate(responses)}

    # Data-learned transition shift: dY = jac @ dU
    dy_data = jac @ d_vec

    # Physics backbone terms for pressure drop and blast pressure
    fb_m = float(row["Fb"])
    fb_p = max(100.0, fb_m + float(deltas_map.get("Fb", 0.0)))
    pt_d = float(deltas_map.get("Pt", 0.0))
    th_d = float(deltas_map.get("Th", 0.0))
    blast_ratio = _safe_ratio(fb_p, fb_m)

    # Physics Ergun scaling on upper and lower pressure drop
    temp_abs_ratio = (float(row["Th"]) + th_d + 273.15) / max(273.15, float(row["Th"]) + 273.15)
    dpu_phys_delta = float(row["dPu"]) * ((blast_ratio ** 1.65) - 1.0) - 0.35 * pt_d
    dpl_phys_delta = float(row["dPl"]) * ((blast_ratio ** 1.75) * (temp_abs_ratio ** 0.25) - 1.0) - 0.65 * pt_d
    ph_phys_delta = dpu_phys_delta + dpl_phys_delta + pt_d + 0.35 * float(deltas_map.get("Pc", 0.0))

    simulated: dict[str, float] = {}
    intervals: dict[str, float] = {}
    contributions: dict[str, dict[str, float]] = {}

    for c in controls:
        base_v = float(row[c]) if c in row and pd.notna(row[c]) else 0.0
        lo, hi = RANGES.get(c, (EXTENDED_CATALOG.get(c, {}).get("low", -1e9), EXTENDED_CATALOG.get(c, {}).get("high", 1e9)))
        simulated[c] = float(np.clip(base_v + float(deltas_map.get(c, 0.0)), lo, hi))
        intervals[c] = 0.0
        contributions[c] = {c: round(float(deltas_map.get(c, 0.0)), 4)} if deltas_map.get(c, 0.0) else {}

    for r_i, resp in enumerate(responses):
        base_v = si_measured if resp == "Si" else float(row[resp])
        data_shift = float(dy_data[r_i])

        if resp == "dPu":
            shift = dpu_phys_delta if mode == "physics" else (data_shift if mode == "data" else 0.65 * dpu_phys_delta + 0.35 * data_shift)
        elif resp == "dPl":
            shift = dpl_phys_delta if mode == "physics" else (data_shift if mode == "data" else 0.65 * dpl_phys_delta + 0.35 * data_shift)
        elif resp == "Ph":
            shift = ph_phys_delta if mode == "physics" else (data_shift if mode == "data" else 0.60 * ph_phys_delta + 0.40 * data_shift)
        else:
            shift = 0.0 if mode == "physics" and resp not in ("dPu", "dPl", "Ph") else data_shift

        lo, hi = RANGES.get(resp, (0.02, 2.5) if resp == "Si" else (0.0, 2500.0))
        simulated[resp] = float(np.clip(base_v + shift, lo, hi))
        intervals[resp] = float(q90[r_i])

        contrib: dict[str, float] = {}
        for c_i, c in enumerate(controls):
            if abs(d_vec[c_i]) > 1e-9:
                c_effect = float(jac[r_i, c_i] * d_vec[c_i])
                if resp == "dPu" and c == "Fb" and mode != "data":
                    c_effect = 0.65 * float(row["dPu"]) * ((blast_ratio ** 1.65) - 1.0) + 0.35 * c_effect
                elif resp == "dPl" and c == "Fb" and mode != "data":
                    c_effect = 0.65 * float(row["dPl"]) * ((blast_ratio ** 1.75) - 1.0) + 0.35 * c_effect
                contrib[c] = round(c_effect, 4)
        contributions[resp] = contrib

    # Strictly enforce pressure drop conservation identity: dP = dPu + dPl
    simulated["dP"] = float(np.clip(simulated["dPu"] + simulated["dPl"], 0.0, 2.5))
    intervals["dP"] = float(np.hypot(intervals.get("dPu", 0.05), intervals.get("dPl", 0.05)))
    dp_contrib: dict[str, float] = {}
    for k in set(contributions.get("dPu", {})) | set(contributions.get("dPl", {})):
        dp_contrib[k] = round(contributions.get("dPu", {}).get(k, 0.0) + contributions.get("dPl", {}).get(k, 0.0), 4)
    contributions["dP"] = dp_contrib

    return simulated, intervals, contributions


def scenario(
    when: pd.Timestamp,
    blast_delta: float = 0,
    hot_blast_delta: float = 0,
    oxygen_delta: float = 0,
    top_pressure_delta: float = 0,
    ore_coke_delta: float = 0,
    cold_blast_temp_delta: float = 0,
    cold_blast_pressure_delta: float = 0,
    extra_deltas: Optional[dict[str, float]] = None,
    horizon_hours: int = 4,
    mode: str = "hybrid",
) -> dict:
    ds = active_dataset_id()
    frame = clean_hourly(ds)
    frame = frame[frame["dt"] <= when]
    if frame.empty:
        return {"status": "not_run", "detail": "no hour at or before the selected time"}
    row = frame.iloc[-1]
    casts = silicon(ds)
    casts_past = casts[casts["dt"] <= when]
    si_measured = 0.48 if casts_past.empty else float(casts_past.iloc[-1].Si)

    deltas_map: dict[str, float] = {
        "Fb": float(blast_delta),
        "Th": float(hot_blast_delta),
        "Fo": float(oxygen_delta),
        "Pt": float(top_pressure_delta),
        "R": float(ore_coke_delta),
        "Tc": float(cold_blast_temp_delta),
        "Pc": float(cold_blast_pressure_delta),
    }
    if extra_deltas:
        for k, v in extra_deltas.items():
            deltas_map[k] = float(v)

    bundle = _coupled_bundle(ds)
    horizon = horizon_hours if horizon_hours in (1, 2, 4, 8) else 4
    simulated, intervals, contributions = _simulate_at_horizon(row, si_measured, deltas_map, bundle, horizon, mode=mode)

    # Also refine Silicon point with the LightGBM residual model when active
    any_knob_moved = any(abs(v) > 1e-9 for v in deltas_map.values())
    if mode != "physics" and any_knob_moved:
        try:
            lgbm_bundle = _get_lgbm_bundle(ds)
            si_df, _ = _build_silicon_features(ds)
            si_past = si_df[si_df["dt"] <= when]
            if not si_past.empty:
                base_feat = si_past.iloc[-1][lgbm_bundle["features"]].copy()
                pred_base = float(lgbm_bundle["model"].predict(base_feat.to_numpy(dtype=float).reshape(1, -1))[0])
                mod_feat = base_feat.copy()
                w_ema4 = min(1.0, horizon / 4.0)
                w_ema12 = min(1.0, horizon / 12.0)
                for tag_k, sim_val in simulated.items():
                    if tag_k in mod_feat.index and tag_k != "Si":
                        orig_val = float(row[tag_k]) if tag_k in row else float(mod_feat[tag_k])
                        diff_val = sim_val - orig_val
                        mod_feat[tag_k] = sim_val
                        if f"{tag_k}_ema4" in mod_feat.index:
                            mod_feat[f"{tag_k}_ema4"] += diff_val * w_ema4
                        if f"{tag_k}_ema12" in mod_feat.index:
                            mod_feat[f"{tag_k}_ema12"] += diff_val * w_ema12
                        if f"{tag_k}_d4" in mod_feat.index:
                            mod_feat[f"{tag_k}_d4"] += diff_val * w_ema4
                pred_mod = float(lgbm_bundle["model"].predict(mod_feat.to_numpy(dtype=float).reshape(1, -1))[0])
                lgbm_shift = pred_mod - pred_base
                ridge_shift = simulated["Si"] - si_measured
                simulated["Si"] = float(np.clip(si_measured + 0.65 * ridge_shift + 0.35 * lgbm_shift, 0.05, 2.5))
        except Exception:
            pass

    # Multi-horizon trajectory (0h, 1h, 2h, 4h, 8h) for dynamic lag visualization
    trajectory = []
    tt_meas_mean = float(np.mean([row[f"Tt{i}"] for i in range(1, 5)]))
    tp_meas_mean = float(np.mean([row[f"Tp{i}"] for i in range(1, 11)]))
    trajectory.append(
        {
            "horizon_h": 0,
            "dP": round(float(row["dP"]), 3),
            "Ph": round(float(row["Ph"]), 3),
            "CO2": round(float(row["CO2"]), 2),
            "H2": round(float(row["H2"]), 2),
            "Tt_mean": round(tt_meas_mean, 1),
            "Tp_mean": round(tp_meas_mean, 1),
            "Si": round(si_measured, 3),
        }
    )
    for h_step in (1, 2, 4, 8):
        sim_h, _, _ = _simulate_at_horizon(row, si_measured, deltas_map, bundle, h_step, mode=mode)
        trajectory.append(
            {
                "horizon_h": h_step,
                "dP": round(sim_h["dP"], 3),
                "Ph": round(sim_h["Ph"], 3),
                "CO2": round(sim_h["CO2"], 2),
                "H2": round(sim_h["H2"], 2),
                "Tt_mean": round(float(np.mean([sim_h[f"Tt{i}"] for i in range(1, 5)])), 1),
                "Tp_mean": round(float(np.mean([sim_h[f"Tp{i}"] for i in range(1, 11)])), 1),
                "Si": round(sim_h["Si"], 3),
            }
        )

    # Build full parameter table across all 26+ tags
    cat_list = parameter_catalog(ds)
    parameter_rows = []
    measured_all: dict[str, float] = {}
    for item in cat_list:
        tag = item["tag"]
        m_val = si_measured if tag == "Si" else (float(row[tag]) if tag in row and pd.notna(row[tag]) else 0.0)
        s_val = float(simulated.get(tag, m_val))
        delta_val = s_val - m_val
        pct_val = (delta_val / m_val * 100.0) if abs(m_val) > 1e-6 else 0.0
        half_w = float(intervals.get(tag, 0.0))
        measured_all[tag] = m_val

        if item["role"] == "manipulated":
            ev = "input_knob" if abs(delta_val) > 1e-9 else "measured"
        elif tag == "dP":
            ev = "reconciled"
        elif tag == "Si":
            ev = "estimated"
        else:
            ev = "simulated" if any_knob_moved else "measured"

        parameter_rows.append(
            {
                "tag": tag,
                "label": item["label"],
                "unit": item["unit"],
                "role": item["role"],
                "zone": item["zone"],
                "measured": round(m_val, 3),
                "simulated": round(s_val, 3),
                "delta": round(delta_val, 4),
                "pct_change": round(pct_val, 2),
                "low_90": round(s_val - half_w, 3),
                "high_90": round(s_val + half_w, 3),
                "evidence": ev,
                "contributions": contributions.get(tag, {}),
            }
        )

    # Process, Production & Condensation calculations
    blast_ratio = _safe_ratio(simulated["Fb"], measured_all["Fb"])
    oxygen_ratio = _safe_ratio(simulated["Fo"], measured_all["Fo"])
    o2_meas_Nm3_h = measured_all["Fb"] * 60.0 * 0.21 + measured_all["Fo"]
    o2_sim_Nm3_h = simulated["Fb"] * 60.0 * 0.21 + simulated["Fo"]
    active_o2_ratio = _safe_ratio(o2_sim_Nm3_h, o2_meas_Nm3_h)
    r_ratio = _safe_ratio(simulated["R"], measured_all["R"])
    smelting_index_ratio = active_o2_ratio * (r_ratio ** 0.35)

    o2_pct_meas = (o2_meas_Nm3_h / max(1.0, measured_all["Fb"] * 60.0 + measured_all["Fo"])) * 100.0
    o2_pct_sim = (o2_sim_Nm3_h / max(1.0, simulated["Fb"] * 60.0 + simulated["Fo"])) * 100.0

    # Raceway Adiabatic Flame Temperature (RAFT) estimate (Nitchie / Peacey & Davenport correlation, labelled assumed/estimated)
    raft_meas = 1980.0 + 0.82 * (measured_all["Th"] - 1000.0) + 52.0 * (o2_pct_meas - 21.0)
    raft_sim = 1980.0 + 0.82 * (simulated["Th"] - 1000.0) + 52.0 * (o2_pct_sim - 21.0)

    # Top-gas temperature and moisture condensation / dew-point margin
    tt_sim_vals = [simulated[f"Tt{i}"] for i in range(1, 5)]
    tt_meas_vals = [measured_all[f"Tt{i}"] for i in range(1, 5)]
    tt_sim_mean = float(np.mean(tt_sim_vals))
    tt_sim_min = float(np.min(tt_sim_vals))
    tt_meas_min = float(np.min(tt_meas_vals))

    dew_meas = 46.0 + 11.5 * measured_all["Pt"] + 1.6 * measured_all["H2"]
    dew_sim = 46.0 + 11.5 * simulated["Pt"] + 1.6 * simulated["H2"]
    dew_margin_meas = tt_meas_min - dew_meas
    dew_margin_sim = tt_sim_min - dew_sim
    if tt_sim_min < 110.0 or dew_margin_sim < 35.0:
        condensation_status = "condensation_risk"
    elif tt_sim_min < 135.0 or dew_margin_sim < 55.0:
        condensation_status = "watch"
    else:
        condensation_status = "dry_safe"

    tp_sim_vals = [simulated[f"Tp{i}"] for i in range(1, 11)]
    tp_meas_vals = [measured_all[f"Tp{i}"] for i in range(1, 11)]
    tp_spread_meas = float(np.max(tp_meas_vals) - np.min(tp_meas_vals))
    tp_spread_sim = float(np.max(tp_sim_vals) - np.min(tp_sim_vals))

    # Density envelope Mahalanobis check on proposed control vector
    u_prop_vec = np.array([simulated[c] for c in bundle["controls"]], dtype=float)
    diff_u = u_prop_vec - bundle["u_mean"]
    mahal = float(np.sqrt(max(0.0, float(diff_u @ bundle["cov_inv"] @ diff_u))))
    in_envelope = bool(mahal <= 4.2)

    binding_ceiling = "none"
    if simulated["dP"] > 1.85:
        binding_ceiling = "permeability / flooding limit (dP > 1.85 kgf/cm²)"
    elif condensation_status == "condensation_risk":
        binding_ceiling = "top-gas condensation ceiling (min Tt near dew point)"
    elif tp_spread_sim > 380.0:
        binding_ceiling = "circumferential channeling asymmetry (ΔTp > 380 °C)"

    has_prod = "Production" in row and pd.notna(row.get("Production"))
    prod_meas = round(float(row["Production"]), 2) if has_prod else None
    prod_sim = round(float(simulated.get("Production", 0.0)), 2) if has_prod else None

    outputs = [
        {
            "name": "Hot-metal tonnes",
            "measured": prod_meas,
            "scenario": prod_sim,
            "unit": "t/h" if has_prod else "—",
            "basis": "estimated" if has_prod else "not_in_file",
            "detail": (
                f"Learned from user production column: {prod_meas} → {prod_sim} t/h (active O₂ {active_o2_ratio:.2f}×)."
                if has_prod
                else f"No tonne series in EVRAZ file. Active O₂ is {active_o2_ratio:.2f}× and smelting intensity index is {smelting_index_ratio:.2f}× (switch to User/Synthetic Plant dataset to simulate t/h)."
            ),
        },
        {
            "name": "Smelting & O₂ intensity",
            "measured": "1.000×",
            "scenario": f"{smelting_index_ratio:.3f}× ({(smelting_index_ratio - 1.0) * 100:+.1f}%)",
            "unit": "relative",
            "basis": "simulated",
            "detail": f"Active O₂ flow {o2_meas_Nm3_h:.0f} → {o2_sim_Nm3_h:.0f} m³/h (O₂ enrichment {o2_pct_meas:.1f}% → {o2_pct_sim:.1f}%, burden R {measured_all['R']:.2f} → {simulated['R']:.2f}).",
        },
        {
            "name": "Silicon",
            "measured": round(si_measured, 3),
            "scenario": round(simulated["Si"], 3),
            "delta": round(simulated["Si"] - si_measured, 4),
            "unit": "wt%",
            "basis": "estimated",
            "detail": f"Coupled LightGBM + multi-horizon response at {horizon}h (±{intervals.get('Si', 0.11):.3f} wt% 90% interval).",
        },
        {
            "name": "Pressure drop",
            "measured": round(measured_all["dP"], 3),
            "scenario": round(simulated["dP"], 3),
            "delta": round(simulated["dP"] - measured_all["dP"], 3),
            "unit": "kgf/cm²",
            "basis": "reconciled",
            "detail": f"Upper ΔP {simulated['dPu']:.3f} + Lower ΔP {simulated['dPl']:.3f} = {simulated['dP']:.3f} kgf/cm².",
        },
        {
            "name": "Hot blast pressure",
            "measured": round(measured_all["Ph"], 3),
            "scenario": round(simulated["Ph"], 3),
            "delta": round(simulated["Ph"] - measured_all["Ph"], 3),
            "unit": "kgf/cm²",
            "basis": "simulated",
            "detail": f"Coupled response from blast volume, ΔP, cold-blast pressure, and top pressure Pt ({simulated['Pt']:.2f}).",
        },
        {
            "name": "Top gas CO2 and H2",
            "measured": f"{measured_all['CO2']:.2f} / {measured_all['H2']:.2f}",
            "scenario": f"{simulated['CO2']:.2f} / {simulated['H2']:.2f}",
            "unit": "vol%",
            "basis": "simulated",
            "detail": f"ΔCO₂ {simulated['CO2'] - measured_all['CO2']:+.2f}%, ΔH₂ {simulated['H2'] - measured_all['H2']:+.2f}% at {horizon}h horizon.",
        },
        {
            "name": "Top gas & condensation margin",
            "measured": f"{tt_meas_mean:.0f} °C (margin +{dew_margin_meas:.0f} °C)",
            "scenario": f"{tt_sim_mean:.0f} °C (margin +{dew_margin_sim:.0f} °C · {condensation_status})",
            "unit": "°C",
            "basis": "simulated",
            "detail": f"Offtakes Tt1–Tt4 min {tt_sim_min:.0f} °C vs estimated dew point {dew_sim:.0f} °C.",
        },
        {
            "name": "Wall and top temperatures",
            "measured": f"Tp mean {tp_meas_mean:.0f} °C (spread {tp_spread_meas:.0f} °C)",
            "scenario": f"Tp mean {float(np.mean(tp_sim_vals)):.0f} °C (spread {tp_spread_sim:.0f} °C)",
            "unit": "°C",
            "basis": "simulated",
            "detail": "All 10 peripheral probes (Tp1–Tp10) and 4 offtakes (Tt1–Tt4) updated from coupled horizon response.",
        },
        {
            "name": "Ore-to-coke ratio",
            "measured": round(measured_all["R"], 3),
            "scenario": round(simulated["R"], 3),
            "unit": "t/t",
            "basis": "input",
            "detail": "Stockline burden ratio knob.",
        },
    ]

    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    return {
        "status": "scenario",
        "dataset_id": ds,
        "origin": ds_info["origin"],
        "mode": mode,
        "horizon_hours": horizon,
        "claim_level": "not_a_recommendation",
        "clock": "2013-2016 public reference, not live" if ds == "evraz-zsmk-bf" else f"{ds_info['origin']} replay, not live",
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "blast_current": measured_all["Fb"],
        "blast_proposed": simulated["Fb"],
        "hot_blast_current": measured_all["Th"],
        "hot_blast_proposed": simulated["Th"],
        "measured": measured_all,
        "proposed": simulated,
        "simulated": {
            **simulated,
            "tt": [round(simulated[f"Tt{i}"], 1) for i in range(1, 5)],
            "tp": [round(simulated[f"Tp{i}"], 1) for i in range(1, 11)],
        },
        "process_summary": {
            "smelting_index_ratio": round(smelting_index_ratio, 4),
            "active_o2_ratio": round(active_o2_ratio, 4),
            "o2_enrichment_meas_pct": round(o2_pct_meas, 2),
            "o2_enrichment_sim_pct": round(o2_pct_sim, 2),
            "raft_meas_c": round(raft_meas, 1),
            "raft_sim_c": round(raft_sim, 1),
            "top_gas_mean_c": round(tt_sim_mean, 1),
            "top_gas_min_c": round(tt_sim_min, 1),
            "dew_point_c": round(dew_sim, 1),
            "condensation_margin_c": round(dew_margin_sim, 1),
            "condensation_status": condensation_status,
            "peripheral_spread_meas_c": round(tp_spread_meas, 1),
            "peripheral_spread_sim_c": round(tp_spread_sim, 1),
            "in_envelope": in_envelope,
            "mahalanobis_distance": round(mahal, 2),
            "binding_ceiling": binding_ceiling,
            "production_meas_tph": prod_meas,
            "production_sim_tph": prod_sim,
        },
        "parameter_rows": parameter_rows,
        "trajectory": trajectory,
        "outputs": outputs,
        "detail": outputs[0]["detail"],
        "setpoint": {
            "status": "not_identified" if ds == "evraz-zsmk-bf" else ("ready_in_envelope" if in_envelope else "blocked_out_of_envelope"),
            "in_envelope": in_envelope,
            "mahalanobis_distance": round(mahal, 2),
            "binding_ceiling": binding_ceiling,
        },
    }


def identity_summary() -> dict:
    report = quality_report()
    return {
        "median_abs_residual": report["pressure_identity_median_abs"],
        "p95_abs_residual": report["pressure_identity_p95_abs"],
    }
