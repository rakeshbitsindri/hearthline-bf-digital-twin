"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";

const links = [
  ["/", "Observe & Track"],
  ["/investigate", "Investigate"],
  ["/decide", "Decide"],
  ["/knowledge", "Knowledge & Plant Data"],
  ["/govern", "TRL & Govern"],
  ["/pitch", "Interactive Pitch"],
  ["/visits", "Visits"],
];

export const THEMES = [
  {
    id: "scada-slate",
    name: "SCADA Tactical",
    badge: "Cyan / Slate",
    desc: "High-contrast control room slate with cyan telemetry and emerald/amber/crimson alerts",
    canvasBg: "#070b12",
    shellColor: "#243044",
    bustleColor: "#3b4f6b",
    lightColor: "#e2f1ff",
  },
  {
    id: "hearth-amber",
    name: "Foundry Obsidian",
    badge: "Molten / Charcoal",
    desc: "Deep blast-furnace obsidian with molten iron amber and reducing-gas teal",
    canvasBg: "#0d0b09",
    shellColor: "#3c342b",
    bustleColor: "#6e4b32",
    lightColor: "#f5e6cf",
  },
  {
    id: "daylight-paper",
    name: "Daylight Blueprint",
    badge: "Light / Engineering",
    desc: "Crisp daylight control-room paper with deep navy ink and high-visibility alert badges",
    canvasBg: "#e6ecf2",
    shellColor: "#475569",
    bustleColor: "#64748b",
    lightColor: "#ffffff",
  },
  {
    id: "phosphor-terminal",
    name: "Phosphor Telemetry",
    badge: "Matrix / Oscilloscope",
    desc: "Ultra-fast anomaly spotting on deep oscilloscope black with phosphor green and plasma red",
    canvasBg: "#040806",
    shellColor: "#1b2e23",
    bustleColor: "#284736",
    lightColor: "#d1fae5",
  },
  {
    id: "titanium-industrial",
    name: "Titanium HMI",
    badge: "Gunmetal / Orange",
    desc: "Modern European metallurgy HMI gunmetal steel with safety orange and ice blue",
    canvasBg: "#11151c",
    shellColor: "#323b49",
    bustleColor: "#4a5568",
    lightColor: "#edf2f7",
  },
];

export const ROLES = ["operator", "metallurgist", "viewer", "ot_auditor", "admin"];

function buildEmbeddedClientSimulate(bundle, reqBody = {}) {
  const baseSim = JSON.parse(JSON.stringify(bundle.baseline_sim || {}));
  if (!baseSim.baseline_state) return baseSim;

  const frames = bundle.playback?.frames || [];
  const reqTime = reqBody.t || baseSim.t;
  const matchedFrame = frames.find((f) => f.t === reqTime);
  if (matchedFrame) {
    baseSim.t = matchedFrame.t;
    for (const k of ["Fb", "Fo", "Ph", "Pc", "Tc", "Pt", "Th", "dP", "CO2", "H2", "R", "Si", "dPu", "dPl"]) {
      if (matchedFrame[k] != null) baseSim.baseline_state[k] = Number(matchedFrame[k]);
    }
    if (Array.isArray(matchedFrame.tt)) {
      matchedFrame.tt.forEach((v, i) => { baseSim.baseline_state[`Tt${i + 1}`] = Number(v); });
    }
    if (Array.isArray(matchedFrame.tp)) {
      matchedFrame.tp.forEach((v, i) => { baseSim.baseline_state[`Tp${i + 1}`] = Number(v); });
    }
  }

  const deltas = reqBody.deltas || {};
  const overrides = reqBody.overrides || {};
  const targetProd = Number(reqBody.target_production) || 4500;
  const nearestPreset = [3800, 4000, 4300, 4500, 4850].reduce((a, b) =>
    Math.abs(b - targetProd) < Math.abs(a - targetProd) ? b : a
  );
  const gMap = (bundle.golden_presets && bundle.golden_presets[String(nearestPreset)]) || {};

  const bState = baseSim.baseline_state;
  const sState = { ...bState };
  for (const [k, v] of Object.entries(overrides)) {
    if (v != null) sState[k] = Number(v);
  }
  for (const [k, d] of Object.entries(deltas)) {
    if (d != null && Math.abs(Number(d)) > 1e-6) {
      sState[k] = Number(sState[k] ?? bState[k] ?? 0) + Number(d);
    }
  }

  // Coupled physics response for knob moves
  const dFb = (sState.Fb ?? 3650) - (bState.Fb ?? 3650);
  const dFo = (sState.Fo ?? 18500) - (bState.Fo ?? 18500);
  const dTh = (sState.Th ?? 1090) - (bState.Th ?? 1090);
  const dPt = (sState.Pt ?? 1.42) - (bState.Pt ?? 1.42);
  const dR = (sState.R ?? 4.0) - (bState.R ?? 4.0);
  const dPCI = (sState.PCI ?? 115) - (bState.PCI ?? 115);

  const dRaft = 0.82 * dTh + 0.0085 * dFo - 0.045 * dFb - 1.65 * dPCI;
  const dDp = 0.00048 * dFb + 0.000018 * dFo - 0.22 * dPt + 0.0018 * dPCI;
  const dProd = 0.45 * dFb + 0.056 * dFo - 4.2 * dPCI - Math.max(0, dDp * 320);
  const dHmt = 0.16 * dRaft - 24.0 * dR;
  const dSi = 0.0024 * dHmt - 0.00007 * dFb - 0.06 * dPt;

  baseSim.physics_kpis.RAFT = Number((baseSim.baseline_physics_kpis.RAFT + dRaft).toFixed(1));
  baseSim.physics_kpis.Production = Number((baseSim.baseline_physics_kpis.Production + dProd).toFixed(1));
  baseSim.physics_kpis.Productivity = Number((baseSim.physics_kpis.Production / 2000.0).toFixed(2));
  baseSim.physics_kpis.HMT = Number((baseSim.baseline_physics_kpis.HMT + dHmt).toFixed(1));
  baseSim.physics_kpis.dP = Number(((bState.dP ?? 1.44) + dDp).toFixed(3));
  baseSim.physics_kpis.Si = Number(((bState.Si ?? 0.47) + dSi).toFixed(3));

  sState.dPu = Number(((bState.dPu ?? 0.44) + dDp * 0.35).toFixed(3));
  sState.dPl = Number(((bState.dPl ?? 0.98) + dDp * 0.65).toFixed(3));
  sState.dP = Number((sState.dPu + sState.dPl).toFixed(3));
  sState.Ph = Number(((bState.Ph ?? 2.85) + dDp + dPt).toFixed(3));
  sState.Si = baseSim.physics_kpis.Si;
  sState.Production = baseSim.physics_kpis.Production;
  sState.RAFT = baseSim.physics_kpis.RAFT;
  sState.HMT = baseSim.physics_kpis.HMT;
  baseSim.simulated_state = sState;

  const outSim = [];
  let inGoldCount = 0;
  baseSim.parameters = (baseSim.parameters || []).map((p) => {
    const tag = p.tag;
    const bVal = Number(bState[tag] ?? p.baseline ?? 0);
    const sVal = Number(sState[tag] ?? bVal);
    const g = gMap[tag] || { golden_low: p.golden_low, golden_center: p.golden_center, golden_high: p.golden_high };
    const status = sVal < g.golden_low ? "below_golden" : sVal > g.golden_high ? "above_golden" : "in_golden";
    if (status === "in_golden") inGoldCount += 1;
    else if (tag !== "Production") {
      outSim.push({
        tag,
        label: p.label,
        role: p.role,
        zone: p.zone,
        unit: p.unit,
        simulated: Number(sVal.toFixed(3)),
        golden_low: g.golden_low,
        golden_high: g.golden_high,
        status,
        production_risk_t_d: Number((Math.abs(sVal - (status === "below_golden" ? g.golden_low : g.golden_high)) * 1.5).toFixed(1)),
        warning: status === "below_golden" ? p.below_warning : p.above_warning,
      });
    }
    return {
      ...p,
      baseline: Number(bVal.toFixed(3)),
      simulated: Number(sVal.toFixed(3)),
      delta: Number((sVal - bVal).toFixed(3)),
      golden_low: g.golden_low ?? p.golden_low,
      golden_center: g.golden_center ?? p.golden_center,
      golden_high: g.golden_high ?? p.golden_high,
      simulated_golden_status: status,
    };
  });

  if (baseSim.golden_analysis) {
    baseSim.golden_analysis.target_production = targetProd;
    baseSim.golden_analysis.in_golden_count = inGoldCount;
    baseSim.golden_analysis.simulated_compliance_pct = Number(((100 * inGoldCount) / Math.max(1, baseSim.parameters.length)).toFixed(1));
    baseSim.golden_analysis.out_of_golden_simulated = outSim;
  }
  return baseSim;
}

function resolveEmbeddedApiRequest(urlStr, options = {}) {
  const b = typeof window !== "undefined" ? window.__HEARTHLINE_BUNDLE__ : null;
  if (!b) return null;
  const pathPart = urlStr.replace(/^https?:\/\/[^/]+/, "").replace(/^\/twin-api/, "");
  const [route, qs = ""] = pathPart.split("?");
  const params = new URLSearchParams(qs);
  let body = {};
  if (options?.body && typeof options.body === "string") {
    try { body = JSON.parse(options.body); } catch { body = {}; }
  }

  if (route === "/health") return { status: 200, data: b.health };
  if (route === "/furnace") return { status: 200, data: b.furnace };
  if (route === "/datasets") return { status: 200, data: b.datasets };
  if (route === "/datasets/select") return { status: 200, data: { status: "ok", active: b.datasets?.active, rows_trained: 28032 } };
  if (route === "/playback") return { status: 200, data: b.playback };
  if (route === "/sensitivity") return { status: 200, data: b.sensitivity };
  if (route === "/shortfalls") {
    const tp = Number(params.get("target_production") || 4500);
    const table = b.shortfalls_by_target;
    if (table && typeof table === "object") {
      const nearest = [3800, 4200, 4500, 4850].reduce((x, y) => (Math.abs(y - tp) < Math.abs(x - tp) ? y : x));
      const hit = table[String(nearest)] || table["4500"] || b.shortfalls;
      if (hit) return { status: 200, data: hit };
    }
    if (b.shortfalls) return { status: 200, data: b.shortfalls };
    return { status: 503, data: { detail: "Embedded shortfalls payload missing." } };
  }
  if (route === "/golden-ranges") {
    const tp = Number(params.get("target_production") || 4500);
    const nearest = [3800, 4200, 4500, 4850].reduce((x, y) => (Math.abs(y - tp) < Math.abs(x - tp) ? y : x));
    const hit = b.golden_ranges?.[String(nearest)] || b.golden_ranges?.["4500"];
    if (!hit) return { status: 503, data: { detail: "Embedded golden-ranges payload missing." } };
    return { status: 200, data: hit };
  }
  if (route === "/simulate") return { status: 200, data: buildEmbeddedClientSimulate(b, body) };
  if (route === "/optimize") return { status: 200, data: b.baseline_opt };
  if (route === "/capability") return { status: 200, data: b.capability };
  if (route === "/audit/verify") return { status: 200, data: b.audit_verify };
  if (route === "/audit") {
    if ((options?.method || "GET").toUpperCase() === "POST") {
      if ((body.role || "operator") === "viewer") {
        return { status: 403, data: { detail: "Role 'viewer' is not permitted to perform action." } };
      }
      const ev = {
        id: Date.now() % 10000,
        created_at: new Date().toISOString(),
        actor: body.actor || "operator_user",
        role: body.role || "operator",
        action: body.action || "note",
        target: body.target || "setpoint",
        event_hash: "a94f6e2c81b04d3e7f1298c45601ab32",
        prev_hash: "GENESIS",
      };
      if (b.audit?.events) b.audit.events.push(ev);
      return { status: 200, data: ev };
    }
    return { status: 200, data: b.audit };
  }
  if (route.startsWith("/audit/") && route.endsWith("/confirm-execution")) {
    return { status: 200, data: { id: 1, confirmed_execution: `${body.status}: ${body.notes || "reconciled"}` } };
  }
  if (route === "/modelops/status") return { status: 200, data: b.modelops };
  if (route === "/connector/profiles") return { status: 200, data: b.connector_profiles };
  if (route === "/connector/probe") {
    const op = (body.op || "").toLowerCase();
    if (op !== "read") {
      return {
        status: 403,
        data: { detail: `Operation '${body.op}' is architecture-blocked: Hearthline implements read-only profiles only.` },
      };
    }
    return { status: 200, data: { op: "read", connected: false, detail: "Read-only DMZ adapter active; plant_write_capable=false." } };
  }
  if (route === "/diagnose") {
    if (!b.diagnose) return { status: 503, data: { detail: "Embedded diagnose payload missing." } };
    return { status: 200, data: b.diagnose };
  }
  if (route === "/twin") {
    if (!b.twin) return { status: 503, data: { detail: "Embedded twin payload missing." } };
    return { status: 200, data: b.twin };
  }
  if (route === "/model-card") {
    if (!b.model_card) return { status: 503, data: { detail: "Embedded model-card payload missing." } };
    return { status: 200, data: b.model_card };
  }
  if (route === "/predict/silicon") {
    if (!b.predict_si) return { status: 503, data: { detail: "Embedded predict/silicon payload missing." } };
    return { status: 200, data: b.predict_si };
  }
  if (route === "/knowledge") return { status: 200, data: b.knowledge };
  if (route === "/industrial-data/summary") {
    const ind = b.industrial_data;
    if (!ind || !ind.plant_reference || !Array.isArray(ind.tag_profiles)) {
      return { status: 503, data: { detail: "Embedded industrial-data summary missing plant_reference." } };
    }
    return { status: 200, data: ind };
  }
  return null;
}

if (typeof window !== "undefined" && !window.__HEARTHLINE_FETCH_PATCHED__) {
  window.__HEARTHLINE_FETCH_PATCHED__ = true;
  const origFetch = window.fetch.bind(window);
  window.fetch = async function patchedHearthlineFetch(input, init) {
    const urlStr = typeof input === "string" ? input : input?.url || "";
    if (!urlStr.includes("/twin-api/")) {
      return origFetch(input, init);
    }
    const isGithubIo = window.location.hostname.endsWith("github.io");
    if (!isGithubIo) {
      try {
        const res = await origFetch(input, init);
        if (res.ok || res.status === 403 || res.status === 400) return res;
      } catch {
        // fall through to tunnel or embedded bundle
      }
    }
    // On github.io (or if local proxy unavailable), try live Cloudflare HTTPS tunnel if non-GET or if online, then instant embedded bundle
    const resolved = resolveEmbeddedApiRequest(urlStr, init);
    if (resolved && resolved.data !== undefined && resolved.data !== null) {
      return new Response(JSON.stringify(resolved.data), {
        status: resolved.status,
        headers: { "Content-Type": "application/json" },
      });
    }
    if (isGithubIo) {
      return new Response(JSON.stringify({ detail: `No embedded payload for ${urlStr}` }), {
        status: 503,
        headers: { "Content-Type": "application/json" },
      });
    }
    return origFetch(input, init);
  };
}

const ThemeContext = createContext({
  theme: "scada-slate",
  setTheme: () => {},
  themeMeta: THEMES[0],
  role: "operator",
  setRole: () => {},
});

export function useTwinTheme() {
  return useContext(ThemeContext);
}

export function Frame({ children }) {
  const path = usePathname();
  const [theme, setThemeState] = useState("scada-slate");
  const [role, setRoleState] = useState("operator");

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem("bf_twin_theme");
      if (saved && THEMES.some((t) => t.id === saved)) {
        setThemeState(saved);
        document.documentElement.setAttribute("data-theme", saved);
      } else {
        document.documentElement.setAttribute("data-theme", "scada-slate");
      }
      const savedRole = window.localStorage.getItem("bf_twin_role");
      if (savedRole && ROLES.includes(savedRole)) {
        setRoleState(savedRole);
      }
    } catch {
      document.documentElement.setAttribute("data-theme", "scada-slate");
    }
  }, []);

  function setTheme(nextId) {
    setThemeState(nextId);
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", nextId);
    }
    try {
      window.localStorage.setItem("bf_twin_theme", nextId);
    } catch {
      // ignore storage errors
    }
  }

  function setRole(nextRole) {
    setRoleState(nextRole);
    try {
      window.localStorage.setItem("bf_twin_role", nextRole);
    } catch {
      // ignore storage errors
    }
  }

  const themeMeta = THEMES.find((t) => t.id === theme) || THEMES[0];

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themeMeta, role, setRole }}>
      <div className="shell twin-shell">
        <nav className="top-nav-bar">
          <div className="nav-brand-group">
            <h1>HEARTHLINE</h1>
            <span className="nav-sub-pill">BF DIGITAL TWIN</span>
          </div>

          <div className="nav-links-group">
            {links.map(([href, label]) =>
              href === "/pitch" ? (
                <a key={href} href="/pitch/index.html" className="pitch-nav-link">
                  {label}
                </a>
              ) : (
                <Link key={href} href={href} className={path === href || path === `${href}/` ? "active" : ""}>
                  {label}
                </Link>
              )
            )}
          </div>

          <div className="theme-switcher-bar" role="group" aria-label="Role and interface theme">
            <label className="role-selector-pill" title="Active RBAC role used for audit, sign-off, and governance actions">
              <span>ROLE</span>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>
            <span className="theme-switcher-label">THEME</span>
            {THEMES.map((t) => (
              <button
                key={t.id}
                type="button"
                className={`theme-pill-btn ${theme === t.id ? "active-theme" : ""}`}
                onClick={() => setTheme(t.id)}
                title={`${t.name}: ${t.desc}`}
              >
                <span className={`theme-swatch swatch-${t.id}`} />
                <span>{t.name}</span>
              </button>
            ))}
          </div>
        </nav>
        <main className={path === "/" ? "twin-main-flush" : "twin-main-padded"}>{children}</main>
      </div>
    </ThemeContext.Provider>
  );
}

// Same-origin by default: the Next server proxies /twin-api to the API (see next.config.js),
// and on static GitHub Pages the smart fetch layer serves from the embedded EVRAZ bundle.
export const API = process.env.NEXT_PUBLIC_API || "/twin-api";
