"use client";

import { useEffect, useState } from "react";
import { API } from "../../components/Frame";

export default function Decide() {
  const [card, setCard] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [optResult, setOptResult] = useState(null);
  const [hour, setHour] = useState("");
  const [targets, setTargets] = useState({ prod: 4650, si: 0.45, maxDp: 1.52, minRaft: 2000, maxRaft: 2250 });

  useEffect(() => {
    fetch(`${API}/furnace`)
      .then((r) => r.json())
      .then(async (furnace) => {
        setHour(furnace.to);
        const [model, prediction, opt] = await Promise.all([
          fetch(`${API}/model-card`).then((r) => r.json()),
          fetch(`${API}/predict/silicon?t=${encodeURIComponent(furnace.to)}`).then((r) => r.json()),
          fetch(`${API}/optimize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ t: furnace.to, target_production: 4650, target_si: 0.45, max_dp: 1.52 }),
          }).then((r) => r.json()),
        ]);
        setCard(model);
        setForecast(prediction);
        setOptResult(opt);
      });
  }, []);

  async function handleOptimize(e) {
    e.preventDefault();
    const res = await fetch(`${API}/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        t: hour,
        target_production: Number(targets.prod),
        target_si: Number(targets.si),
        max_dp: Number(targets.maxDp),
        min_raft: Number(targets.minRaft),
        max_raft: Number(targets.maxRaft),
      }),
    }).then((r) => r.json());
    setOptResult(res);
  }

  if (!card || !forecast) return <p className="muted">Loading walk-forward model card and optimizer…</p>;

  return (
    <section>
      <h2>Decide · Inverse Target Production Optimizer & Walk-Forward Forecast</h2>
      <p className="muted">
        Served silicon model: <b>{forecast.served_model}</b>. Conformal 90% interval: {forecast.low.toFixed(3)} to{" "}
        {forecast.high.toFixed(3)} wt%.
      </p>

      <div className="grid" style={{ marginBottom: "1.4rem" }}>
        <div className="card">
          <span>Next Cast [Si], estimated</span>
          <strong>{forecast.point.toFixed(3)} wt%</strong>
        </div>
        <div className="card">
          <span>90% Conformal Interval</span>
          <strong>
            {forecast.low.toFixed(3)} to {forecast.high.toFixed(3)}
          </strong>
        </div>
        <div className="card">
          <span>Persistence Baseline RMSE</span>
          <strong>{card.persistence_rmse.toFixed(4)} wt%</strong>
        </div>
        <div className="card">
          <span>LightGBM Walk-Forward RMSE</span>
          <strong>{card.lightgbm_rmse.toFixed(4)} wt%</strong>
        </div>
      </div>

      <form onSubmit={handleOptimize} className="transport" style={{ marginBottom: "1.2rem" }}>
        <label>
          Target Production (t/d)
          <input
            type="number"
            value={targets.prod}
            onChange={(e) => setTargets({ ...targets, prod: e.target.value })}
          />
        </label>
        <label>
          Target [Si] (wt%)
          <input
            type="number"
            step="0.01"
            value={targets.si}
            onChange={(e) => setTargets({ ...targets, si: e.target.value })}
          />
        </label>
        <label>
          Max ΔP (kgf/cm²)
          <input
            type="number"
            step="0.02"
            value={targets.maxDp}
            onChange={(e) => setTargets({ ...targets, maxDp: e.target.value })}
          />
        </label>
        <button type="submit" className="primary-btn">
          Calculate Optimal Setpoints
        </button>
      </form>

      {optResult && (
        <>
          <div className="grid" style={{ marginBottom: "1.2rem" }}>
            <div className="card">
              <span>Achieved Production</span>
              <strong>{optResult.achieved_production} t/day</strong>
            </div>
            <div className="card">
              <span>Achieved [Si] & RAFT</span>
              <strong>
                {optResult.achieved_si}% · {optResult.achieved_raft}°C
              </strong>
            </div>
            <div className="card">
              <span>Achieved ΔP & Fuel Rate</span>
              <strong>
                {optResult.achieved_dp} kgf/cm² · {optResult.achieved_fuel_rate} kg/t
              </strong>
            </div>
            <div className="card">
              <span>Binding Ceiling ({optResult.binding_ceiling})</span>
              <strong>{optResult.max_feasible_production} t/day</strong>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Manipulated Parameter</th>
                <th>Current Value</th>
                <th>Current Golden Status</th>
                <th>Golden Range @ Target</th>
                <th>Recommended Setpoint</th>
                <th>Difference (Δ)</th>
                <th>Validated Envelope</th>
                <th>Response Lag</th>
              </tr>
            </thead>
            <tbody>
              {optResult.recommendations.map((r) => (
                <tr key={r.tag} title={r.current_warning || "Inside Golden Range"}>
                  <td>
                    <b>{r.label}</b> ({r.tag})
                  </td>
                  <td>
                    {r.current} {r.unit}
                  </td>
                  <td>
                    <span className={`golden-badge golden-badge-${r.current_golden_status || "in_golden"}`}>
                      {r.current_golden_status === "below_golden"
                        ? "BELOW GOLDEN"
                        : r.current_golden_status === "above_golden"
                          ? "ABOVE GOLDEN"
                          : "IN GOLDEN"}
                    </span>
                  </td>
                  <td style={{ fontFamily: "IBM Plex Mono, monospace" }}>
                    {r.golden_low} to {r.golden_high} {r.unit}
                  </td>
                  <td>
                    <b>
                      {r.recommended} {r.unit}
                    </b>
                  </td>
                  <td className={r.delta >= 0 ? "up" : "down"}>
                    {r.delta >= 0 ? "+" : ""}
                    {r.delta} {r.unit}
                  </td>
                  <td>
                    {r.envelope_min} to {r.envelope_max} {r.unit}
                  </td>
                  <td>{r.lag_h}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
