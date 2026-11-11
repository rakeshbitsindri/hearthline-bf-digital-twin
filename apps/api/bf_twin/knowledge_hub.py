"""Built-in Domain Knowledge Hub, Running-Plant EVRAZ Industrial Data Profile, & Exceptions Register."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from bf_twin.store import (
    PARAMETER_CATALOG,
    PUBLIC,
    RANGES,
    ROOT,
    active_dataset_id,
    clean_hourly,
    hourly,
    labeled_regimes,
    list_datasets,
    quality_report,
    silicon,
)

KNOWLEDGE_DIR = ROOT / "knowledge"

CHAPTER_CATEGORY = {
    "README": "Overview & Evidence Grades",
    "01-parameter-catalog": "Sensors & Metallurgy",
    "02-derived-indices": "Physics & Balances",
    "03-physics-equations": "Physics & Balances",
    "04-hidden-state-mechanisms": "Shortfall Mystery & Failure Modes",
    "05-failure-mode-catalog": "Shortfall Mystery & Failure Modes",
    "06-plant-case-studies": "Global Plant Benchmarks",
    "07-ml-literature": "Machine Learning & Causality",
    "08-lag-reference": "Machine Learning & Causality",
    "09-confounding-and-causality": "Machine Learning & Causality",
    "10-datasets-and-benchmarks": "Industrial Datasets & Provenance",
    "11-pending-validation": "Governance & Pending Validation",
    "12-references": "Overview & Evidence Grades",
    "13-parameter-tiers": "Governance & Pending Validation",
    "14-dynamic-twin-model": "Physics & Balances",
    "15-data-time-and-provenance": "Industrial Datasets & Provenance",
    "16-twin-commissioning-and-acceptance": "Governance & Pending Validation",
}

EXCEPTIONS_AND_BOUNDARIES = [
    {
        "id": "EX-01",
        "category": "TRL 7-9 Physical Plant Boundary",
        "severity": "blocking_for_trl7_claim",
        "title": "No live socket to an operating blast furnace OT historian",
        "status": "software_harness_ready_awaiting_plant",
        "detail": (
            "TRL 6 is demonstrated on the 29,602-hour EVRAZ ZSMK industrial blast furnace dataset. "
            "True TRL 7-9 certification requires a signed plant data agreement, an industrial DMZ read-replica "
            "(OSIsoft PI Web API or OPC-UA), and a 12-to-24-week shadow-mode campaign on an active furnace."
        ),
        "unblock_requirement": "Plant DMZ read-only endpoint (BF_PI_BASE_URL or BF_OPCUA_ENDPOINT) + shadow-mode trial.",
    },
    {
        "id": "EX-02",
        "category": "Public Industrial Dataset Scope (EVRAZ ZSMK 2013-2016)",
        "severity": "data_scope_limitation",
        "title": "Missing cast tonnage, PCI, separate coke rate, top-gas CO, and HMT in EVRAZ file",
        "status": "enforced_by_capability_matrix",
        "detail": (
            "The public EVRAZ ZSMK sensor series provides 28 real furnace tags + 16,589 cast silicon lab analyses, "
            "but omits hot-metal tonnes, pulverised coal injection (PCI), charged coke rate, top-gas CO, cooling-stave "
            "heat loss, and hot-metal temperature. Verified shortfall (Gate 0), gas utilisation etaCO, and absolute "
            "RAFT/HMT are therefore withheld or marked assumption-dependent on EVRAZ, and unlock automatically when a "
            "full-sensor plant file is selected."
        ),
        "unblock_requirement": "Provide cast-weight / torpedo-car tonnage, PCI, coke rate, CO, and HMT columns (see DATA_REQUEST.md).",
    },
    {
        "id": "EX-03",
        "category": "Sampling Resolution Blindness",
        "severity": "observability_limit",
        "title": "1-hour averaging hides sub-hour slips, hangs, tuyere spikes, and channeling precursors",
        "status": "flagged_in_ui_and_connector",
        "detail": (
            "Rapid burden slips, hangs, check-valve pressure spikes, and water-leak excursions occur on 10-second to "
            "5-minute timescales. Until minute-level historian archives or within-hour __std/__min/__max/__exc "
            "companions are ingested, sub-hour transient phenomena remain below the sampling interval."
        ),
        "unblock_requirement": "Enable 1-minute historian pull or within-hour __std/__min/__max/__exc companions.",
    },
    {
        "id": "EX-04",
        "category": "Causal Identifiability under Closed-Loop Operator Control",
        "severity": "causal_guardrail",
        "title": "Observational blast-to-silicon level correlation is confounded by operator control policy",
        "status": "blocked_by_identifiability_audit",
        "detail": (
            "Operators adjust blast, moisture, and fuel in response to unlogged furnace observations. "
            "In EVRAZ ZSMK, 4-hour change correlations between blast and next-cast silicon are -0.05 to +0.03. "
            "Routine autonomous setpoints are therefore not claimed as causal guarantees; recommendations are "
            "framed as constrained envelope associations requiring operator review."
        ),
        "unblock_requirement": "Raw-material disturbance logs (CSR, RDI, moisture) + plant-approved management-of-change dither trials.",
    },
    {
        "id": "EX-05",
        "category": "Pending Metallurgical Coefficients (PV-01 to PV-10)",
        "severity": "pending_metallurgist_signoff",
        "title": "10 literature equations have plant-specific or OCR-ambiguous coefficients",
        "status": "pending_validation",
        "detail": (
            "Items PV-01 through PV-10 in knowledge/11-pending-validation.md (including Geerdes Annex III thermal "
            "equivalence convention, cohesive-zone shrinkage permeability K(Sr), flooding density correction, Iida "
            "slag viscosity table, and EVRAZ RAFT/HMT intercepts) are never fabricated as measured constants."
        ),
        "unblock_requirement": "Site metallurgist sign-off with furnace-calibrated constants recorded via pv_signoff audit.",
    },
    {
        "id": "EX-06",
        "category": "Enterprise IT / OT Production Infrastructure",
        "severity": "deployment_environment",
        "title": "Public showcase runs open without corporate SAML/OIDC SSO, TLS client certs, or HA Postgres",
        "status": "open_by_design_for_public_demo",
        "detail": (
            "To allow zero-cost frictionless evaluation over the internet, the public showcase defaults to an open "
            "session with role switcher enabled and SQLite storage. A plant installation requires corporate SSO "
            "(OIDC/SAML), industrial DMZ firewalling, secret vaulting, and managed PostgreSQL."
        ),
        "unblock_requirement": "Phase D plant IT/OT deployment checklist in ENTERPRISE_READINESS.md.",
    },
]


def _extract_title_and_headings(md_text: str, fallback: str) -> tuple[str, list[str]]:
    title = fallback
    headings: list[str] = []
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# ") and title == fallback:
            title = s[2:].strip()
        elif s.startswith("## "):
            headings.append(s[3:].strip())
    return title, headings


def _count_evidence_tags(md_text: str) -> dict[str, int]:
    return {
        "peer_reviewed_P": len(re.findall(r"\[P\]", md_text)),
        "company_report_C": len(re.findall(r"\[C\]", md_text)),
        "trade_press_T": len(re.findall(r"\[T\]", md_text)),
        "inference_I": len(re.findall(r"\[I\]", md_text)),
    }


def list_knowledge_articles(query: Optional[str] = None) -> dict[str, Any]:
    """Return all accumulated domain knowledge chapters, plant dataset docs, and key architecture specs."""
    docs: list[dict[str, Any]] = []

    # 1. Core 17 knowledge/*.md chapters
    if KNOWLEDGE_DIR.exists():
        for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
            slug = path.stem
            text = path.read_text(encoding="utf-8", errors="replace")
            title, headings = _extract_title_and_headings(text, slug)
            ev = _count_evidence_tags(text)
            docs.append(
                {
                    "slug": slug,
                    "source_group": "knowledge_base",
                    "category": CHAPTER_CATEGORY.get(slug, "Domain Reference"),
                    "filename": f"knowledge/{path.name}",
                    "title": title,
                    "headings": headings,
                    "word_count": len(text.split()),
                    "evidence_counts": ev,
                    "excerpt": " ".join(
                        [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")][:3]
                    )[:280],
                    "content": text,
                }
            )

    # 2. Running-plant EVRAZ dataset documentation
    for path in sorted(PUBLIC.glob("*.md")):
        slug = f"evraz-{path.stem.lower()}"
        text = path.read_text(encoding="utf-8", errors="replace")
        title, headings = _extract_title_and_headings(text, path.stem)
        docs.append(
            {
                "slug": slug,
                "source_group": "industrial_plant_data",
                "category": "Industrial Datasets & Provenance",
                "filename": f"data/public/evraz-zsmk-2013-2016/{path.name}",
                "title": f"EVRAZ ZSMK Plant Data: {title}",
                "headings": headings,
                "word_count": len(text.split()),
                "evidence_counts": _count_evidence_tags(text),
                "excerpt": " ".join(
                    [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")][:3]
                )[:280],
                "content": text,
            }
        )

    # 3. Key architecture, readiness, and data-request specifications
    spec_files = [
        "PATENTABILITY_AND_DISCLOSURE.md",
        "CLAUDE.md",
        "ENTERPRISE_READINESS.md",
        "DATA_REQUEST.md",
        "PHYSICS_MODEL_DESIGN.md",
        "OBSERVABILITY_DESIGN.md",
        "ML_ARCHITECTURE.md",
        "OPTIMIZATION_DESIGN.md",
        "CONNECTOR_DESIGN.md",
        "COMMISSIONING_PLAN.md",
        "RISK_REGISTER.md",
    ]
    for fname in spec_files:
        p = ROOT / fname
        if not p.exists():
            continue
        slug = f"spec-{p.stem.lower()}"
        text = p.read_text(encoding="utf-8", errors="replace")
        title, headings = _extract_title_and_headings(text, p.stem)
        docs.append(
            {
                "slug": slug,
                "source_group": "architecture_spec",
                "category": "Architecture & Enterprise Readiness",
                "filename": fname,
                "title": title,
                "headings": headings,
                "word_count": len(text.split()),
                "evidence_counts": _count_evidence_tags(text),
                "excerpt": " ".join(
                    [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")][:3]
                )[:280],
                "content": text,
            }
        )

    if query and query.strip():
        q = query.strip().lower()
        docs = [
            d
            for d in docs
            if q in d["title"].lower() or q in d["content"].lower() or q in d["category"].lower()
        ]

    total_words = sum(d["word_count"] for d in docs)
    total_citations = sum(sum(d["evidence_counts"].values()) for d in docs)

    return {
        "total_documents": len(docs),
        "total_words": total_words,
        "total_evidence_tags": total_citations,
        "categories": sorted({d["category"] for d in docs}),
        "exceptions": EXCEPTIONS_AND_BOUNDARIES,
        "documents": docs,
    }


def industrial_plant_data_summary(sample_limit: int = 24) -> dict[str, Any]:
    """
    Comprehensive statistical & engineering profile of the running-plant EVRAZ ZSMK (2013-2016)
    blast furnace sensor dataset and the currently active dataset.
    """
    evraz_raw = hourly("evraz-zsmk-bf")
    evraz_clean = clean_hourly("evraz-zsmk-bf")
    evraz_si = silicon("evraz-zsmk-bf")
    qual = quality_report(evraz_raw)
    regimes = labeled_regimes()

    on_wind_mask = evraz_raw["Fb"] > 1000.0
    zero_wind_hours = int((evraz_raw["Fb"] == 0).sum())

    cat_map = {item["tag"]: item for item in PARAMETER_CATALOG}
    viol_map = {v["tag"]: v for v in qual["violations"]}

    tag_profiles = []
    for col in [c for c in evraz_raw.columns if c != "dt"]:
        s_raw = pd.to_numeric(evraz_raw[col], errors="coerce").dropna()
        s_clean = pd.to_numeric(evraz_clean[col], errors="coerce").dropna()
        meta = cat_map.get(col, {})
        v_info = viol_map.get(col, {})
        tag_profiles.append(
            {
                "tag": col,
                "label": meta.get("label", col),
                "unit": meta.get("unit", ""),
                "role": meta.get("role", "state_response"),
                "zone": meta.get("zone", "shaft"),
                "count": int(len(s_raw)),
                "raw_min": round(float(s_raw.min()), 3),
                "p05": round(float(s_clean.quantile(0.05)), 3),
                "median": round(float(s_clean.median()), 3),
                "mean": round(float(s_clean.mean()), 3),
                "p95": round(float(s_clean.quantile(0.95)), 3),
                "raw_max": round(float(s_raw.max()), 3),
                "instrument_span": list(RANGES[col]) if col in RANGES else None,
                "span_violations": int(v_info.get("violations", 0)),
                "violation_pct": round(100.0 * float(v_info.get("fraction", 0.0)), 2),
            }
        )

    # Add cast silicon chemical lab profile
    si_vals = pd.to_numeric(evraz_si["Si"], errors="coerce").dropna()
    si_lag1 = float(si_vals.autocorr(lag=1)) if len(si_vals) > 10 else 0.74
    n_eff_si = int(len(si_vals) * (1.0 - si_lag1) / max(1e-6, 1.0 + si_lag1))
    persist_rmse = float(np.sqrt(np.mean(np.square(np.diff(si_vals.to_numpy()))))) if len(si_vals) > 2 else 0.12
    tag_profiles.append(
        {
            "tag": "Si",
            "label": "Cast Hot-Metal Silicon (Lab)",
            "unit": "wt%",
            "role": "outcome",
            "zone": "hearth",
            "count": int(len(si_vals)),
            "raw_min": round(float(si_vals.min()), 3),
            "p05": round(float(si_vals.quantile(0.05)), 3),
            "median": round(float(si_vals.median()), 3),
            "mean": round(float(si_vals.mean()), 3),
            "p95": round(float(si_vals.quantile(0.95)), 3),
            "raw_max": round(float(si_vals.max()), 3),
            "instrument_span": [0.05, 3.5],
            "span_violations": int(((si_vals < 0.05) | (si_vals > 3.5)).sum()),
            "violation_pct": round(100.0 * float(((si_vals < 0.05) | (si_vals > 3.5)).mean()), 2),
        }
    )

    # Circumferential peripheral temperature asymmetry (Tp1..Tp10) on on-wind hours
    on_clean = evraz_clean[evraz_clean["Fb"] > 1000.0]
    tp_cols = [f"Tp{i}" for i in range(1, 11)]
    stave_profile = []
    for col in tp_cols:
        s = on_clean[col]
        stave_profile.append(
            {
                "tag": col,
                "p10": round(float(s.quantile(0.10)), 1),
                "median": round(float(s.median()), 1),
                "p90": round(float(s.quantile(0.90)), 1),
            }
        )
    tp_matrix = on_clean[tp_cols].to_numpy(dtype=float)
    tp_ranges = np.max(tp_matrix, axis=1) - np.min(tp_matrix, axis=1)

    # Sample recent on-wind records merged with latest cast Si for live inspection
    sample_limit = max(5, min(int(sample_limit), 100))
    merged_sample = pd.merge_asof(
        on_clean.iloc[::250].head(sample_limit).sort_values("dt"),
        evraz_si.sort_values("dt"),
        on="dt",
        direction="backward",
    )
    sample_rows = []
    keep_cols = ["Fb", "Fo", "Th", "Pt", "Ph", "dPu", "dPl", "dP", "CO2", "H2", "R", "Tt1", "Tp4", "Tp9", "Si"]
    for _, r in merged_sample.iterrows():
        rec: dict[str, Any] = {"dt": pd.Timestamp(r["dt"]).isoformat(sep=" ")}
        for c in keep_cols:
            if c in r and pd.notna(r[c]):
                rec[c] = round(float(r[c]), 3 if c in ("Si", "dPu", "dPl", "dP", "Pt", "Ph", "R") else 1)
        sample_rows.append(rec)

    return {
        "plant_reference": {
            "id": "evraz-zsmk-bf",
            "plant": "EVRAZ ZSMK (West Siberian Metallurgical Combine, Novokuznetsk)",
            "evidence_class": "public_reference (measured running-plant sensors, not this customer's furnace, not live)",
            "citation": "Trofimov, V. B. Data collected by blast-furnace sensors. Data in Brief 63 (2025) 112159. DOI: 10.1016/j.dib.2025.112159",
            "mendeley_doi": "10.17632/6d7jbc7tb5.1",
            "licence": "CC BY 4.0",
            "campaign_start": pd.Timestamp(evraz_raw["dt"].iloc[0]).isoformat(sep=" "),
            "campaign_end": pd.Timestamp(evraz_raw["dt"].iloc[-1]).isoformat(sep=" "),
            "hourly_rows": int(len(evraz_raw)),
            "on_wind_hours": int(on_wind_mask.sum()),
            "on_wind_pct": round(100.0 * float(on_wind_mask.mean()), 2),
            "low_blast_hours": int((~on_wind_mask).sum()),
            "zero_blast_hours": zero_wind_hours,
            "cast_silicon_analyses": int(len(evraz_si)),
            "silicon_persistence_rmse_wt_pct": round(persist_rmse, 4),
            "silicon_lag1_autocorr": round(si_lag1, 3),
            "effective_independent_blocks": n_eff_si,
            "assumed_working_volume_m3": 2000.0,
            "assumed_nameplate_t_d": 4500.0,
            "pressure_identity_median_residual": round(float(qual["pressure_identity_median_abs"]), 6),
            "pressure_identity_p95_residual": round(float(qual["pressure_identity_p95_abs"]), 4),
            "circumferential_tp_median_spread_c": round(float(np.median(tp_ranges)), 1),
            "circumferential_tp_gt150c_pct": round(100.0 * float(np.mean(tp_ranges > 150.0)), 1),
        },
        "active_dataset_id": active_dataset_id(),
        "registered_datasets": list_datasets(),
        "tag_profiles": tag_profiles,
        "stave_azimuthal_profile": stave_profile,
        "labeled_furnace_regimes": regimes,
        "sample_plant_records": sample_rows,
        "exceptions": EXCEPTIONS_AND_BOUNDARIES,
    }


def export_plant_slice_csv(limit: int = 500) -> str:
    """Export a clean CSV extract of the running-plant EVRAZ ZSMK dataset for external engineering verification."""
    limit = max(50, min(int(limit), 5000))
    h = hourly("evraz-zsmk-bf").tail(limit).copy()
    casts = silicon("evraz-zsmk-bf")
    merged = pd.merge_asof(h.sort_values("dt"), casts.sort_values("dt"), on="dt", direction="backward")
    return merged.to_csv(index=False)
