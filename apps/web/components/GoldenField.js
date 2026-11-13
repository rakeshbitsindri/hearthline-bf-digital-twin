"use client";

import { useEffect, useMemo, useState } from "react";
import { API } from "./Frame";

const LEVERS = [
  { tag: "Fb", short: "Blast", zone: "raceway" },
  { tag: "Fo", short: "Oxygen", zone: "raceway" },
  { tag: "Th", short: "Hot blast", zone: "raceway" },
  { tag: "Pt", short: "Top pressure", zone: "top" },
  { tag: "BlastMoisture", short: "Moisture", zone: "raceway" },
  { tag: "R", short: "Ore / coke", zone: "shaft" },
];

const ZONES = [
  { id: "top", label: "Top", y: 28, h: 70 },
  { id: "shaft", label: "Shaft", y: 108, h: 110 },
  { id: "bosh", label: "Bosh", y: 228, h: 70 },
  { id: "raceway", label: "Raceway", y: 308, h: 78 },
];

function statusOf(value, low, high) {
  if (value == null || low == null || high == null) return "in_golden";
  if (value < low) return "below_golden";
  if (value > high) return "above_golden";
  return "in_golden";
}

function zoneOf(tag) {
  return LEVERS.find((l) => l.tag === tag)?.zone || "shaft";
}

export function GoldenField({ targetProd }) {
  const [hour, setHour] = useState("");
  const [sim, setSim] = useState(null);
  const [deltas, setDeltas] = useState({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let cancel = false;
    fetch(`${API}/furnace`)
      .then((r) => r.json())
      .then((f) => {
        if (!cancel) setHour(f.to || "");
      })
      .catch(() => {});
    return () => {
      cancel = true;
    };
  }, []);

  useEffect(() => {
    if (!hour) return undefined;
    const handle = setTimeout(() => {
      setBusy(true);
      fetch(`${API}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          t: hour,
          deltas,
          target_production: Number(targetProd) || 4500,
          horizon_hours: 24,
        }),
      })
        .then((r) => r.json())
        .then((body) => {
          if (body && Array.isArray(body.parameters)) setSim(body);
        })
        .catch(() => {})
        .finally(() => setBusy(false));
    }, 140);
    return () => clearTimeout(handle);
  }, [hour, deltas, targetProd]);

  const byTag = useMemo(() => {
    const map = {};
    for (const p of sim?.parameters || []) map[p.tag] = p;
    return map;
  }, [sim]);

  const levers = LEVERS.map((lever) => {
    const p = byTag[lever.tag];
    if (!p) return null;
    const value = Number(p.simulated);
    const low = Number(p.golden_low);
    const high = Number(p.golden_high);
    const center = Number(p.golden_center ?? (low + high) / 2);
    const baseline = Number(p.baseline);
    const span = Math.max(high - low, Math.abs(high) * 0.04, 1);
    const min = Math.min(low - span, value, baseline);
    const max = Math.max(high + span, value, baseline);
    const status = p.simulated_golden_status || statusOf(value, low, high);
    const off = status === "in_golden" ? 0 : value < low ? low - value : value - high;
    return { ...lever, ...p, value, low, high, center, baseline, min, max, status, off };
  }).filter(Boolean);

  const worst = [...(sim?.parameters || [])]
    .filter((p) => p.simulated_golden_status && p.simulated_golden_status !== "in_golden" && p.tag !== "Production")
    .sort((a, b) => Number(b.production_risk_t_d || 0) - Number(a.production_risk_t_d || 0))
    .slice(0, 5);

  const zoneHeat = {};
  for (const z of ZONES) {
    const rows = (sim?.parameters || []).filter((p) => (p.zone || zoneOf(p.tag)) === z.id && p.tag !== "Production");
    const bad = rows.filter((p) => p.simulated_golden_status && p.simulated_golden_status !== "in_golden");
    zoneHeat[z.id] = rows.length ? bad.length / rows.length : 0;
  }

  function setLever(tag, nextValue, baseline) {
    const delta = Number((nextValue - baseline).toFixed(3));
    setDeltas((prev) => ({ ...prev, [tag]: Math.abs(delta) < 1e-6 ? 0 : delta }));
  }

  function pullAll() {
    const next = {};
    for (const lever of levers) {
      if (lever.status === "in_golden") continue;
      next[lever.tag] = Number((lever.center - lever.baseline).toFixed(3));
    }
    setDeltas(next);
  }

  const compliance = sim?.golden_analysis?.simulated_compliance_pct;
  const outCount = (sim?.golden_analysis?.out_of_golden_simulated || []).length;

  return (
    <section className="golden-field" aria-label="Golden band field">
      <header className="gf-head">
        <div>
          <p className="gf-kicker">Cut plane · golden band</p>
          <h3>Where the furnace has left the golden band</h3>
          <p className="muted">
            Each lane is one lever. The bright corridor is the golden band for {targetProd} t/d. Drag a marker back into the corridor.
            This is a what-if on the advisory twin. It does not write to the furnace.
          </p>
        </div>
        <div className="gf-score">
          <strong className={outCount ? "gf-hot" : "gf-ok"}>{compliance == null ? "—" : `${compliance}%`}</strong>
          <span>{outCount} outside the band</span>
          <button type="button" className="primary-btn" onClick={pullAll} disabled={!levers.length}>
            Pull levers to center
          </button>
        </div>
      </header>

      <div className="gf-stage">
        <div className="gf-cut" aria-hidden="true">
          <svg viewBox="0 0 280 430" className="gf-svg">
            <defs>
              <linearGradient id="gf-shell" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0" stopColor="rgba(140,170,200,0.35)" />
                <stop offset="1" stopColor="rgba(40,60,80,0.2)" />
              </linearGradient>
              <clipPath id="gf-shaft">
                <path d="M70 18 H210 V120 L232 250 L210 400 H70 L48 250 L70 120 Z" />
              </clipPath>
            </defs>
            <path d="M70 18 H210 V120 L232 250 L210 400 H70 L48 250 L70 120 Z" fill="url(#gf-shell)" stroke="rgba(180,210,230,0.45)" />
            <g clipPath="url(#gf-shaft)">
              {ZONES.map((z) => (
                <rect
                  key={z.id}
                  x="48"
                  y={z.y}
                  width="184"
                  height={z.h}
                  className={zoneHeat[z.id] > 0.34 ? "gf-zone gf-zone-hot" : zoneHeat[z.id] > 0 ? "gf-zone gf-zone-warm" : "gf-zone gf-zone-ok"}
                />
              ))}
              {Array.from({ length: 14 }).map((_, i) => (
                <circle key={i} cx={90 + (i % 5) * 18} cy={80 + i * 18} r={i % 3 === 0 ? 2.4 : 1.5} className={`gf-mote gf-mote-${i % 3}`}>
                  <animate attributeName="cx" values={`${80 + (i % 5) * 22};${90 + ((i * 3) % 5) * 18};${80 + (i % 5) * 22}`} dur={`${5.5 + (i % 4)}s`} repeatCount="indefinite" />
                  <animate attributeName="cy" values="390;40;390" dur={`${6 + (i % 5) * 0.6}s`} repeatCount="indefinite" />
                </circle>
              ))}
              <rect className="gf-scan" x="48" y="18" width="184" height="8" />
            </g>
            {ZONES.map((z) => (
              <text key={z.id} x="18" y={z.y + 18} className="gf-zone-label">
                {z.label}
              </text>
            ))}
          </svg>
          <div className="gf-legend">
            <span>in band</span>
            <i className="gf-legend-bar" />
            <span>off band</span>
          </div>
        </div>

        <div className="gf-lanes">
          {levers.map((lever) => {
            const pos = ((lever.value - lever.min) / (lever.max - lever.min)) * 100;
            const bandL = ((lever.low - lever.min) / (lever.max - lever.min)) * 100;
            const bandW = ((lever.high - lever.low) / (lever.max - lever.min)) * 100;
            return (
              <label key={lever.tag} className={`gf-lane gf-lane-${lever.status}`}>
                <div className="gf-lane-name">
                  <b>{lever.short}</b>
                  <em>{lever.status === "in_golden" ? "in band" : lever.status === "below_golden" ? "below" : "above"}</em>
                </div>
                <div className="gf-track">
                  <i className="gf-corridor" style={{ left: `${bandL}%`, width: `${bandW}%` }} />
                  <i className="gf-marker" style={{ left: `${pos}%` }} />
                </div>
                <input
                  type="range"
                  min={lever.min}
                  max={lever.max}
                  step={lever.step || (lever.max - lever.min) / 80}
                  value={lever.value}
                  aria-label={`${lever.label} what-if`}
                  onChange={(e) => setLever(lever.tag, Number(e.target.value), lever.baseline)}
                />
                <div className="gf-lane-read">
                  <span>
                    {lever.value.toFixed(lever.unit === "kgf/cm²" || lever.tag === "R" ? 2 : 0)} {lever.unit}
                  </span>
                  <span>
                    band {lever.low.toFixed(lever.tag === "R" || lever.unit === "kgf/cm²" ? 2 : 0)}–
                    {lever.high.toFixed(lever.tag === "R" || lever.unit === "kgf/cm²" ? 2 : 0)}
                  </span>
                </div>
              </label>
            );
          })}
          {!levers.length && <p className="muted">{busy ? "Reading the furnace hour…" : "Golden field is waiting for the twin."}</p>}
        </div>

        <aside className="gf-off">
          <p className="gf-kicker">Largest diversions</p>
          {worst.length === 0 && <p className="muted">Every shown tag is inside its golden band.</p>}
          {worst.map((p) => {
            const lever = LEVERS.some((l) => l.tag === p.tag);
            return (
              <button
                key={p.tag}
                type="button"
                className={`gf-chip gf-chip-${p.simulated_golden_status}`}
                disabled={!lever}
                title={lever ? "Move this lever to the golden center" : "Response tag. Move the levers that feed this zone."}
                onClick={() => {
                  if (!lever) return;
                  const center = Number(p.golden_center ?? (Number(p.golden_low) + Number(p.golden_high)) / 2);
                  setLever(p.tag, center, Number(p.baseline));
                }}
              >
                <b>{p.tag}</b>
                <span>{p.simulated_golden_status === "below_golden" ? "low" : "high"}</span>
                <small>{lever ? p.zone : `${p.zone} · response`}</small>
              </button>
            );
          })}
        </aside>
      </div>
    </section>
  );
}
