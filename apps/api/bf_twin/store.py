"""Load the immutable EVRAZ workbooks and user-uploaded datasets into a local cache."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PUBLIC = ROOT / "data" / "public" / "evraz-zsmk-2013-2016"
CACHE = ROOT / "data" / "cache"
USER_DIR = ROOT / "data" / "user_uploads"
RAW_NAME = "1_blast_furnace_data_first_dataset.xlsx"
LABELED_NAME = "2_blast_furnace_data_second_dataset.xlsx"

RANGES: dict[str, tuple[float, float]] = {
    "Fb": (0, 5000),
    "Ph": (0, 4),
    "Pc": (0, 4),
    "Tc": (0, 150),
    "Fo": (0, 40000),
    "dP": (0, 2.5),
    "dPu": (0, 2.5),
    "dPl": (0, 2.5),
    "Pt": (0, 2.5),
    "Th": (0, 1800),
    "CO2": (0, 30),
    "H2": (0, 15),
}
for _i in range(1, 5):
    RANGES[f"Tt{_i}"] = (0, 1100)
for _i in range(1, 11):
    RANGES[f"Tp{_i}"] = (0, 1100)

TAGS = list(RANGES) + ["R"]
EVIDENCE = {name: "measured" for name in TAGS}
EVIDENCE["R"] = "derived_latent"

PARAMETER_CATALOG: list[dict[str, Any]] = [
    {"tag": "Fb", "label": "Blast volume", "unit": "m³/min", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "raceway", "low": 0, "high": 5000, "min": 1500.0, "max": 4500.0, "delta_min": -800, "delta_max": 800, "step": 10.0, "lag_h": 1.0, "pos": [5.2, -1.0, 0.0]},
    {"tag": "Th", "label": "Hot blast temp", "unit": "°C", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "raceway", "low": 0, "high": 1800, "min": 850.0, "max": 1280.0, "delta_min": -150, "delta_max": 150, "step": 5.0, "lag_h": 1.5, "pos": [5.2, 0.2, 0.0]},
    {"tag": "Fo", "label": "Oxygen flow", "unit": "m³/h", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "raceway", "low": 0, "high": 40000, "min": 0.0, "max": 35000.0, "delta_min": -6000, "delta_max": 6000, "step": 100.0, "lag_h": 1.0, "pos": [-5.2, -1.0, 0.0]},
    {"tag": "Pt", "label": "Top gas pressure", "unit": "kgf/cm²", "role": "manipulated", "group": "Top Gas & Throat", "zone": "top_cone", "low": 0, "high": 2.5, "min": 0.8, "max": 2.2, "delta_min": -0.4, "delta_max": 0.4, "step": 0.01, "lag_h": 0.5, "pos": [4.8, 10.2, 0.0]},
    {"tag": "R", "label": "Ore-to-coke ratio", "unit": "t/t", "role": "manipulated", "group": "Burden & Charging", "zone": "stockline", "low": 1.5, "high": 6.5, "min": 2.8, "max": 5.2, "delta_min": -0.8, "delta_max": 0.8, "step": 0.02, "lag_h": 6.0, "pos": [0.0, 13.6, 0.0]},
    {"tag": "PCI", "label": "PCI Coal Injection", "unit": "kg/tHM", "role": "manipulated", "group": "Injectants & Fuel", "zone": "raceway", "low": 0, "high": 260, "min": 0.0, "max": 210.0, "delta_min": -60, "delta_max": 60, "step": 2.0, "lag_h": 2.5, "pos": [-5.2, 0.2, 0.0], "default_assumed": 115.0},
    {"tag": "CokeRate", "label": "Charged Coke Rate", "unit": "kg/tHM", "role": "manipulated", "group": "Injectants & Fuel", "zone": "stockline", "low": 240, "high": 550, "min": 260.0, "max": 480.0, "delta_min": -60, "delta_max": 60, "step": 2.0, "lag_h": 6.5, "pos": [-3.8, 12.8, 0.0], "default_assumed": 375.0},
    {"tag": "BlastMoisture", "label": "Blast Moisture / Steam", "unit": "g/Nm³", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "blast_main", "low": 0, "high": 60, "min": 5.0, "max": 45.0, "delta_min": -12, "delta_max": 18, "step": 0.5, "lag_h": 0.8, "pos": [5.2, -2.0, 0.0], "default_assumed": 16.0},
    {"tag": "BurdenFe", "label": "Burden Fe Grade", "unit": "wt%", "role": "disturbance", "group": "Burden & Charging", "zone": "upper_shaft", "low": 50, "high": 68, "min": 54.0, "max": 65.0, "delta_min": -4, "delta_max": 4, "step": 0.2, "lag_h": 6.0, "pos": [3.8, 12.8, 0.0], "default_assumed": 58.5},
    {"tag": "CokeCSR", "label": "Coke CSR Strength", "unit": "%", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "cohesive_zone", "low": 45, "high": 75, "min": 52.0, "max": 72.0, "delta_min": -8, "delta_max": 8, "step": 0.5, "lag_h": 7.0, "pos": [-4.8, 5.2, 0.0], "default_assumed": 64.0},
    {"tag": "SinterRDI", "label": "Sinter RDI Fines", "unit": "%", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "upper_shaft", "low": 15, "high": 45, "min": 18.0, "max": 38.0, "delta_min": -8, "delta_max": 10, "step": 0.5, "lag_h": 4.5, "pos": [-4.8, 8.8, 0.0], "default_assumed": 26.5},
    {"tag": "AlkaliInput", "label": "Alkali Load (K₂O+Na₂O)", "unit": "kg/tHM", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "cohesive_zone", "low": 0.2, "high": 6.0, "min": 0.5, "max": 5.5, "delta_min": -1.5, "delta_max": 2.5, "step": 0.1, "lag_h": 12.0, "pos": [4.9, 5.8, 0.0], "default_assumed": 2.1},
    {"tag": "ZnInput", "label": "Zinc Input Load", "unit": "g/tHM", "role": "disturbance", "group": "Condensation & Alkalis", "zone": "upper_shaft", "low": 10, "high": 400, "min": 30.0, "max": 350.0, "delta_min": -70, "delta_max": 160, "step": 5.0, "lag_h": 12.0, "pos": [4.9, 8.2, 0.0], "default_assumed": 115.0},
    {"tag": "Tc", "label": "Cold blast temp", "unit": "°C", "role": "manipulated", "group": "Blast & Tuyeres", "zone": "blast_main", "low": 0, "high": 150, "min": 40.0, "max": 145.0, "delta_min": -40, "delta_max": 40, "step": 1.0, "lag_h": 0.5, "pos": [-4.8, -2.5, 0.0]},
    {"tag": "Pc", "label": "Cold blast pressure", "unit": "kgf/cm²", "role": "manipulated", "group": "Pressures & Permeability", "zone": "blast_main", "low": 0, "high": 4.0, "min": 1.6, "max": 3.6, "delta_min": -0.5, "delta_max": 0.5, "step": 0.02, "lag_h": 0.5, "pos": [-4.8, -1.9, 1.2]},
    {"tag": "Ph", "label": "Hot blast pressure", "unit": "kgf/cm²", "role": "state_response", "group": "Pressures & Permeability", "zone": "raceway", "low": 0, "high": 4.0, "min": 1.5, "max": 3.5, "step": 0.02, "lag_h": 0.5, "pos": [4.8, -0.3, 1.5]},
    {"tag": "dP", "label": "Total pressure drop", "unit": "kgf/cm²", "role": "state_response", "group": "Pressures & Permeability", "zone": "cohesive_zone", "low": 0, "high": 2.5, "min": 0.8, "max": 2.1, "step": 0.01, "lag_h": 1.0, "pos": [-5.2, 5.2, 0.0]},
    {"tag": "dPu", "label": "Upper pressure drop", "unit": "kgf/cm²", "role": "state_response", "group": "Pressures & Permeability", "zone": "upper_shaft", "low": 0, "high": 2.5, "min": 0.15, "max": 1.1, "step": 0.01, "lag_h": 1.5, "pos": [-5.0, 8.0, 0.0]},
    {"tag": "dPl", "label": "Lower pressure drop", "unit": "kgf/cm²", "role": "state_response", "group": "Pressures & Permeability", "zone": "lower_shaft", "low": 0, "high": 2.5, "min": 0.5, "max": 1.6, "step": 0.01, "lag_h": 1.0, "pos": [-5.0, 3.0, 0.0]},
    {"tag": "CO2", "label": "Top gas CO₂", "unit": "vol%", "role": "state_response", "group": "Top Gas & Throat", "zone": "top_cone", "low": 0, "high": 30, "min": 14.0, "max": 26.0, "step": 0.1, "lag_h": 1.5, "pos": [-4.2, 11.6, 0.0]},
    {"tag": "H2", "label": "Top gas H₂", "unit": "vol%", "role": "state_response", "group": "Top Gas & Throat", "zone": "top_cone", "low": 0, "high": 15, "min": 2.0, "max": 11.0, "step": 0.1, "lag_h": 1.0, "pos": [-4.2, 10.6, 0.0]},
]
for _i in range(1, 5):
    PARAMETER_CATALOG.append(
        {"tag": f"Tt{_i}", "label": f"Top gas offtake {_i}", "unit": "°C", "role": "state_response", "group": "Top Gas & Throat", "zone": "top_cone", "low": 0, "high": 1100, "min": 60.0, "max": 350.0, "step": 2.0, "lag_h": 1.0, "pos": [2.6 if _i in (1, 4) else -2.6, 12.6, 2.2 if _i <= 2 else -2.2]}
    )
for _i in range(1, 11):
    _angle = (_i - 1) * (2 * np.pi / 10.0)
    PARAMETER_CATALOG.append(
        {"tag": f"Tp{_i}", "label": f"Peripheral probe {_i}", "unit": "°C", "role": "state_response", "group": "Peripheral Wall Array", "zone": "shaft_wall", "low": 0, "high": 1100, "min": 80.0, "max": 750.0, "step": 5.0, "lag_h": 1.5, "pos": [float(np.cos(_angle) * 4.35), 6.2, float(np.sin(_angle) * 4.35)]}
    )
PARAMETER_CATALOG.extend(
    [
        {"tag": "Si", "label": "Hot metal silicon [Si]", "unit": "wt%", "role": "outcome", "group": "Hot Metal & Production", "zone": "hearth", "low": 0.05, "high": 2.5, "min": 0.15, "max": 1.2, "step": 0.01, "lag_h": 4.0, "pos": [0.0, -2.8, 2.8]},
        {"tag": "Production", "label": "Hot Metal Production", "unit": "t/day", "role": "outcome", "group": "Hot Metal & Production", "zone": "hearth", "low": 0, "high": 6500, "min": 2000.0, "max": 6000.0, "step": 25.0, "lag_h": 2.0, "pos": [3.2, -2.8, 1.5], "default_assumed": 4500.0},
        {"tag": "HMT", "label": "Hot Metal Temp", "unit": "°C", "role": "outcome", "group": "Hot Metal & Production", "zone": "hearth", "low": 1350, "high": 1580, "min": 1440.0, "max": 1545.0, "step": 2.0, "lag_h": 4.0, "pos": [-3.2, -2.8, 1.5], "default_assumed": 1495.0},
        {"tag": "RAFT", "label": "Raceway Flame Temp (RAFT)", "unit": "°C", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "raceway", "low": 1750, "high": 2450, "min": 1850.0, "max": 2350.0, "step": 5.0, "lag_h": 0.2, "pos": [2.2, -0.5, 1.8], "default_assumed": 2080.0},
        {"tag": "CZHeight", "label": "Cohesive Zone Root Height", "unit": "m", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "cohesive_zone", "low": 1.5, "high": 7.5, "min": 2.2, "max": 6.8, "step": 0.1, "lag_h": 3.0, "pos": [0.0, 3.4, 2.8], "default_assumed": 3.8},
        {"tag": "CondensationIdx", "label": "Alkali/Zn Condensation Load", "unit": "index", "role": "derived_latent", "group": "Internal Zones & Condensation", "zone": "upper_shaft", "low": 0, "high": 100, "min": 0.0, "max": 100.0, "step": 1.0, "lag_h": 8.0, "pos": [0.0, 8.4, 2.8], "default_assumed": 24.0},
    ]
)

# Optional extended columns supported when user uploads plant data
EXTENDED_CATALOG: dict[str, dict[str, Any]] = {
    "PCI": {"tag": "PCI", "label": "PCI coal injection", "unit": "kg/tHM", "role": "manipulated", "zone": "raceway", "low": 0, "high": 260, "delta_min": -40, "delta_max": 40, "step": 2},
    "CokeRate": {"tag": "CokeRate", "label": "Coke rate", "unit": "kg/tHM", "role": "manipulated", "zone": "stockline", "low": 240, "high": 550, "delta_min": -40, "delta_max": 40, "step": 2},
    "Steam": {"tag": "Steam", "label": "Blast moisture / steam", "unit": "g/Nm³", "role": "manipulated", "zone": "blast_main", "low": 0, "high": 60, "delta_min": -15, "delta_max": 15, "step": 1},
    "CO": {"tag": "CO", "label": "Top gas CO", "unit": "vol%", "role": "state_response", "zone": "top_cone", "low": 10, "high": 35},
    "HMT": {"tag": "HMT", "label": "Hot metal temperature", "unit": "°C", "role": "outcome", "zone": "hearth", "low": 1350, "high": 1580},
    "Production": {"tag": "Production", "label": "Hot-metal production", "unit": "t/h", "role": "outcome", "zone": "hearth", "low": 0, "high": 450},
}

_MEM_CACHE: dict[str, Any] = {}
_DEFAULT_DATASET = "evraz-zsmk-bf"
_ACTIVE_POINTER = CACHE / "active_dataset.json"


def _read_active_pointer() -> str:
    """The selected dataset is persisted so a restart or a second worker reads the same one."""
    try:
        return str(json.loads(_ACTIVE_POINTER.read_text())["id"])
    except Exception:
        return _DEFAULT_DATASET


_ACTIVE_DATASET: str = _read_active_pointer()


def active_dataset_id() -> str:
    return _ACTIVE_DATASET


def active_dataset_meta() -> dict[str, Any]:
    ds_list = list_datasets()
    found = next((d for d in ds_list if d["id"] == _ACTIVE_DATASET), ds_list[0])
    return {
        **found,
        "working_volume_m3": 2000.0,
        "nameplate_t_per_day": 4500.0,
    }


def set_active_dataset(dataset_id: str) -> dict[str, Any]:
    global _ACTIVE_DATASET
    available = {d["id"] for d in list_datasets()}
    if dataset_id not in available:
        raise KeyError(f"Unknown dataset: {dataset_id}")
    _ACTIVE_DATASET = dataset_id
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        _ACTIVE_POINTER.write_text(json.dumps({"id": dataset_id}))
    except OSError:
        pass
    return active_dataset_meta()


def select_dataset(dataset_id: str) -> dict[str, Any]:
    return set_active_dataset(dataset_id)


def ingest_user_dataset(filename: str, content: bytes, column_map: Optional[dict] = None) -> dict[str, Any]:
    return upload_user_dataset(filename, content)


def published_at() -> pd.Timestamp:
    return pd.Timestamp("2025-09-15T21:34:04Z")


def ensure_cache() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    USER_DIR.mkdir(parents=True, exist_ok=True)
    hourly_path = CACHE / "hourly.parquet"
    silicon_path = CACHE / "silicon.parquet"
    if hourly_path.exists() and silicon_path.exists():
        return
    hourly_df = pd.read_excel(PUBLIC / RAW_NAME, sheet_name="data")
    silicon_df = pd.read_excel(PUBLIC / RAW_NAME, sheet_name="Si")
    hourly_df["dt"] = pd.to_datetime(hourly_df["dt"])
    silicon_df["dt"] = pd.to_datetime(silicon_df["dt"])
    hourly_df = hourly_df.sort_values("dt")
    silicon_df = silicon_df.sort_values("dt")
    hourly_df.to_parquet(hourly_path, index=False)
    silicon_df.to_parquet(silicon_path, index=False)


def _ensure_synthetic_user_demo() -> Path:
    """Create a rich synthetic plant dataset with production, PCI, coke rate, CO, and HMT for testing user-data mode."""
    USER_DIR.mkdir(parents=True, exist_ok=True)
    demo_path = USER_DIR / "synthetic_plant_bf1.parquet"
    meta_path = USER_DIR / "synthetic_plant_bf1.json"
    if demo_path.exists() and meta_path.exists():
        return demo_path
    ensure_cache()
    base = pd.read_parquet(CACHE / "hourly.parquet").sort_values("dt").tail(2400).copy().reset_index(drop=True)
    casts = pd.read_parquet(CACHE / "silicon.parquet").sort_values("dt")
    merged = pd.merge_asof(base, casts, on="dt", direction="backward")
    for col, (lo, hi) in RANGES.items():
        merged[col] = merged[col].where((merged[col] >= lo) & (merged[col] <= hi), np.nan).ffill().bfill()
    merged["Si"] = merged["Si"].ffill().bfill().fillna(0.48)

    rng = np.random.default_rng(42)
    n = len(merged)
    fb_norm = (merged["Fb"] - 3200.0) / 400.0
    fo_norm = (merged["Fo"] - 12000.0) / 4000.0
    th_norm = (merged["Th"] - 1120.0) / 80.0
    r_norm = (merged["R"] - 4.1) / 0.4

    merged["PCI"] = np.clip(145.0 + 18.0 * fo_norm + 8.0 * th_norm + rng.normal(0, 2.5, n), 80.0, 210.0).round(2)
    merged["CokeRate"] = np.clip(365.0 - 24.0 * r_norm - 0.55 * (merged["PCI"] - 145.0) + rng.normal(0, 3.0, n), 290.0, 460.0).round(2)
    merged["Steam"] = np.clip(16.0 + 2.5 * fb_norm - 1.5 * th_norm + rng.normal(0, 0.8, n), 4.0, 40.0).round(2)
    merged["CO"] = np.clip(22.8 - 0.55 * (merged["CO2"] - 19.0) + 0.015 * (merged["PCI"] - 145.0) + rng.normal(0, 0.25, n), 16.0, 29.0).round(2)
    merged["HMT"] = np.clip(1488.0 + 42.0 * (merged["Si"] - 0.48) + 0.18 * (merged["Th"] - 1120.0) - 8.0 * r_norm + rng.normal(0, 3.5, n), 1410.0, 1545.0).round(1)
    # Production (t/h) driven by active O2 in blast + enrichment, ore/coke ratio, and permeability penalty
    o2_active = (merged["Fb"] * 60.0 * 0.21 + merged["Fo"]) / 48000.0
    dp_penalty = np.maximum(0.0, merged["dP"] - 1.48) * 32.0
    merged["Production"] = np.clip(
        185.0 * o2_active + 11.5 * r_norm + 0.06 * (merged["Th"] - 1120.0) - dp_penalty + rng.normal(0, 1.8, n),
        60.0,
        250.0,
    ).round(2)

    merged.to_parquet(demo_path, index=False)
    meta = {
        "id": "synthetic-plant-bf1",
        "name": "Synthetic Full-Sensor Plant (with Tonnes, PCI, Coke, CO, HMT)",
        "origin": "synthetic",
        "campaign": "synthetic-validation-2400h",
        "timezone": "UTC",
        "live": False,
        "rows": int(len(merged)),
        "has_production": True,
        "has_co": True,
        "description": "Synthetic validation dataset with 32 columns including Production (t/h), PCI, CokeRate, Steam, CO, and HMT to test full user-data learning.",
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    return demo_path


def list_datasets() -> list[dict[str, Any]]:
    ensure_cache()
    _ensure_synthetic_user_demo()
    evraz_hours = _load_evraz_hourly()
    evraz_si = _load_evraz_silicon()
    items: list[dict[str, Any]] = [
        {
            "id": "evraz-zsmk-bf",
            "name": "EVRAZ ZSMK Public Reference (2013–2016)",
            "origin": "public_reference",
            "campaign": "2013-2016-public",
            "timezone": "unconfirmed",
            "live": False,
            "rows": int(len(evraz_hours)),
            "casts": int(len(evraz_si)),
            "has_production": False,
            "has_co": False,
            "active": _ACTIVE_DATASET == "evraz-zsmk-bf",
        }
    ]
    for meta_file in sorted(USER_DIR.glob("*.json")):
        try:
            meta = json.loads(meta_file.read_text())
            meta["active"] = _ACTIVE_DATASET == meta["id"]
            items.append(meta)
        except Exception:
            continue
    return items


def upload_user_dataset(filename: str, content: bytes, dataset_name: Optional[str] = None) -> dict[str, Any]:
    """Ingest a user CSV, Excel, or Parquet file, standardize columns, and register it for simulation."""
    USER_DIR.mkdir(parents=True, exist_ok=True)
    lower = filename.lower()
    buf = io.BytesIO(content)
    if lower.endswith(".parquet"):
        df = pd.read_parquet(buf)
    elif lower.endswith(".xlsx") or lower.endswith(".xls"):
        df = pd.read_excel(buf)
    else:
        df = pd.read_csv(buf)

    if df.empty or len(df) < 10:
        raise ValueError("Uploaded dataset must have at least 10 rows of furnace history.")

    # Locate timestamp column or synthesize hourly index
    dt_col = None
    for candidate in ["dt", "timestamp", "time", "date", "datetime", "Date", "Timestamp"]:
        if candidate in df.columns:
            dt_col = candidate
            break
    if dt_col is not None:
        df["dt"] = pd.to_datetime(df[dt_col], errors="coerce")
        df = df.dropna(subset=["dt"]).sort_values("dt").reset_index(drop=True)
    else:
        df["dt"] = pd.date_range("2025-01-01 00:00:00", periods=len(df), freq="1h")

    # Map common column aliases to canonical names
    alias_map = {
        "blast": "Fb",
        "blast_volume": "Fb",
        "blast_flow": "Fb",
        "hot_blast_temp": "Th",
        "blast_temp": "Th",
        "oxygen": "Fo",
        "oxygen_flow": "Fo",
        "top_pressure": "Pt",
        "ore_coke": "R",
        "ore_to_coke": "R",
        "cold_blast_temp": "Tc",
        "cold_blast_pressure": "Pc",
        "hot_blast_pressure": "Ph",
        "pressure_drop": "dP",
        "upper_dp": "dPu",
        "lower_dp": "dPl",
        "co2": "CO2",
        "h2": "H2",
        "co": "CO",
        "silicon": "Si",
        "si": "Si",
        "production": "Production",
        "hm_tonnes": "Production",
        "tonnes": "Production",
        "prod_tph": "Production",
        "pci": "PCI",
        "pci_rate": "PCI",
        "coke_rate": "CokeRate",
        "steam": "Steam",
        "hmt": "HMT",
        "hot_metal_temp": "HMT",
    }
    rename_dict = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if col not in TAGS and col not in EXTENDED_CATALOG and key in alias_map:
            rename_dict[col] = alias_map[key]
    if rename_dict:
        df = df.rename(columns=rename_dict)

    # Ensure core columns exist so 3D visualization and physics checks work seamlessly;
    # if a user uploads partial columns, fill missing structural geometry display tags from median reference with 'assumed' flag
    ref = _load_evraz_hourly().tail(len(df)).reset_index(drop=True)
    missing_core: list[str] = []
    for col in TAGS:
        if col not in df.columns:
            missing_core.append(col)
            df[col] = float(ref[col].median())
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").ffill().bfill()

    if "Si" not in df.columns:
        df["Si"] = 0.48
        missing_core.append("Si")
    else:
        df["Si"] = pd.to_numeric(df["Si"], errors="coerce").ffill().bfill().fillna(0.48)

    for ext_col in EXTENDED_CATALOG:
        if ext_col in df.columns:
            df[ext_col] = pd.to_numeric(df[ext_col], errors="coerce").ffill().bfill()

    slug = "".join(c if c.isalnum() else "-" for c in Path(filename).stem.lower()).strip("-") or "user-bf"
    dataset_id = f"user-{slug}"
    parquet_path = USER_DIR / f"{dataset_id}.parquet"
    meta_path = USER_DIR / f"{dataset_id}.json"

    df.to_parquet(parquet_path, index=False)
    meta = {
        "id": dataset_id,
        "name": dataset_name or f"User Dataset ({filename})",
        "origin": "user_plant",
        "campaign": f"user-upload-{len(df)}h",
        "timezone": "plant_local",
        "live": False,
        "rows": int(len(df)),
        "casts": int(df["Si"].notna().sum()),
        "has_production": "Production" in df.columns,
        "has_co": "CO" in df.columns,
        "missing_core_assumed": missing_core,
        "columns": [c for c in df.columns if c != "dt"],
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    _MEM_CACHE.clear()
    set_active_dataset(dataset_id)
    return meta


def _load_evraz_hourly() -> pd.DataFrame:
    if "evraz_hourly" not in _MEM_CACHE:
        ensure_cache()
        frame = pd.read_parquet(CACHE / "hourly.parquet")
        frame["dt"] = pd.to_datetime(frame["dt"])
        _MEM_CACHE["evraz_hourly"] = frame.sort_values("dt").reset_index(drop=True)
    return _MEM_CACHE["evraz_hourly"]


def _load_evraz_silicon() -> pd.DataFrame:
    if "evraz_silicon" not in _MEM_CACHE:
        ensure_cache()
        frame = pd.read_parquet(CACHE / "silicon.parquet")
        frame["dt"] = pd.to_datetime(frame["dt"])
        _MEM_CACHE["evraz_silicon"] = frame.sort_values("dt").reset_index(drop=True)
    return _MEM_CACHE["evraz_silicon"]


def hourly(dataset_id: Optional[str] = None) -> pd.DataFrame:
    ds = dataset_id or _ACTIVE_DATASET
    if ds == "evraz-zsmk-bf":
        return _load_evraz_hourly()
    cache_key = f"hourly::{ds}"
    if cache_key not in _MEM_CACHE:
        _ensure_synthetic_user_demo()
        path = USER_DIR / f"{ds.replace('synthetic-plant-bf1', 'synthetic_plant_bf1')}.parquet"
        if not path.exists():
            path = USER_DIR / f"{ds}.parquet"
        frame = pd.read_parquet(path)
        frame["dt"] = pd.to_datetime(frame["dt"])
        _MEM_CACHE[cache_key] = frame.sort_values("dt").reset_index(drop=True)
    return _MEM_CACHE[cache_key]


def clean_hourly(dataset_id: Optional[str] = None) -> pd.DataFrame:
    """Return hourly frame with out-of-span instrument sentinels (e.g. 3311 C) replaced by causal ffill."""
    ds = dataset_id or _ACTIVE_DATASET
    cache_key = f"clean_hourly::{ds}"
    if cache_key not in _MEM_CACHE:
        raw = hourly(ds).copy()
        for col, (lo, hi) in RANGES.items():
            if col in raw.columns:
                raw[col] = raw[col].where((raw[col] >= lo) & (raw[col] <= hi), np.nan).ffill().bfill()
        raw["dP"] = raw["dPu"] + raw["dPl"]
        _MEM_CACHE[cache_key] = raw
    return _MEM_CACHE[cache_key]


def silicon(dataset_id: Optional[str] = None) -> pd.DataFrame:
    ds = dataset_id or _ACTIVE_DATASET
    if ds == "evraz-zsmk-bf":
        return _load_evraz_silicon()
    frame = hourly(ds)
    if "Si" in frame.columns:
        return frame[["dt", "Si"]].dropna().reset_index(drop=True)
    return _load_evraz_silicon()


def labeled_regimes() -> list[dict[str, Any]]:
    """Load the 8 named furnace operating states from the second EVRAZ workbook."""
    if "labeled_regimes" in _MEM_CACHE:
        return _MEM_CACHE["labeled_regimes"]
    path = PUBLIC / LABELED_NAME
    if not path.exists():
        return []
    df = pd.read_excel(path, sheet_name="data")
    df["dt"] = pd.to_datetime(df["dt"])
    state_col = "State of blast furnace"
    if state_col not in df.columns:
        return []
    out: list[dict[str, Any]] = []
    for state_name, group in df.groupby(state_col, sort=False):
        row = group.iloc[len(group) // 2]
        probes = [float(min(1100, max(0, row[f"Tp{i}"]))) for i in range(1, 11)]
        tops = [float(min(1100, max(0, row[f"Tt{i}"]))) for i in range(1, 5)]
        out.append(
            {
                "state": str(state_name),
                "count": int(len(group)),
                "t": pd.Timestamp(row["dt"]).isoformat(sep=" "),
                "Fb": float(row["Fb"]),
                "Th": float(min(1800, max(0, row["Th"]))),
                "Fo": float(row["Fo"]),
                "Pt": float(row["Pt"]),
                "R": float(row["R"]),
                "dP": float(row["dP"]),
                "dPu": float(row["dPu"]),
                "dPl": float(row["dPl"]),
                "CO2": float(row["CO2"]),
                "H2": float(row["H2"]),
                "tp_spread": round(max(probes) - min(probes), 1),
                "tt_mean": round(float(np.mean(tops)), 1),
            }
        )
    _MEM_CACHE["labeled_regimes"] = out
    return out


def parameter_catalog(dataset_id: Optional[str] = None) -> list[dict[str, Any]]:
    ds = dataset_id or _ACTIVE_DATASET
    frame = hourly(ds)
    catalog = [dict(item) for item in PARAMETER_CATALOG]
    seen = {item["tag"] for item in catalog}
    for ext_col, meta in EXTENDED_CATALOG.items():
        if ext_col in frame.columns and ext_col not in seen:
            catalog.append(dict(meta))
            seen.add(ext_col)
    return catalog


def quality_report(frame: Optional[pd.DataFrame] = None) -> dict:
    frame = hourly() if frame is None else frame
    rows = []
    for name, (low, high) in RANGES.items():
        series = frame[name]
        bad = (series < low) | (series > high)
        rows.append(
            {
                "tag": name,
                "low": low,
                "high": high,
                "violations": int(bad.sum()),
                "fraction": float(bad.mean()),
                "min": float(series.min()),
                "max": float(series.max()),
            }
        )
    residual = (frame["dPu"] + frame["dPl"] - frame["dP"]).abs()
    return {
        "rows": int(len(frame)),
        "violations": rows,
        "pressure_identity_median_abs": float(residual.median()),
        "pressure_identity_p95_abs": float(residual.quantile(0.95)),
    }


def capability(dataset_id: Optional[str] = None) -> list[dict]:
    ds = dataset_id or _ACTIVE_DATASET
    frame = hourly(ds)
    has_prod = "Production" in frame.columns
    has_co = "CO" in frame.columns
    return [
        {"feature": "hourly_playback", "status": "ready", "detail": f"{len(frame):,} hourly rows"},
        {"feature": "silicon_forecast", "status": "ready", "detail": "cast silicon is present; walk-forward LightGBM active"},
        {"feature": "coupled_simulation", "status": "ready", "detail": "multi-horizon (1h–8h) coupled parameter response learned from data"},
        {"feature": "pressure_identity", "status": "ready", "detail": "dPu + dPl compared with dP"},
        {"feature": "circumferential_gas", "status": "ready", "detail": "ten peripheral temperatures, angles unknown"},
        {
            "feature": "gas_utilisation",
            "status": "ready" if has_co else "not_run",
            "detail": "etaCO computed from CO and CO2" if has_co else "CO is absent; CO2 alone cannot form etaCO",
        },
        {
            "feature": "verified_shortfall",
            "status": "ready" if has_prod else "not_testable",
            "detail": "production series present in active dataset" if has_prod else "no hot-metal tonne series",
        },
        {"feature": "heat_loss", "status": "not_run", "detail": "cooling-water flow and temperature rise are absent"},
        {"feature": "alkali_ledger", "status": "not_testable", "detail": "alkali analyses are absent"},
        {"feature": "hearth_level", "status": "not_estimable", "detail": "cast weights and hearth geometry are absent"},
        {"feature": "inverse_setpoint", "status": "not_identified", "detail": "blast-silicon level correlation is not an identified effect"},
    ]


def slice_series(tag: str, start: Optional[str], end: Optional[str], limit: int = 500) -> dict:
    frame_h = hourly()
    if tag not in TAGS and tag != "Si" and tag not in frame_h.columns:
        raise KeyError(tag)
    if tag == "Si":
        frame = silicon()
        column = "Si"
        evidence = "measured"
    else:
        frame = frame_h
        column = tag
        evidence = EVIDENCE.get(tag, "measured")
    if start:
        frame = frame[frame["dt"] >= pd.Timestamp(start)]
    if end:
        frame = frame[frame["dt"] <= pd.Timestamp(end)]
    frame = frame.tail(limit)
    points = []
    for event_time, value in zip(frame["dt"], frame[column]):
        stamp = pd.Timestamp(event_time)
        points.append({"t": stamp.isoformat(sep=" "), "v": None if pd.isna(value) else float(value)})
    return {
        "tag": tag,
        "evidence": evidence,
        "timezone": "unconfirmed",
        "points": points,
    }


def playback(stride: int = 6, dataset_id: Optional[str] = None) -> dict:
    """Downsampled hours for interactive scrubbing. Silicon is the latest cast at or before each hour."""
    ds = dataset_id or _ACTIVE_DATASET
    stride = max(1, min(int(stride), 48))
    cache_key = f"playback::{ds}::{stride}"
    if cache_key in _MEM_CACHE:
        return _MEM_CACHE[cache_key]

    hours = clean_hourly(ds).iloc[::stride].reset_index(drop=True)
    casts = silicon(ds).rename(columns={"Si": "Si_cast"})
    if "Si_cast" in hours.columns:
        hours = hours.drop(columns=["Si_cast"])
    merged = pd.merge_asof(
        hours.sort_values("dt"),
        casts[["dt", "Si_cast"]].sort_values("dt"),
        on="dt",
        direction="backward",
    )
    probes = [f"Tp{i}" for i in range(1, 11)]
    ext_cols = [c for c in EXTENDED_CATALOG if c in merged.columns]
    # Blast reference for the campaign, so each frame can declare whether the hour is a
    # qualified operating point. The UI opens on a qualified hour instead of an arbitrary index.
    from bf_twin.simulator import REGIME_ON_WIND_FRAC, REGIME_REDUCED_FRAC, blast_reference

    fb_reference = blast_reference(clean_hourly(ds))
    frames = []
    for row in merged.itertuples(index=False):
        fb_frac = float(row.Fb) / max(1e-6, fb_reference)
        item: dict[str, Any] = {
            "t": pd.Timestamp(row.dt).isoformat(sep=" "),
            "regime": (
                "on_wind"
                if fb_frac >= REGIME_ON_WIND_FRAC
                else "reduced_blast"
                if fb_frac >= REGIME_REDUCED_FRAC
                else "off_wind"
            ),
            "qualified": bool(fb_frac >= REGIME_ON_WIND_FRAC),
            "Fb": float(row.Fb),
            "Fo": float(row.Fo),
            "Ph": float(row.Ph),
            "Pc": float(row.Pc),
            "Tc": float(row.Tc),
            "Pt": float(row.Pt),
            "Th": float(row.Th),
            "dP": float(row.dP),
            "CO2": float(row.CO2),
            "H2": float(row.H2),
            "R": float(row.R),
            "Si": None if pd.isna(row.Si_cast) else float(row.Si_cast),
            "dPu": float(row.dPu),
            "dPl": float(row.dPl),
            "tt": [float(min(1100, max(0, getattr(row, f"Tt{i}")))) for i in range(1, 5)],
            "tp": [float(min(1100, max(0, getattr(row, name)))) for name in probes],
        }
        for ext_col in ext_cols:
            val = getattr(row, ext_col, None)
            item[ext_col] = None if val is None or pd.isna(val) else float(val)
        frames.append(item)

    ds_info = next((d for d in list_datasets() if d["id"] == ds), list_datasets()[0])
    result = {
        "dataset_id": ds,
        "dataset_name": ds_info["name"],
        "origin": ds_info["origin"],
        "has_production": ds_info.get("has_production", False),
        "has_co": ds_info.get("has_co", False),
        "stride_hours": stride,
        "count": len(frames),
        "clock": "2013-2016 public reference, not live" if ds == "evraz-zsmk-bf" else f"{ds_info['origin']} replay, not live",
        "catalog": parameter_catalog(ds),
        "regimes": labeled_regimes() if ds == "evraz-zsmk-bf" else [],
        "frames": frames,
    }
    _MEM_CACHE[cache_key] = result
    return result


WINDOW_HOURS = {"1h": 1, "6h": 6, "24h": 24, "7d": 168, "30d": 720}


def parameter_window_stats(window: str = "24h", t: Optional[str] = None, dataset_id: Optional[str] = None) -> dict[str, Any]:
    """Prometheus-style range stats. The archive step is one hour, so a minute window does not exist."""
    key = window if window in WINDOW_HOURS else "24h"
    hours = WINDOW_HOURS[key]
    frame = clean_hourly(dataset_id)
    end = pd.Timestamp(t) if t else pd.Timestamp(frame["dt"].max())
    start = end - pd.Timedelta(hours=max(0, hours - 1))
    sl = frame[(frame["dt"] >= start) & (frame["dt"] <= end)]
    if sl.empty:
        sl = frame.tail(hours)
    catalog = {item["tag"]: item for item in PARAMETER_CATALOG}
    parameters = []
    for col in [c for c in sl.columns if c != "dt"]:
        numeric = pd.to_numeric(sl[col], errors="coerce")
        clean = numeric.dropna()
        if clean.empty:
            continue
        step = max(1, len(numeric) // 24)
        spark = [None if pd.isna(v) else round(float(v), 3) for v in numeric.iloc[::step].tail(24)]
        last = float(clean.iloc[-1])
        first = float(clean.iloc[0])
        meta = catalog.get(col, {})
        parameters.append(
            {
                "tag": col,
                "label": meta.get("label", col),
                "unit": meta.get("unit", ""),
                "role": meta.get("role", "state_response"),
                "samples": int(clean.shape[0]),
                "last": round(last, 3),
                "min": round(float(clean.min()), 3),
                "max": round(float(clean.max()), 3),
                "avg": round(float(clean.mean()), 3),
                "stddev": round(float(clean.std(ddof=0) or 0.0), 3),
                "delta": round(last - first, 3),
                "spark": spark,
            }
        )
    meta = active_dataset_meta()
    return {
        "dataset_id": meta.get("id"),
        "dataset_name": meta.get("name"),
        "origin": meta.get("origin"),
        "window": key,
        "window_hours": hours,
        "sampling_interval": "1h",
        "minute_stats": "unavailable",
        "minute_note": "This archive is one row per hour. Minute min, max, and standard deviation are below the sampling interval.",
        "from": str(sl["dt"].iloc[0]),
        "to": str(sl["dt"].iloc[-1]),
        "rows": int(len(sl)),
        "parameters": parameters,
    }


def write_card(card: dict, dataset_id: Optional[str] = None) -> None:
    ds = dataset_id or _ACTIVE_DATASET
    CACHE.mkdir(parents=True, exist_ok=True)
    suffix = "" if ds == "evraz-zsmk-bf" else f"_{ds}"
    (CACHE / f"model_card{suffix}.json").write_text(json.dumps(card, indent=2))


def read_card(dataset_id: Optional[str] = None) -> Optional[dict]:
    ds = dataset_id or _ACTIVE_DATASET
    suffix = "" if ds == "evraz-zsmk-bf" else f"_{ds}"
    path = CACHE / f"model_card{suffix}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())
