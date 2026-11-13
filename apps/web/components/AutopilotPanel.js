"use client";

import { useEffect, useState } from "react";
import { API } from "./Frame";

export function AutopilotPanel({ hour, targetProd, onApplyTwin }) {
  const [plan, setPlan] = useState(null);
  const [dispatchNote, setDispatchNote] = useState("");

  useEffect(() => {
    if (!hour) return undefined;
    let cancel = false;
    fetch(`${API}/autopilot/advise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ t: hour, target_production: Number(targetProd) || 4500 }),
    })
      .then((r) => r.json())
      .then((body) => {
        if (!cancel && body && Array.isArray(body.steps)) setPlan(body);
      })
      .catch(() => {});
    return () => {
      cancel = true;
    };
  }, [hour, targetProd]);

  async function tryDispatch() {
    setDispatchNote("");
    try {
      const res = await fetch(`${API}/autopilot/dispatch`, { method: "POST" });
      const body = await res.json().catch(() => ({}));
      setDispatchNote(body.detail || "Dispatch refused. No write path to SCADA.");
    } catch {
      setDispatchNote("Dispatch refused. No write path to SCADA.");
    }
  }

  return (
    <section className="autopilot">
      <header>
        <p className="gf-kicker">Advisory autopilot · write path absent</p>
        <h3>Hold production by the golden band</h3>
        <p className="muted">{plan?.situation || "Reading the current hour and the sensor bands."}</p>
      </header>
      <div className="ap-actions">
        <button type="button" className="primary-btn" onClick={onApplyTwin} disabled={!plan?.steps?.length}>
          Apply on the advisory twin
        </button>
        <button type="button" onClick={tryDispatch}>
          Send to SCADA
        </button>
      </div>
      {dispatchNote && <p className="ap-block">{dispatchNote}</p>}
      <ol className="ap-steps">
        {(plan?.steps || []).map((step) => (
          <li key={step.tag}>
            <b>{step.label}</b>
            <span>
              {step.now} → {step.golden_center} {step.unit}
            </span>
            <small>{step.shadow_plugins?.[0]?.command} · not sent</small>
          </li>
        ))}
        {plan && plan.steps.length === 0 && <li>Manipulated tags are already inside the golden band.</li>}
      </ol>
    </section>
  );
}
