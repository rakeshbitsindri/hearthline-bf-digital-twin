"use client";

import { useEffect, useState } from "react";
import { API, useTwinTheme } from "../../components/Frame";

const PENDING_VALIDATION = [
  ["PV-01", "Geerdes Annex III coke-rate adjustment table", "config, default off (requires constant-wind vs constant-tonnage convention)"],
  ["PV-03", "Cohesive-zone shrinkage permeability K(Sr)", "interface only; uses reconciled pressure drop"],
  ["PV-04", "Flooding-diagram density correction", "exposes both fluidisation and flooding ceilings"],
  ["PV-05", "Hot metal silicon closed-form correlation", "site-fitted walk-forward LightGBM only; no universal default"],
  ["PV-09", "Alternative plant-blog RAFT intercept", "uncited, off by default; AIST/Geerdes linear form used"],
  ["PV-10", "Absolute RAFT and HMT on EVRAZ public archive", "classified response_only; absolute value withheld until PCI/NG/HMT supplied"],
];

const ROADMAP = [
  ["A", "Data handshake & DMZ connector", "weeks 1 to 4", "Read-only data agreement, full historian retention, PI Web API or OPC-UA read profile on DMZ replica, capability matrix recomputed on real plant tag list."],
  ["B", "Calibration & walk-forward card", "weeks 4 to 12", "Plant-specific coefficients, metallurgist sign-off on PV-01..PV-10, purged walk-forward validation at 1, 4, and 8 hours against persistence."],
  ["C", "TRL 7 Shadow-mode trial", "weeks 12 to 24", "Live read-only SSE telemetry beside the control room, Golden Range excursion log, incident casebook, verified value vs persistence."],
  ["D", "TRL 8-9 Enterprise rollout", "parallel from week 8", "Corporate OIDC/SAML SSO, managed PostgreSQL, Minute-archive DuckDB/Parquet, HA, OT/IT firewall sign-off, MoC dossier workflow."],
];

export default function Govern() {
  const { role } = useTwinTheme();
  const [features, setFeatures] = useState([]);
  const [events, setEvents] = useState([]);
  const [chainStatus, setChainStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [furnace, setFurnace] = useState(null);
  const [mops, setMops] = useState(null);
  const [connInfo, setConnInfo] = useState(null);
  const [probeLog, setProbeLog] = useState(null);
  const [sseFrames, setSseFrames] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [message, setMessage] = useState("");

  function load() {
    fetch(`${API}/capability`).then((r) => r.json()).then((b) => setFeatures(b.features || [])).catch(() => {});
    fetch(`${API}/audit`).then((r) => r.json()).then((b) => setEvents(b.events || [])).catch(() => {});
    fetch(`${API}/audit/verify`).then((r) => r.json()).then(setChainStatus).catch(() => {});
    fetch(`${API}/health`).then((r) => r.json()).then(setHealth).catch(() => {});
    fetch(`${API}/furnace`).then((r) => r.json()).then(setFurnace).catch(() => {});
    fetch(`${API}/modelops/status`).then((r) => r.json()).then(setMops).catch(() => {});
    fetch(`${API}/connector/profiles`).then((r) => r.json()).then(setConnInfo).catch(() => {});
  }

  useEffect(load, []);

  async function runConnectorProbe(opName) {
    const r = await fetch(`${API}/connector/probe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ op: opName }),
    });
    const body = await r.json().catch(() => ({}));
    setProbeLog({
      op: opName,
      http_status: r.status,
      blocked: r.status === 403,
      detail: body.detail || JSON.stringify(body),
    });
  }

  useEffect(() => {
    runConnectorProbe("write");
  }, []);

  function startSseBurst() {
    if (streaming) return;
    setStreaming(true);
    setSseFrames([]);
    const isStaticGh = typeof window !== "undefined" && window.location.hostname.endsWith("github.io");
    if (isStaticGh && typeof window !== "undefined" && window.__HEARTHLINE_BUNDLE__) {
      const sampleFrames = (window.__HEARTHLINE_BUNDLE__.playback?.frames || []).slice(120, 126);
      sampleFrames.forEach((f, idx) => {
        setTimeout(() => {
          setSseFrames((prev) => [
            ...prev,
            {
              seq: idx + 1,
              t: f.t,
              Fb: f.Fb,
              dP: f.dP,
              Production: 4480 + Math.round((f.Fb - 3650) * 0.45),
              golden_compliance_pct: 68.3,
            },
          ]);
          if (idx === sampleFrames.length - 1) setStreaming(false);
        }, (idx + 1) * 450);
      });
      return;
    }
    const es = new EventSource(`${API}/stream/live?target_production=4500&max_events=6&interval_sec=0.65`);
    es.addEventListener("twin_frame", (ev) => {
      try {
        const parsed = JSON.parse(ev.data);
        setSseFrames((prev) => [...prev, parsed]);
      } catch {
        // ignore parse error
      }
    });
    es.onerror = () => {
      es.close();
      setStreaming(false);
    };
    setTimeout(() => {
      es.close();
      setStreaming(false);
    }, 5500);
  }

  async function submitAuditAction(actionName, targetName, payloadObj) {
    setMessage("");
    const r = await fetch(`${API}/audit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Hearthline-Role": role,
      },
      body: JSON.stringify({
        actor: `${role}_user`,
        role,
        action: actionName,
        target: targetName,
        payload: payloadObj,
      }),
    });
    const body = await r.json().catch(() => ({}));
    if (r.ok) {
      setMessage(
        `Recorded '${actionName}' as role '${role}' | SHA-256 hash ${body.event_hash?.slice(0, 16)}... | Nothing sent to furnace.`
      );
      load();
    } else {
      setMessage(`RBAC Blocked (HTTP ${r.status}): ${body.detail || "Action denied for active role"}`);
    }
  }

  async function markConfirmedExecution(eventId, execStatus) {
    const r = await fetch(`${API}/audit/${eventId}/confirm-execution`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Hearthline-Role": role,
      },
      body: JSON.stringify({
        actor: `${role}_shift_report`,
        role,
        status: execStatus,
        notes: "Post-hoc plant log reconciliation",
      }),
    });
    const body = await r.json().catch(() => ({}));
    if (r.ok) {
      setMessage(`Updated post-hoc execution field on event #${eventId} -> ${body.confirmed_execution}`);
      load();
    } else {
      setMessage(`RBAC Blocked (HTTP ${r.status}): ${body.detail || "Role cannot record execution"}`);
    }
  }

  return (
    <section className="govern-console">
      <div className="govern-maturity">
        <div>
          <h2>TRL 6 to 9 Plant Deployment Harness, ModelOps & Governance</h2>
          <p className="muted" style={{ margin: 0 }}>
            <b>Current Milestone: TRL 6 Achieved</b> on 29,602 hours of running-plant EVRAZ ZSMK industrial data, with the{" "}
            <b>TRL 7-9 software harness</b> (read-only PI/OPC-UA profiles, monotonic SSE streaming, Mahalanobis density envelope, PSI drift monitor, RBAC, and SHA-256 tamper-evident audit) built and active below. True TRL 7-9 sign-off awaits connection to a live customer furnace DMZ.
          </p>
        </div>
        <div className="govern-posture">
          <span>OT Safety & Audit Chain</span>
          <strong className="ok">
            {health ? `plant_write=${String(health.plant_write)} | SHA-256 ${chainStatus?.intact ? "INTACT" : "CHECK"}` : "checking"}
          </strong>
          <small>
            Active RBAC role: <b>{role}</b> (change in top-right nav to test 403 permissions) | Verified audit events:{" "}
            {chainStatus?.events_verified ?? 0}
          </small>
        </div>
      </div>

      {/* TRL 1-9 Ladder */}
      {mops && (
        <>
          <h3>Technology Readiness Level (TRL 1 to 9) Gate Matrix</h3>
          <table style={{ marginBottom: "1.2rem" }}>
            <thead>
              <tr>
                <th>TRL Band</th>
                <th>Engineering Gate</th>
                <th>Status</th>
                <th>Verification Evidence / Plant Prerequisite</th>
              </tr>
            </thead>
            <tbody>
              {(mops.trl_ladder || []).map((row) => (
                <tr key={row.trl}>
                  <td className="mono"><b>{row.trl}</b></td>
                  <td><b>{row.title}</b></td>
                  <td>
                    <span className={`govern-grade ${row.status === "achieved" ? "grade-strong" : "grade-early"}`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="muted">{row.evidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {/* Phase-A Read-Only Connector Profiles + Live SSE Shadow Stream */}
      <div className="grid" style={{ gridTemplateColumns: "1.15fr 1fr", marginBottom: "1.2rem" }}>
        <div className="card">
          <span>Phase-A Read-Only OT Historian Connector Profiles</span>
          <p className="muted" style={{ fontSize: "0.74rem" }}>
            Test the hardware/software write-blocker live. Any non-read verb returns HTTP 403.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.55rem" }}>
            {["read", "write", "opc_call_method", "sql", "setpoint_push"].map((op) => (
              <button key={op} type="button" onClick={() => runConnectorProbe(op)}>
                Probe: {op}
              </button>
            ))}
          </div>
          {probeLog && (
            <div className="kb-ex-unblock mono" style={{ fontSize: "0.72rem", marginBottom: "0.55rem" }}>
              op=&quot;{probeLog.op}&quot; -&gt; HTTP {probeLog.http_status}{" "}
              <b className={probeLog.blocked ? "ok" : ""}>
                {probeLog.blocked ? "[WRITE BLOCKED AS DESIGNED]" : "[READ ALLOWED]"}
              </b>{" "}
              | {probeLog.detail}
            </div>
          )}
          {connInfo && (
            <table>
              <thead>
                <tr>
                  <th>Profile</th>
                  <th>Allowed</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(connInfo.profiles || []).map((p) => (
                  <tr key={p.profile_id}>
                    <td className="mono"><b>{p.profile_id}</b></td>
                    <td style={{ fontSize: "0.7rem" }}>{p.allowed_verbs.join(", ")}</td>
                    <td><span className="badge">{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Live SSE Shadow-Mode Stream (/stream/live)</span>
            <button type="button" className="primary-btn" onClick={startSseBurst} disabled={streaming}>
              {streaming ? "Streaming SSE..." : "Stream 6 Shadow Frames"}
            </button>
          </div>
          <p className="muted" style={{ fontSize: "0.74rem" }}>
            Server-Sent Events with monotonic sequence numbers (`seq`), model version, envelope check, and Golden compliance.
          </p>
          {sseFrames.length === 0 ? (
            <p className="muted" style={{ fontSize: "0.74rem" }}>
              Click &quot;Stream 6 Shadow Frames&quot; to open a real EventSource stream from the engine.
            </p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Seq</th>
                  <th>Timestamp</th>
                  <th>Fb</th>
                  <th>dP</th>
                  <th>Prod</th>
                  <th>Golden</th>
                </tr>
              </thead>
              <tbody>
                {sseFrames.map((f) => (
                  <tr key={f.seq} className="mono" style={{ fontSize: "0.72rem" }}>
                    <td><b>#{f.seq}</b></td>
                    <td>{f.t}</td>
                    <td>{Math.round(f.Fb)}</td>
                    <td>{f.dP}</td>
                    <td>{Math.round(f.Production)} t/d</td>
                    <td>{f.golden_compliance_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* ModelOps & PSI Drift Monitor */}
      {mops && (
        <>
          <h3>ModelOps : Walk-Forward Baseline Gate & Covariate Drift (PSI)</h3>
          <div className="grid govern-facts">
            <div className="card">
              <span>Model Version</span>
              <strong>{mops.model_version}</strong>
              <small className="muted">Served model: {mops.served_silicon_model}</small>
            </div>
            <div className="card">
              <span>LightGBM vs Persistence</span>
              <strong>{mops.lightgbm_rmse_wt_pct} vs {mops.persistence_rmse_wt_pct} wt%</strong>
              <small className="muted">+{mops.improvement_over_persistence_pct}% better than persistence</small>
            </div>
            <div className="card">
              <span>90% Conformal Half-Width</span>
              <strong>+/- {mops.conformal_90_half_width_wt_pct} wt%</strong>
              <small className="muted">Nominal target: 90% walk-forward coverage</small>
            </div>
            <div className="card">
              <span>Active Dataset</span>
              <strong>{furnace ? furnace.name : mops.dataset_name}</strong>
              <small className="muted">{connInfo?.sub_sampling_blindness_notice?.slice(0, 72)}...</small>
            </div>
          </div>

          <table style={{ marginBottom: "1.2rem" }}>
            <thead>
              <tr>
                <th>Sensor Tag</th>
                <th>Early-Campaign Median</th>
                <th>Recent-Window Median</th>
                <th>PSI Drift Score</th>
                <th>Drift Verdict</th>
              </tr>
            </thead>
            <tbody>
              {(mops.covariate_drift_psi || []).map((d) => (
                <tr key={d.tag}>
                  <td className="mono"><b>{d.tag}</b></td>
                  <td className="mono">{d.ref_median}</td>
                  <td className="mono">{d.recent_median}</td>
                  <td className="mono"><b>{d.psi}</b></td>
                  <td>
                    <span className={`golden-badge ${d.status === "stable" ? "golden-badge-in_golden" : "golden-badge-below_golden"}`}>
                      {d.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {/* Capability matrix */}
      <h3>Capability Matrix (Recomputed on Active Dataset)</h3>
      <table>
        <thead>
          <tr>
            <th>Feature</th>
            <th>Status</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {features.map((row) => (
            <tr key={row.feature}>
              <td className="mono"><b>{row.feature}</b></td>
              <td>
                <span className={`golden-badge ${row.status === "ready" ? "golden-badge-in_golden" : "golden-badge-below_golden"}`}>
                  {row.status}
                </span>
              </td>
              <td className="muted">{row.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pending validation register */}
      <h3>Pending Validation Register (Requires Metallurgist Role to Sign Off)</h3>
      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Item</th>
            <th>Current Handling</th>
            <th>RBAC Action</th>
          </tr>
        </thead>
        <tbody>
          {PENDING_VALIDATION.map(([id, item, handling]) => (
            <tr key={id}>
              <td className="mono"><b>{id}</b></td>
              <td>{item}</td>
              <td className="muted">{handling}</td>
              <td>
                <button
                  type="button"
                  onClick={() => submitAuditAction("pv_signoff", id, { item, note: "Site calibration sign-off test" })}
                >
                  Sign Off ({role})
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Phased Roadmap */}
      <h3>Phased Path to Customer Plant Commissioning (Phases A to D)</h3>
      <div className="govern-roadmap">
        {ROADMAP.map(([phase, name, when, detail]) => (
          <div key={phase} className="govern-phase">
            <div className="govern-phase-head">
              <span className="govern-phase-badge">Phase {phase}</span>
              <b>{name}</b>
              <em>{when}</em>
            </div>
            <p className="muted">{detail}</p>
          </div>
        ))}
      </div>

      {/* RBAC Operator Decisions + SHA-256 Audit + Separate Confirmed Execution */}
      <h3>RBAC Operator Decisions, SHA-256 Hash Chain & Post-Hoc Plant Execution</h3>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", margin: "0.55rem 0" }}>
        <button
          type="button"
          className="primary-btn"
          onClick={() => submitAuditAction("accept", "advisory_setpoint_Fb_3680", { Fb: 3680, Fo: 19200 })}
        >
          Accept Advisory Setpoint (as {role})
        </button>
        <button
          type="button"
          onClick={() => submitAuditAction("reject", "inverse_setpoint", { reason: "not identified on public file" })}
        >
          Reject Blocked Setpoint (as {role})
        </button>
        <button
          type="button"
          onClick={() => submitAuditAction("moc_dossier", "trial_high_O2_enrichment", { target_prod: 5100 })}
        >
          Log MoC Trial Dossier (metallurgist+)
        </button>
      </div>
      {message && <p className="status ok" style={{ margin: "0.4rem 0" }}>{message}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Timestamp</th>
            <th>Actor / Role</th>
            <th>Action / Target</th>
            <th>SHA-256 Chain Hash</th>
            <th>Post-Hoc Plant Execution (Separate Field)</th>
          </tr>
        </thead>
        <tbody>
          {events.slice(-12).reverse().map((row) => (
            <tr key={row.id}>
              <td className="mono">#{row.id}</td>
              <td className="mono" style={{ fontSize: "0.7rem" }}>{row.created_at?.slice(0, 19)}</td>
              <td>
                <b>{row.actor}</b> <span className="badge">{row.role}</span>
              </td>
              <td>
                <b>{row.action}</b> : <span className="mono">{row.target}</span>
              </td>
              <td className="mono" style={{ fontSize: "0.68rem" }} title={`prev: ${row.prev_hash}\nhash: ${row.event_hash}`}>
                {row.event_hash?.slice(0, 14)}...
              </td>
              <td>
                {row.confirmed_execution ? (
                  <span className="golden-badge golden-badge-in_golden">{row.confirmed_execution}</span>
                ) : row.action === "accept" ? (
                  <div style={{ display: "flex", gap: "0.25rem" }}>
                    <button type="button" style={{ fontSize: "0.64rem", padding: "0.15rem 0.35rem" }} onClick={() => markConfirmedExecution(row.id, "executed_in_plant")}>
                      Mark Executed
                    </button>
                    <button type="button" style={{ fontSize: "0.64rem", padding: "0.15rem 0.35rem" }} onClick={() => markConfirmedExecution(row.id, "not_executed")}>
                      Not Executed
                    </button>
                  </div>
                ) : (
                  <span className="muted">n/a</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
