"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import { API, useTwinTheme } from "../components/Frame";
import { ParameterStats } from "../components/ParameterStats";

const TwinCanvas = dynamic(() => import("../components/TwinCanvas"), { ssr: false });

function furnaceClass(demand) {
  const bands = [
    [2500, "Small"],
    [5500, "Medium"],
    [8000, "Large"],
    [12000, "Very large"],
    [1e9, "Super-large"],
  ];
  let name = "Medium";
  for (const [hi, label] of bands) {
    if (Number(demand) < hi) {
      name = label;
      break;
    }
  }
  const volume = name === "Medium" ? 2000 : Math.min(5800, Math.max(350, Number(demand) / 2.2));
  return { name, volume: Math.round(volume) };
}

const KNOB_DEFS = [
  { tag: "Fb", label: "Blast Flow (Fb)", unit: "m³/min", group: "blast", minDelta: -800, maxDelta: 800, step: 10, tau: "1.0h" },
  { tag: "Th", label: "Hot Blast Temp (Th)", unit: "°C", group: "blast", minDelta: -150, maxDelta: 150, step: 5, tau: "1.5h" },
  { tag: "Fo", label: "Oxygen Flow (Fo)", unit: "m³/h", group: "blast", minDelta: -8000, maxDelta: 8000, step: 250, tau: "1.0h" },
  { tag: "BlastMoisture", label: "Blast Moisture", unit: "g/Nm³", group: "blast", minDelta: -12, maxDelta: 18, step: 0.5, tau: "0.8h" },
  { tag: "Pt", label: "Top Pressure (Pt)", unit: "kgf/cm²", group: "blast", minDelta: -0.35, maxDelta: 0.35, step: 0.01, tau: "0.6h" },
  { tag: "R", label: "Ore / Coke Ratio (R)", unit: "t/t", group: "burden", minDelta: -0.7, maxDelta: 0.7, step: 0.02, tau: "6.0h" },
  { tag: "PCI", label: "PCI Coal Injection", unit: "kg/tHM", group: "burden", minDelta: -60, maxDelta: 75, step: 2, tau: "2.5h" },
  { tag: "CokeRate", label: "Charged Coke Rate", unit: "kg/tHM", group: "burden", minDelta: -70, maxDelta: 70, step: 2, tau: "6.5h" },
  { tag: "BurdenFe", label: "Burden Fe Grade", unit: "wt%", group: "burden", minDelta: -3.5, maxDelta: 3.5, step: 0.2, tau: "6.0h" },
  { tag: "CokeCSR", label: "Coke CSR Strength", unit: "%", group: "cond", minDelta: -8, maxDelta: 8, step: 0.5, tau: "7.0h" },
  { tag: "SinterRDI", label: "Sinter RDI Fines", unit: "%", group: "cond", minDelta: -8, maxDelta: 10, step: 0.5, tau: "4.5h" },
  { tag: "AlkaliInput", label: "Alkali Load (K₂O+Na₂O)", unit: "kg/tHM", group: "cond", minDelta: -1.5, maxDelta: 2.5, step: 0.1, tau: "12.0h" },
  { tag: "ZnInput", label: "Zinc Load (Zn)", unit: "g/tHM", group: "cond", minDelta: -70, maxDelta: 160, step: 5, tau: "12.0h" },
];

const ZERO_DELTAS = Object.fromEntries(KNOB_DEFS.map((k) => [k.tag, 0]));

// Fast-triage furnace zones. Each groups the sensors an operator scans together when a
// production issue shows up, so anomalies can be located by region in one glance.
const FURNACE_ZONES = [
  { id: "blast", name: "Blast & Tuyeres", tags: ["Fb", "Th", "Fo", "BlastMoisture", "Pt", "RAFT", "O2TotalPct"] },
  { id: "top", name: "Top & Offtake Gas", tags: ["Tt1", "Tt2", "Tt3", "Tt4", "CO2", "H2"] },
  { id: "walls", name: "Shaft Wall Staves", tags: ["Tp1", "Tp2", "Tp3", "Tp4", "Tp5", "Tp6", "Tp7", "Tp8", "Tp9", "Tp10"] },
  { id: "perm", name: "Pressure / Permeability", tags: ["dPu", "dPl", "dP", "Ph", "Pc"] },
  { id: "cohesive", name: "Cohesive & Condensation", tags: ["CZHeight", "CondensationIdx", "SinterRDI", "CokeCSR", "AlkaliInput", "ZnInput"] },
  { id: "hearth", name: "Hearth & Product", tags: ["Si", "HMT", "Production", "R", "BurdenFe", "CokeRate", "PCI"] },
];

// Evidence class is shown on the value, not only in a side panel, per the project's provenance rule.
const EVIDENCE_LABEL = {
  reconciled: "meas",
  simulated: "sim",
  assumed: "assum",
  unavailable: "n/a",
};

const GOLDEN_STATUS_LABEL = {
  in_golden: "IN GOLDEN",
  below_golden: "BELOW GOLDEN",
  above_golden: "ABOVE GOLDEN",
};

function evidenceHint(tag, st) {
  if (!st) return tag;
  if (st.status === "measured_anchored") return `${tag}: reconciled onto this furnace's sensor.`;
  if (st.status === "physics_estimated") return `${tag}: computed from measured inputs only.`;
  const assumed = (st.assumed_inputs || []).join(", ");
  if (st.status === "not_qualified") {
    return `${tag}: the furnace is not in a qualified operating regime this hour, so no absolute value is served.`;
  }
  if (st.status === "response_only") {
    return `${tag}: no sensor in this dataset and outside the validated band ${st.band[0]} to ${st.band[1]}. Rests on assumed ${assumed}. Only its response to a change is usable.`;
  }
  return `${tag}: no sensor in this dataset. Rests on assumed ${assumed}.`;
}

function GoldenRangeBar({ min, max, goldenLow, goldenHigh, baseline, simulated, status }) {
  if (goldenLow == null || goldenHigh == null) return null;
  const loBound = Math.min(Number(min ?? goldenLow * 0.7), Number(goldenLow), Number(baseline ?? goldenLow), Number(simulated ?? goldenLow));
  const hiBound = Math.max(Number(max ?? goldenHigh * 1.3), Number(goldenHigh), Number(baseline ?? goldenHigh), Number(simulated ?? goldenHigh));
  const span = Math.max(1e-6, hiBound - loBound);
  const gLeft = Math.max(0, Math.min(100, ((Number(goldenLow) - loBound) / span) * 100));
  const gRight = Math.max(gLeft + 2, Math.min(100, ((Number(goldenHigh) - loBound) / span) * 100));
  const basePct = Math.max(1, Math.min(99, ((Number(baseline ?? goldenLow) - loBound) / span) * 100));
  const simPct = Math.max(1, Math.min(99, ((Number(simulated ?? goldenLow) - loBound) / span) * 100));

  return (
    <div className="golden-track" title={`Golden Range ${goldenLow} to ${goldenHigh} | Baseline ${baseline} | Simulated ${simulated}`}>
      <div
        className="golden-zone-band"
        style={{ left: `${gLeft.toFixed(1)}%`, width: `${Math.max(3, gRight - gLeft).toFixed(1)}%` }}
      />
      <div className="golden-base-tick" style={{ left: `${basePct.toFixed(1)}%` }} title={`Historical Baseline ${baseline}`} />
      <div
        className={`golden-sim-dot golden-dot-${status || "in_golden"}`}
        style={{ left: `${simPct.toFixed(1)}%` }}
        title={`Current / Simulated ${simulated}`}
      />
    </div>
  );
}

function Sparkline24h({ trajectory, field, label, unit, goldenLow, goldenHigh, color }) {
  if (!trajectory || trajectory.length < 2) return null;
  const vals = trajectory.map((pt) => Number(pt[field] ?? 0));
  const allBounds = [...vals];
  if (goldenLow != null && goldenHigh != null) {
    allBounds.push(Number(goldenLow), Number(goldenHigh));
  }
  const min = Math.min(...allBounds);
  const max = Math.max(...allBounds);
  const span = Math.max(1e-4, max - min);
  const w = 220;
  const h = 46;
  const points = vals
    .map((v, i) => {
      const x = (i / (vals.length - 1)) * (w - 12) + 6;
      const y = h - 6 - ((v - min) / span) * (h - 14);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const delta = vals[vals.length - 1] - vals[0];
  const gTopY = goldenHigh != null ? h - 6 - ((Number(goldenHigh) - min) / span) * (h - 14) : null;
  const gBotY = goldenLow != null ? h - 6 - ((Number(goldenLow) - min) / span) * (h - 14) : null;
  const stroke = color || "var(--heat)";

  return (
    <div className="spark-card">
      <div className="spark-head">
        <span>{label}</span>
        <b>
          {vals[vals.length - 1].toFixed(Math.abs(vals[0]) < 5 ? 3 : 1)} {unit}
          {Math.abs(delta) > 1e-4 && (
            <em className={delta >= 0 ? "up" : "down"}>
              {" "}
              ({delta >= 0 ? "+" : ""}
              {delta.toFixed(Math.abs(vals[0]) < 5 ? 3 : 1)})
            </em>
          )}
        </b>
      </div>
      <svg viewBox={`0 0 ${w} ${h}`} className="spark-svg">
        {gTopY != null && gBotY != null && (
          <rect
            x="4"
            y={Math.min(gTopY, gBotY)}
            width={w - 8}
            height={Math.max(2, Math.abs(gBotY - gTopY))}
            fill="rgba(16, 185, 129, 0.16)"
          />
        )}
        <polyline fill="none" stroke={stroke} strokeWidth="2" points={points} />
      </svg>
    </div>
  );
}

function RunTrace({ points }) {
  const recorded = points.map((p) => Number(p.recorded)).filter((v) => Number.isFinite(v));
  const held = points.map((p) => Number(p.held)).filter((v) => Number.isFinite(v));
  const all = [...recorded, ...held];
  if (all.length < 2) return null;
  const min = Math.min(...all);
  const max = Math.max(...all);
  const span = max - min || 1;
  const path = (key) => points.map((p, i) => {
    const v = Number(p[key]);
    if (!Number.isFinite(v)) return null;
    const x = (i / Math.max(1, points.length - 1)) * 280;
    const y = 46 - ((v - min) / span) * 40;
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).filter(Boolean).join(" ");
  return (
    <div className="run-trace">
      <svg viewBox="0 0 280 52" aria-label="Production through the run">
        <path d={path("recorded")} className="run-recorded" />
        <path d={path("held")} className="run-held" />
      </svg>
      <span>recorded</span>
      <span>this run</span>
    </div>
  );
}

export default function TwinWorkbench() {
  const { themeMeta } = useTwinTheme();

  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);
  const [frames, setFrames] = useState([]);
  const [index, setIndex] = useState(0);
  const [customTimestamp, setCustomTimestamp] = useState(null);
  const [runMode, setRunMode] = useState(null);
  const [paused, setPaused] = useState(false);
  const [runTrace, setRunTrace] = useState([]);
  const [fineNow, setFineNow] = useState(null);
  const [fineMeta, setFineMeta] = useState(null);
  const [fineLevers, setFineLevers] = useState([]);
  const [recovery, setRecovery] = useState(0);
  const [speed, setSpeed] = useState(4);
  const [open, setOpen] = useState(0.74);
  const [mode, setMode] = useState("hybrid");
  const [knobTab, setKnobTab] = useState("all");
  const [paramFilter, setParamFilter] = useState("all");
  const [selectedTag, setSelectedTag] = useState("Fb");

  const [viewMode, setViewMode] = useState("cockpit");
  const [anomalyPinsOnly, setAnomalyPinsOnly] = useState(false);
  const [sensorQuery, setSensorQuery] = useState("");
  const [sensorSort, setSensorSort] = useState("risk");

  const [requiredProd, setRequiredProd] = useState(4500);
  const [shortfallData, setShortfallData] = useState(null);
  const [shortfallCategory, setShortfallCategory] = useState("all");

  const [deltas, setDeltas] = useState(ZERO_DELTAS);
  const [overrides, setOverrides] = useState({});
  const [switches, setSwitches] = useState({
    switch_dehumidification: false,
    switch_center_coke: true,
    switch_alkali_flush: false,
    show_all_pins: true,
  });

  const [simResult, setSimResult] = useState(null);
  const [sensitivity, setSensitivity] = useState(null);
  const [optTarget, setOptTarget] = useState({ prod: 4500, si: 0.45, maxDp: 1.52 });
  const [optResult, setOptResult] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [error, setError] = useState("");

  function loadAll(stride = 6, targetProd = requiredProd) {
    Promise.all([
      fetch(`${API}/datasets`).then((r) => r.json()),
      fetch(`${API}/playback?stride=${stride}`).then((r) => r.json()),
      fetch(`${API}/sensitivity`).then((r) => r.json()),
      fetch(`${API}/shortfalls?target_production=${targetProd}&limit=16`).then((r) => r.json()),
    ])
      .then(([dsBody, playBody, sensBody, sfBody]) => {
        setDatasets(dsBody.datasets || []);
        setActiveDataset(dsBody.active || null);
        const loaded = playBody.frames || [];
        setFrames(loaded);
        // Open on a steady, qualified on-wind hour with normal blast & oxygen enrichment.
        const start = Math.floor((loaded.length || 1) * 0.46);
        const steady = loaded.findIndex((f, i) => i >= start && f.qualified && f.Fb >= 3400 && (f.Fo == null || f.Fo >= 12000));
        const qualified = steady >= 0 ? steady : loaded.findIndex((f, i) => i >= start && f.qualified);
        setIndex(qualified >= 0 ? qualified : Math.max(0, loaded.findIndex((f) => f.qualified)));
        setCustomTimestamp(null);
        setSensitivity(sensBody);
        setShortfallData(sfBody);
      })
      .catch(() => setError("The twin API is not reachable. Confirm the API server is running."));
  }

  useEffect(() => {
    loadAll(6, requiredProd);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetch(`${API}/shortfalls?target_production=${requiredProd}&limit=16`)
        .then((r) => (r.ok ? r.json() : null))
        .then((body) => {
          if (body) setShortfallData(body);
        })
        .catch(() => {});
    }, 180);
    return () => clearTimeout(timer);
  }, [requiredProd]);

  const simToken = useRef(0);
  const simBusy = useRef(false);

  useEffect(() => {
    if (runMode !== "history" || paused) return undefined;
    if (!frames.length) return undefined;
    const timer = setInterval(() => {
      if (simBusy.current) return;
      setCustomTimestamp(null);
      setIndex((cur) => (cur + 1) % frames.length);
    }, Math.max(1200, 2400 / speed));
    return () => clearInterval(timer);
  }, [runMode, paused, frames.length, speed]);

  useEffect(() => {
    if (paused || (runMode !== "autopilot" && runMode !== "goal")) return undefined;
    let cancel = false;
    const timer = setInterval(() => {
      const steps = runMode === "autopilot" ? 1 : Math.min(60, Math.max(1, speed * 8));
      fetch(`${API}/play/fine/tick`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: runMode, steps, target_production: Number(requiredProd) || 4500 }),
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((body) => {
          if (cancel || !body?.latest) return;
          setFineNow(body.latest);
          setFineMeta(body);
          if (Array.isArray(body.levers)) setFineLevers(body.levers);
          setRunTrace((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.t === body.latest.t) return prev;
            return [...prev, { t: body.latest.t, mode: runMode, recorded: null, held: body.latest.Production }].slice(-60);
          });
        })
        .catch(() => {});
    }, 1000);
    return () => {
      cancel = true;
      clearInterval(timer);
    };
  }, [runMode, paused, speed, requiredProd]);

  useEffect(() => {
    if (!simResult || (runMode !== "history" && runMode !== "goal")) return;
    setRunTrace((prev) => {
      const last = prev[prev.length - 1];
      if (last && last.t === simResult.t && last.mode === runMode) return prev;
      return [...prev, {
        t: simResult.t,
        mode: runMode,
        recorded: simResult.baseline_physics_kpis?.Production,
        held: simResult.physics_kpis?.Production,
      }].slice(-36);
    });
  }, [simResult, runMode]);

  const frame = frames[index];
  const activeTimestamp = customTimestamp || frame?.t;

  useEffect(() => {
    if (!activeTimestamp) return undefined;
    const token = ++simToken.current;
    simBusy.current = true;
    const handle = setTimeout(() => {
      fetch(`${API}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          t: activeTimestamp,
          deltas,
          overrides,
          switches,
          mode,
          horizon_hours: 24,
          target_production: Number(requiredProd) || 4500,
        }),
      })
        .then((r) => {
          if (!r.ok) throw new Error("simulate failed");
          return r.json();
        })
        .then((data) => {
          if (token !== simToken.current) return;
          setError("");
          setSimResult(data);
        })
        .catch(() => {})
        .finally(() => {
          if (token === simToken.current) simBusy.current = false;
        });
    }, 100);
    return () => clearTimeout(handle);
  }, [activeTimestamp, deltas, overrides, switches, mode, requiredProd]);

  async function handleDatasetSwitch(dsId) {
    setRunMode(null);
    await fetch(`${API}/datasets/select`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: dsId }),
    });
    setDeltas(ZERO_DELTAS);
    setOverrides({});
    loadAll(6, requiredProd);
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadStatus(`Uploading and learning from ${file.name}`);
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`${API}/datasets/upload`, { method: "POST", body: fd });
    if (res.ok) {
      const body = await res.json();
      setUploadStatus(`Learned from ${body.dataset.rows.toLocaleString()} rows (${file.name}).`);
      setDeltas(ZERO_DELTAS);
      setOverrides({});
      loadAll(4, requiredProd);
    } else {
      setUploadStatus("Upload failed. Check CSV/XLSX/Parquet columns.");
    }
  }

  async function runTargetOptimizer() {
    if (!activeTimestamp) return;
    try {
      const r = await fetch(`${API}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          t: activeTimestamp,
          target_production: Number(optTarget.prod),
          target_si: Number(optTarget.si),
          max_dp: Number(optTarget.maxDp),
        }),
      });
      if (r.ok) {
        const body = await r.json();
        setOptResult(body);
        setRequiredProd(Number(optTarget.prod));
      }
    } catch {
      // ignore transient error
    }
  }

  function applyOptimizedSetpoints() {
    if (!optResult?.recommended_overrides) return;
    setDeltas(ZERO_DELTAS);
    setOverrides(optResult.recommended_overrides);
  }

  function snapKnobToGolden(tag, goldenCenter) {
    if (goldenCenter == null) return;
    setDeltas((prev) => ({ ...prev, [tag]: 0 }));
    setOverrides((prev) => ({ ...prev, [tag]: Number(goldenCenter) }));
  }

  function applyRecovery(pct) {
    setRecovery(pct);
    if (!simResult?.parameters || pct <= 0) {
      setOverrides({});
      setDeltas(ZERO_DELTAS);
      return;
    }
    const next = {};
    for (const p of simResult.parameters) {
      if (p.role !== "manipulated" || p.golden_center == null || p.baseline == null) continue;
      const target = Number(p.baseline) + (Number(p.golden_center) - Number(p.baseline)) * (pct / 100);
      next[p.tag] = Number(target.toFixed(3));
    }
    setDeltas(ZERO_DELTAS);
    setOverrides(next);
  }

  function snapAllKnobsToGolden() {
    if (!simResult?.parameters) return;
    const nextOverrides = {};
    for (const k of KNOB_DEFS) {
      const p = simResult.parameters.find((r) => r.tag === k.tag);
      if (p && p.golden_center != null && p.simulated_golden_status !== "in_golden") {
        nextOverrides[k.tag] = Number(p.golden_center);
      }
    }
    setDeltas(ZERO_DELTAS);
    setOverrides((prev) => ({ ...prev, ...nextOverrides }));
  }

  async function beginRun(next) {
    if (runMode === next) {
      fetch(`${API}/play/fine/stop`, { method: "POST" }).catch(() => {});
      setFineNow(null);
      setRunMode(null);
      setOverrides({});
      setDeltas(ZERO_DELTAS);
      setRecovery(0);
      return;
    }
    setPaused(false);
    setCustomTimestamp(null);
    setRunTrace([]);
    if (next === "history") {
      fetch(`${API}/play/fine/stop`, { method: "POST" }).catch(() => {});
      setFineNow(null);
      setOverrides({});
      setDeltas(ZERO_DELTAS);
      setRecovery(0);
      setRunMode("history");
      return;
    }
    if (next === "autopilot") {
      setOverrides({});
      setDeltas(ZERO_DELTAS);
      setRecovery(0);
      const synthetic = datasets.find((d) => d.origin === "synthetic" || d.id === "synthetic-plant-bf1");
      if (synthetic && activeDataset?.id !== synthetic.id) {
        await fetch(`${API}/datasets/select`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dataset_id: synthetic.id }),
        });
        await fetch(`${API}/play/fine/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode: "autopilot", target_production: Number(requiredProd) || 4500 }),
        });
        setRunMode("autopilot");
        loadAll(6, requiredProd);
        return;
      }
      await fetch(`${API}/play/fine/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "autopilot", target_production: Number(requiredProd) || 4500 }),
      });
      setRunMode("autopilot");
      return;
    }
    const golden = await fetch(`${API}/golden-ranges?target_production=${Number(requiredProd) || 4500}`).then((r) => r.json());
    const held = {};
    Object.values(golden.ranges || {}).forEach((g) => {
      if (g.role === "manipulated" && g.golden_center != null) held[g.tag] = Number(g.golden_center);
    });
    setDeltas(ZERO_DELTAS);
    setOverrides(held);
    setRecovery(100);
    await fetch(`${API}/play/fine/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "goal", target_production: Number(requiredProd) || 4500 }),
    });
    setRunMode("goal");
  }

  function jumpToHistoricalEpisode(epTime, topCauseTag) {
    setRunMode(null);
    setDeltas(ZERO_DELTAS);
    setOverrides({});
    setCustomTimestamp(epTime);
    if (frames.length > 0) {
      const targetMs = new Date(epTime.replace(" ", "T")).getTime();
      let bestIdx = 0;
      let bestDist = Infinity;
      frames.forEach((f, idx) => {
        const d = Math.abs(new Date(f.t.replace(" ", "T")).getTime() - targetMs);
        if (d < bestDist) {
          bestDist = d;
          bestIdx = idx;
        }
      });
      setIndex(bestIdx);
    }
    if (topCauseTag) {
      setSelectedTag(topCauseTag);
    }
  }

  function resetAll() {
    setDeltas(ZERO_DELTAS);
    setOverrides({});
    setOptResult(null);
  }

  const paramByTag = useMemo(() => {
    const map = {};
    for (const p of simResult?.parameters || []) {
      map[p.tag] = p;
    }
    return map;
  }, [simResult]);

  // Per-zone anomaly rollup for the fast triage strip.
  const zoneHealth = useMemo(() => {
    return FURNACE_ZONES.map((z) => {
      let issues = 0;
      let totalRisk = 0;
      let worst = null;
      let worstRisk = -1;
      let present = 0;
      for (const tag of z.tags) {
        const p = paramByTag[tag];
        if (!p) continue;
        present += 1;
        const st = p.simulated_golden_status;
        if (st && st !== "in_golden") {
          issues += 1;
          const risk = Number(p.production_risk_t_d || 0);
          totalRisk += risk;
          if (risk > worstRisk) {
            worstRisk = risk;
            worst = p;
          }
        }
      }
      const firstPresent = z.tags.find((t) => paramByTag[t]);
      return { ...z, issues, totalRisk, worst, present, firstPresent };
    });
  }, [paramByTag]);

  const visibleKnobs = useMemo(() => {
    if (knobTab === "all" || knobTab === "out_golden") {
      if (knobTab === "out_golden") {
        return KNOB_DEFS.filter((k) => {
          const p = paramByTag[k.tag];
          return p && p.simulated_golden_status !== "in_golden";
        });
      }
      return KNOB_DEFS;
    }
    return KNOB_DEFS.filter((k) => k.group === knobTab);
  }, [knobTab, paramByTag]);

  const filteredParams = useMemo(() => {
    let list = simResult?.parameters || [];
    if (paramFilter === "out_golden") {
      list = list.filter((p) => p.simulated_golden_status && p.simulated_golden_status !== "in_golden");
    } else if (paramFilter !== "all") {
      list = list.filter((p) => p.role === paramFilter);
    }
    if (sensorQuery.trim()) {
      const q = sensorQuery.trim().toLowerCase();
      list = list.filter((p) => p.tag.toLowerCase().includes(q) || (p.label || "").toLowerCase().includes(q));
    }
    const sorted = list.slice();
    if (sensorSort === "risk") {
      sorted.sort((a, b) => Number(b.production_risk_t_d || 0) - Number(a.production_risk_t_d || 0));
    } else if (sensorSort === "delta") {
      sorted.sort((a, b) => Math.abs(Number(b.delta || 0)) - Math.abs(Number(a.delta || 0)));
    } else if (sensorSort === "tag") {
      sorted.sort((a, b) => a.tag.localeCompare(b.tag));
    } else if (sensorSort === "zone") {
      sorted.sort((a, b) => (a.zone || "").localeCompare(b.zone || ""));
    }
    return sorted;
  }, [simResult, paramFilter, sensorQuery, sensorSort]);

  const filteredEpisodes = useMemo(() => {
    const eps = shortfallData?.episodes || [];
    if (shortfallCategory === "all") return eps;
    return eps.filter((e) => e.category === shortfallCategory);
  }, [shortfallData, shortfallCategory]);

  if (error) return <p className="cockpit-error">{error}</p>;
  if (!frame || !simResult) return <p className="cockpit-error">Initializing coupled digital twin</p>;

  const simState = simResult.simulated_state;
  const baseState = simResult.baseline_state;
  const kpis = simResult.physics_kpis;
  const baseKpis = simResult.baseline_physics_kpis;
  const reconciliation = simResult.reconciliation || {};
  const kpiStatus = reconciliation.kpi_status || {};
  const bandWarnings = reconciliation.warnings || [];
  const regime = simResult.operating_regime || { regime: "on_wind", qualified: true };
  const goldenAnalysis = simResult.golden_analysis || {};
  const outOfGoldenSim = goldenAnalysis.out_of_golden_simulated || [];
  const histRootCauses = goldenAnalysis.historical_root_causes || [];
  const selectedParamObj = simResult.parameters.find((p) => p.tag === selectedTag) || simResult.parameters[0];
  const totalZoneIssues = zoneHealth.reduce((acc, z) => acc + z.issues, 0);

  return (
    <section className="twin-workbench">
      {/* Top Dataset, Mode, Required Production Target & Primary KPI Ribbon */}
      <header className="twin-topbar">
        <div className="topbar-controls">
          <div className="topbar-left-group">
            <label className="top-select">
              <span>Active Furnace Data</span>
              <select value={activeDataset?.id || ""} onChange={(e) => handleDatasetSwitch(e.target.value)}>
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="upload-btn">
              <span>Upload Your BF Data (CSV/XLSX/Parquet)</span>
              <input type="file" accept=".csv,.xlsx,.xls,.parquet" onChange={handleFileUpload} />
            </label>
            <label className="top-select">
              <span>Simulation Engine</span>
              <select value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="hybrid">Hybrid (Physics + Learned Data)</option>
                <option value="data_only">Pure Data-Driven (Learned Jacobian)</option>
                <option value="physics_only">First-Principles Physics Only</option>
              </select>
            </label>

            <div className="golden-target-control">
              <label>
                <span>Required Production (Golden Range Basis)</span>
                <div className="golden-target-inputs">
                  <input
                    type="number"
                    min="1500"
                    max="16000"
                    step="50"
                    value={requiredProd}
                    onChange={(e) => {
                      const v = Number(e.target.value);
                      setRequiredProd(v);
                      setOptTarget((prev) => ({ ...prev, prod: v }));
                    }}
                  />
                  <em>t/day</em>
                  {[4500, 6500, 8000, 10000].map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      className={Number(requiredProd) === preset ? "active-preset" : ""}
                      onClick={() => {
                        setRequiredProd(preset);
                        setOptTarget((prev) => ({ ...prev, prod: preset }));
                      }}
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </label>
              <p className="muted" style={{ margin: "0.35rem 0 0" }}>
                Furnace class {furnaceClass(requiredProd).name} · assumed working volume {furnaceClass(requiredProd).volume} m³ · 2.2 t/m³·day
              </p>
            </div>
          </div>

          <div className="topbar-right-group">
            <div className="view-mode-switcher">
              <span>Workspace View</span>
              <div className="view-mode-pills">
                {[
                  ["cockpit", "3D Cockpit"],
                  ["radar", "Issue Radar"],
                  ["matrix", "Data Matrix"],
                ].map(([id, lbl]) => (
                  <button key={id} type="button" className={viewMode === id ? "active" : ""} onClick={() => setViewMode(id)}>
                    {lbl}
                  </button>
                ))}
              </div>
            </div>

            <div className="golden-compliance-pill">
              <span>Golden Compliance @ {requiredProd} t/d</span>
              <strong className={outOfGoldenSim.length === 0 ? "ok" : "warn"}>
                {goldenAnalysis.in_golden_count ?? 0}/{goldenAnalysis.total_parameters ?? 41} in Golden (
                {goldenAnalysis.simulated_compliance_pct ?? 100}%)
              </strong>
              <div className="golden-pill-actions">
                <button type="button" onClick={snapAllKnobsToGolden} title="Set all out-of-golden knobs to their Golden Center for the required production">
                  Align Knobs to Golden
                </button>
                <button
                  type="button"
                  className={knobTab === "history" ? "active" : ""}
                  onClick={() => setKnobTab(knobTab === "history" ? "all" : "history")}
                >
                  Historical Shortfalls ({shortfallData?.episodes?.length || 0})
                </button>
              </div>
            </div>
          </div>

          {uploadStatus && <span className="upload-badge">{uploadStatus}</span>}
        </div>

        <div className="kpi-ribbon">
          {[
            ["Production", "Production", `${kpis.Production.toFixed(0)} t/d`, kpis.Production - baseKpis.Production, "t/d"],
            ["Productivity", "Production", `${kpis.Productivity.toFixed(2)} t/m³d`, kpis.Productivity - baseKpis.Productivity, ""],
            ["Hot Metal [Si]", "Si", `${simState.Si.toFixed(3)} %`, simState.Si - baseState.Si, "%"],
            ["Hot Metal Temp", "HMT", `${kpis.HMT.toFixed(0)} °C`, kpis.HMT - baseKpis.HMT, "°C"],
            ["RAFT Flame", "RAFT", `${kpis.RAFT.toFixed(0)} °C`, kpis.RAFT - baseKpis.RAFT, "°C"],
            ["Total ΔP", "dP", `${simState.dP.toFixed(2)} kgf/cm²`, simState.dP - baseState.dP, ""],
            ["Gas Util ηCO", "EtaCO", `${kpis.EtaCO.toFixed(1)} %`, kpis.EtaCO - baseKpis.EtaCO, "%"],
            ["Condensation", "CondensationIdx", `${kpis.CondensationIdx.toFixed(1)} idx`, kpis.CondensationIdx - baseKpis.CondensationIdx, ""],
            ["CZ Root Height", "CZHeight", `${kpis.CZHeight.toFixed(2)} m`, kpis.CZHeight - baseKpis.CZHeight, "m"],
            ["Fuel Rate", "FuelRate", `${kpis.FuelRate.toFixed(0)} kg/t`, kpis.FuelRate - baseKpis.FuelRate, "kg/t"],
          ].map(([title, tag, val, diff, u]) => {
            const st = kpiStatus[tag];
            const absolute = !st || st.show_absolute;
            const pRow = paramByTag[tag];
            const gSt = pRow?.simulated_golden_status;
            return (
              <div
                key={title}
                className={`kpi-pill${absolute ? "" : " kpi-pill-unavailable"}${
                  gSt && gSt !== "in_golden" ? ` kpi-golden-${gSt}` : ""
                }`}
                title={pRow?.golden_warning || evidenceHint(tag, st)}
                onClick={() => pRow && setSelectedTag(tag)}
              >
                <span>
                  {title}
                  {st && <i className={`kpi-evidence kpi-evidence-${st.evidence}`}>{EVIDENCE_LABEL[st.evidence]}</i>}
                </span>
                <strong>{absolute ? val : "not computable"}</strong>
                {pRow?.golden_low != null && (
                  <small className="kpi-golden-sub">
                    Golden {pRow.golden_low} to {pRow.golden_high}
                  </small>
                )}
                <em className={Math.abs(diff) < 1e-3 ? "flat" : diff > 0 ? "up" : "down"}>
                  {Math.abs(diff) < 1e-3
                    ? absolute
                      ? "baseline"
                      : "no response"
                    : `${diff > 0 ? "+" : ""}${Math.abs(diff) < 1 ? diff.toFixed(3) : diff.toFixed(1)} ${u}`}
                </em>
              </div>
            );
          })}
        </div>

        {/* Zone Health Triage Strip: locate sensor issues by furnace region in one glance */}
        <div className="zone-triage-strip">
          {zoneHealth.map((z) => {
            const hasFault = z.issues > 0 && z.worst?.simulated_golden_status === "above_golden";
            const cls = z.issues === 0 ? "" : hasFault ? "zone-has-fault" : "zone-has-warn";
            const activeZone = z.tags.includes(selectedTag);
            return (
              <button
                key={z.id}
                type="button"
                className={`zone-triage-card ${cls} ${activeZone ? "zone-active" : ""}`}
                onClick={() => setSelectedTag(z.worst?.tag || z.firstPresent || selectedTag)}
                title={
                  z.issues === 0
                    ? `${z.name}: all ${z.present} sensors inside Golden Range`
                    : `${z.name}: ${z.issues} sensor(s) out of Golden Range. Worst: ${z.worst?.tag} (-${z.worst?.production_risk_t_d} t/d)`
                }
              >
                <div className="zone-triage-top">
                  <span>{z.name}</span>
                  <span className={`zone-triage-count ${z.issues === 0 ? "ok" : "bad"}`}>
                    {z.issues === 0 ? "OK" : `${z.issues} ISSUE${z.issues > 1 ? "S" : ""}`}
                  </span>
                </div>
                <div className="zone-triage-sub">
                  <span>{z.present} sensors</span>
                  {z.issues > 0 ? <span className="down">-{z.totalRisk.toFixed(0)} t/d</span> : <span className="ok">nominal</span>}
                </div>
              </button>
            );
          })}
        </div>

        {/* Golden Range Production Warning Strip */}
        {outOfGoldenSim.length > 0 && (
          <div className="golden-warning-strip">
            <div className="gw-head">
              <strong>
                Golden Range Warnings @ {requiredProd} t/d ({outOfGoldenSim.length} out of golden, {totalZoneIssues} flagged)
              </strong>
              {goldenAnalysis.simulated_shortfall_vs_target_t_d > 0 && (
                <span className="gw-shortfall-badge">
                  Production Shortfall vs Target -{goldenAnalysis.simulated_shortfall_vs_target_t_d} t/d (72h Rolling{" "}
                  {goldenAnalysis.rolling_72h_production_t_d} t/d)
                </span>
              )}
            </div>
            <div className="gw-chips">
              {outOfGoldenSim.slice(0, 8).map((item) => (
                <button
                  key={item.tag}
                  type="button"
                  className={`gw-chip gw-${item.status} ${selectedTag === item.tag ? "gw-selected" : ""}`}
                  title={item.warning}
                  onClick={() => setSelectedTag(item.tag)}
                >
                  <b>{item.tag}</b>
                  <span>
                    {item.simulated} {item.unit} ({item.status === "below_golden" ? `below ${item.golden_low}` : `above ${item.golden_high}`})
                  </span>
                  {item.production_risk_t_d > 0 && <em>-{item.production_risk_t_d} t/d risk</em>}
                </button>
              ))}
            </div>
          </div>
        )}

        {simResult.envelope && !simResult.envelope.routine_setpoint_allowed && simResult.envelope.moc_dossier && (
          <div className="regime-strip">
            <strong>MoC Trial Dossier Required</strong>
            <span>
              {simResult.envelope.moc_dossier.reason} | {simResult.envelope.moc_dossier.governance_rule}
            </span>
          </div>
        )}
        {!regime.qualified && (
          <div className="regime-strip">
            <strong>{regime.regime.replace("_", " ")}</strong>
            <span>
              Blast is at {Math.round((regime.blast_fraction_of_median || 0) * 100)}% of the campaign median (
              {regime.blast_reference_m3_min} m³/min). {regime.detail} Setpoints are suppressed for this hour.
            </span>
          </div>
        )}
        {bandWarnings.length > 0 && (
          <div className="band-warning-strip">
            <strong>Outside validated band</strong>
            {bandWarnings.map((w) => {
              const withheld = kpiStatus[w.quantity] && !kpiStatus[w.quantity].show_absolute;
              return (
                <span key={w.quantity} className={`bw-${w.source || "correlation"}`} title={w.detail}>
                  {w.quantity}{" "}
                  {w.status === "saturated"
                    ? "saturated"
                    : withheld
                      ? `withheld, outside ${w.band[0]} to ${w.band[1]}`
                      : `${w.value} vs ${w.band[0]} to ${w.band[1]}`}
                  <i>{w.source === "measurement" ? "furnace" : "model"}</i>
                </span>
              );
            })}
          </div>
        )}
      </header>

      {/* Main 3-Column Digital Twin Workspace */}
      <div className={`workbench-grid mode-${viewMode}`}>
        {/* Left Column: All Knobs with Golden Ranges, Historical Shortfall Explorer & Inverse Optimizer */}
        <aside className="dock left-dock">
          <div className="dock-tabs">
            {[
              ["all", "All 13 Knobs"],
              ["out_golden", "Out of Golden"],
              ["blast", "Blast/Tuyere"],
              ["burden", "Fuel/Burden"],
              ["cond", "Alkali/Quality"],
              ["history", "Historical Drops"],
              ["opt", "Optimizer"],
            ].map(([id, title]) => (
              <button key={id} type="button" className={knobTab === id ? "active" : ""} onClick={() => setKnobTab(id)}>
                {title}
              </button>
            ))}
          </div>

          {knobTab === "opt" ? (
            <div className="optimizer-box">
              <h3>Inverse Target Production Optimizer</h3>
              <p className="muted">
                Enter your desired hot-metal production and quality targets. The twin solves for the required parameter setpoints inside the Golden Range and operating envelope.
              </p>
              <label>
                Target Production (t/day)
                <input
                  type="number"
                  value={optTarget.prod}
                  onChange={(e) => {
                    setOptTarget({ ...optTarget, prod: e.target.value });
                    setRequiredProd(Number(e.target.value) || 4500);
                  }}
                />
              </label>
              <label>
                Target Silicon [Si] (wt%)
                <input
                  type="number"
                  step="0.01"
                  value={optTarget.si}
                  onChange={(e) => setOptTarget({ ...optTarget, si: e.target.value })}
                />
              </label>
              <label>
                Max Permissible ΔP (kgf/cm²)
                <input
                  type="number"
                  step="0.02"
                  value={optTarget.maxDp}
                  onChange={(e) => setOptTarget({ ...optTarget, maxDp: e.target.value })}
                />
              </label>
              <div className="opt-actions">
                <button type="button" className="primary-btn" onClick={runTargetOptimizer}>
                  Solve Required Parameters
                </button>
                {optResult && (
                  <button type="button" onClick={applyOptimizedSetpoints}>
                    Apply Setpoints to Twin
                  </button>
                )}
              </div>

              {optResult && (
                <div className="opt-results">
                  <p className="status">
                    Status <b className={optResult.feasible ? "ok" : "not"}>{optResult.status}</b> | {optResult.furnace_class?.name || furnaceClass(optTarget.prod).name} furnace | Achieved{" "}
                    <b>{optResult.achieved_production} t/d</b> at <b>{optResult.achieved_si}% Si</b> | Binding ceiling{" "}
                    {optResult.binding_ceiling} ({optResult.max_feasible_production} t/d)
                  </p>
                  <table>
                    <thead>
                      <tr>
                        <th>Parameter</th>
                        <th>Current</th>
                        <th>Golden Range</th>
                        <th>Recommended</th>
                        <th>Delta</th>
                      </tr>
                    </thead>
                    <tbody>
                      {optResult.recommendations.map((r) => (
                        <tr key={r.tag}>
                          <td>{r.label}</td>
                          <td>{r.current}</td>
                          <td>
                            <small>
                              {r.golden_low} to {r.golden_high}
                            </small>
                          </td>
                          <td>
                            <b>{r.recommended}</b>
                          </td>
                          <td className={r.delta >= 0 ? "up" : "down"}>
                            {r.delta >= 0 ? "+" : ""}
                            {r.delta}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ) : knobTab === "history" ? (
            <div className="history-shortfall-box">
              <div className="hs-header">
                <h3>Historical Production Shortfall Root-Cause Explorer</h3>
                <p className="muted">
                  Backward-compatible Golden Range attribution across history. Click any historical episode below to jump the Digital Twin to that timestamp and inspect the parameters that caused production to drop.
                </p>
              </div>

              <div className="hs-current-box">
                <div className="hs-cur-head">
                  <strong>Active Timestamp {simResult.t}</strong>
                  <span>
                    Prod <b>{goldenAnalysis.actual_production_t_d} t/d</b> | 72h Ref{" "}
                    <b>{goldenAnalysis.rolling_72h_production_t_d} t/d</b> | Target <b>{requiredProd} t/d</b>
                  </span>
                </div>
                {histRootCauses.length === 0 ? (
                  <p className="muted">All historical parameters at {simResult.t} are within their Golden Range for {requiredProd} t/d.</p>
                ) : (
                  <div className="hs-cause-list">
                    {histRootCauses.slice(0, 5).map((c) => (
                      <div key={c.tag} className={`hs-cause-item hs-${c.status}`} onClick={() => setSelectedTag(c.tag)}>
                        <div className="hs-cause-top">
                          <b>
                            {c.tag} {c.label} <small>(lag {c.lag_h}h)</small>
                          </b>
                          <span className="hs-loss-pill">
                            -{c.estimated_loss_t_d} t/d ({c.share_of_shortfall_pct}%)
                          </span>
                        </div>
                        <div className="hs-cause-nums">
                          <span>
                            Historical <b>{c.value_at_lag} {c.unit}</b> (72h ref {c.ref_72h_value})
                          </span>
                          <span>
                            Golden <b>{c.golden_low} to {c.golden_high} {c.unit}</b>
                          </span>
                        </div>
                        <p className="hs-cause-mech">{c.mechanism}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="hs-episodes-header">
                <strong>Detected Historical Drop Episodes ({filteredEpisodes.length})</strong>
                <div className="hs-filter-pills">
                  {[
                    ["all", "All"],
                    ["permeability_or_thermal_mystery", "Constant-Wind Mystery"],
                    ["constant_wind_shortfall", "O2 / Thermal Cut"],
                    ["wind_or_enrichment_shortfall", "Deep Drop"],
                  ].map(([id, lbl]) => (
                    <button key={id} type="button" className={shortfallCategory === id ? "active" : ""} onClick={() => setShortfallCategory(id)}>
                      {lbl}
                    </button>
                  ))}
                </div>
              </div>

              <div className="hs-episode-list">
                {filteredEpisodes.map((ep) => (
                  <div
                    key={ep.t}
                    className={`hs-episode-card ${simResult.t === ep.t ? "active-episode" : ""}`}
                    onClick={() => jumpToHistoricalEpisode(ep.t, ep.top_causes?.[0]?.tag)}
                  >
                    <div className="hs-ep-top">
                      <b>{ep.t}</b>
                      <span className="hs-ep-cat">{ep.category.replace(/_/g, " ")}</span>
                    </div>
                    <div className="hs-ep-metrics">
                      <span>
                        Prod <b>{ep.actual_production_t_d} t/d</b> (72h ref {ep.rolling_72h_production_t_d} t/d)
                      </span>
                      <em className="down">
                        -{Math.max(ep.drop_vs_rolling_72h_t_d, ep.shortfall_vs_target_t_d).toFixed(0)} t/d drop
                      </em>
                    </div>
                    <div className="hs-ep-causes">
                      {(ep.top_causes || []).slice(0, 3).map((tc) => (
                        <span key={tc.tag} className={`hs-ep-chip hs-chip-${tc.status}`}>
                          {tc.tag} {tc.value_at_lag} {tc.status === "below_golden" ? "<" : ">"}{" "}
                          {tc.status === "below_golden" ? tc.golden_low : tc.golden_high} (-{tc.estimated_loss_t_d} t/d)
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              <div className="switches-box">
                <div className="switches-header">
                  <span>Process Switches & Golden Alignment</span>
                  <div style={{ display: "flex", gap: "0.35rem" }}>
                    <button type="button" onClick={snapAllKnobsToGolden}>
                      Snap All to Golden
                    </button>
                    <button type="button" onClick={resetAll}>
                      Reset Knobs
                    </button>
                  </div>
                </div>
                <div className="switch-grid">
                  {[
                    ["switch_dehumidification", "Blast Dehumidifier (-7.5 g/Nm³)"],
                    ["switch_center_coke", "Center Coke Charging"],
                    ["switch_alkali_flush", "Slag Alkali Flush Mode"],
                    ["show_all_pins", "Show All 10 Wall Pins"],
                  ].map(([k, title]) => (
                    <label key={k} className="switch-pill">
                      <input
                        type="checkbox"
                        checked={Boolean(switches[k])}
                        onChange={(e) => setSwitches({ ...switches, [k]: e.target.checked })}
                      />
                      <span>{title}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="knob-list">
                {visibleKnobs.map((k) => {
                  const baseVal = Number(baseState[k.tag] ?? 0);
                  const curVal = Number(simState[k.tag] ?? baseVal);
                  const dVal = curVal - baseVal;
                  const pRow = paramByTag[k.tag];
                  const gStatus = pRow?.simulated_golden_status || "in_golden";
                  const isOut = gStatus !== "in_golden";
                  return (
                    <div
                      key={k.tag}
                      className={`knob-item ${selectedTag === k.tag ? "selected" : ""} ${isOut ? `knob-${gStatus}` : "knob-in_golden"}`}
                      onClick={() => setSelectedTag(k.tag)}
                    >
                      <div className="knob-head">
                        <span>
                          {k.label} <small>(lag {k.tau})</small>
                        </span>
                        <b>
                          {curVal.toFixed(k.step < 1 ? 2 : 0)} {k.unit}
                          {Math.abs(dVal) > 1e-4 && (
                            <em className={dVal >= 0 ? "up" : "down"}>
                              {" "}
                              ({dVal >= 0 ? "+" : ""}
                              {dVal.toFixed(k.step < 1 ? 2 : 0)})
                            </em>
                          )}
                        </b>
                      </div>

                      {pRow && pRow.golden_low != null && (
                        <div className="knob-golden-meta">
                          <span className="knob-golden-band-text">
                            Golden @ {requiredProd} t/d <b>{pRow.golden_low} to {pRow.golden_high}</b> {k.unit}
                          </span>
                          <span className={`golden-badge golden-badge-${gStatus}`}>
                            {GOLDEN_STATUS_LABEL[gStatus]}
                            {isOut && pRow.production_risk_t_d > 0 ? ` (-${pRow.production_risk_t_d} t/d)` : ""}
                          </span>
                        </div>
                      )}

                      <input
                        type="range"
                        min={k.minDelta}
                        max={k.maxDelta}
                        step={k.step}
                        value={deltas[k.tag] || 0}
                        onChange={(e) => {
                          const v = Number(e.target.value);
                          setOverrides((prev) => {
                            const next = { ...prev };
                            delete next[k.tag];
                            return next;
                          });
                          setDeltas((prev) => ({ ...prev, [k.tag]: v }));
                        }}
                      />

                      {pRow && pRow.golden_low != null && (
                        <GoldenRangeBar
                          min={pRow.min}
                          max={pRow.max}
                          goldenLow={pRow.golden_low}
                          goldenHigh={pRow.golden_high}
                          baseline={pRow.baseline}
                          simulated={pRow.simulated}
                          status={gStatus}
                        />
                      )}

                      {isOut && pRow?.golden_warning && (
                        <div className="knob-warning-note">
                          <span>{pRow.golden_warning}</span>
                          <button
                            type="button"
                            onClick={(ev) => {
                              ev.stopPropagation();
                              snapKnobToGolden(k.tag, pRow.golden_center);
                            }}
                          >
                            Set Golden ({pRow.golden_center})
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </aside>

        {/* Center Stage: 3D Cutaway + Stave Radar + Time Scrubber + 24h Propagation Sparklines */}
        <div className="center-stage">
          {runMode ? (
            <div className="play-layout">
            <div className="play-stats-stage">
              <p className="run-caption">
                {runMode === "history" && `${paused ? "Paused · " : ""}Historical replay · ${simResult.t} · recorded sensors, no adjustment`}
                {runMode === "autopilot" && `${paused ? "Paused · " : ""}Autopilot · own flow ${fineNow?.t || "—"} · T+${fineMeta?.sim_s ?? 0}s · ring ${fineMeta?.count ?? 0}/${fineMeta?.capacity ?? 4096}`}
                {runMode === "goal" && `${paused ? "Paused · " : ""}Goal test · own flow ${fineNow?.t || "—"} · T+${fineMeta?.sim_s ?? 0}s · ring ${fineMeta?.count ?? 0}/${fineMeta?.capacity ?? 4096}`}
              </p>
              {runTrace.length > 1 && <RunTrace points={runTrace} />}
              {runMode === "autopilot" && (
                <div className="ap-levers">
                  <p className="gf-kicker">Your levers · autopilot moves the others</p>
                  {fineLevers.map((lever) => (
                    <label key={lever.tag}>
                      <span>{lever.tag}{lever.held ? " · held" : ""}</span>
                      <input
                        type="range"
                        min={lever.min}
                        max={lever.max}
                        step={(lever.max - lever.min) / 80}
                        value={lever.value}
                        onChange={(e) => {
                          const value = Number(e.target.value);
                          setFineLevers((prev) => prev.map((item) => (item.tag === lever.tag ? { ...item, value, held: true } : item)));
                          fetch(`${API}/play/fine/hold`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ tag: lever.tag, value }),
                          }).catch(() => {});
                        }}
                      />
                      <b>{Number(lever.value).toFixed(lever.tag === "R" || lever.tag === "Pt" ? 2 : 0)}</b>
                    </label>
                  ))}
                </div>
              )}
              <ParameterStats
                liveSensors={simResult.parameters}
                recovery={runMode === "history" ? 0 : recovery}
                onRecovery={runMode === "history" ? null : applyRecovery}
                caption={runMode === "history" ? "Recorded hour" : runMode === "goal" ? "Held toward the production goal · 1 s" : "Autopilot · 1 s"}
                fineNow={fineNow}
              />
            </div>
            <aside className="run-warnings" aria-live="polite">
              <p className="gf-kicker">Warnings</p>
              <p className="muted">{simResult.t}</p>
              {(simResult.parameters || []).filter((p) => p.simulated_golden_status && p.simulated_golden_status !== "in_golden").slice(0, 12).map((p) => (
                <article key={p.tag} className={`run-warn run-warn-${p.simulated_golden_status}`}>
                  <b>{p.label}</b>
                  <span>{p.simulated_golden_status === "below_golden" ? "below" : "above"} · {p.simulated} {p.unit}</span>
                  <small>{p.golden_warning || p.baseline_golden_warning || ""}</small>
                </article>
              ))}
              {(simResult.parameters || []).every((p) => !p.simulated_golden_status || p.simulated_golden_status === "in_golden") && (
                <p className="muted">No tag is outside its golden band.</p>
              )}
            </aside>
            </div>
          ) : (
          <div className="canvas-holder">
            <TwinCanvas
              simState={simState}
              baseState={baseState}
              kpis={kpis}
              paramByTag={paramByTag}
              open={open}
              selectedTag={selectedTag}
              onSelectTag={setSelectedTag}
              showAllPins={switches.show_all_pins}
              anomalyPinsOnly={anomalyPinsOnly}
              themeMeta={themeMeta}
            />
            <div className="canvas-overlay-badge">
              <span>Timestamp {simResult.t} | {simResult.model_version || "hearthline-hybrid-0.4.0"}</span>
              <span>
                Target {requiredProd} t/d | Envelope {simResult.envelope?.in_envelope !== false ? "IN" : "OUT"} (D={simResult.envelope?.mahalanobis_distance ?? 0}) | Ceiling {kpis.binding_ceiling} ({kpis.max_feasible_production} t/d)
              </span>
            </div>
            <div className="canvas-filter-floating">
              <button type="button" className={anomalyPinsOnly ? "active" : ""} onClick={() => setAnomalyPinsOnly((v) => !v)}>
                {anomalyPinsOnly ? "Showing anomalies only" : "Highlight anomalies only"}
              </button>
            </div>
          </div>
          )}

          {!runMode && (
          <>
          {/* Radial Stave & Offtake Anomaly Mini-Map for instant peripheral issue spotting */}
          <div className="stave-radar-strip">
            <div className="stave-group-box">
              <div className="stave-group-head">
                <span>Shaft Wall Staves Tp1 to Tp10</span>
                <span>Click a cell to inspect</span>
              </div>
              <div className="stave-cells">
                {Array.from({ length: 10 }, (_, i) => {
                  const tag = `Tp${i + 1}`;
                  const p = paramByTag[tag];
                  const val = Number(simState[tag] ?? 0);
                  const st = p?.simulated_golden_status || "in_golden";
                  return (
                    <button
                      key={tag}
                      type="button"
                      className={`stave-cell stave-${st} ${selectedTag === tag ? "stave-selected" : ""}`}
                      onClick={() => setSelectedTag(tag)}
                      title={`${tag} ${Math.round(val)} degC. Golden ${p?.golden_low} to ${p?.golden_high}. ${
                        st === "in_golden" ? "Nominal" : st === "below_golden" ? "Below golden" : "Above golden"
                      }`}
                    >
                      <span>{i + 1}</span>
                      <b>{Math.round(val)}</b>
                    </button>
                  );
                })}
              </div>
            </div>
            <div className="stave-group-box">
              <div className="stave-group-head">
                <span>Top Offtake Tt1 to Tt4</span>
                <span>degC</span>
              </div>
              <div className="offtake-cells">
                {Array.from({ length: 4 }, (_, i) => {
                  const tag = `Tt${i + 1}`;
                  const p = paramByTag[tag];
                  const val = Number(simState[tag] ?? 0);
                  const st = p?.simulated_golden_status || "in_golden";
                  return (
                    <button
                      key={tag}
                      type="button"
                      className={`stave-cell stave-${st} ${selectedTag === tag ? "stave-selected" : ""}`}
                      onClick={() => setSelectedTag(tag)}
                      title={`${tag} ${Math.round(val)} degC. Golden ${p?.golden_low} to ${p?.golden_high}.`}
                    >
                      <span>{i + 1}</span>
                      <b>{Math.round(val)}</b>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
          </>
          )}

          <div className="transport-bar">
            {[
              ["history", "Play history"],
              ["autopilot", "Autopilot"],
              ["goal", "Goal test"],
            ].map(([id, label]) => (
              <button key={id} type="button" className={runMode === id ? "primary-btn" : ""} onClick={() => beginRun(id)}>
                {runMode === id ? "Stop" : label}
              </button>
            ))}
            {runMode && (
              <button type="button" onClick={() => setPaused((v) => !v)}>
                {paused ? "Resume" : "Pause"}
              </button>
            )}
            {(runMode === "history" || runMode === "goal") && (
            <label>
              Speed
              <input type="range" min="1" max="8" value={speed} onChange={(e) => setSpeed(Number(e.target.value))} />
            </label>
            )}
            {!runMode && (
            <label>
              Cutaway
              <input type="range" min="0.05" max="1" step="0.02" value={open} onChange={(e) => setOpen(Number(e.target.value))} />
            </label>
            )}
            {!runMode && (
            <input
              className="scrub"
              type="range"
              min="0"
              max={Math.max(0, frames.length - 1)}
              value={index}
              onChange={(e) => {
                setCustomTimestamp(null);
                setIndex(Number(e.target.value));
              }}
            />
            )}
          </div>

          {!runMode && (
          <div className="trajectory-strip">
            <Sparkline24h
              trajectory={simResult.trajectory_24h}
              field="Production"
              label="24h Production Response"
              unit="t/d"
              goldenLow={paramByTag.Production?.golden_low}
              goldenHigh={paramByTag.Production?.golden_high}
              color="var(--heat)"
            />
            <Sparkline24h
              trajectory={simResult.trajectory_24h}
              field="Si"
              label="24h Silicon [Si] Response"
              unit="%"
              goldenLow={paramByTag.Si?.golden_low}
              goldenHigh={paramByTag.Si?.golden_high}
              color="var(--warn)"
            />
            <Sparkline24h
              trajectory={simResult.trajectory_24h}
              field="dP"
              label="24h Total ΔP Response"
              unit="kgf/cm²"
              goldenLow={paramByTag.dP?.golden_low}
              goldenHigh={paramByTag.dP?.golden_high}
              color="var(--gas)"
            />
            <Sparkline24h
              trajectory={simResult.trajectory_24h}
              field="CondensationIdx"
              label="24h Condensation Load"
              unit="idx"
              goldenLow={paramByTag.CondensationIdx?.golden_low}
              goldenHigh={paramByTag.CondensationIdx?.golden_high}
              color="var(--fault)"
            />
          </div>
          )}
        </div>

        {/* Right Column: Searchable, Risk-Sorted 41-Sensor Matrix with Golden Ranges */}
        <aside className="dock right-dock">
          <div className="dock-tabs">
            {[
              ["all", "All 41 Tags"],
              ["out_golden", `Out (${outOfGoldenSim.length})`],
              ["outcome", "Outcomes"],
              ["state_response", "Sensors"],
              ["derived_latent", "Zones"],
              ["manipulated", "Inputs"],
            ].map(([id, title]) => (
              <button key={id} type="button" className={paramFilter === id ? "active" : ""} onClick={() => setParamFilter(id)}>
                {title}
              </button>
            ))}
          </div>

          <div className="matrix-search-bar">
            <input
              type="text"
              placeholder="Search sensor tag or name (e.g. Tp4, pressure, silicon)"
              value={sensorQuery}
              onChange={(e) => setSensorQuery(e.target.value)}
            />
            <select value={sensorSort} onChange={(e) => setSensorSort(e.target.value)} title="Sort sensor matrix">
              <option value="risk">Sort: Production risk</option>
              <option value="delta">Sort: Largest change</option>
              <option value="tag">Sort: Tag A-Z</option>
              <option value="zone">Sort: Zone</option>
            </select>
          </div>

          {selectedParamObj && (
            <div className="selected-sensor-card">
              <div className="sel-head">
                <strong>
                  {selectedParamObj.tag} | {selectedParamObj.label}
                </strong>
                <span className={`golden-badge golden-badge-${selectedParamObj.simulated_golden_status || "in_golden"}`}>
                  {GOLDEN_STATUS_LABEL[selectedParamObj.simulated_golden_status || "in_golden"]}
                </span>
              </div>
              <p className="muted">
                Baseline <b>{selectedParamObj.baseline}</b> {"->"} Simulated{" "}
                <b>
                  {selectedParamObj.simulated} {selectedParamObj.unit}
                </b>{" "}
                (Delta {selectedParamObj.delta >= 0 ? "+" : ""}
                {selectedParamObj.delta}, {selectedParamObj.pct_change}%) | Lag {selectedParamObj.lag_h}h
              </p>

              {selectedParamObj.golden_low != null && (
                <div className="sel-golden-detail">
                  <div className="sel-golden-nums">
                    <span>
                      Golden Range @ {requiredProd} t/d{" "}
                      <b>
                        {selectedParamObj.golden_low} to {selectedParamObj.golden_high} {selectedParamObj.unit}
                      </b>{" "}
                      (Center {selectedParamObj.golden_center})
                    </span>
                    {selectedParamObj.production_risk_t_d > 0 && (
                      <em className="down">Est. Impact -{selectedParamObj.production_risk_t_d} t/d</em>
                    )}
                  </div>
                  <GoldenRangeBar
                    min={selectedParamObj.min}
                    max={selectedParamObj.max}
                    goldenLow={selectedParamObj.golden_low}
                    goldenHigh={selectedParamObj.golden_high}
                    baseline={selectedParamObj.baseline}
                    simulated={selectedParamObj.simulated}
                    status={selectedParamObj.simulated_golden_status}
                  />
                  <div className="sel-golden-rules">
                    <div className={selectedParamObj.simulated_golden_status === "below_golden" ? "rule-active" : ""}>
                      <b>If Below {selectedParamObj.golden_low}:</b> {selectedParamObj.below_warning}
                    </div>
                    <div className={selectedParamObj.simulated_golden_status === "above_golden" ? "rule-active" : ""}>
                      <b>If Above {selectedParamObj.golden_high}:</b> {selectedParamObj.above_warning}
                    </div>
                  </div>
                </div>
              )}

              {sensitivity?.jacobian?.[selectedParamObj.tag] && (
                <div className="jac-chips">
                  {Object.entries(sensitivity.jacobian[selectedParamObj.tag])
                    .slice(0, 5)
                    .map(([inCol, slope]) => (
                      <span key={inCol} className="jac-chip">
                        d{selectedParamObj.tag}/d{inCol} = {Number(slope).toExponential(2)}
                      </span>
                    ))}
                </div>
              )}
            </div>
          )}

          {histRootCauses.length > 0 && simResult.attributions?.length === 0 && (
            <div className="attribution-box hist-attr-box">
              <h4>
                Historical Shortfall Root Causes @ {simResult.t} (-{goldenAnalysis.shortfall_vs_target_t_d} t/d vs Target)
              </h4>
              <table>
                <thead>
                  <tr>
                    <th>Parameter</th>
                    <th>Hist Value</th>
                    <th>Golden Range</th>
                    <th>Status</th>
                    <th>Loss</th>
                  </tr>
                </thead>
                <tbody>
                  {histRootCauses.slice(0, 5).map((c) => (
                    <tr key={c.tag} onClick={() => setSelectedTag(c.tag)} style={{ cursor: "pointer" }} title={c.mechanism}>
                      <td>
                        <b>{c.tag}</b> <small>({c.lag_h}h)</small>
                      </td>
                      <td>
                        {c.value_at_lag} {c.unit}
                      </td>
                      <td>
                        <small>
                          {c.golden_low} to {c.golden_high}
                        </small>
                      </td>
                      <td>
                        <span className={`golden-badge golden-badge-${c.status}`}>
                          {c.status === "below_golden" ? "LOW" : "HIGH"}
                        </span>
                      </td>
                      <td className="down">-{c.estimated_loss_t_d} t/d</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {simResult.attributions?.length > 0 && (
            <div className="attribution-box">
              <h4>Active Knob Cause to Effect Breakdown</h4>
              <table>
                <thead>
                  <tr>
                    <th>Changed Knob</th>
                    <th>Delta Prod</th>
                    <th>Delta [Si]</th>
                    <th>Delta dP</th>
                    <th>Delta RAFT</th>
                  </tr>
                </thead>
                <tbody>
                  {simResult.attributions.map((a) => (
                    <tr key={a.input}>
                      <td>
                        {a.input} ({a.delta_input >= 0 ? "+" : ""}
                        {a.delta_input})
                      </td>
                      <td className={a.effect_Production_t_d >= 0 ? "up" : "down"}>
                        {a.effect_Production_t_d >= 0 ? "+" : ""}
                        {a.effect_Production_t_d} t/d
                      </td>
                      <td>
                        {a.effect_Si_wt_pct >= 0 ? "+" : ""}
                        {a.effect_Si_wt_pct}%
                      </td>
                      <td>
                        {a.effect_dP_kgf_cm2 >= 0 ? "+" : ""}
                        {a.effect_dP_kgf_cm2}
                      </td>
                      <td>
                        {a.effect_RAFT_C >= 0 ? "+" : ""}
                        {a.effect_RAFT_C} degC
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="param-table-scroll">
            <table className="param-matrix-table">
              <thead>
                <tr>
                  <th>Sensor / Tag</th>
                  <th>Sim</th>
                  <th>Golden Range</th>
                  <th>Status / Risk</th>
                </tr>
              </thead>
              <tbody>
                {filteredParams.map((p) => {
                  const gSt = p.simulated_golden_status || "in_golden";
                  return (
                    <tr
                      key={p.tag}
                      className={`${selectedTag === p.tag ? "selected-row" : ""} ${gSt !== "in_golden" ? `row-${gSt}` : ""}`}
                      onClick={() => setSelectedTag(p.tag)}
                      title={p.golden_warning || `${p.label}: inside Golden Range (${p.golden_low} to ${p.golden_high} ${p.unit})`}
                    >
                      <td>
                        <b>{p.tag}</b>
                        <small>{p.label}</small>
                      </td>
                      <td>
                        <b>{p.simulated}</b> <small>{p.unit}</small>
                        {Math.abs(p.delta) >= 1e-4 && (
                          <div className={p.delta > 0 ? "up" : "down"} style={{ fontSize: "0.62rem" }}>
                            {p.delta > 0 ? "+" : ""}
                            {p.delta}
                          </div>
                        )}
                      </td>
                      <td>
                        <div className="table-golden-cell">
                          <small>
                            {p.golden_low} to {p.golden_high}
                          </small>
                          <GoldenRangeBar
                            min={p.min}
                            max={p.max}
                            goldenLow={p.golden_low}
                            goldenHigh={p.golden_high}
                            baseline={p.baseline}
                            simulated={p.simulated}
                            status={gSt}
                          />
                        </div>
                      </td>
                      <td>
                        <span className={`golden-badge golden-badge-${gSt}`}>
                          {gSt === "in_golden" ? "GOLDEN" : gSt === "below_golden" ? "LOW" : "HIGH"}
                        </span>
                        {p.production_risk_t_d > 0 && <small className="table-risk-sub">-{p.production_risk_t_d} t/d</small>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </aside>
      </div>
    </section>
  );
}
