"use client";

import { useEffect, useMemo, useState } from "react";
import { API } from "./Frame";

const WINDOWS = [
  ["1h", "1 hour"],
  ["6h", "6 hours"],
  ["24h", "1 day"],
  ["7d", "7 days"],
  ["30d", "30 days"],
];

const HEADLINE = ["Production", "Si", "dP", "HMT", "RAFT", "Fb", "EtaCO"];
const ROLE_RANK = { outcome: 0, manipulated: 1, disturbance: 2, state_response: 3, derived_latent: 4 };

function fmt(value) {
  if (value == null || Number.isNaN(Number(value))) return "—";
  const n = Number(value);
  const abs = Math.abs(n);
  if (abs >= 100) return n.toFixed(0);
  if (abs >= 10) return n.toFixed(1);
  return n.toFixed(2);
}

function stateLabel(status) {
  if (status === "below_golden") return "LOW";
  if (status === "above_golden") return "HIGH";
  if (status === "in_golden") return "IN";
  return "";
}

function Spark({ points }) {
  const vals = (points || []).filter((v) => v != null);
  if (vals.length < 2) return <svg className="ps-spark" viewBox="0 0 120 28" />;
  const min = Math.min(...vals);
  const max = Math.max(...vals);
  const span = max - min || 1;
  const d = vals
    .map((v, i) => {
      const x = (i / (vals.length - 1)) * 120;
      const y = 26 - ((v - min) / span) * 22;
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
  const up = vals[vals.length - 1] >= vals[0];
  return (
    <svg className="ps-spark" viewBox="0 0 120 28" aria-hidden="true">
      <path d={d} className={up ? "ps-up" : "ps-down"} />
    </svg>
  );
}

export function ParameterStats({ liveSensors = null, recovery = 0, onRecovery = null, caption = "", fineNow = null }) {
  const [windowId, setWindowId] = useState("24h");
  const [query, setQuery] = useState("");
  const [body, setBody] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancel = false;
    setError("");
    fetch(`${API}/stats/windows?window=${windowId}`)
      .then((r) => {
        if (!r.ok) throw new Error("stats unavailable");
        return r.json();
      })
      .then((data) => {
        if (!cancel) setBody(data);
      })
      .catch(() => {
        if (!cancel) setError("Long-window stats need the live archive API.");
      });
    return () => {
      cancel = true;
    };
  }, [windowId]);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const archive = new Map((body?.parameters || []).map((p) => [p.tag, p]));
    const source = liveSensors?.length
      ? liveSensors.map((p) => {
          const hist = archive.get(p.tag) || {};
          return {
            ...hist,
            tag: p.tag,
            label: p.label || hist.label || p.tag,
            unit: p.unit || hist.unit || "",
            role: p.role || hist.role || "",
            last: fineNow?.[p.tag] ?? p.simulated ?? p.baseline ?? hist.last,
            recorded: p.baseline,
            status: p.simulated_golden_status || "in_golden",
            golden_low: p.golden_low,
            golden_high: p.golden_high,
            golden_center: p.golden_center,
          };
        })
      : body?.parameters || [];
    return source
      .filter((p) => !q || `${p.tag} ${p.label} ${p.role}`.toLowerCase().includes(q))
      .sort((a, b) => (ROLE_RANK[a.role] ?? 9) - (ROLE_RANK[b.role] ?? 9) || a.tag.localeCompare(b.tag));
  }, [body, query, liveSensors, fineNow]);

  const headlines = HEADLINE.map((tag) => rows.find((p) => p.tag === tag)).filter(Boolean);

  return (
    <section className="param-stats">
      <header className="ps-head">
        <div>
          <p className="gf-kicker">{body?.origin === "synthetic" ? "Synthetic furnace · hourly samples" : "Archive range · hourly samples"}</p>
          <h3>{caption || (liveSensors ? "Sensors at this hour" : "Long-window stats for every parameter")}</h3>
          <p className="muted">
            {body?.dataset_name ? `${body.dataset_name}. ` : ""}
            Current reading on each card, with min, average, and max over the selected window.
            {body?.minute_note ? ` ${body.minute_note}` : ""}
          </p>
          {onRecovery && (
            <label className="ps-lever">
              <span>Bring levers to the golden level for this production</span>
              <input
                type="range"
                min="0"
                max="100"
                value={recovery}
                onChange={(e) => onRecovery(Number(e.target.value))}
              />
              <b>{recovery}%</b>
            </label>
          )}
        </div>
        <div className="ps-controls">
          {WINDOWS.map(([id, label]) => (
            <button key={id} type="button" className={windowId === id ? "primary-btn" : ""} onClick={() => setWindowId(id)}>
              {label}
            </button>
          ))}
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter tag or name" aria-label="Filter parameters" />
        </div>
      </header>
      {body && (
        <p className="ps-range">
          {body.rows} hourly samples · {body.from} → {body.to} · step {body.sampling_interval}
        </p>
      )}
      {error && <p className="muted">{error}</p>}
      {headlines.length > 0 && (
        <div className="ix-strip">
          {headlines.map((p) => (
            <div key={p.tag} className={`ix-counter ix-${p.status || "idle"}`}>
              <span>{p.label}</span>
              <strong>{fmt(p.last)}</strong>
              <em>{p.unit || p.tag}</em>
            </div>
          ))}
        </div>
      )}
      <div className="ix-table-wrap">
        <table className="ix-table">
          <thead>
            <tr>
              <th>Statistic</th>
              <th>Current</th>
              <th>Recorded</th>
              <th>Min</th>
              <th>Avg</th>
              <th>Max</th>
              <th>Δ</th>
              <th>State</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.tag} className={p.status ? `ix-row-${p.status}` : ""}>
                <td className="ix-name">
                  <b>{p.label}</b>
                  <small>{p.tag}</small>
                  <Spark points={p.spark} />
                </td>
                <td className="ix-num">{fmt(p.last)}</td>
                <td className="ix-num ix-dim">{fmt(p.recorded)}</td>
                <td className="ix-num">{fmt(p.min)}</td>
                <td className="ix-num">{fmt(p.avg)}</td>
                <td className="ix-num">{fmt(p.max)}</td>
                <td className={`ix-num ${Number(p.delta) >= 0 ? "ps-up-text" : "ps-down-text"}`}>
                  {p.delta == null ? "—" : `${Number(p.delta) >= 0 ? "+" : ""}${fmt(p.delta)}`}
                </td>
                <td><i className={`ix-state ix-state-${p.status || "none"}`}>{stateLabel(p.status) || "—"}</i></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
