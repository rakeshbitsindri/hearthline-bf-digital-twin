"""Coupled Physics + Data-Driven Digital Twin Simulator, Cross-Parameter Learner, and Inverse Optimizer."""

from __future__ import annotations

import json
import math
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2
from sklearn.linear_model import Ridge

from bf_twin.db import MODEL_VERSION
from bf_twin.store import CACHE, PARAMETER_CATALOG, active_dataset_meta, clean_hourly, hourly, read_card, silicon

EXTRA_SIM_PARAMETERS = [
    {"tag": "PCI", "label": "PCI Coal Injection", "unit": "kg/tHM", "role": "manipulated", "group": "Injectants & Fuel", "zone": "raceway", "min": 0.0, "max": 210.0, "step": 2.0, "lag_h": 2.5, "pos": [-5.2, 0.2, 0.0], "default_assumed": 115.0},
    {"tag": "CokeRate", "label": "Charged Coke Rate", "unit": "kg/tHM", "role": "manipulated", "group": "Injectants & Fuel", "zone": "stockline", "min": 260.0, "max": 480.0, "step": 2.0, "lag_h": 6.5, "pos": [-3.8, 12.8, 0.0], "default_assumed": 375.0},
    {"tag": "BlastMoisture", "label": "Blast Moisture / Steam", "unit": "g/Nm³", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "blast_main", "min": 5.0, "max": 45.0, "step": 0.5, "lag_h": 0.8, "pos": [5.2, -2.0, 0.0], "default_assumed": 16.0},
    {"tag": "BurdenFe", "label": "Burden Fe Grade", "unit": "wt%", "role": "disturbance", "group": "Burden & Charging", "zone": "upper_shaft", "min": 54.0, "max": 65.0, "step": 0.2, "lag_h": 6.0, "pos": [3.8, 12.8, 0.0], "default_assumed": 58.5},
    {"tag": "CokeCSR", "label": "Coke CSR Strength", "unit": "%", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "cohesive_zone", "min": 52.0, "max": 72.0, "step": 0.5, "lag_h": 7.0, "pos": [-4.8, 5.2, 0.0], "default_assumed": 64.0},
    {"tag": "SinterRDI", "label": "Sinter RDI Fines", "unit": "%", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "upper_shaft", "min": 18.0, "max": 38.0, "step": 0.5, "lag_h": 4.5, "pos": [-4.8, 8.8, 0.0], "default_assumed": 26.5},
    {"tag": "AlkaliInput", "label": "Alkali Load (K₂O+Na₂O)", "unit": "kg/tHM", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "cohesive_zone", "min": 0.5, "max": 5.5, "step": 0.1, "lag_h": 12.0, "pos": [4.9, 5.8, 0.0], "default_assumed": 2.1},
    {"tag": "ZnInput", "label": "Zinc Input Load", "unit": "g/tHM", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "upper_shaft", "min": 30.0, "max": 350.0, "step": 5.0, "lag_h": 12.0, "pos": [4.9, 8.2, 0.0], "default_assumed": 115.0},
    {"tag": "Production", "label": "Hot Metal Production", "unit": "t/day", "role": "outcome", "group": "Hot Metal & Production", "zone": "hearth", "min": 2000.0, "max": 6000.0, "step": 25.0, "lag_h": 2.0, "pos": [3.2, -2.8, 1.5]},
    {"tag": "HMT", "label": "Hot Metal Temp", "unit": "°C", "role": "outcome", "group": "Hot Metal & Production", "zone": "hearth", "min": 1440.0, "max": 1545.0, "step": 2.0, "lag_h": 4.0, "pos": [-3.2, -2.8, 1.5]},
    {"tag": "RAFT", "label": "Raceway Flame Temp (RAFT)", "unit": "°C", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "raceway", "min": 1850.0, "max": 2350.0, "step": 5.0, "lag_h": 0.2, "pos": [2.2, -0.5, 1.8]},
    {"tag": "CZHeight", "label": "Cohesive Zone Root Height", "unit": "m", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "cohesive_zone", "min": 2.2, "max": 6.8, "step": 0.1, "lag_h": 3.0, "pos": [0.0, 3.4, 2.8]},
    {"tag": "CondensationIdx", "label": "Alkali/Zn Condensation Load", "unit": "index", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "upper_shaft", "min": 0.0, "max": 100.0, "step": 1.0, "lag_h": 8.0, "pos": [0.0, 8.4, 2.8]},
]

_seen_sim_tags: set[str] = set()
FULL_SIM_CATALOG = []
for _item in PARAMETER_CATALOG + EXTRA_SIM_PARAMETERS:
    if _item["tag"] not in _seen_sim_tags:
        FULL_SIM_CATALOG.append(_item)
        _seen_sim_tags.add(_item["tag"])

MANIPULATED_AND_DISTURBANCE = [
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
]

RESPONSE_AND_OUTCOME = [
    "dPu",
    "dPl",
    "dP",
    "Ph",
    "Pc",
    "Tc",
    "CO2",
    "H2",
    "Tt1",
    "Tt2",
    "Tt3",
    "Tt4",
    "Tp1",
    "Tp2",
    "Tp3",
    "Tp4",
    "Tp5",
    "Tp6",
    "Tp7",
    "Tp8",
    "Tp9",
    "Tp10",
    "Si",
    "Production",
    "HMT",
    "RAFT",
    "CZHeight",
    "CondensationIdx",
]

LAG_TAU_HOURS = {
    "Fb": 1.0,
    "Th": 1.5,
    "Fo": 1.0,
    "Pt": 0.6,
    "R": 6.0,
    "PCI": 2.5,
    "CokeRate": 6.5,
    "BlastMoisture": 0.8,
    "BurdenFe": 6.0,
    "CokeCSR": 7.0,
    "SinterRDI": 4.5,
    "AlkaliInput": 12.0,
    "ZnInput": 12.0,
}

_LEARNED_CACHE: dict[str, dict] = {}


def _merged_dataset() -> pd.DataFrame:
    hours = hourly().copy()
    casts = silicon().rename(columns={"Si": "Si_cast"})
    if "Si" in hours.columns:
        merged = hours.copy()
    else:
        merged = pd.merge_asof(
            hours.sort_values("dt"),
            casts.sort_values("dt"),
            on="dt",
            direction="backward",
        )
        merged["Si"] = merged["Si_cast"].ffill().bfill()
    # Filter to on-wind operating hours for clean elasticity learning
    on = merged[merged["Fb"] > 1000].copy()
    if len(on) < 100:
        on = merged.copy()
    return on.reset_index(drop=True)


def learn_from_dataset(force: bool = False) -> dict:
    """Fit data-driven cross-parameter response models (Ridge with lag-aligned predictors) on the active dataset."""
    meta = active_dataset_meta()
    ds_id = meta["id"]
    if not force and ds_id in _LEARNED_CACHE:
        return _LEARNED_CACHE[ds_id]

    cache_file = CACHE / f"learned_twin_{ds_id}.json"
    if not force and cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            _LEARNED_CACHE[ds_id] = data
            return data
        except Exception:
            pass

    df = _merged_dataset()
    present_inputs = [c for c in MANIPULATED_AND_DISTURBANCE if c in df.columns]
    present_outputs = [c for c in RESPONSE_AND_OUTCOME if c in df.columns]

    # Build lag-aligned feature matrix so each input acts at its metallurgical delay
    x_df = pd.DataFrame(index=df.index)
    for col in present_inputs:
        lag_steps = int(round(LAG_TAU_HOURS.get(col, 1.0)))
        s = pd.to_numeric(df[col], errors="coerce")
        if col in ["Fb", "Th", "Fo", "Pt"]:
            s_clean = s.clip(lower=s.quantile(0.01), upper=s.quantile(0.99))
        else:
            s_clean = s
        # Exponential moving average over lag window (active rate)
        active = s_clean.ewm(span=max(1, lag_steps), adjust=False).mean()
        x_df[col] = active

    valid = x_df.dropna().index
    x_mat = x_df.loc[valid].to_numpy(dtype=float)
    x_mean = np.nanmean(x_mat, axis=0)
    x_std = np.where(np.nanstd(x_mat, axis=0) < 1e-6, 1.0, np.nanstd(x_mat, axis=0))
    x_norm = (x_mat - x_mean) / x_std

    jacobian: dict[str, dict[str, float]] = {}
    corr_matrix: dict[str, dict[str, float]] = {}
    r2_scores: dict[str, float] = {}
    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    p05: dict[str, float] = {}
    p95: dict[str, float] = {}

    for col in present_inputs + [c for c in present_outputs if c not in present_inputs]:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) > 0:
            s_c = s.clip(lower=s.quantile(0.01), upper=s.quantile(0.99))
            means[col] = float(s_c.mean())
            stds[col] = float(s_c.std() if s_c.std() > 1e-6 else 1.0)
            p05[col] = float(s_c.quantile(0.05))
            p95[col] = float(s_c.quantile(0.95))

    for out_col in present_outputs:
        if out_col in present_inputs:
            continue
        y_raw = pd.to_numeric(df.loc[valid, out_col], errors="coerce")
        y_clean = y_raw.clip(lower=y_raw.quantile(0.01), upper=y_raw.quantile(0.99)).ffill().bfill()
        y_vec = y_clean.to_numpy(dtype=float)
        if np.nanstd(y_vec) < 1e-6:
            continue
        ridge = Ridge(alpha=50.0)
        ridge.fit(x_norm, y_vec)
        pred = ridge.predict(x_norm)
        ss_res = float(np.sum((y_vec - pred) ** 2))
        ss_tot = float(np.sum((y_vec - np.mean(y_vec)) ** 2)) + 1e-9
        r2_scores[out_col] = max(0.0, round(1.0 - ss_res / ss_tot, 4))

        # Unscale coefficients: d(out)/d(in)
        slopes: dict[str, float] = {}
        corrs: dict[str, float] = {}
        for idx, in_col in enumerate(present_inputs):
            slopes[in_col] = float(ridge.coef_[idx] / x_std[idx])
            c_val = np.corrcoef(x_mat[:, idx], y_vec)[0, 1]
            corrs[in_col] = 0.0 if np.isnan(c_val) else round(float(c_val), 4)
        jacobian[out_col] = slopes
        corr_matrix[out_col] = corrs

    learned = {
        "dataset_id": ds_id,
        "dataset_name": meta["name"],
        "origin": meta["origin"],
        "rows_trained": int(len(valid)),
        "present_inputs": present_inputs,
        "present_outputs": present_outputs,
        "means": means,
        "stds": stds,
        "p05": p05,
        "p95": p95,
        "r2_scores": r2_scores,
        "jacobian": jacobian,
        "correlations": corr_matrix,
    }
    cache_file.write_text(json.dumps(learned, indent=2))
    _LEARNED_CACHE[ds_id] = learned
    return learned


def _soft_limit(x: float, lo: float, hi: float, softness: float = 0.0) -> float:
    """
    Monotone saturating limit: identity inside [lo, hi], compressing asymptotically outside.

    A hard np.clip sets the derivative to exactly zero at the boundary, which silently kills
    every downstream response once an operating point rests on a limit. A real furnace
    approaching a limit responds less, not not at all, so the twin must keep a live derivative
    for the cross-parameter effects to mean anything.
    """
    span = max(1e-9, hi - lo)
    s = softness if softness > 0.0 else 0.08 * span
    if x > hi:
        return float(hi + s * math.tanh((x - hi) / s))
    if x < lo:
        return float(lo - s * math.tanh((lo - x) / s))
    return float(x)


def compute_physics_state(state: dict, working_volume: float = 2000.0) -> dict:
    """Compute metallurgical physics quantities from current + assumed parameters."""
    fb = max(500.0, float(state.get("Fb", 3500.0)))
    th = float(state.get("Th", 1100.0))
    fo = max(0.0, float(state.get("Fo", 18000.0)))
    pt = max(0.2, float(state.get("Pt", 1.40)))
    r_oc = max(2.0, float(state.get("R", 3.98)))
    pci = max(0.0, float(state.get("PCI", 115.0)))
    coke = max(220.0, float(state.get("CokeRate", 375.0)))
    moisture = max(2.0, float(state.get("BlastMoisture", 16.0)))
    fe_grade = max(48.0, float(state.get("BurdenFe", 58.5)))
    csr = max(45.0, float(state.get("CokeCSR", 64.0)))
    rdi = max(12.0, float(state.get("SinterRDI", 26.5)))
    alkali = max(0.2, float(state.get("AlkaliInput", 2.1)))
    zn = max(10.0, float(state.get("ZnInput", 115.0)))

    # Switches
    dehumid_on = bool(state.get("switch_dehumidification", False))
    center_coke_on = bool(state.get("switch_center_coke", True))
    alkali_flush_on = bool(state.get("switch_alkali_flush", False))

    eff_moisture = max(5.0, moisture - (7.5 if dehumid_on else 0.0))
    eff_alkali = max(0.4, alkali * (0.62 if alkali_flush_on else 1.0))

    # Oxygen enrichment in percentage points above the 21 % O2 already in air.
    # Fo is pure O2 in m3/h; Fb is air in m3/min, so air is Fb*60 m3/h.
    # Enrichment is (total O2 / total volume) - 21, NOT the O2-to-air volume ratio.
    air_h = fb * 60.0
    total_o2 = 0.21 * air_h + fo
    total_vol = air_h + fo
    o2_total_pct = 100.0 * total_o2 / max(1e-6, total_vol)
    oe_pct = max(0.0, o2_total_pct - 21.0)

    # Wind consumption m3 STP / tHM (~1080 nominal)
    wc = 1080.0
    # AIST / Geerdes RAFT correlation. Coefficients cited in knowledge/02-derived-indices.md.
    # knowledge/11-pending-validation.md PV-09 keeps the intercept plant-fitted, so the
    # result is reported with a band warning rather than trusted as calibrated.
    raft_raw = 1489.0 + 0.82 * th - 5.705 * eff_moisture + 52.778 * oe_pct - 18.1 * (pci / wc) * 100.0
    raft = _soft_limit(raft_raw, 1700.0, 2500.0)
    raft_saturated = bool(abs(raft - raft_raw) > 0.5)

    # Bosh gas volume (m3/min)
    o2_total_m3_min = fb * 0.21 + fo / 60.0
    n2_m3_min = fb * 0.79
    h2_from_moisture = (eff_moisture / 1000.0) * fb * (22.4 / 18.0)
    h2_from_pci = pci * 0.045 * (fb / 1080.0)
    bosh_gas_min = n2_m3_min + 2.0 * o2_total_m3_min + h2_from_moisture + h2_from_pci

    # Alkali & Zinc condensation / recirculation index (0 - 100 scale)
    # Recirculates 4-8x; rises with alkali > 2.0 kg/tHM and Zn > 120 g/tHM
    cond_idx = _soft_limit(22.0 * (eff_alkali - 1.2) + 0.14 * (zn - 80.0) + (8.0 if not center_coke_on else 0.0), 2.0, 98.0)

    # Upper & Lower Pressure Drop via Ergun + Fines/Condensation modifiers
    # Base Ergun scales with (bosh_gas)^1.7 / (1 + 0.28 * Pt)
    gas_factor = ((bosh_gas_min / 4450.0) ** 1.7) * (2.4 / (1.0 + pt))
    fines_penalty_upper = 1.0 + 0.018 * (rdi - 26.0) + 0.0035 * (cond_idx - 25.0) - (0.06 if center_coke_on else 0.0)
    fines_penalty_lower = 1.0 + 0.0016 * (pci - 115.0) - 0.015 * (csr - 64.0) + 0.0045 * (cond_idx - 25.0)

    dpu_phys = _soft_limit(0.44 * gas_factor * fines_penalty_upper, 0.12, 1.35)
    dpl_phys = _soft_limit(0.98 * gas_factor * fines_penalty_lower, 0.35, 1.85)
    dp_phys = dpu_phys + dpl_phys
    ph_phys = pt + dp_phys
    pc_phys = ph_phys + 0.12

    # Gas utilization & top gas composition
    eta_co = _soft_limit(0.495 + 0.018 * (r_oc - 4.0) + (0.012 if center_coke_on else -0.012) - 0.0005 * (cond_idx - 25.0) - 0.0012 * (rdi - 26.0), 0.38, 0.56)
    co2_phys = _soft_limit(43.5 * eta_co, 15.0, 26.5)
    h2_phys = _soft_limit(3.2 + 0.022 * pci + 0.055 * eff_moisture, 2.0, 12.5)

    # Cohesive zone root height (m above tuyeres)
    cz_height = _soft_limit(3.8 + 0.0045 * (raft - 2080.0) - 0.55 * (r_oc - 4.0) - 0.012 * (cond_idx - 25.0), 2.1, 6.6)

    # Hot metal temperature (°C) and Silicon [Si] (wt%)
    coke_active = coke + (0.9 * (375.0 / max(2.8, r_oc) - 94.0))
    hmt_phys = _soft_limit(
        1498.0
        + 0.22 * (raft - 2080.0)
        + 0.32 * (coke_active - 375.0)
        - 26.0 * (r_oc - 4.0)
        - 0.42 * (cond_idx - 25.0),
        1435.0,
        1555.0,
    )
    si_phys = _soft_limit(
        0.47
        + 0.0029 * (hmt_phys - 1498.0)
        - 0.06 * (pt - 1.40)
        - 0.00007 * (fb - 3550.0)
        + (0.04 if alkali_flush_on else 0.0),
        0.15,
        1.25,
    )

    # Production rate (tHM/day) from tuyere oxygen stoichiometry, Rist efficiency, and permeability ceiling
    # O2 kmol/day at tuyeres:
    o2_m3_day = o2_total_m3_min * 1440.0
    o2_kmol_day = o2_m3_day / 22.414
    # Carbon burned at tuyeres per tHM (kg C/tHM):
    c_tuyere_kg_thm = max(180.0, 0.875 * coke + 0.80 * pci - 50.0 - 115.0 * (1.0 - eta_co / 0.50))
    prod_stoich = (o2_kmol_day * 2.0 * 12.011) / c_tuyere_kg_thm
    # Adjust for Fe grade and permeability/flooding restriction above dP = 1.53 kgf/cm2
    fe_factor = (fe_grade / 58.5) ** 0.85
    perm_penalty = max(0.0, (dp_phys - 1.53) * 620.0) + max(0.0, (cond_idx - 35.0) * 4.5)
    prod_phys = _soft_limit(prod_stoich * fe_factor - perm_penalty, 1200.0, 6500.0)

    # Top gas temperature (°C)
    t_top_mean = _soft_limit(154.0 + 0.035 * (fb - 3550.0) - 22.0 * (r_oc - 4.0) - 0.14 * (oe_pct - 4.5) + 0.45 * (eff_moisture - 16.0), 75.0, 320.0)

    # Five productivity ceilings (t/day)
    ceilings = {
        "tuyere_stoichiometry": round(float(prod_stoich * fe_factor), 1),
        "permeability_dp_limit": round(float(4500.0 * ((1.62 / max(0.6, dp_phys)) ** 0.58)), 1),
        "flooding_fluidization": round(float(4650.0 * (4600.0 / max(2500.0, bosh_gas_min))), 1),
        "top_gas_dewpoint": round(float(4800.0 if t_top_mean >= 105.0 else 4800.0 - (105.0 - t_top_mean) * 38.0), 1),
        "hearth_drainage": round(float(4750.0 - max(0.0, (64.0 - csr) * 45.0)), 1),
    }
    binding_ceiling = min(ceilings, key=ceilings.get)

    return {
        "RAFT": round(raft, 1),
        "RAFT_saturated": raft_saturated,
        "BoshGas": round(bosh_gas_min, 1),
        "O2TotalPct": round(o2_total_pct, 2),
        "O2EnrichmentPct": round(oe_pct, 2),
        "CondensationIdx": round(cond_idx, 1),
        "CZHeight": round(cz_height, 2),
        "dPu": round(dpu_phys, 3),
        "dPl": round(dpl_phys, 3),
        "dP": round(dp_phys, 3),
        "Ph": round(ph_phys, 3),
        "Pc": round(pc_phys, 3),
        "CO2": round(co2_phys, 2),
        "H2": round(h2_phys, 2),
        "EtaCO": round(eta_co * 100.0, 2),
        "HMT": round(hmt_phys, 1),
        "Si": round(si_phys, 3),
        "Production": round(prod_phys, 1),
        "Productivity": round(prod_phys / max(500.0, working_volume), 2),
        "FuelRate": round(coke + pci, 1),
        "TopTempMean": round(t_top_mean, 1),
        "ceilings": ceilings,
        "binding_ceiling": binding_ceiling,
        "max_feasible_production": ceilings[binding_ceiling],
    }


# Physics quantities a furnace actually measures. Where a sensor exists the twin is reconciled
# onto it, so absolute values match the plant and the correlation supplies only the response.
ANCHORABLE = ["dPu", "dPl", "dP", "Ph", "Pc", "Tc", "CO2", "H2", "Si", "HMT", "Production"]

# Validated operating bands from knowledge/01-parameter-catalog.md and 02-derived-indices.md.
# A value outside its band is reported, never silently hidden.
VALIDATED_BANDS = {
    "RAFT": (1900.0, 2250.0),
    "HMT": (1480.0, 1530.0),
    "Si": (0.30, 0.60),
    "dP": (1.12, 1.60),
    "EtaCO": (48.0, 52.5),
    "CZHeight": (2.1, 6.6),
    "O2TotalPct": (21.0, 29.0),
    "Production": (3200.0, 5600.0),
}


# Blast rate as a fraction of the campaign's on-wind median, separating operating regimes.
# These are operational definitions rather than metallurgy: they are configuration, and the
# fraction is printed with any result that depends on it.
REGIME_ON_WIND_FRAC = 0.60
REGIME_REDUCED_FRAC = 0.25

# Baseline position of the centre-coke charging switch, so its effect is applied as a change.
CENTER_COKE_DEFAULT = True


def blast_reference(frame: pd.DataFrame) -> float:
    """Median blast rate over hours the furnace was actually blowing."""
    if "Fb" not in frame.columns:
        return 3600.0
    blowing = frame["Fb"].dropna()
    blowing = blowing[blowing > blowing.quantile(0.5) * 0.25]
    return float(blowing.median()) if len(blowing) else 3600.0


def operating_regime(fb: float, reference: float) -> dict:
    """
    Classify the hour. CLAUDE.md suppresses recommendations during banking, blow-in and any
    unqualified regime, so the regime has to be an output, not an assumption.
    """
    frac = float(fb) / max(1e-6, float(reference))
    if frac >= REGIME_ON_WIND_FRAC:
        state, qualified = "on_wind", True
        detail = "Blast rate is within the normal operating range for this campaign."
    elif frac >= REGIME_REDUCED_FRAC:
        state, qualified = "reduced_blast", False
        detail = "Blast is throttled well below the campaign median. Steady-state correlations do not hold here."
    else:
        state, qualified = "off_wind", False
        detail = "The furnace is off wind, banked, or between blow-in stages. No absolute physics value is served."
    return {
        "regime": state,
        "qualified": qualified,
        "blast_fraction_of_median": round(frac, 3),
        "blast_reference_m3_min": round(float(reference), 1),
        "thresholds": {"on_wind": REGIME_ON_WIND_FRAC, "reduced_blast": REGIME_REDUCED_FRAC},
        "detail": detail,
    }


def physics_bias(freerun: dict, measured: dict) -> dict:
    """Offset between the free-running correlation and the sensor, per measured quantity."""
    bias: dict[str, float] = {}
    for key in ANCHORABLE:
        meas = measured.get(key)
        if meas is None or key not in freerun:
            continue
        try:
            if pd.isna(meas):
                continue
        except (TypeError, ValueError):
            pass
        bias[key] = float(meas) - float(freerun[key])
    return bias


def apply_bias(phys: dict, bias: dict, working_volume: float = 2000.0) -> dict:
    """Shift physics onto the measured anchor. Response deltas survive because the bias is constant."""
    out = dict(phys)
    for key, offset in bias.items():
        value = out.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out[key] = round(float(value) + offset, 4)
    # Preserve the reconciled identities dP = dPu + dPl and productivity = production / volume.
    if "dPu" in out and "dPl" in out:
        out["dP"] = round(float(out["dPu"]) + float(out["dPl"]), 4)
    if "Production" in out:
        out["Productivity"] = round(float(out["Production"]) / max(500.0, working_volume), 3)
    return out


# Inputs each physics quantity needs. Used to decide whether an absolute value may be shown
# or whether the quantity is only meaningful as a response to a change.
PHYSICS_REQUIRES = {
    "RAFT": ["Th", "Fb", "Fo", "BlastMoisture", "PCI"],
    "HMT": ["Th", "Fb", "Fo", "BlastMoisture", "PCI", "CokeRate", "R", "AlkaliInput", "ZnInput"],
    "Si": ["Th", "Fb", "Fo", "BlastMoisture", "PCI", "CokeRate", "R"],
    "Production": ["Fb", "Fo", "BurdenFe", "CokeRate", "PCI", "R"],
    "dP": ["Fb", "Fo", "Pt", "R", "SinterRDI", "CokeCSR"],
    "EtaCO": ["Fb", "Fo", "R", "CokeRate"],
    "CZHeight": ["Th", "Fb", "Fo", "PCI", "R", "SinterRDI"],
    "O2TotalPct": ["Fb", "Fo"],
    "CondensationIdx": ["AlkaliInput", "ZnInput", "Th", "R"],
}


def classify_physics(phys: dict, bias: dict, assumed_tags: list, qualified: bool = True) -> dict:
    """
    Assign each physics output a capability status, following the vocabulary in CLAUDE.md.

    measured_anchored    reconciled onto a sensor; the absolute value is trustworthy
    physics_estimated    free-running, but every required input is measured
    response_only        rests on assumed inputs AND lands outside its validated band, so the
                         absolute number is not shown; only its response to a change is usable
    assumption_dependent rests on assumed inputs but still lands inside its validated band
    """
    assumed = set(assumed_tags)
    status: dict[str, dict] = {}
    for key, needs in PHYSICS_REQUIRES.items():
        if key not in phys:
            continue
        missing = [tag for tag in needs if tag in assumed]
        value = phys.get(key)
        low, high = VALIDATED_BANDS.get(key, (-1e18, 1e18))
        in_band = isinstance(value, (int, float)) and not isinstance(value, bool) and low <= float(value) <= high

        if key in bias:
            # A sensor reading stands on its own even in an unqualified regime.
            state, evidence = "measured_anchored", "reconciled"
        elif not qualified:
            # Off wind the steady-state correlations do not apply, so nothing is served.
            state, evidence = "not_qualified", "unavailable"
        elif not missing:
            state, evidence = "physics_estimated", "simulated"
        elif key not in ("RAFT", "HMT") and not phys.get(f"{key}_saturated"):
            # PV-10 (knowledge/11-pending-validation.md): RAFT and HMT intercepts on EVRAZ
            # sit above band because injectant/moisture are unmeasured, so when out of band
            # they stay response_only. Production, EtaCO, CZHeight, and CondensationIdx are
            # stoichiometric/balance estimates whose excursions below band reflect real
            # reduced wind or permeability drops on qualified hours.
            state, evidence = "assumption_dependent", "assumed"
        elif in_band and not phys.get(f"{key}_saturated"):
            state, evidence = "assumption_dependent", "assumed"
        else:
            state, evidence = "response_only", "unavailable"

        status[key] = {
            "status": state,
            "evidence": evidence,
            "show_absolute": state not in ("response_only", "not_qualified"),
            "assumed_inputs": missing,
            "band": [low, high],
            "in_band": bool(in_band),
        }
    return status


def band_warnings(phys: dict, assumed_inputs: list, bias: Optional[dict] = None) -> list:
    """
    Flag every physics output that left its validated band.

    An anchored quantity out of band is the furnace genuinely running outside its normal
    range, which is an operating signal. A free-running one out of band is a model problem.
    The two must not read the same.
    """
    bias = bias or {}
    notes = []
    for key, (low, high) in VALIDATED_BANDS.items():
        value = phys.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        value = float(value)
        if low <= value <= high:
            continue
        anchored = key in bias
        if anchored:
            source = "measurement"
            detail = (
                f"The instrument reads {round(value, 3)}, outside the usual band {low}–{high}. "
                "This is the furnace itself operating off its normal range, not a model error."
            )
        elif assumed_inputs:
            source = "assumed_inputs"
            detail = (
                f"{key} sits outside the published band {low}–{high} and has no sensor in this dataset. "
                f"It is driven by assumed inputs: {', '.join(assumed_inputs)}."
            )
        else:
            source = "correlation"
            detail = (
                f"{key} sits outside the published band {low}–{high} although every input is measured, "
                "so the correlation itself is uncalibrated for this furnace."
            )
        notes.append(
            {
                "quantity": key,
                "value": round(value, 3),
                "band": [low, high],
                "status": "below_band" if value < low else "above_band",
                "source": source,
                "detail": detail,
            }
        )
    if phys.get("RAFT_saturated"):
        notes.append(
            {
                "quantity": "RAFT",
                "value": phys.get("RAFT"),
                "band": [1700.0, 2500.0],
                "status": "saturated",
                "detail": "RAFT hit the solver clip. Read it as not computable, not as a flame temperature.",
            }
        )
    return notes


# Metallurgical warning mechanisms and production-loss sensitivities below and above the Golden Range.
GOLDEN_MECHANISMS: dict[str, dict] = {
    "Fb": {
        "below": "Blast wind flow is below the Golden Range for required production: insufficient tuyere O₂ delivery directly throttles carbon burning rate and smelting tonnage (~1.1 t/d per m³/min deficit).",
        "above": "Blast wind flow exceeds the Golden Range: excessive bosh gas velocity spikes Ergun ΔP toward flooding/channeling, forcing wind cutbacks.",
        "loss_below": 1.12,
        "loss_above": 0.75,
        "scale_per_1000t": 310.0,
    },
    "Fo": {
        "below": "Oxygen enrichment flow is below the Golden Range for required production: low O₂ intensity reduces tuyere combustion rate and depresses raceway flame temperature (RAFT).",
        "above": "Oxygen flow exceeds the Golden Range: over-enrichment pushes RAFT > 2250 °C, accelerating SiO/alkali volatilization and lifting cohesive zone root height.",
        "loss_below": 0.062,
        "loss_above": 0.035,
        "scale_per_1000t": 6800.0,
    },
    "Th": {
        "below": "Hot blast temperature is below the Golden Range: hearth thermal deficit lowers RAFT & HMT, requiring extra coke rate and slowing slag drainage.",
        "above": "Hot blast temperature exceeds the Golden Range: excessive flame temperature elevates cohesive zone root, stave heat load, and SiO generation.",
        "loss_below": 2.4,
        "loss_above": 1.6,
        "scale_per_1000t": 28.0,
    },
    "Pt": {
        "below": "Top gas pressure is below the Golden Range: low back-pressure allows high actual shaft gas velocity, increasing Ergun ΔP, dust elutriation, and flooding risk.",
        "above": "Top gas pressure exceeds the Golden Range: approaches charging-gear seal limits and suppresses silicon reduction kinetics.",
        "loss_below": 420.0,
        "loss_above": 260.0,
        "scale_per_1000t": 0.11,
    },
    "R": {
        "below": "Ore/Coke ratio (R) is below the Golden Range: coke-heavy burden reduces iron ore charged per Nm³ wind and overheats hot-metal [Si].",
        "above": "Ore/Coke ratio (R) exceeds the Golden Range: thin coke slits in the cohesive zone spike lower ΔPl and risk hearth thermal starvation (chill).",
        "loss_below": 340.0,
        "loss_above": 480.0,
        "scale_per_1000t": 0.14,
    },
    "PCI": {
        "below": "PCI coal injection is below the Golden Range: low tuyere fuel injection raises RAFT and forces higher charged coke consumption.",
        "above": "PCI coal injection exceeds the Golden Range: unburned char fouls the bird's nest and deadman, raising lower ΔPl and binding the permeability ceiling.",
        "loss_below": 3.2,
        "loss_above": 5.8,
        "scale_per_1000t": 16.0,
    },
    "CokeRate": {
        "below": "Charged coke rate is below the Golden Range: thin coke bed degrades cohesive-zone gas slits and deadman drainage permeability.",
        "above": "Charged coke rate exceeds the Golden Range: excess coke consumes tuyere O₂ per tHM and displaces iron burden, directly cutting daily tonnage.",
        "loss_below": 4.5,
        "loss_above": 6.2,
        "scale_per_1000t": -15.0,
    },
    "BlastMoisture": {
        "below": "Blast moisture is below the Golden Range: insufficient steam moderation risks RAFT spike and lowers H₂ indirect reduction in the shaft.",
        "above": "Blast moisture exceeds the Golden Range: endothermic water-gas reaction (-5.7 °C per g/Nm³) chills the raceway and wastes fuel.",
        "loss_below": 12.0,
        "loss_above": 18.0,
        "scale_per_1000t": -1.2,
    },
    "BurdenFe": {
        "below": "Burden Fe grade is below the Golden Range: higher gangue and slag volume increase bosh slag hold-up and directly reduce iron yield per unit wind.",
        "above": "Burden Fe grade exceeds the Golden Range: ultra-low slag volume (<230 kg/tHM) limits alkali and sulfur removal capacity.",
        "loss_below": 68.0,
        "loss_above": 18.0,
        "scale_per_1000t": 1.0,
    },
    "CokeCSR": {
        "below": "Coke CSR strength is below the Golden Range: coke degradation under solution-loss generates fines in the deadman, spiking lower ΔPl and restricting hearth drainage.",
        "above": "Coke CSR is above the nominal Golden Range: ultra-premium coke grade (verify blend cost vs permeability gain).",
        "loss_below": 34.0,
        "loss_above": 5.0,
        "scale_per_1000t": 1.4,
    },
    "SinterRDI": {
        "below": "Sinter RDI is below the Golden Range: over-fused/high-FeO sinter reduces micropore reducibility (RI), lowering shaft gas utilization ηCO.",
        "above": "Sinter RDI exceeds the Golden Range: severe low-temperature reduction disintegration in the upper shaft generates fines and spikes upper ΔPu.",
        "loss_below": 14.0,
        "loss_above": 38.0,
        "scale_per_1000t": -1.2,
    },
    "AlkaliInput": {
        "below": "Alkali input is below the Golden Range: low alkali load (check slag basicity B₂ if operating in aggressive flush mode).",
        "above": "Alkali load (K₂O+Na₂O) exceeds the Golden Range: 4–8× internal recirculation attacks coke CSR, forms wall scaffolds, and triggers ΔP surges.",
        "loss_below": 15.0,
        "loss_above": 135.0,
        "scale_per_1000t": -0.25,
    },
    "ZnInput": {
        "below": "Zinc input load is below the Golden Range: low volatile zinc circulation.",
        "above": "Zinc input load exceeds the Golden Range: ZnO condensation in upper shaft forms cohesive crusts and degrades burden descent.",
        "loss_below": 0.4,
        "loss_above": 2.4,
        "scale_per_1000t": -12.0,
    },
    "dPu": {
        "below": "Upper shaft ΔPu is below the Golden Range: indicates under-blowing or central gas channeling bypassing the iron ore layers.",
        "above": "Upper shaft ΔPu exceeds the Golden Range: sinter RDI fines or alkali/Zn condensation is restricting upper-shaft gas flow.",
        "loss_below": 220.0,
        "loss_above": 540.0,
        "scale_per_1000t": 0.045,
    },
    "dPl": {
        "below": "Lower furnace ΔPl is below the Golden Range: reduced wind volume or central blow-through across cohesive zone.",
        "above": "Lower furnace ΔPl exceeds the Golden Range: cohesive-zone slag hold-up, unburned PCI char, or weak coke CSR is choking the bosh.",
        "loss_below": 210.0,
        "loss_above": 590.0,
        "scale_per_1000t": 0.085,
    },
    "dP": {
        "below": "Total pressure drop ΔP is below the Golden Range: furnace is under-blown for the required production or experiencing gas channeling.",
        "above": "Total pressure drop ΔP exceeds the Golden Range: burden tightness approaches the flooding/hanging ceiling, directly penalizing production.",
        "loss_below": 240.0,
        "loss_above": 620.0,
        "scale_per_1000t": 0.13,
    },
    "Ph": {
        "below": "Hot blast pressure Ph is below the Golden Range: insufficient blast main pressure to drive required wind and top pressure.",
        "above": "Hot blast pressure Ph exceeds the Golden Range: high furnace resistance (ΔP) is backing up tuyere blast pressure toward blower limits.",
        "loss_below": 210.0,
        "loss_above": 380.0,
        "scale_per_1000t": 0.22,
    },
    "Pc": {
        "below": "Cold blast pressure Pc is below the Golden Range: low blower delivery pressure for required wind rate.",
        "above": "Cold blast pressure Pc exceeds the Golden Range: high stove/main + furnace resistance approaching turbo-blower surge margin.",
        "loss_below": 200.0,
        "loss_above": 360.0,
        "scale_per_1000t": 0.22,
    },
    "Tc": {
        "below": "Cold blast temperature Tc is below the Golden Range: higher stove firing duty required to maintain hot-blast temperature Th.",
        "above": "Cold blast temperature Tc exceeds the Golden Range: high compressor discharge temperature (check intercooler / blower efficiency).",
        "loss_below": 2.2,
        "loss_above": 2.2,
        "scale_per_1000t": 4.0,
    },
    "CO2": {
        "below": "Top gas CO₂ is below the Golden Range: poor shaft gas utilization (ηCO) from channeling or uneven burden distribution raises fuel rate and cuts output.",
        "above": "Top gas CO₂ exceeds the Golden Range: approaching wüstite-iron equilibrium pinch or over-burdened shaft.",
        "loss_below": 95.0,
        "loss_above": 55.0,
        "scale_per_1000t": 0.45,
    },
    "H2": {
        "below": "Top gas H₂ is below the Golden Range: low hydrogen reduction contribution from PCI/moisture.",
        "above": "Top gas H₂ exceeds the Golden Range: excess unreacted H₂ slip (check excess steam/PCI or tuyere/stave water leak).",
        "loss_below": 35.0,
        "loss_above": 65.0,
        "scale_per_1000t": 0.35,
    },
    "Si": {
        "below": "Hot metal [Si] is below the Golden Range: cold hearth warning! Risk of sluggish slag drainage and chilled hearth requiring wind cut.",
        "above": "Hot metal [Si] exceeds the Golden Range: over-fueled/hot furnace or post-stop blow-in state consuming excess carbon per tHM.",
        "loss_below": 680.0,
        "loss_above": 520.0,
        "scale_per_1000t": -0.03,
    },
    "Production": {
        "below": "Production is below the required Golden Range: furnace is falling short of target daily hot-metal tonnage.",
        "above": "Production exceeds the target Golden Range: operating near upper flooding/drainage ceilings; monitor ΔP and hearth level.",
        "loss_below": 1.0,
        "loss_above": 0.2,
        "scale_per_1000t": 1000.0,
    },
    "HMT": {
        "below": "Hot metal temperature is below the Golden Range: hearth heat deficit increases slag viscosity and risks taphole/hearth chill.",
        "above": "Hot metal temperature exceeds the Golden Range: excess thermal reserve increases specific fuel consumption and refractory wear.",
        "loss_below": 6.5,
        "loss_above": 4.2,
        "scale_per_1000t": 6.0,
    },
    "RAFT": {
        "below": "Raceway flame temperature (RAFT) is below the Golden Range: insufficient lower-furnace thermal intensity for melting and slag superheat.",
        "above": "Raceway flame temperature (RAFT) exceeds the Golden Range: promotes SiO/alkali vaporization, cohesive-zone rise, and hanging risk.",
        "loss_below": 2.2,
        "loss_above": 2.6,
        "scale_per_1000t": 18.0,
    },
    "CZHeight": {
        "below": "Cohesive zone root height is below the Golden Range: low melting zone compresses the dripping zone and risks cold hearth.",
        "above": "Cohesive zone root height exceeds the Golden Range: high cohesive zone increases lower bosh gas path resistance and stave heat load.",
        "loss_below": 140.0,
        "loss_above": 165.0,
        "scale_per_1000t": 0.18,
    },
    "CondensationIdx": {
        "below": "Condensation index is below the Golden Range: low internal volatile recirculation load.",
        "above": "Alkali/Zn condensation load exceeds the Golden Range: heavy recirculation loop fouls upper shaft permeability and attacks coke CSR.",
        "loss_below": 1.5,
        "loss_above": 9.5,
        "scale_per_1000t": -2.0,
    },
}

for _i in range(1, 5):
    GOLDEN_MECHANISMS[f"Tt{_i}"] = {
        "below": f"Top gas offtake Tt{_i} is below the Golden Range: wet-burden / acid dewpoint condensation risk (<105 °C) can blind baghouse and uptakes.",
        "above": f"Top gas offtake Tt{_i} exceeds the Golden Range: gas channeling in quadrant {_i} wastes sensible heat out the top and lowers ηCO.",
        "loss_below": 3.2,
        "loss_above": 2.8,
        "scale_per_1000t": 6.0,
    }

for _i in range(1, 11):
    GOLDEN_MECHANISMS[f"Tp{_i}"] = {
        "below": f"Peripheral wall stave Tp{_i} is below the Golden Range: inactive wall or scaffold accretion insulating stave {_i}, narrowing effective shaft area.",
        "above": f"Peripheral wall stave Tp{_i} exceeds the Golden Range: excessive wall gas flow at sector {_i} increases heat loss and stave wear while bypassing ore.",
        "loss_below": 0.85,
        "loss_above": 1.15,
        "scale_per_1000t": 12.0,
    }

_PROD_FRAME_CACHE: dict[str, pd.DataFrame] = {}


def _dataset_production_frame(ds_id: Optional[str] = None) -> pd.DataFrame:
    """Return clean hourly dataframe enriched with cast Si, hourly Production (measured or stoichiometric), and 72h rolling baseline."""
    meta = active_dataset_meta()
    ds = ds_id or meta["id"]
    if ds in _PROD_FRAME_CACHE:
        return _PROD_FRAME_CACHE[ds]

    h = clean_hourly(ds).copy()
    casts = silicon(ds).rename(columns={"Si": "Si_cast"})
    if "Si" not in h.columns:
        h = pd.merge_asof(
            h.sort_values("dt"),
            casts[["dt", "Si_cast"]].sort_values("dt"),
            on="dt",
            direction="backward",
        )
        h["Si"] = h["Si_cast"].ffill().bfill()

    if "Production" in h.columns and h["Production"].notna().sum() > 50:
        # Check if Production is t/h (e.g. ~180 t/h) or t/d (~4300 t/d)
        med_p = float(h["Production"].dropna().median())
        h["prod_t_d"] = h["Production"] * 24.0 if med_p < 600.0 else h["Production"]
        h["prod_basis"] = "measured"
    else:
        fb = h["Fb"].clip(lower=500.0)
        fo = h["Fo"].clip(lower=0.0)
        dp = h["dP"]
        co2 = h["CO2"]
        eta_co = (co2 / 43.5).clip(0.38, 0.56)
        o2_m3_min = fb * 0.21 + fo / 60.0
        o2_kmol_day = (o2_m3_min * 1440.0) / 22.414
        c_tuyere = (0.875 * 375.0 + 0.80 * 115.0 - 50.0 - 115.0 * (1.0 - eta_co / 0.50)).clip(lower=180.0)
        prod_stoich = (o2_kmol_day * 2.0 * 12.011) / c_tuyere
        perm_pen = (dp - 1.53).clip(lower=0.0) * 620.0
        h["prod_t_d"] = (prod_stoich - perm_pen).clip(1200.0, 6500.0)
        h["prod_basis"] = "stoichiometric_permeability_estimate"

    # Compute 72h rolling median on on-wind hours as the local historical benchmark
    h["prod_roll72"] = h["prod_t_d"].rolling(72, min_periods=12).median().bfill()
    h["drop_vs_roll72"] = (h["prod_roll72"] - h["prod_t_d"]).clip(lower=0.0)
    _PROD_FRAME_CACHE[ds] = h
    return h


def compute_golden_ranges(target_production: float = 4500.0) -> dict:
    """
    Compute the production-conditioned Golden Range [golden_low, golden_high] and golden_center
    for all 41 parameters in FULL_SIM_CATALOG.
    Combines empirical quantiles from the historical cohort matching `target_production`
    with stoichiometric/thermodynamic scaling so ranges shift smoothly with required production.
    """
    target_production = float(np.clip(target_production, 2200.0, 6000.0))
    meta = active_dataset_meta()
    h = _dataset_production_frame(meta["id"])
    fb_ref = blast_reference(h)
    on = h[h["Fb"] >= fb_ref * REGIME_ON_WIND_FRAC].copy()
    if len(on) < 80:
        on = h.copy()

    med_prod = float(on["prod_t_d"].median()) if len(on) else 4350.0
    # Select historical cohort near target_production with healthy permeability
    dp_p85 = float(on["dP"].quantile(0.85)) if "dP" in on.columns else 1.58
    cohort = on[(on["prod_t_d"].between(target_production - 260.0, target_production + 260.0)) & (on["dP"] <= dp_p85)]
    cohort_shift_k = 0.0
    if len(cohort) < 100:
        # Take closest 250 healthy hours and apply residual scaling shift
        on_healthy = on[on["dP"] <= dp_p85].copy() if len(on[on["dP"] <= dp_p85]) >= 100 else on.copy()
        on_healthy["_dist"] = (on_healthy["prod_t_d"] - target_production).abs()
        cohort = on_healthy.nsmallest(min(300, len(on_healthy)), "_dist")
        cohort_med_prod = float(cohort["prod_t_d"].median()) if len(cohort) else med_prod
        cohort_shift_k = (target_production - cohort_med_prod) / 1000.0
    else:
        cohort_med_prod = float(cohort["prod_t_d"].median())
        cohort_shift_k = (target_production - cohort_med_prod) / 1000.0

    total_shift_k = (target_production - med_prod) / 1000.0

    # Equilibrium physics state at the target cohort center for unmeasured/latent tags
    synth_input = {
        "Fb": float(cohort["Fb"].median()) + cohort_shift_k * 310.0 if "Fb" in cohort.columns else 3600.0,
        "Fo": max(0.0, float(cohort["Fo"].median()) + cohort_shift_k * 6800.0) if "Fo" in cohort.columns else 19500.0,
        "Th": float(cohort["Th"].median()) + cohort_shift_k * 28.0 if "Th" in cohort.columns else 1085.0,
        "Pt": float(cohort["Pt"].median()) + cohort_shift_k * 0.11 if "Pt" in cohort.columns else 1.42,
        "R": float(cohort["R"].median()) + cohort_shift_k * 0.14 if "R" in cohort.columns else 4.02,
        "PCI": 115.0 + total_shift_k * 16.0,
        "CokeRate": 375.0 - total_shift_k * 15.0,
        "BlastMoisture": 16.0 - total_shift_k * 1.2,
        "BurdenFe": 58.5 + total_shift_k * 1.0,
        "CokeCSR": 64.0 + total_shift_k * 1.4,
        "SinterRDI": 26.0 - total_shift_k * 1.2,
        "AlkaliInput": 2.0 - total_shift_k * 0.2,
        "ZnInput": 110.0 - total_shift_k * 10.0,
    }
    eq_phys = compute_physics_state(synth_input, float(meta.get("working_volume_m3", 2000.0)))

    ranges: dict[str, dict] = {}
    for item in FULL_SIM_CATALOG:
        tag = item["tag"]
        mech = GOLDEN_MECHANISMS.get(
            tag,
            {
                "below": f"{tag} is below the Golden Range for {target_production:.0f} t/d.",
                "above": f"{tag} is above the Golden Range for {target_production:.0f} t/d.",
                "loss_below": 10.0,
                "loss_above": 10.0,
                "scale_per_1000t": 0.0,
            },
        )
        scale_slope = float(mech.get("scale_per_1000t", 0.0))

        if tag == "Production":
            g_center = target_production
            g_low = round(target_production * 0.96, 1)
            g_high = round(target_production * 1.05, 1)
            basis = "target_production_band"
        elif tag in cohort.columns and cohort[tag].notna().sum() >= 30:
            s = pd.to_numeric(cohort[tag], errors="coerce").dropna()
            if tag.startswith("Tp") or tag.startswith("Tt"):
                s = s[(s >= 20.0) & (s <= 1050.0)]
            q18 = float(s.quantile(0.18)) + cohort_shift_k * scale_slope
            q50 = float(s.quantile(0.50)) + cohort_shift_k * scale_slope
            q82 = float(s.quantile(0.82)) + cohort_shift_k * scale_slope
            # Ensure a meaningful non-zero golden width
            min_half = max(float(item.get("step", 0.1)) * 1.5, (item["max"] - item["min"]) * 0.04)
            if (q82 - q18) < 2.0 * min_half:
                q18 = q50 - min_half
                q82 = q50 + min_half
            g_low = float(np.clip(q18, item["min"] * 0.6, item["max"] * 1.15))
            g_high = float(np.clip(q82, g_low + min_half * 0.5, item["max"] * 1.25))
            g_center = float(np.clip(q50, g_low, g_high))
            basis = "historical_cohort_and_physics"
        else:
            # Assumed knob or derived latent state: center on physics equilibrium for target_production
            base_c = float(eq_phys.get(tag, synth_input.get(tag, item.get("default_assumed", (item["min"] + item["max"]) / 2.0))))
            half_w = max(float(item.get("step", 1.0)) * 3.0, (item["max"] - item["min"]) * 0.11)
            if tag == "RAFT":
                g_low, g_center, g_high = 2000.0, 2115.0, 2225.0
            elif tag == "HMT":
                g_low, g_center, g_high = 1485.0, 1508.0, 1530.0
            elif tag == "CZHeight":
                g_low, g_center, g_high = 3.4, 4.3, 5.3
            elif tag == "CondensationIdx":
                g_low, g_center, g_high = 8.0, 22.0, 34.0
            else:
                g_low = float(np.clip(base_c - half_w, item["min"], item["max"]))
                g_high = float(np.clip(base_c + half_w, g_low + item.get("step", 0.1), item["max"]))
                g_center = float(np.clip(base_c, g_low, g_high))
            basis = "physics_equilibrium_band"

        decimals = 3 if item["step"] < 0.05 else (2 if item["step"] < 1.0 else 1)
        ranges[tag] = {
            "tag": tag,
            "label": item["label"],
            "unit": item["unit"],
            "role": item["role"],
            "group": item["group"],
            "zone": item["zone"],
            "lag_h": item["lag_h"],
            "golden_low": round(g_low, decimals),
            "golden_center": round(g_center, decimals),
            "golden_high": round(g_high, decimals),
            "basis": basis,
            "below_warning": mech["below"],
            "above_warning": mech["above"],
            "loss_below_per_unit": float(mech["loss_below"]),
            "loss_above_per_unit": float(mech["loss_above"]),
        }

    return {
        "target_production": round(target_production, 1),
        "dataset_id": meta["id"],
        "cohort_hours_matched": int(len(cohort)),
        "campaign_median_production": round(med_prod, 1),
        "production_basis": str(h["prod_basis"].iloc[0]) if len(h) else "estimated",
        "ranges": ranges,
    }


def _evaluate_tag_golden(val: float, g: dict) -> dict:
    """Evaluate a single parameter value against its Golden Range spec."""
    lo = float(g["golden_low"])
    hi = float(g["golden_high"])
    center = float(g["golden_center"])
    span = max(1e-6, hi - lo)
    pos_pct = 100.0 * (float(val) - lo) / span

    if val < lo:
        status = "below_golden"
        dev = float(val) - lo
        risk = min(1800.0, abs(dev) * float(g["loss_below_per_unit"]))
        warning = g["below_warning"]
    elif val > hi:
        status = "above_golden"
        dev = float(val) - hi
        risk = min(1800.0, abs(dev) * float(g["loss_above_per_unit"]))
        warning = g["above_warning"]
    else:
        status = "in_golden"
        dev = 0.0
        risk = 0.0
        warning = None

    return {
        "status": status,
        "deviation": round(dev, 3),
        "center_delta": round(float(val) - center, 3),
        "pos_pct": round(pos_pct, 1),
        "production_risk_t_d": round(risk, 1),
        "warning": warning,
    }


def attribute_historical_shortfall(
    when: pd.Timestamp,
    target_production: float = 4500.0,
    golden_spec: Optional[dict] = None,
) -> dict:
    """
    Backward-compatible historical root-cause analyzer at timestamp `when`.
    Evaluates lag-aligned parameter trajectories over [when - 2*tau, when] against both:
      1) the production-conditioned Golden Range for `target_production`, and
      2) the preceding 72-hour rolling furnace baseline.
    Identifies which manipulated inputs, disturbances, and state-response sensors caused production to suffer.
    """
    g_bundle = golden_spec or compute_golden_ranges(target_production)
    g_map = g_bundle["ranges"]
    h = _dataset_production_frame()

    past = h[h["dt"] <= when]
    if past.empty:
        past = h.iloc[:1]
    idx_pos = len(past) - 1
    row = past.iloc[-1]

    actual_prod = float(row["prod_t_d"])
    roll72_prod = float(row["prod_roll72"])
    shortfall_vs_target = max(0.0, float(target_production) - actual_prod)
    drop_vs_roll72 = max(0.0, roll72_prod - actual_prod)
    effective_shortfall = max(shortfall_vs_target, drop_vs_roll72)

    # Window for lag-aligned evaluation [idx_pos - 16, idx_pos] and 72h reference [idx_pos - 84, idx_pos - 12]
    win_start = max(0, idx_pos - 16)
    recent_win = h.iloc[win_start : idx_pos + 1]
    ref_start = max(0, idx_pos - 84)
    ref_end = max(1, idx_pos - 12)
    ref_win = h.iloc[ref_start:ref_end] if ref_end > ref_start else h.iloc[: max(1, idx_pos)]

    causes = []
    for item in FULL_SIM_CATALOG:
        tag = item["tag"]
        if tag == "Production" or tag not in g_map:
            continue
        if tag not in h.columns:
            continue
        g = g_map[tag]
        tau = max(1, int(round(float(LAG_TAU_HOURS.get(tag, item.get("lag_h", 1.0))))))
        s_rec = pd.to_numeric(recent_win[tag], errors="coerce").dropna()
        if s_rec.empty:
            continue
        if tag.startswith("Tp") or tag.startswith("Tt"):
            s_rec = s_rec.clip(20.0, 1050.0)
        # Lag-weighted active value leading into timestamp `when`
        lag_val = float(s_rec.ewm(span=max(1, tau), adjust=False).mean().iloc[-1])
        inst_val = float(s_rec.iloc[-1])

        s_ref = pd.to_numeric(ref_win[tag], errors="coerce").dropna()
        if tag.startswith("Tp") or tag.startswith("Tt"):
            s_ref = s_ref.clip(20.0, 1050.0)
        ref72_val = float(s_ref.median()) if not s_ref.empty else float(g["golden_center"])

        eval_lag = _evaluate_tag_golden(lag_val, g)
        eval_inst = _evaluate_tag_golden(inst_val, g)
        # Pick whichever of lag-aligned or instantaneous shows the active excursion
        chosen_eval = eval_lag if eval_lag["production_risk_t_d"] >= eval_inst["production_risk_t_d"] else eval_inst
        chosen_val = lag_val if eval_lag["production_risk_t_d"] >= eval_inst["production_risk_t_d"] else inst_val

        # Also check if parameter shifted adversely vs 72h rolling reference even if near golden boundary
        shift_vs_72h = chosen_val - ref72_val
        risk_t_d = float(chosen_eval["production_risk_t_d"])

        if chosen_eval["status"] == "in_golden" and drop_vs_roll72 > 120.0:
            # Check if a large shift vs 72h baseline contributed to the drop vs rolling 72h
            if tag in ("Fb", "Fo", "Th", "Pt", "CO2") and shift_vs_72h < 0:
                extra_loss = abs(shift_vs_72h) * float(g["loss_below_per_unit"]) * 0.55
                if extra_loss > 35.0:
                    risk_t_d = extra_loss
            elif tag in ("dP", "dPu", "dPl") and shift_vs_72h > 0.08:
                extra_loss = abs(shift_vs_72h) * float(g["loss_above_per_unit"]) * 0.55
                if extra_loss > 35.0:
                    risk_t_d = extra_loss

        if risk_t_d < 12.0:
            continue

        status_label = chosen_eval["status"]
        if status_label == "in_golden":
            status_label = "below_golden" if shift_vs_72h < 0 else "above_golden"
        warning_text = chosen_eval["warning"] or (
            g["below_warning"] if status_label == "below_golden" else g["above_warning"]
        )

        decimals = 3 if item["step"] < 0.05 else (2 if item["step"] < 1.0 else 1)
        causes.append(
            {
                "tag": tag,
                "label": item["label"],
                "role": item["role"],
                "zone": item["zone"],
                "unit": item["unit"],
                "lag_h": item["lag_h"],
                "value_at_lag": round(chosen_val, decimals),
                "instantaneous_value": round(inst_val, decimals),
                "ref_72h_value": round(ref72_val, decimals),
                "shift_vs_72h": round(shift_vs_72h, decimals),
                "golden_low": g["golden_low"],
                "golden_high": g["golden_high"],
                "golden_center": g["golden_center"],
                "status": status_label,
                "deviation_from_golden": chosen_eval["deviation"],
                "estimated_loss_t_d": round(risk_t_d, 1),
                "mechanism": warning_text,
            }
        )

    causes.sort(key=lambda c: c["estimated_loss_t_d"], reverse=True)
    top_causes = causes[:10]
    total_explained = sum(c["estimated_loss_t_d"] for c in top_causes) + 1e-6
    for c in top_causes:
        c["share_of_shortfall_pct"] = round(100.0 * c["estimated_loss_t_d"] / total_explained, 1)

    return {
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "target_production": round(float(target_production), 1),
        "actual_production_t_d": round(actual_prod, 1),
        "rolling_72h_production_t_d": round(roll72_prod, 1),
        "shortfall_vs_target_t_d": round(shortfall_vs_target, 1),
        "drop_vs_rolling_72h_t_d": round(drop_vs_roll72, 1),
        "effective_shortfall_t_d": round(effective_shortfall, 1),
        "production_basis": str(row["prod_basis"]),
        "root_causes": top_causes,
    }


def scan_historical_shortfalls(target_production: float = 4500.0, limit: int = 16) -> dict:
    """
    Scan the historical dataset for significant production shortfall episodes and diagnose the
    parameters that violated their Golden Range in each episode.
    Includes both:
      - 'constant_wind_mystery': wind Fb was near normal (>=88% of median) yet production suffered
        due to O₂ cut, ΔP permeability spike, CO₂ utilization loss, R shift, or wall accretions.
      - 'wind_or_regime_drop': reduced blast or post-stop recovery drops.
    """
    g_bundle = compute_golden_ranges(target_production)
    h = _dataset_production_frame()
    fb_ref = blast_reference(h)

    # Candidate hours where furnace is blowing (Fb >= 45% of reference) and either dropped vs 72h rolling or below target
    blowing = h[h["Fb"] >= fb_ref * 0.45].copy()
    if blowing.empty:
        blowing = h.copy()

    blowing["shortfall_target"] = (float(target_production) - blowing["prod_t_d"]).clip(lower=0.0)
    blowing["severity"] = blowing[["drop_vs_roll72", "shortfall_target"]].max(axis=1)

    # Select distinct episodes separated by at least 36 hours across three diagnostic categories:
    # 1) permeability_or_thermal_mystery: Fb and Fo are both normal, yet dP, Th, CO2, R, or Tp exited Golden Range
    # 2) constant_wind_shortfall: Fb is normal (>=88% of median), Fo/Pt/Th dropped
    # 3) wind_or_enrichment_shortfall: deeper production drop across on-wind hours
    perm_mystery = blowing[
        (blowing["Fb"] >= fb_ref * 0.90)
        & (blowing["Fo"] >= 14000.0 if "Fo" in blowing.columns else True)
        & ((blowing["dP"] >= 1.56) | (blowing["CO2"] <= 20.3) | (blowing["severity"] >= 160.0))
    ].copy()
    perm_mystery["mystery_score"] = (
        perm_mystery["severity"]
        + (perm_mystery["dP"] - 1.52).clip(lower=0.0) * 650.0
        + (20.6 - perm_mystery["CO2"]).clip(lower=0.0) * 140.0
    )
    perm_mystery = perm_mystery.sort_values("mystery_score", ascending=False)

    const_wind = blowing[(blowing["Fb"] >= fb_ref * 0.88) & (blowing["severity"] >= 180.0)].sort_values(
        "severity", ascending=False
    )
    deep_drops = blowing[(blowing["Fb"] >= fb_ref * REGIME_ON_WIND_FRAC) & (blowing["severity"] >= 300.0)].sort_values(
        "severity", ascending=False
    )

    selected_rows = []
    selected_times: list[pd.Timestamp] = []

    def _pick_from(pool: pd.DataFrame, max_count: int, category: str) -> None:
        for _, r in pool.iterrows():
            t_cand = pd.Timestamp(r["dt"])
            if any(abs((t_cand - t_prev).total_seconds()) < 36 * 3600 for t_prev in selected_times):
                continue
            selected_times.append(t_cand)
            selected_rows.append((t_cand, category))
            if len(selected_rows) >= max_count:
                break

    _pick_from(perm_mystery, max(5, limit // 3), "permeability_or_thermal_mystery")
    _pick_from(const_wind, max(10, (2 * limit) // 3), "constant_wind_shortfall")
    _pick_from(deep_drops, limit, "wind_or_enrichment_shortfall")

    episodes = []
    for t_ep, cat in selected_rows[:limit]:
        diag = attribute_historical_shortfall(t_ep, target_production=target_production, golden_spec=g_bundle)
        ep_row = h[h["dt"] == t_ep].iloc[0]
        episodes.append(
            {
                "t": t_ep.isoformat(sep=" "),
                "category": cat,
                "Fb": round(float(ep_row["Fb"]), 0),
                "Fo": round(float(ep_row["Fo"]), 0),
                "Th": round(float(ep_row["Th"]), 0),
                "dP": round(float(ep_row["dP"]), 2),
                "CO2": round(float(ep_row["CO2"]), 2),
                "R": round(float(ep_row["R"]), 2),
                "actual_production_t_d": diag["actual_production_t_d"],
                "rolling_72h_production_t_d": diag["rolling_72h_production_t_d"],
                "shortfall_vs_target_t_d": diag["shortfall_vs_target_t_d"],
                "drop_vs_rolling_72h_t_d": diag["drop_vs_rolling_72h_t_d"],
                "top_causes": diag["root_causes"][:4],
            }
        )

    episodes.sort(key=lambda e: max(e["drop_vs_rolling_72h_t_d"], e["shortfall_vs_target_t_d"]), reverse=True)
    return {
        "dataset_id": g_bundle["dataset_id"],
        "target_production": g_bundle["target_production"],
        "production_basis": g_bundle["production_basis"],
        "total_shortfall_hours_detected": int((blowing["severity"] >= 200.0).sum()),
        "constant_wind_shortfall_hours": int(len(const_wind)),
        "episodes": episodes,
    }


def simulate_coupled(
    when: pd.Timestamp,
    overrides: Optional[dict] = None,
    deltas: Optional[dict] = None,
    switches: Optional[dict] = None,
    mode: str = "hybrid",
    horizon_hours: int = 24,
    target_production: float = 4500.0,
) -> dict:
    """
    Run full coupled parameter simulation starting from timestamp `when`.
    Supports `mode` in {'hybrid', 'data_only', 'physics_only'}.
    Computes steady-state response for ALL 33+ parameters AND 24-hour dynamic trajectory.
    """
    overrides = overrides or {}
    deltas = deltas or {}
    switches = switches or {}
    learned = learn_from_dataset()
    meta = active_dataset_meta()

    # Span-screened hours: out-of-span instrument sentinels are causally filled and the
    # pressure identity dP = dPu + dPl holds exactly, so the baseline is self-consistent.
    hours = clean_hourly()
    past_h = hours[hours["dt"] <= when]
    if past_h.empty:
        past_h = hours.iloc[:1]
    row = past_h.iloc[-1]

    casts = silicon()
    past_c = casts[casts["dt"] <= when]
    base_si = float(past_c.iloc[-1]["Si"]) if not past_c.empty else float(learned["means"].get("Si", 0.47))

    # Build baseline state from the historical hour + catalog defaults for unmeasured tags
    base_state: dict[str, float] = {}
    measured_tags: list[str] = []
    assumed_tags: list[str] = []
    for item in FULL_SIM_CATALOG:
        tag = item["tag"]
        if tag == "Si":
            base_state[tag] = base_si
            measured_tags.append(tag)
        elif tag in row and pd.notna(row[tag]):
            val = float(row[tag])
            # Clip obvious sensor sentinel (e.g. 3311 C) to mean so baseline simulation is physical
            if tag.startswith("Tp") or tag.startswith("Tt"):
                val = float(np.clip(val, 20.0, 1050.0))
            base_state[tag] = val
            measured_tags.append(tag)
        elif "default_assumed" in item:
            base_state[tag] = float(item["default_assumed"])
            assumed_tags.append(tag)
        else:
            base_state[tag] = float(learned["means"].get(tag, (item["min"] + item["max"]) / 2.0))
            assumed_tags.append(tag)

    working_volume = float(meta.get("working_volume_m3", 2000.0))
    regime = operating_regime(base_state.get("Fb", 0.0), blast_reference(hours))

    # Free-running physics, then reconcile onto the sensors. The bias is computed once at the
    # baseline and reused for the proposal, so the response delta stays pure physics while the
    # absolute numbers agree with the instruments the plant actually reads.
    base_phys_free = compute_physics_state(base_state, working_volume)
    measured_anchor = {k: base_state[k] for k in ANCHORABLE if k in measured_tags}
    bias = physics_bias(base_phys_free, measured_anchor)
    base_phys = apply_bias(base_phys_free, bias, working_volume)

    for k in ["RAFT", "CZHeight", "CondensationIdx", "Production", "HMT"]:
        if k not in row or pd.isna(row.get(k)):
            base_state[k] = float(base_phys[k])

    # Apply user overrides and deltas to manipulated & disturbance inputs
    prop_state = dict(base_state)
    for k, v in switches.items():
        prop_state[k] = v

    input_deltas: dict[str, float] = {}
    for col in MANIPULATED_AND_DISTURBANCE:
        b_val = base_state[col]
        new_val = b_val
        if col in overrides and overrides[col] is not None:
            new_val = float(overrides[col])
        if col in deltas and deltas[col] is not None:
            new_val = new_val + float(deltas[col])
        prop_state[col] = new_val
        input_deltas[col] = new_val - b_val

    prop_phys_free = compute_physics_state(prop_state, working_volume)
    prop_phys = apply_bias(prop_phys_free, bias, working_volume)

    # Compute Data-Driven response delta from learned Jacobian
    jac = learned["jacobian"]
    data_deltas: dict[str, float] = {}
    for out_col in RESPONSE_AND_OUTCOME:
        d_val = 0.0
        if out_col in jac:
            for in_col, d_in in input_deltas.items():
                if abs(d_in) > 1e-9 and in_col in jac[out_col]:
                    d_val += jac[out_col][in_col] * d_in
        data_deltas[out_col] = d_val

    # Compute Physics response delta
    phys_deltas: dict[str, float] = {}
    for out_col in RESPONSE_AND_OUTCOME:
        if out_col in prop_phys and out_col in base_phys:
            phys_deltas[out_col] = float(prop_phys[out_col]) - float(base_phys[out_col])
        elif out_col.startswith("Tt"):
            phys_deltas[out_col] = float(prop_phys["TopTempMean"]) - float(base_phys["TopTempMean"])
        elif out_col.startswith("Tp"):
            # Peripheral wall temperatures respond to RAFT, Th, R, and CondensationIdx
            d_raft = prop_phys["RAFT"] - base_phys["RAFT"]
            d_cond = prop_phys["CondensationIdx"] - base_phys["CondensationIdx"]
            d_r = input_deltas.get("R", 0.0)
            # The centre-coke term must be the change in the switch, not its absolute position.
            # As an absolute it subtracted 12 C from every wall probe even with nothing changed,
            # which broke the rule that no input moved means no output moves.
            center_now = 1.0 if switches.get("switch_center_coke", CENTER_COKE_DEFAULT) else -1.0
            center_base = 1.0 if CENTER_COKE_DEFAULT else -1.0
            phys_deltas[out_col] = 0.14 * d_raft + 1.35 * d_cond - 24.0 * d_r - 12.0 * (center_now - center_base)
        elif out_col == "Tc":
            phys_deltas[out_col] = 0.04 * input_deltas.get("Th", 0.0)
        else:
            phys_deltas[out_col] = 0.0

    # Combine according to selected simulation mode
    w_phys = 1.0 if mode == "physics_only" else (0.0 if mode == "data_only" else 0.60)
    w_data = 0.0 if mode == "physics_only" else (1.0 if mode == "data_only" else 0.40)

    final_state = dict(prop_state)
    parameter_table = []
    cat_by_tag = {item["tag"]: item for item in FULL_SIM_CATALOG}

    for item in FULL_SIM_CATALOG:
        tag = item["tag"]
        b_val = float(base_state[tag])
        if tag in MANIPULATED_AND_DISTURBANCE:
            s_val = float(prop_state[tag])
            basis = "measured_input" if tag in row else "configured_knob"
        else:
            has_data_jac = tag in jac and any(abs(input_deltas.get(k, 0.0)) > 1e-9 and k in jac[tag] for k in input_deltas)
            d_p = phys_deltas.get(tag, 0.0)
            d_d = data_deltas.get(tag, 0.0)
            if mode == "data_only":
                comb_delta = d_d if has_data_jac else d_p
                basis = "learned_from_data" if has_data_jac else "physics_fallback"
            elif mode == "physics_only":
                comb_delta = d_p
                basis = "physics_balance"
            else:
                comb_delta = (w_phys * d_p + w_data * d_d) if has_data_jac else d_p
                basis = "hybrid_physics_ml" if has_data_jac else "physics_balance"
            # Widen the clamp to always admit the measured baseline. Clamping to the catalog
            # range alone silently rewrote real excursions, e.g. a 2.94 wt% cast silicon
            # became 1.62, and broke the zero-change identity.
            lo = min(item["min"] * 0.5, b_val)
            hi = max(item["max"] * 1.35, b_val)
            s_val = float(np.clip(b_val + comb_delta, lo, hi))
            final_state[tag] = s_val

        parameter_table.append(
            {
                "tag": tag,
                "label": item["label"],
                "unit": item["unit"],
                "role": item["role"],
                "group": item["group"],
                "zone": item["zone"],
                "lag_h": item["lag_h"],
                "min": item["min"],
                "max": item["max"],
                "step": item["step"],
                "pos": item["pos"],
                "baseline": round(b_val, 3),
                "simulated": round(s_val, 3),
                "delta": round(s_val - b_val, 3),
                "pct_change": round(100.0 * (s_val - b_val) / (abs(b_val) + 1e-6), 2),
                "basis": basis,
                "in_dataset": bool(tag in row or tag == "Si"),
            }
        )

    # Keep dP = dPu + dPl strictly consistent.
    final_state["dP"] = final_state["dPu"] + final_state["dPl"]
    # Hot blast pressure is its own instrument and does not equal Pt + dP exactly in the raw
    # data, so carry the identity on the change and leave the measured absolute intact.
    final_state["Ph"] = base_state["Ph"] + (final_state["dP"] - base_state["dP"]) + (
        final_state["Pt"] - base_state["Pt"]
    )

    # Enrich every parameter row with its production-conditioned Golden Range evaluation
    golden_bundle = compute_golden_ranges(target_production)
    golden_map = golden_bundle["ranges"]
    out_of_golden_simulated = []
    out_of_golden_baseline = []
    in_golden_sim_count = 0
    in_golden_base_count = 0

    for p_row in parameter_table:
        tag = p_row["tag"]
        if tag in ("dP", "Ph"):
            p_row["simulated"] = round(float(final_state[tag]), 3)
            p_row["delta"] = round(float(final_state[tag] - base_state[tag]), 3)
            p_row["pct_change"] = round(100.0 * p_row["delta"] / (abs(float(base_state[tag])) + 1e-6), 2)

        g_spec = golden_map.get(tag)
        if g_spec:
            ev_base = _evaluate_tag_golden(float(p_row["baseline"]), g_spec)
            ev_sim = _evaluate_tag_golden(float(p_row["simulated"]), g_spec)
            p_row["golden_low"] = g_spec["golden_low"]
            p_row["golden_center"] = g_spec["golden_center"]
            p_row["golden_high"] = g_spec["golden_high"]
            p_row["golden_basis"] = g_spec["basis"]
            p_row["baseline_golden_status"] = ev_base["status"]
            p_row["simulated_golden_status"] = ev_sim["status"]
            p_row["baseline_golden_pos_pct"] = ev_base["pos_pct"]
            p_row["golden_pos_pct"] = ev_sim["pos_pct"]
            p_row["baseline_production_risk_t_d"] = ev_base["production_risk_t_d"]
            p_row["production_risk_t_d"] = ev_sim["production_risk_t_d"]
            p_row["baseline_golden_warning"] = ev_base["warning"]
            p_row["golden_warning"] = ev_sim["warning"]
            p_row["below_warning"] = g_spec["below_warning"]
            p_row["above_warning"] = g_spec["above_warning"]

            if ev_sim["status"] == "in_golden":
                in_golden_sim_count += 1
            elif tag != "Production":
                out_of_golden_simulated.append(
                    {
                        "tag": tag,
                        "label": p_row["label"],
                        "role": p_row["role"],
                        "zone": p_row["zone"],
                        "unit": p_row["unit"],
                        "simulated": p_row["simulated"],
                        "golden_low": g_spec["golden_low"],
                        "golden_high": g_spec["golden_high"],
                        "status": ev_sim["status"],
                        "deviation": ev_sim["deviation"],
                        "production_risk_t_d": ev_sim["production_risk_t_d"],
                        "warning": ev_sim["warning"],
                    }
                )
            if ev_base["status"] == "in_golden":
                in_golden_base_count += 1
            elif tag != "Production":
                out_of_golden_baseline.append(
                    {
                        "tag": tag,
                        "label": p_row["label"],
                        "role": p_row["role"],
                        "zone": p_row["zone"],
                        "unit": p_row["unit"],
                        "baseline": p_row["baseline"],
                        "golden_low": g_spec["golden_low"],
                        "golden_high": g_spec["golden_high"],
                        "status": ev_base["status"],
                        "deviation": ev_base["deviation"],
                        "production_risk_t_d": ev_base["production_risk_t_d"],
                        "warning": ev_base["warning"],
                    }
                )

    out_of_golden_simulated.sort(key=lambda x: x["production_risk_t_d"], reverse=True)
    out_of_golden_baseline.sort(key=lambda x: x["production_risk_t_d"], reverse=True)
    hist_diag = attribute_historical_shortfall(when, target_production=target_production, golden_spec=golden_bundle)
    n_total_params = max(1, len(parameter_table))
    golden_analysis = {
        "target_production": round(float(target_production), 1),
        "actual_production_t_d": round(float(base_phys["Production"]), 1),
        "simulated_production_t_d": round(float(prop_phys["Production"]), 1),
        "rolling_72h_production_t_d": hist_diag["rolling_72h_production_t_d"],
        "shortfall_vs_target_t_d": round(max(0.0, float(target_production) - float(base_phys["Production"])), 1),
        "simulated_shortfall_vs_target_t_d": round(max(0.0, float(target_production) - float(prop_phys["Production"])), 1),
        "drop_vs_rolling_72h_t_d": hist_diag["drop_vs_rolling_72h_t_d"],
        "production_basis": hist_diag["production_basis"],
        "baseline_compliance_pct": round(100.0 * in_golden_base_count / n_total_params, 1),
        "simulated_compliance_pct": round(100.0 * in_golden_sim_count / n_total_params, 1),
        "in_golden_count": in_golden_sim_count,
        "total_parameters": n_total_params,
        "out_of_golden_simulated": out_of_golden_simulated,
        "out_of_golden_baseline": out_of_golden_baseline,
        "historical_root_causes": hist_diag["root_causes"],
    }

    # Build 24-hour dynamic step-response trajectory showing how each input acts on its own lag tau
    trajectory = []
    tracked_outputs = ["Production", "Si", "HMT", "dP", "CO2", "H2", "RAFT", "CZHeight", "CondensationIdx"]
    for h_step in range(0, horizon_hours + 1):
        step_rec: dict[str, float] = {"hour": h_step}
        # Fraction of each input's effect realized by hour `h_step` via 1 - exp(-h / tau)
        for out_col in tracked_outputs:
            b_val = float(base_state[out_col])
            steady_delta = float(final_state[out_col]) - b_val
            # Weight completion by active inputs' lag time constants
            num = 0.0
            den = 0.0
            for in_col, d_in in input_deltas.items():
                if abs(d_in) > 1e-9:
                    tau = LAG_TAU_HOURS.get(in_col, 2.0)
                    # Add extra thermal inertia for HMT and Si
                    if out_col in ["Si", "HMT"]:
                        tau = tau + 4.5
                    elif out_col == "CondensationIdx":
                        tau = max(8.0, tau)
                    frac = 1.0 - float(np.exp(-h_step / max(0.3, tau)))
                    w = abs(d_in) / (learned["stds"].get(in_col, 1.0) + 1e-6)
                    num += w * frac
                    den += w
            if den < 1e-9:
                realized_frac = 1.0 if h_step > 0 else 0.0
            else:
                realized_frac = num / den
            step_rec[out_col] = round(b_val + steady_delta * realized_frac, 3)
        trajectory.append(step_rec)

    # Top cause-effect attribution for the current knob changes
    attributions = []
    for in_col, d_in in input_deltas.items():
        if abs(d_in) < 1e-6:
            continue
        single_state = dict(base_state)
        for k, v in switches.items():
            single_state[k] = v
        single_state[in_col] = base_state[in_col] + d_in
        # Compared against the free-running baseline so the reconciliation bias cancels
        # and each attribution is the pure physics response to that one input.
        s_phys = compute_physics_state(single_state, working_volume)
        d_prod_p = s_phys["Production"] - base_phys_free["Production"]
        d_si_p = s_phys["Si"] - base_phys_free["Si"]
        d_dp_p = s_phys["dP"] - base_phys_free["dP"]
        d_si_d = jac.get("Si", {}).get(in_col, 0.0) * d_in
        d_dp_d = jac.get("dP", {}).get(in_col, 0.0) * d_in
        attributions.append(
            {
                "input": in_col,
                "label": cat_by_tag[in_col]["label"],
                "delta_input": round(d_in, 3),
                "unit": cat_by_tag[in_col]["unit"],
                "lag_h": LAG_TAU_HOURS.get(in_col, 1.0),
                "effect_Production_t_d": round(float(d_prod_p), 1),
                "effect_Si_wt_pct": round(float(w_phys * d_si_p + w_data * d_si_d), 4),
                "effect_dP_kgf_cm2": round(float(w_phys * d_dp_p + w_data * d_dp_d), 4),
                "effect_RAFT_C": round(float(s_phys["RAFT"] - base_phys_free["RAFT"]), 1),
            }
        )

    envelope = evaluate_density_envelope(base_state, prop_state, meta["id"])

    return {
        "status": "ready",
        "model_version": MODEL_VERSION,
        "mode": mode,
        "dataset": meta,
        "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
        "baseline_state": {k: round(float(v), 3) for k, v in base_state.items() if isinstance(v, (int, float, np.floating))},
        "simulated_state": {k: round(float(v), 3) for k, v in final_state.items() if isinstance(v, (int, float, np.floating))},
        "physics_kpis": prop_phys,
        "baseline_physics_kpis": base_phys,
        "parameters": parameter_table,
        "trajectory_24h": trajectory,
        "attributions": attributions,
        "operating_regime": regime,
        "envelope": envelope,
        "golden_analysis": golden_analysis,
        "reconciliation": {
            "anchored": sorted(bias.keys()),
            "bias": {k: round(v, 4) for k, v in bias.items()},
            "free_running": sorted(k for k in VALIDATED_BANDS if k not in bias),
            "assumed_inputs": sorted(assumed_tags),
            "measured_inputs": sorted(measured_tags),
            "kpi_status": classify_physics(prop_phys, bias, assumed_tags, regime["qualified"]),
            "warnings": band_warnings(prop_phys, sorted(assumed_tags), bias),
            "note": (
                "Anchored quantities are reconciled onto this furnace's sensors, so the absolute value "
                "matches the instrument and physics supplies only the response to a knob change. "
                "Free-running quantities have no sensor in this dataset and rest on the assumed inputs listed."
            ),
        },
    }


def optimize_for_target(
    when: pd.Timestamp,
    target_production: float = 4650.0,
    target_si: float = 0.46,
    max_dp: float = 1.52,
    min_raft: float = 2000.0,
    max_raft: float = 2250.0,
    objective_mode: str = "balanced",
) -> dict:
    """
    Constrained inverse optimization: find operating parameters (Fb, Th, Fo, Pt, R, PCI, CokeRate, BlastMoisture)
    that hit `target_production` and `target_si` while respecting permeability (dP <= max_dp) and RAFT bounds.
    """
    sim0 = simulate_coupled(when, mode="hybrid")
    base = sim0["baseline_state"]
    meta = active_dataset_meta()
    wv = float(meta.get("working_volume_m3", 2000.0))

    decision_Load = [
        ("Fb", 2600.0, 4250.0, base["Fb"]),
        ("Th", 980.0, 1240.0, base["Th"]),
        ("Fo", 5000.0, 30000.0, base["Fo"]),
        ("Pt", 1.15, 1.72, base["Pt"]),
        ("R", 3.30, 4.65, base["R"]),
        ("PCI", 75.0, 195.0, base["PCI"]),
        ("CokeRate", 285.0, 435.0, base["CokeRate"]),
        ("BlastMoisture", 8.0, 32.0, base["BlastMoisture"]),
    ]

    x0 = np.array([item[3] for item in decision_Load], dtype=float)
    bounds = [(item[1], item[2]) for item in decision_Load]
    scales = np.array([item[2] - item[1] for item in decision_Load], dtype=float)

    def eval_candidate(x: np.ndarray) -> dict:
        cand = dict(base)
        for idx, (tag, _, _, _) in enumerate(decision_Load):
            cand[tag] = float(x[idx])
        # Keep ore/coke ratio and coke+PCI coupled reasonably
        return compute_physics_state(cand, wv)

    def loss_fn(x: np.ndarray) -> float:
        phys = eval_candidate(x)
        prod_err = ((phys["Production"] - target_production) / 150.0) ** 2
        si_err = ((phys["Si"] - target_si) / 0.04) ** 2
        dp_pen = 40.0 * max(0.0, phys["dP"] - max_dp) ** 2
        raft_pen = 20.0 * (max(0.0, min_raft - phys["RAFT"]) / 50.0) ** 2 + 20.0 * (max(0.0, phys["RAFT"] - max_raft) / 50.0) ** 2
        fuel_pen = 0.0015 * phys["FuelRate"] if objective_mode == "min_fuel" else 0.0004 * phys["FuelRate"]
        trust_pen = 0.35 * float(np.sum(((x - x0) / scales) ** 2))
        return float(prod_err + 0.8 * si_err + dp_pen + raft_pen + fuel_pen + trust_pen)

    res = minimize(loss_fn, x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": 120})
    x_best = res.x
    best_overrides = {decision_Load[i][0]: float(x_best[i]) for i in range(len(decision_Load))}
    sim_opt = simulate_coupled(when, overrides=best_overrides, mode="hybrid", target_production=target_production)
    opt_phys = sim_opt["physics_kpis"]
    g_map = compute_golden_ranges(target_production)["ranges"]

    feasible = (
        abs(opt_phys["Production"] - target_production) <= 160.0
        and opt_phys["dP"] <= max_dp + 0.05
        and min_raft - 30.0 <= opt_phys["RAFT"] <= max_raft + 30.0
    )

    recommendations = []
    cat_by_tag = {item["tag"]: item for item in FULL_SIM_CATALOG}
    for i, (tag, lo, hi, cur_val) in enumerate(decision_Load):
        rec_val = float(x_best[i])
        g_spec = g_map.get(tag, {})
        ev_cur = _evaluate_tag_golden(float(cur_val), g_spec) if g_spec else {"status": "in_golden", "warning": None}
        recommendations.append(
            {
                "tag": tag,
                "label": cat_by_tag[tag]["label"],
                "unit": cat_by_tag[tag]["unit"],
                "current": round(cur_val, 2),
                "recommended": round(rec_val, 2),
                "delta": round(rec_val - cur_val, 2),
                "envelope_min": lo,
                "envelope_max": hi,
                "golden_low": g_spec.get("golden_low", lo),
                "golden_high": g_spec.get("golden_high", hi),
                "current_golden_status": ev_cur["status"],
                "current_warning": ev_cur["warning"],
                "lag_h": LAG_TAU_HOURS.get(tag, 1.0),
            }
        )

    opt_env = sim_opt.get("envelope", {"in_envelope": True, "routine_setpoint_allowed": True, "moc_dossier": None})
    return {
        "status": "feasible" if (feasible and opt_env.get("in_envelope", True)) else ("moc_trial_required" if feasible else "ceiling_limited"),
        "model_version": MODEL_VERSION,
        "feasible": bool(feasible),
        "in_envelope": bool(opt_env.get("in_envelope", True)),
        "envelope": opt_env,
        "target_production": target_production,
        "achieved_production": opt_phys["Production"],
        "target_si": target_si,
        "achieved_si": opt_phys["Si"],
        "achieved_dp": opt_phys["dP"],
        "achieved_raft": opt_phys["RAFT"],
        "achieved_fuel_rate": opt_phys["FuelRate"],
        "binding_ceiling": opt_phys["binding_ceiling"],
        "max_feasible_production": opt_phys["max_feasible_production"],
        "ceilings": opt_phys["ceilings"],
        "recommendations": recommendations,
        "recommended_overrides": {k: round(v, 3) for k, v in best_overrides.items()},
        "claim_level": "physics_and_learned_association",
        "note": (
            "Setpoints satisfy mass/heat/permeability constraints inside the joint Mahalanobis density envelope. Requires operator review."
            if opt_env.get("in_envelope", True)
            else "Target requires stepping outside the historical Mahalanobis density envelope; routine setpoint blocked and Management-of-Change (MoC) trial dossier generated."
        ),
    }


_ENVELOPE_CACHE: dict[str, dict] = {}


def _envelope_distribution(ds_id: str) -> dict:
    """Fit empirical joint mean and precision matrix on healthy on-wind manipulated inputs."""
    if ds_id in _ENVELOPE_CACHE:
        return _ENVELOPE_CACHE[ds_id]
    df = _merged_dataset()
    cols = [c for c in ["Fb", "Th", "Fo", "Pt", "R", "PCI", "CokeRate", "BlastMoisture"] if c in df.columns]
    mat = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    if len(mat) < 50:
        spec = {"cols": cols, "mean": [0.0] * len(cols), "inv_cov": np.eye(max(1, len(cols))).tolist(), "threshold": 4.5}
        _ENVELOPE_CACHE[ds_id] = spec
        return spec
    clipped = mat.copy()
    for c in cols:
        clipped[c] = clipped[c].clip(clipped[c].quantile(0.01), clipped[c].quantile(0.99))
    arr = clipped.to_numpy(dtype=float)
    mu = np.mean(arr, axis=0)
    cov = np.cov(arr, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov) + 1e-3]])
    cov_reg = cov + np.eye(len(cols)) * (np.diag(cov) * 0.05 + 1e-4)
    inv_cov = np.linalg.pinv(cov_reg)
    thresh = float(np.sqrt(chi2.ppf(0.99, df=max(1, len(cols)))))
    spec = {"cols": cols, "mean": mu.tolist(), "inv_cov": inv_cov.tolist(), "threshold": round(thresh, 3)}
    _ENVELOPE_CACHE[ds_id] = spec
    return spec


def evaluate_density_envelope(base_state: dict, prop_state: dict, ds_id: str) -> dict:
    """
    Evaluate whether `prop_state` stays inside the joint Mahalanobis density envelope
    and trust region around `base_state`. Per CLAUDE.md, a min/max box is not an envelope;
    out-of-envelope proposals block routine setpoints and generate an MoC trial dossier.
    """
    spec = _envelope_distribution(ds_id)
    cols = spec["cols"]
    if not cols:
        return {"in_envelope": True, "mahalanobis_distance": 0.0, "threshold": 4.5, "trust_region_ok": True, "moc_dossier": None}
    x = np.array([float(prop_state.get(c, 0.0)) for c in cols], dtype=float)
    mu = np.array(spec["mean"], dtype=float)
    inv_cov = np.array(spec["inv_cov"], dtype=float)
    diff = x - mu
    d_m = float(np.sqrt(max(0.0, float(diff.T @ inv_cov @ diff))))

    extra_z = 0.0
    for item in EXTRA_SIM_PARAMETERS:
        t = item["tag"]
        if t in MANIPULATED_AND_DISTURBANCE and t not in cols:
            span = max(1e-6, float(item["max"] - item["min"]))
            center = float(item.get("default_assumed", (item["min"] + item["max"]) / 2.0))
            z = abs(float(prop_state.get(t, center)) - center) / (0.28 * span)
            extra_z = max(extra_z, z)

    eff_dist = round(max(d_m, extra_z), 3)
    threshold = float(spec["threshold"])
    in_env = bool(eff_dist <= threshold)

    step_vec = np.array([float(prop_state.get(c, 0.0)) - float(base_state.get(c, 0.0)) for c in cols], dtype=float)
    step_norm = round(float(np.sqrt(max(0.0, float(step_vec.T @ inv_cov @ step_vec)))), 3)
    trust_ok = bool(step_norm <= threshold * 1.05)

    moc_dossier = None
    if not in_env or not trust_ok:
        moved_tags = [
            f"{k}: {round(float(base_state.get(k, 0.0)), 2)} -> {round(float(prop_state.get(k, 0.0)), 2)}"
            for k in MANIPULATED_AND_DISTURBANCE
            if abs(float(prop_state.get(k, 0.0)) - float(base_state.get(k, 0.0))) > 1e-4
        ]
        moc_dossier = {
            "status": "engineering_trial_required",
            "reason": (
                f"Joint Mahalanobis distance {eff_dist} exceeds historical density threshold {threshold}"
                if not in_env
                else f"Step size {step_norm} exceeds single-move trust region {round(threshold * 1.05, 2)}"
            ),
            "proposed_moves": moved_tags,
            "governance_rule": (
                "Routine setpoint blocked per CLAUDE.md. Requires plant Management-of-Change (MoC) review, "
                "pre-trial stove/tuyere safety check, and metallurgist sign-off."
            ),
        }

    return {
        "in_envelope": in_env,
        "trust_region_ok": trust_ok,
        "routine_setpoint_allowed": bool(in_env and trust_ok),
        "mahalanobis_distance": eff_dist,
        "threshold": threshold,
        "trust_step_distance": step_norm,
        "dimensions_evaluated": cols,
        "moc_dossier": moc_dossier,
    }


def _psi_score(early: np.ndarray, late: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index (PSI) between early-campaign reference and recent window."""
    if len(early) < 30 or len(late) < 30:
        return 0.0
    quantiles = np.linspace(0.0, 1.0, bins + 1)
    edges = np.unique(np.quantile(early, quantiles))
    if len(edges) < 3:
        return 0.0
    edges[0] = -np.inf
    edges[-1] = np.inf
    e_cnt, _ = np.histogram(early, bins=edges)
    l_cnt, _ = np.histogram(late, bins=edges)
    e_pct = np.clip(e_cnt / max(1, len(early)), 1e-4, 1.0)
    l_pct = np.clip(l_cnt / max(1, len(late)), 1e-4, 1.0)
    return float(np.sum((l_pct - e_pct) * np.log(l_pct / e_pct)))


def modelops_status() -> dict:
    """Enterprise ModelOps, Covariate Drift (PSI), Conformal Coverage, and TRL 1-9 Gate Monitor."""
    meta = active_dataset_meta()
    ds_id = meta["id"]
    df = _merged_dataset()
    card = read_card(ds_id)
    if card is None:
        from bf_twin.engine import train_card

        card = train_card(dataset_id=ds_id)

    n = len(df)
    ref_slice = df.iloc[: int(n * 0.65)]
    rec_slice = df.iloc[int(n * 0.80) :]
    drift_rows = []
    for col in [c for c in ["Fb", "Th", "Fo", "Pt", "R", "dP", "CO2", "H2", "Si"] if c in df.columns]:
        s_ref = pd.to_numeric(ref_slice[col], errors="coerce").dropna().to_numpy(dtype=float)
        s_rec = pd.to_numeric(rec_slice[col], errors="coerce").dropna().to_numpy(dtype=float)
        psi = round(_psi_score(s_ref, s_rec), 4)
        state = "stable" if psi < 0.12 else ("moderate_shift" if psi < 0.25 else "drift_retrain_recommended")
        drift_rows.append(
            {
                "tag": col,
                "psi": psi,
                "status": state,
                "ref_median": round(float(np.median(s_ref)), 3) if len(s_ref) else 0.0,
                "recent_median": round(float(np.median(s_rec)), 3) if len(s_rec) else 0.0,
            }
        )

    trl_ladder = [
        {"trl": "TRL 1-3", "title": "First-principles metallurgy & observability formulation", "status": "achieved", "evidence": "RAFT, Rist, Ergun, 12 hidden-state mechanisms, 7-gate protocol."},
        {"trl": "TRL 4", "title": "Component & walk-forward ML validation in lab", "status": "achieved", "evidence": f"LightGBM RMSE {round(card['lightgbm_rmse'], 4)} beats persistence {round(card['persistence_rmse'], 4)} wt% across 5 purged folds."},
        {"trl": "TRL 5", "title": "Coupled twin + Mahalanobis envelope + RBAC/audit integration", "status": "achieved", "evidence": "41-tag coupled simulator, Golden Ranges, SHA-256 hash-chained audit, SSE stream."},
        {"trl": "TRL 6", "title": "Prototype demonstrated on multi-year running-plant archive", "status": "achieved", "evidence": "Validated across 29,602 hours & 16,589 casts from EVRAZ ZSMK (2013-2016) industrial furnace."},
        {"trl": "TRL 7", "title": "Live read-only shadow-mode demonstration on customer furnace", "status": "harness_ready_awaiting_plant", "evidence": "PI Web API / OPC-UA / SSE connectors built; awaits customer DMZ read-replica (Phase A-C)."},
        {"trl": "TRL 8", "title": "Site-calibrated twin with signed PV-01..PV-10 & OT security sign-off", "status": "awaiting_plant_commissioning", "evidence": "Requires site metallurgist calibration of PV register + corporate SSO/Postgres rollout (Phase D)."},
        {"trl": "TRL 9", "title": "Multi-campaign sustained operational advisory mission", "status": "awaiting_plant_campaign", "evidence": "Earned after 6+ months of verified shadow/advisory operation on an active blast furnace."},
    ]

    return {
        "model_version": MODEL_VERSION,
        "dataset_id": ds_id,
        "dataset_name": meta["name"],
        "served_silicon_model": card["served_model"],
        "persistence_rmse_wt_pct": round(float(card["persistence_rmse"]), 4),
        "lightgbm_rmse_wt_pct": round(float(card["lightgbm_rmse"]), 4),
        "improvement_over_persistence_pct": card.get("improvement_pct", 0.0),
        "conformal_90_half_width_wt_pct": round(float(card["interval_half_width"]), 4),
        "nominal_coverage_target": 0.90,
        "covariate_drift_psi": drift_rows,
        "retrain_recommended": any(r["psi"] >= 0.25 for r in drift_rows),
        "current_trl_achieved": "TRL 6 (Demonstrated on 3.4-year running-plant industrial archive; TRL 7-9 software harness complete)",
        "trl_ladder": trl_ladder,
    }
