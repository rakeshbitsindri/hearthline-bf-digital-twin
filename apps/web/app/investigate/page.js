"use client";

import { useEffect, useState } from "react";
import { API } from "../../components/Frame";

export default function Investigate() {
  const [twin, setTwin] = useState(null);
  const [gates, setGates] = useState([]);
  const [sensitivity, setSensitivity] = useState(null);
  const [targetProd, setTargetProd] = useState(4500);
  const [shortfalls, setShortfalls] = useState(null);
  const [goldenRanges, setGoldenRanges] = useState(null);

  useEffect(() => {
    fetch(`${API}/furnace`)
      .then((r) => r.json())
      .then(async (furnace) => {
        const [state, diagnosis, sens, sf, gr] = await Promise.all([
          fetch(`${API}/twin?t=${encodeURIComponent(furnace.to)}`).then((r) => r.json()),
          fetch(`${API}/diagnose`).then((r) => r.json()),
          fetch(`${API}/sensitivity`).then((r) => r.json()),
          fetch(`${API}/shortfalls?target_production=4500&limit=12`).then((r) => r.json()),
          fetch(`${API}/golden-ranges?target_production=4500`).then((r) => r.json()),
        ]);
        setTwin(state);
        setGates(diagnosis.gates || []);
        setSensitivity(sens);
        setShortfalls(sf);
        setGoldenRanges(gr);
      });
  }, []);

  async function refreshTarget(newTarget) {
    setTargetProd(newTarget);
    const [sf, gr] = await Promise.all([
      fetch(`${API}/shortfalls?target_production=${newTarget}&limit=12`).then((r) => r.json()),
      fetch(`${API}/golden-ranges?target_production=${newTarget}`).then((r) => r.json()),
    ]);
    setShortfalls(sf);
    setGoldenRanges(gr);
  }

  if (!twin || !sensitivity) return <p className="muted">Loading cross-parameter sensitivity matrix & probes…</p>;

  const inputs = sensitivity.present_inputs || [];
  const keyOutputs = ["Si", "dP", "dPu", "dPl", "CO2", "H2", "Ph", "Tp1", "Tp4", "Tp8"].filter(
    (o) => sensitivity.correlations?.[o]
  );

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", marginBottom: "1rem" }}>
        <div>
          <h2>Investigate · Historical Shortfall Root-Cause Attribution & Golden Range Reference</h2>
          <p className="muted" style={{ margin: 0 }}>
            Active dataset: <b>{sensitivity.dataset_name}</b> ({sensitivity.rows_trained?.toLocaleString()} operating hours analyzed).
            Select required production to inspect historical shortfall episodes and parameter Golden Ranges.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span className="muted">Required Production:</span>
          {[3800, 4200, 4500, 4850].map((p) => (
            <button
              key={p}
              type="button"
              className={Number(targetProd) === p ? "primary-btn" : ""}
              onClick={() => refreshTarget(p)}
            >
              {p} t/d
            </button>
          ))}
        </div>
      </div>

      {shortfalls && (
        <>
          <h3>
            Historical Production Drop Episodes vs Golden Range @ {shortfalls.target_production} t/d (
            {shortfalls.total_shortfall_hours_detected?.toLocaleString()} shortfall hours,{" "}
            {shortfalls.constant_wind_shortfall_hours?.toLocaleString()} constant-wind hours)
          </h3>
          <table style={{ marginBottom: "1.6rem" }}>
            <thead>
              <tr>
                <th>Historical Timestamp</th>
                <th>Category</th>
                <th>Actual vs 72h Ref</th>
                <th>Shortfall Drop</th>
                <th>Primary Golden Range Root Causes (Lag-Aligned)</th>
              </tr>
            </thead>
            <tbody>
              {(shortfalls.episodes || []).map((ep) => (
                <tr key={ep.t}>
                  <td style={{ fontFamily: "IBM Plex Mono, monospace" }}>
                    <b>{ep.t}</b>
                  </td>
                  <td>
                    <span className="badge">{ep.category.replace(/_/g, " ")}</span>
                  </td>
                  <td>
                    <b>{ep.actual_production_t_d} t/d</b> <span className="muted">(72h: {ep.rolling_72h_production_t_d} t/d)</span>
                  </td>
                  <td className="down">
                    <b>−{Math.max(ep.drop_vs_rolling_72h_t_d, ep.shortfall_vs_target_t_d).toFixed(0)} t/d</b>
                  </td>
                  <td>
                    {(ep.top_causes || []).map((c) => (
                      <div key={c.tag} style={{ fontSize: "0.76rem", marginBottom: "0.2rem" }}>
                        <span className={`golden-badge golden-badge-${c.status}`} style={{ marginRight: "0.35rem" }}>
                          {c.tag} {c.status === "below_golden" ? "BELOW" : "ABOVE"}
                        </span>
                        <b>
                          {c.value_at_lag} {c.unit}
                        </b>{" "}
                        vs Golden [{c.golden_low} to {c.golden_high}] -&gt;{" "}
                        <em className="down">−{c.estimated_loss_t_d} t/d ({c.share_of_shortfall_pct}%)</em> ·{" "}
                        <span className="muted">{c.mechanism}</span>
                      </div>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h2>Learned Cross-Parameter Lag-Aligned Correlation Matrix</h2>
      <div className="matrix-scroll" style={{ overflowX: "auto", marginBottom: "1.5rem" }}>
        <table>
          <thead>
            <tr>
              <th>Output \ Input</th>
              <th>Model R²</th>
              {inputs.map((inCol) => (
                <th key={inCol}>{inCol}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {keyOutputs.map((outCol) => (
              <tr key={outCol}>
                <td>
                  <b>{outCol}</b>
                </td>
                <td>{(sensitivity.r2_scores?.[outCol] ?? 0).toFixed(2)}</td>
                {inputs.map((inCol) => {
                  const c = sensitivity.correlations?.[outCol]?.[inCol] ?? 0;
                  const bg =
                    c >= 0
                      ? `rgba(224, 122, 61, ${Math.min(0.65, Math.abs(c) * 1.4)})`
                      : `rgba(143, 191, 182, ${Math.min(0.65, Math.abs(c) * 1.4)})`;
                  return (
                    <td key={inCol} style={{ background: bg, fontFamily: "IBM Plex Mono, monospace", fontSize: "0.78rem" }}>
                      {c >= 0 ? "+" : ""}
                      {c.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {goldenRanges && (
        <>
          <h2>All-Parameter Golden Range Catalog @ {goldenRanges.target_production} t/d</h2>
          <table style={{ marginBottom: "1.6rem" }}>
            <thead>
              <tr>
                <th>Tag</th>
                <th>Role / Zone</th>
                <th>Golden Range @ {goldenRanges.target_production} t/d</th>
                <th>Warning if Below Golden Range</th>
                <th>Warning if Above Golden Range</th>
              </tr>
            </thead>
            <tbody>
              {Object.values(goldenRanges.ranges || {}).map((g) => (
                <tr key={g.tag}>
                  <td>
                    <b>{g.tag}</b>
                    <div>
                      <small className="muted">{g.label}</small>
                    </div>
                  </td>
                  <td>
                    <span className="badge">{g.role}</span> · <small className="muted">{g.zone}</small>
                  </td>
                  <td style={{ fontFamily: "IBM Plex Mono, monospace" }}>
                    <b>
                      {g.golden_low} to {g.golden_high} {g.unit}
                    </b>
                    <div>
                      <small className="muted">Center: {g.golden_center}</small>
                    </div>
                  </td>
                  <td style={{ fontSize: "0.75rem" }}>{g.below_warning}</td>
                  <td style={{ fontSize: "0.75rem" }}>{g.above_warning}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h2>7-Gate Production Shortfall & Observability Protocol</h2>
      <table>
        <thead>
          <tr>
            <th>Gate</th>
            <th>Status</th>
            <th>Diagnostic Evidence</th>
          </tr>
        </thead>
        <tbody>
          {gates.map((gate) => (
            <tr key={gate.gate}>
              <td>
                <b>
                  Gate {gate.gate} · {gate.name}
                </b>
              </td>
              <td className={gate.status === "ready" ? "ok status" : "not status"}>{gate.status}</td>
              <td>{gate.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
