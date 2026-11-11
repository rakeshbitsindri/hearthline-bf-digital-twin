"use client";

import { useEffect, useMemo, useState } from "react";
import { API } from "../../components/Frame";

function renderFormattedInline(text) {
  if (!text) return null;
  const cleaned = text
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1");
  const tokens = cleaned.split(/(\*\*[^*]+\*\*|\[P\]|\[C\]|\[T\]|\[I\]|`[^`]+`)/g);
  return tokens.map((tok, i) => {
    if (!tok) return null;
    if (tok === "[P]" || tok === "[C]" || tok === "[T]" || tok === "[I]") {
      const code = tok.slice(1, 2);
      const labelMap = { P: "Peer-Reviewed", C: "Plant/Company", T: "Trade Press", I: "Derived Inference" };
      return (
        <span key={i} className={`ev-grade-pill ev-grade-${code}`} title={labelMap[code]}>
          {tok}
        </span>
      );
    }
    if (tok.startsWith("**") && tok.endsWith("**") && tok.length > 4) {
      return <strong key={i} className="kb-strong-inline">{tok.slice(2, -2)}</strong>;
    }
    if (tok.startsWith("`") && tok.endsWith("`") && tok.length > 2) {
      return <code key={i} className="kb-inline-code">{tok.slice(1, -1)}</code>;
    }
    return <span key={i}>{tok}</span>;
  });
}

function InteractiveWorkedExample({ doc, plantData }) {
  const slug = doc?.slug || "";

  // State for Example 1: Parameter Catalog & Unit/Span Converter
  const [selTag, setSelTag] = useState("Fb");
  const [testVal, setTestVal] = useState(3680);

  // State for Example 2: Physics & Derived Indices Solver
  const [exTh, setExTh] = useState(1090);
  const [exFb, setExFb] = useState(3680);
  const [exFo, setExFo] = useState(18500);
  const [exMoist, setExMoist] = useState(16);
  const [exPci, setExPci] = useState(115);

  // State for Example 3: 12 Hidden Shortfall Mechanisms & Failure Modes
  const [mechIdx, setMechIdx] = useState(0);

  // State for Example 4: Global Plant Case Studies Comparator
  const [benchPlant, setBenchPlant] = useState("posco");

  // State for Example 5: ML Autocorrelation & Lag Simulator
  const [rho, setRho] = useState(0.74);
  const [lagTau, setLagTau] = useState(2.5);

  // State for Example 6: Sensor Tier & PV Unlocker
  const [tiers, setTiers] = useState({
    tonnes: false,
    pci_coke: false,
    co_gas: false,
    minute_std: false,
    stave_cooling: false,
  });

  const tagProfiles = plantData?.tag_profiles || [];
  const chosenTagProfile = tagProfiles.find((t) => t.tag === selTag) || tagProfiles[0] || {
    tag: "Fb",
    label: "Blast volume",
    unit: "m³/min",
    role: "manipulated",
    zone: "blast",
    p05: 2921,
    median: 3652,
    p95: 3989,
    instrument_span: [500, 4500],
  };

  function selectCatalogTag(tag) {
    setSelTag(tag);
    const found = tagProfiles.find((t) => t.tag === tag);
    if (found) setTestVal(found.median);
  }

  // Decide which interactive lab to render based on document slug
  const isParamDoc = slug.includes("01-parameter") || slug.includes("column_map");
  const isPhysicsDoc = slug.includes("02-derived") || slug.includes("03-physics") || slug.includes("14-dynamic") || slug.includes("physics_model");
  const isMysteryDoc = slug.includes("04-hidden") || slug.includes("05-failure") || slug.includes("observability");
  const isCaseDoc = slug.includes("06-plant") || slug.includes("10-datasets") || slug.includes("evraz-profile") || slug.includes("evraz-citation");
  const isMlDoc = slug.includes("07-ml") || slug.includes("08-lag") || slug.includes("09-confounding") || slug.includes("ml_architecture") || slug.includes("optimization");

  if (isParamDoc) {
    const span = chosenTagProfile.instrument_span || [0, 5000];
    const inSpan = testVal >= span[0] && testVal <= span[1];
    const inGolden = testVal >= chosenTagProfile.p05 && testVal <= chosenTagProfile.p95;
    let siConversion = `${testVal} ${chosenTagProfile.unit}`;
    if (chosenTagProfile.unit === "m³/min") siConversion = `${(testVal / 60).toFixed(2)} m³/s STP (${(testVal * 60).toFixed(0)} m³/h)`;
    else if (chosenTagProfile.unit === "m³/h") siConversion = `${(testVal / 3600).toFixed(3)} m³/s STP (${(testVal / 60).toFixed(1)} m³/min)`;
    else if (chosenTagProfile.unit === "°C") siConversion = `${(Number(testVal) + 273.15).toFixed(2)} K (Kelvin)`;
    else if (chosenTagProfile.unit === "kgf/cm²") siConversion = `${(testVal * 98.0665).toFixed(1)} kPa (${(testVal * 0.9807).toFixed(3)} bar)`;

    return (
      <div className="kb-interactive-example-box">
        <div className="kb-ex-banner">
          <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
          <strong>Live Sensor Tag Inspector, Strict SI Unit Converter & EVRAZ Plant Comparator</strong>
        </div>
        <div className="kb-ex-grid2">
          <div>
            <label className="kb-ex-label">
              1. Select Any Blast Furnace Parameter Tag (from EVRAZ ZSMK 28-Tag Catalog)
              <select value={selTag} onChange={(e) => selectCatalogTag(e.target.value)} style={{ width: "100%", marginTop: "0.3rem" }}>
                {tagProfiles.map((t) => (
                  <option key={t.tag} value={t.tag}>
                    {t.tag} - {t.label} ({t.unit}) [{t.role}]
                  </option>
                ))}
              </select>
            </label>
            <div style={{ marginTop: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                <span>2. Test Live Sensor Reading ({chosenTagProfile.tag})</span>
                <b className="mono">{testVal} {chosenTagProfile.unit}</b>
              </div>
              <input
                type="range"
                min={Math.min(span[0], chosenTagProfile.p05 * 0.6)}
                max={Math.max(span[1], chosenTagProfile.p95 * 1.25)}
                step={chosenTagProfile.p95 < 10 ? 0.02 : 5}
                value={testVal}
                onChange={(e) => setTestVal(Number(e.target.value))}
                style={{ width: "100%", marginTop: "0.3rem", accentColor: "var(--heat)" }}
              />
            </div>
          </div>
          <div className="kb-ex-metrics-grid">
            <div className="kb-ex-stat-card">
              <span>Strict SI / Engineering Conversion</span>
              <strong className="mono">{siConversion}</strong>
              <small>Parameter role: <b>{chosenTagProfile.role}</b> | Zone: <b>{chosenTagProfile.zone}</b></small>
            </div>
            <div className="kb-ex-stat-card">
              <span>Running-Plant EVRAZ Distribution</span>
              <strong className="mono">Median: {chosenTagProfile.median} {chosenTagProfile.unit}</strong>
              <small>P05 to P95 band: {chosenTagProfile.p05} to {chosenTagProfile.p95} {chosenTagProfile.unit}</small>
            </div>
            <div className="kb-ex-stat-card">
              <span>Instrument Span & Sentinel Gate</span>
              <strong className={inSpan ? "ok mono" : "down mono"}>
                {inSpan ? "VALID INSTRUMENT READING" : "OUT-OF-SPAN SENTINEL FAULT"}
              </strong>
              <small>Valid span: {span[0]} to {span[1]} | Operating band: {inGolden ? "Normal (P05-P95)" : "Excursion"}</small>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isPhysicsDoc) {
    const airH = exFb * 60.0;
    const o2Pct = (100.0 * (0.21 * airH + exFo)) / Math.max(1, airH + exFo);
    const oePts = Math.max(0, o2Pct - 21.0);
    const termTh = 0.82 * exTh;
    const termMoist = -5.705 * exMoist;
    const termO2 = 52.778 * oePts;
    const termPci = -18.1 * (exPci / 1080.0) * 100.0;
    const raftRaw = 1489.0 + termTh + termMoist + termO2 + termPci;
    const boshGas = exFb * 0.79 + 2.0 * (exFb * 0.21 + exFo / 60.0) + (exMoist / 1000.0) * exFb * 1.244 + exPci * 0.045 * (exFb / 1080.0);
    const dpEst = 1.28 * Math.pow(boshGas / 4450.0, 1.7) * (1.0 + 0.0012 * (exPci - 115.0));
    // 4 conflicting industrial permeability conventions from 02-derived-indices.md
    const kFlowOverDp = boshGas / Math.max(0.2, dpEst);
    const kNippon = Math.pow(boshGas / 1000.0, 1.7) / Math.max(0.2, Math.pow(2.85, 2) - Math.pow(1.42, 2));
    const kThyssenInverse = (dpEst * 1000.0) / Math.max(100, boshGas);

    return (
      <div className="kb-interactive-example-box">
        <div className="kb-ex-banner">
          <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
          <strong>Step-by-Step AIST/Geerdes RAFT Balance & 4-Convention Permeability Calculator</strong>
        </div>
        <div className="kb-ex-grid2">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.65rem" }}>
            <label className="kb-ex-label">
              Hot Blast Temp Th: <b className="mono">{exTh} °C</b>
              <input type="range" min="940" max="1220" step="5" value={exTh} onChange={(e) => setExTh(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
            <label className="kb-ex-label">
              Blast Wind Fb: <b className="mono">{exFb} m³/min</b>
              <input type="range" min="2600" max="4200" step="20" value={exFb} onChange={(e) => setExFb(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
            <label className="kb-ex-label">
              Oxygen Flow Fo: <b className="mono">{exFo} m³/h</b>
              <input type="range" min="0" max="28000" step="500" value={exFo} onChange={(e) => setExFo(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
            <label className="kb-ex-label">
              Blast Moisture: <b className="mono">{exMoist} g/Nm³</b>
              <input type="range" min="5" max="40" step="1" value={exMoist} onChange={(e) => setExMoist(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
            <label className="kb-ex-label" style={{ gridColumn: "span 2" }}>
              PCI Coal Injection Rate: <b className="mono">{exPci} kg/tHM</b>
              <input type="range" min="0" max="190" step="5" value={exPci} onChange={(e) => setExPci(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
          </div>
          <div className="kb-ex-metrics-grid">
            <div className="kb-ex-stat-card">
              <span>Worked RAFT Equation Breakdown</span>
              <strong className="mono">{raftRaw.toFixed(1)} °C (O2 Enrichment: +{oePts.toFixed(2)} pts)</strong>
              <small className="mono">
                1489 + {termTh.toFixed(0)}(Th) {termMoist.toFixed(0)}(H2O) + {termO2.toFixed(0)}(O2) {termPci.toFixed(0)}(PCI)
              </small>
            </div>
            <div className="kb-ex-stat-card">
              <span>Bosh Gas & Ergun Pressure Drop</span>
              <strong className="mono">V_bosh = {boshGas.toFixed(0)} m³/min | dP = {dpEst.toFixed(2)} kgf/cm²</strong>
              <small>Scales as (V_bosh)^1.7 across upper ore/sinter and lower cohesive bed</small>
            </div>
            <div className="kb-ex-stat-card">
              <span>Permeability Conventions (Why Definitions Matter!)</span>
              <strong className="mono">
                K_flow={kFlowOverDp.toFixed(0)} (higher=better) | K_TK={kThyssenInverse.toFixed(3)} (lower=better)
              </strong>
              <small>Nippon/POSCO K_np={kNippon.toFixed(2)} vs Thyssenkrupp inverse resistance K_TK</small>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isMysteryDoc) {
    const MECHANISMS = [
      {
        name: "1. Azimuthal Wall Channelling & Asymmetric Gas Flow",
        sheet: "Fb = 3,650 m³/min, Th = 1,085 °C, Pt = 1.42 kgf/cm² (100% normal hourly sheet)",
        hidden: "Quadrant staves Tp4-Tp5 surge to 680-715 °C while Tp8-Tp10 sit at 190 °C; gas bypasses iron ore layers.",
        lag: "15 min to 2 hours (channelling) -> 4 to 6 hours (production & etaCO loss)",
        evrazCase: "2014-04-28 16:00:00 (Tp5 = 713.9 °C vs Golden 300-495 °C, -252 t/d loss)",
        action: "Adjust movable throat armor / bell-less chute rings to suppress wall flow and open center chimney.",
      },
      {
        name: "2. Alkali (K2O+Na2O) & Zinc Cyclic Condensation Loop",
        sheet: "Manipulated blast and burden ratio R look identical to the previous week.",
        hidden: "Alkalis vaporize in raceway (>1,900 °C) and condense at 750-950 °C in mid-shaft, recirculating 4-8x, attacking coke CSR and forming wall scaffolds that peel off into the hearth.",
        lag: "3 to 14 days integral accumulation (invisible in any single-hour snapshot)",
        evrazCase: "2013-08-20 08:00:00 (Fb = 3,657 m³/min normal, dP surged to 1.53 kgf/cm², -1,003 t/d drop)",
        action: "Switch to Slag Alkali Flush Mode: lower slag basicity B2 = CaO/SiO2 by 0.05-0.08 to reject K2O into slag.",
      },
      {
        name: "3. Sinter RDI Upper-Shaft Reduction Disintegration",
        sheet: "Charged ore/coke weight ratio R = 4.00 t/t is unchanged.",
        hidden: "Hematite-to-magnetite lattice expansion at 500-550 °C shatters high-RDI sinter into <3 mm fines, choking upper shaft permeability (dPu spikes first while dPl is initially flat).",
        lag: "1.5 to 4.5 hours after stockline charging",
        evrazCase: "2013-11-21 11:00:00 (Normal wind Fb = 3,518, upper dPu spiked, -863 t/d shortfall)",
        action: "Reduce sinter RDI (<28%), increase nut coke mixing in ore layer, or trim ore/coke ratio R.",
      },
      {
        name: "4. Cohesive Zone Root Drop & Impending Hearth Chill",
        sheet: "Wind volume Fb is steady, but unlogged burden moisture or ore reducibility shifted.",
        hidden: "Softening-melting cohesive zone root drops toward tuyeres; dripping path shortens, hot metal temperature (HMT) and [Si] fall, and viscous FeO-rich primary slag floods the bosh.",
        lag: "6 to 10 hours (burden descent + hearth thermal capacitance)",
        evrazCase: "2016-01-20 01:00:00 (Th dropped to 979 °C & Fo cut, production fell -1,213 t/d)",
        action: "Raise hot blast temperature Th, charge extra coke blanks, and avoid excess steam injection.",
      },
    ];
    const m = MECHANISMS[mechIdx] || MECHANISMS[0];

    return (
      <div className="kb-interactive-example-box">
        <div className="kb-ex-banner">
          <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
          <strong>Why Production Falls When the Operating Sheet Looks Unchanged (Live Case Simulator)</strong>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.7rem" }}>
          {MECHANISMS.map((item, idx) => (
            <button key={item.name} type="button" className={mechIdx === idx ? "primary-btn" : ""} onClick={() => setMechIdx(idx)}>
              {item.name.split(".")[0]}. {item.name.split(".")[1].slice(0, 28)}...
            </button>
          ))}
        </div>
        <div className="kb-ex-metrics-grid" style={{ gridTemplateColumns: "repeat(2, 1fr)" }}>
          <div className="kb-ex-stat-card">
            <span>What the Operator Sheet Shows (The Illusion)</span>
            <strong className="mono">{m.sheet}</strong>
            <small>Manipulated setpoints appear unchanged on standard hourly summaries.</small>
          </div>
          <div className="kb-ex-stat-card">
            <span>What the Hidden State & Response Sensors Reveal</span>
            <strong>{m.hidden}</strong>
            <small>Lag window: <b>{m.lag}</b></small>
          </div>
          <div className="kb-ex-stat-card">
            <span>Verified EVRAZ ZSMK Plant Archive Example</span>
            <strong className="mono warn">{m.evrazCase}</strong>
            <small>Reproducible in the Observe &amp; Track Historical Drops explorer.</small>
          </div>
          <div className="kb-ex-stat-card">
            <span>Metallurgical Corrective Action</span>
            <strong className="ok">{m.action}</strong>
            <small>Guided by the 7-Gate Observability Protocol.</small>
          </div>
        </div>
      </div>
    );
  }

  if (isCaseDoc) {
    const BENCHMARKS = {
      evraz: { name: "EVRAZ ZSMK Reference BF (Russia, 2013-2016)", vol: 2000, prod: 4500, pty: 2.25, coke: 375, pci: 115, siRmse: "0.113 wt% (Walk-forward LightGBM vs 0.120 persistence)" },
      posco: { name: "POSCO Gwangyang / Pohang Smart BF (Korea)", vol: 5500, prod: 12100, pty: 2.20, coke: 305, pci: 185, siRmse: "0.085-0.105 wt% (Smart furnace + tuyere cameras)" },
      nippon: { name: "Nippon Steel Oita #2 / Kimitsu (Japan)", vol: 5775, prod: 12700, pty: 2.20, coke: 315, pci: 175, siRmse: "VENUS expert system + 3D shaft probes" },
      tk: { name: "Thyssenkrupp Schwelgern #2 (Germany)", vol: 5513, prod: 12000, pty: 2.18, coke: 310, pci: 180, siRmse: "THYBAS mass/heat balance + inverse shaft K index" },
      tata: { name: "Tata Steel IJmuiden #7 / Jamshedpur (NL / India)", vol: 4450, prod: 9800, pty: 2.20, coke: 320, pci: 170, siRmse: "Acoustic top-gas temperature mapping + Rist control" },
    };
    const b = BENCHMARKS[benchPlant] || BENCHMARKS.posco;

    return (
      <div className="kb-interactive-example-box">
        <div className="kb-ex-banner">
          <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
          <strong>Global Ironmaking Benchmark Comparator vs. Running-Plant EVRAZ ZSMK</strong>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.7rem" }}>
          {Object.entries(BENCHMARKS).map(([k, v]) => (
            <button key={k} type="button" className={benchPlant === k ? "primary-btn" : ""} onClick={() => setBenchPlant(k)}>
              {v.name.split("(")[0]}
            </button>
          ))}
        </div>
        <div className="kb-ex-metrics-grid">
          <div className="kb-ex-stat-card">
            <span>Selected Plant & Working Volume</span>
            <strong className="mono">{b.vol.toLocaleString()} m³ ({b.prod.toLocaleString()} tHM/day)</strong>
            <small>{b.name} | Productivity: {b.pty} t/m³·d</small>
          </div>
          <div className="kb-ex-stat-card">
            <span>Reductant Split (Coke + PCI)</span>
            <strong className="mono">Coke: {b.coke} kg/t + PCI: {b.pci} kg/t (Total: {b.coke + b.pci} kg/t)</strong>
            <small>Compare against EVRAZ reference basis (375 coke + 115 PCI = 490 kg/tHM)</small>
          </div>
          <div className="kb-ex-stat-card">
            <span>Published Twin / ML Benchmark</span>
            <strong className="ok">{b.siRmse}</strong>
            <small>Credible industrial band: [Si] RMSE 0.08 to 0.11 wt%, HMT MAE 8 to 18 °C</small>
          </div>
        </div>
      </div>
    );
  }

  if (isMlDoc) {
    const nRaw = 29602;
    const nEff = Math.round((nRaw * (1 - rho)) / Math.max(0.01, 1 + rho));
    const pct1h = Math.round(100 * (1 - Math.exp(-1 / lagTau)));
    const pct4h = Math.round(100 * (1 - Math.exp(-4 / lagTau)));
    const pct8h = Math.round(100 * (1 - Math.exp(-8 / lagTau)));

    return (
      <div className="kb-interactive-example-box">
        <div className="kb-ex-banner">
          <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
          <strong>Effective Sample Size n_eff = N(1-rho)/(1+rho) & Metallurgical Lag Completion Calculator</strong>
        </div>
        <div className="kb-ex-grid2">
          <div>
            <label className="kb-ex-label">
              Lag-1 Autocorrelation rho_1 (EVRAZ Cast [Si] = 0.74, Hourly Th = 0.96): <b className="mono">{rho.toFixed(2)}</b>
              <input type="range" min="0.10" max="0.97" step="0.02" value={rho} onChange={(e) => setRho(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
            <label className="kb-ex-label" style={{ marginTop: "0.55rem", display: "block" }}>
              Input Transport Time Constant tau (Blast=1h, PCI=2.5h, Coke=6.5h, Alkali=12h): <b className="mono">{lagTau} hours</b>
              <input type="range" min="0.5" max="12.0" step="0.5" value={lagTau} onChange={(e) => setLagTau(Number(e.target.value))} style={{ width: "100%" }} />
            </label>
          </div>
          <div className="kb-ex-metrics-grid">
            <div className="kb-ex-stat-card">
              <span>True Independent Sample Size (n_eff)</span>
              <strong className="mono">{nEff.toLocaleString()} independent blocks (from {nRaw.toLocaleString()} raw hours)</strong>
              <small>Why random train/test split is banned: adjacent hours share {(rho * 100).toFixed(0)}% state memory.</small>
            </div>
            <div className="kb-ex-stat-card">
              <span>Step-Response Realization 1 - exp(-t / tau)</span>
              <strong className="mono">1h: {pct1h}% | 4h: {pct4h}% | 8h: {pct8h}% realized</strong>
              <small>Same-hour SHAP attribution misses {100 - pct1h}% of a tau={lagTau}h burden/fuel move.</small>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default Example 6: Governance, Sensor Tiers & Pending Validation Unlocker
  const unlockedCount =
    5 +
    (tiers.tonnes ? 1 : 0) +
    (tiers.pci_coke ? 2 : 0) +
    (tiers.co_gas ? 1 : 0) +
    (tiers.minute_std ? 1 : 0) +
    (tiers.stave_cooling ? 1 : 0);

  return (
    <div className="kb-interactive-example-box">
      <div className="kb-ex-banner">
        <span className="kb-ex-pill">INTERACTIVE WORKED EXAMPLE</span>
        <strong>Interactive Plant Instrumentation Tier & Pending-Validation (PV-01..PV-10) Unlocker</strong>
      </div>
      <p className="muted" style={{ margin: "0 0 0.55rem", fontSize: "0.8rem" }}>
        Toggle the plant data streams below to see how Hearthline&apos;s capability matrix and pending-validation gates automatically upgrade from <code>not_testable</code> / <code>response_only</code> to <code>ready</code> during Phase A-B commissioning:
      </p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem", marginBottom: "0.65rem" }}>
        {[
          ["tonnes", "Add Cast Weight / Torpedo Tonnes (Unlocks Gate 0 Shortfall)"],
          ["pci_coke", "Add PCI & Coke Rate Logs (Unlocks Absolute RAFT & HMT / PV-10)"],
          ["co_gas", "Add Top-Gas CO Analyser (Unlocks Exact Rist etaCO)"],
          ["minute_std", "Add 1-Min __std/__min/__max Companions (Unlocks Slip/Hang Precursors)"],
          ["stave_cooling", "Add Stave Cooling Water dT & Flow (Unlocks Wall Heat-Loss Balance)"],
        ].map(([k, label]) => (
          <button
            key={k}
            type="button"
            className={tiers[k] ? "primary-btn" : ""}
            onClick={() => setTiers((prev) => ({ ...prev, [k]: !prev[k] }))}
          >
            {tiers[k] ? "[ENABLED] " : "+ "} {label}
          </button>
        ))}
      </div>
      <div className="kb-ex-metrics-grid">
        <div className="kb-ex-stat-card">
          <span>Active Capability Gates Ready</span>
          <strong className="mono ok">{unlockedCount} / 11 Plant Capabilities Ready</strong>
          <small>Zero fabricated defaults: missing streams stay explicitly gated until ticked above.</small>
        </div>
        <div className="kb-ex-stat-card">
          <span>Gate 0 Tonnage & Gas Utilisation</span>
          <strong className="mono">
            Shortfall: {tiers.tonnes ? "READY (Reconciled)" : "NOT_TESTABLE"} | etaCO: {tiers.co_gas ? "READY (Measured CO+CO2)" : "NOT_RUN (CO absent)"}
          </strong>
          <small>Matches CLAUDE.md constitutional provenance rules.</small>
        </div>
        <div className="kb-ex-stat-card">
          <span>RAFT / HMT & Sub-Hour Transients</span>
          <strong className="mono">
            RAFT/HMT: {tiers.pci_coke ? "PHYSICS_ESTIMATED" : "RESPONSE_ONLY"} | Slips: {tiers.minute_std ? "OBSERVABLE (1-min)" : "BELOW_SAMPLING"}
          </strong>
          <small>Clears EX-02, EX-03, and PV-10 on customer plant data.</small>
        </div>
      </div>
    </div>
  );
}

function StructuredInteractiveDocument({ doc, plantData }) {
  const sections = useMemo(() => {
    if (!doc?.content) return [];
    const lines = doc.content.replace(/[\u2013\u2014]/g, "-").split("\n");
    const parsedSections = [];
    let currentSection = { heading: "Executive Summary & Reference Scope", blocks: [] };
    let i = 0;

    while (i < lines.length) {
      const raw = lines[i];
      const trimmed = raw.trim();
      if (!trimmed) {
        i += 1;
        continue;
      }
      if (trimmed.startsWith("# ")) {
        i += 1;
        continue;
      }
      if (trimmed.startsWith("## ")) {
        if (currentSection.blocks.length > 0) {
          parsedSections.push(currentSection);
        }
        currentSection = { heading: trimmed.slice(3).trim(), blocks: [] };
        i += 1;
        continue;
      }
      if (trimmed.startsWith("### ")) {
        currentSection.blocks.push({ type: "h3", text: trimmed.slice(4).trim() });
        i += 1;
        continue;
      }
      if (trimmed.startsWith("```")) {
        const formulaLines = [];
        i += 1;
        while (i < lines.length && !lines[i].trim().startsWith("```")) {
          formulaLines.push(lines[i]);
          i += 1;
        }
        i += 1;
        currentSection.blocks.push({ type: "formula", text: formulaLines.join("\n") });
        continue;
      }
      if (trimmed.startsWith("|") && i + 1 < lines.length && lines[i + 1].trim().startsWith("|")) {
        const tbl = [];
        while (i < lines.length && lines[i].trim().startsWith("|")) {
          tbl.push(lines[i].trim());
          i += 1;
        }
        const rows = tbl
          .filter((r) => !/^\|[\s\-:|]+\|$/.test(r))
          .map((r) =>
            r
              .replace(/^\||\|$/g, "")
              .split("|")
              .map((c) => c.trim())
          );
        if (rows.length > 0) {
          currentSection.blocks.push({ type: "table", header: rows[0], rows: rows.slice(1) });
        }
        continue;
      }
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        const items = [];
        while (i < lines.length && (lines[i].trim().startsWith("- ") || lines[i].trim().startsWith("* "))) {
          items.push(lines[i].trim().slice(2));
          i += 1;
        }
        currentSection.blocks.push({ type: "ul", items });
        continue;
      }
      if (/^\d+\.\s/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
          items.push(lines[i].trim().replace(/^\d+\.\s/, ""));
          i += 1;
        }
        currentSection.blocks.push({ type: "ol", items });
        continue;
      }
      currentSection.blocks.push({ type: "p", text: trimmed });
      i += 1;
    }
    if (currentSection.blocks.length > 0) {
      parsedSections.push(currentSection);
    }
    return parsedSections;
  }, [doc]);

  if (!doc) return null;

  return (
    <div className="kb-structured-doc">
      {/* Interactive Worked Example & Live Simulator at the top of every document */}
      <InteractiveWorkedExample doc={doc} plantData={plantData} />

      {/* Section Jump Bar */}
      {sections.length > 1 && (
        <div className="kb-toc-strip">
          <span className="mono" style={{ fontSize: "0.68rem", color: "var(--muted)" }}>SECTIONS ({sections.length}):</span>
          {sections.map((sec, idx) => (
            <a key={idx} href={`#kb-sec-${idx}`} className="kb-toc-pill">
              {sec.heading}
            </a>
          ))}
        </div>
      )}

      {/* Structured Engineering Section Cards */}
      <div className="kb-sections-stack">
        {sections.map((sec, sIdx) => (
          <section key={sIdx} id={`kb-sec-${sIdx}`} className="kb-section-card">
            <div className="kb-section-header">
              <span className="kb-section-num">0{sIdx + 1}</span>
              <h3>{renderFormattedInline(sec.heading)}</h3>
            </div>
            <div className="kb-section-body">
              {sec.blocks.map((b, bIdx) => {
                if (b.type === "h3") {
                  return <h4 key={bIdx} className="kb-subhead">{renderFormattedInline(b.text)}</h4>;
                }
                if (b.type === "formula") {
                  return (
                    <div key={bIdx} className="kb-formula-card">
                      <div className="kb-formula-tag">IMPLEMENTED EQUATION / SPECIFICATION</div>
                      <pre className="kb-pre">{b.text}</pre>
                    </div>
                  );
                }
                if (b.type === "ul") {
                  return (
                    <div key={bIdx} className="kb-bullet-grid">
                      {b.items.map((it, j) => (
                        <div key={j} className="kb-bullet-card">
                          {renderFormattedInline(it)}
                        </div>
                      ))}
                    </div>
                  );
                }
                if (b.type === "ol") {
                  return (
                    <ol key={bIdx} className="kb-list">
                      {b.items.map((it, j) => <li key={j}>{renderFormattedInline(it)}</li>)}
                    </ol>
                  );
                }
                if (b.type === "table") {
                  return (
                    <div key={bIdx} className="kb-table-wrap">
                      <table>
                        <thead>
                          <tr>
                            {b.header.map((h, j) => <th key={j}>{renderFormattedInline(h)}</th>)}
                          </tr>
                        </thead>
                        <tbody>
                          {b.rows.map((r, rIdx) => (
                            <tr key={rIdx}>
                              {r.map((cell, cIdx) => <td key={cIdx}>{renderFormattedInline(cell)}</td>)}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  );
                }
                return <p key={bIdx} className="kb-para">{renderFormattedInline(b.text)}</p>;
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

export default function KnowledgeAndPlantPage() {
  const [tab, setTab] = useState("library");
  const [kb, setKb] = useState(null);
  const [plantData, setPlantData] = useState(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("ALL");
  const [selectedSlug, setSelectedSlug] = useState("01-parameter-catalog");
  const [tagFilter, setTagFilter] = useState("");
  const [fullScreenDoc, setFullScreenDoc] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/knowledge`).then((r) => r.json()),
      fetch(`${API}/industrial-data/summary?sample_limit=25`).then((r) => r.json()),
    ])
      .then(([kbBody, plantBody]) => {
        setKb(kbBody);
        setPlantData(plantBody);
        if (kbBody?.documents?.length && !kbBody.documents.some((d) => d.slug === "01-parameter-catalog")) {
          setSelectedSlug(kbBody.documents[0].slug);
        }
      })
      .catch(() => {});
  }, []);

  const filteredDocs = useMemo(() => {
    const docs = kb?.documents || [];
    return docs.filter((d) => {
      if (category !== "ALL" && d.category !== category) return false;
      if (search.trim()) {
        const q = search.trim().toLowerCase();
        return (
          d.title.toLowerCase().includes(q) ||
          d.content.toLowerCase().includes(q) ||
          d.filename.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [kb, category, search]);

  const activeDoc = useMemo(() => {
    if (!filteredDocs.length) return null;
    return filteredDocs.find((d) => d.slug === selectedSlug) || filteredDocs[0];
  }, [filteredDocs, selectedSlug]);

  const filteredPlantTags = useMemo(() => {
    const tags = plantData?.tag_profiles || [];
    if (!tagFilter.trim()) return tags;
    const q = tagFilter.trim().toLowerCase();
    return tags.filter(
      (t) => t.tag.toLowerCase().includes(q) || t.label.toLowerCase().includes(q) || t.role.toLowerCase().includes(q)
    );
  }, [plantData, tagFilter]);

  if (!kb || !plantData) {
    return <p className="muted" style={{ padding: "2rem" }}>Loading interactive metallurgical knowledge studio &amp; EVRAZ ZSMK plant archive...</p>;
  }

  const pr = plantData.plant_reference;

  return (
    <section className={`knowledge-hub-shell ${fullScreenDoc ? "kb-fullscreen-active" : ""}`}>
      <div className="kb-hero-strip">
        <div>
          <h2>Interactive Metallurgical Knowledge Studio &amp; Running-Plant Industrial Data</h2>
          <p className="muted" style={{ margin: 0 }}>
            <b>{kb.total_documents} interactive engineering documents with live worked examples</b> ({kb.total_words.toLocaleString()} words,{" "}
            {kb.total_evidence_tags} graded literature citations) + <b>{pr.hourly_rows.toLocaleString()} real blast-furnace sensor hours</b>{" "}
            and <b>{pr.cast_silicon_analyses.toLocaleString()} chemical lab casts</b> from EVRAZ ZSMK (2013-2016, public_reference, CC BY 4.0).
          </p>
        </div>

        <div className="kb-top-tabs">
          {[
            ["library", `Interactive Knowledge Studio (${kb.total_documents} Docs)`],
            ["plant", `Running-Plant Data (${pr.hourly_rows.toLocaleString()}h EVRAZ)`],
            ["exceptions", `Exceptions & Boundaries (${kb.exceptions.length})`],
          ].map(([id, label]) => (
            <button key={id} type="button" className={tab === id ? "primary-btn" : ""} onClick={() => setTab(id)}>
              {label}
            </button>
          ))}
          {tab === "library" && (
            <button
              type="button"
              onClick={() => setFullScreenDoc((v) => !v)}
              style={{ borderColor: "var(--heat)", color: "var(--heat)", fontWeight: 600 }}
            >
              {fullScreenDoc ? "Show Chapter Sidebar" : "Full-Screen Document Mode"}
            </button>
          )}
        </div>
      </div>

      {tab === "library" && (
        <div className={`kb-library-workspace ${fullScreenDoc ? "kb-workspace-fullscreen" : ""}`}>
          {!fullScreenDoc && (
            <aside className="kb-sidebar">
              <input
                type="text"
                className="kb-search-input"
                placeholder="Search equations, RAFT, alkali, POSCO, causality, PV-05..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <div className="kb-cat-pills">
                {["ALL", ...(kb.categories || [])].map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={category === cat ? "active" : ""}
                    onClick={() => setCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
              <div className="kb-doc-list">
                {filteredDocs.map((doc) => {
                  const evTotal = Object.values(doc.evidence_counts || {}).reduce((a, b) => a + b, 0);
                  return (
                    <button
                      key={doc.slug}
                      type="button"
                      className={`kb-doc-card ${activeDoc?.slug === doc.slug ? "active" : ""}`}
                      onClick={() => setSelectedSlug(doc.slug)}
                    >
                      <div className="kb-doc-card-top">
                        <span className="kb-doc-cat">{doc.category}</span>
                        <span className="kb-doc-words">{doc.word_count.toLocaleString()} w</span>
                      </div>
                      <strong>{doc.title.replace(/[\u2013\u2014]/g, "-")}</strong>
                      <small className="kb-doc-file">
                        Interactive Doc + Worked Example {evTotal > 0 ? `| ${evTotal} refs` : ""}
                      </small>
                    </button>
                  );
                })}
              </div>
            </aside>
          )}

          <article className="kb-reader-pane">
            {activeDoc ? (
              <>
                <div className="kb-reader-meta">
                  <div>
                    <h2 style={{ margin: "0 0 0.25rem", fontSize: "1.45rem" }}>
                      {activeDoc.title.replace(/[\u2013\u2014]/g, "-")}
                    </h2>
                    <span className="badge">{activeDoc.category}</span>
                    <span className="muted" style={{ marginLeft: "0.6rem" }}>
                      {activeDoc.word_count.toLocaleString()} words | Interactive Engineering Reference &amp; Live Worked Example
                    </span>
                  </div>
                  <div className="kb-ev-summary">
                    {fullScreenDoc && (
                      <select
                        value={activeDoc.slug}
                        onChange={(e) => setSelectedSlug(e.target.value)}
                        style={{ marginRight: "0.5rem" }}
                      >
                        {filteredDocs.map((d) => (
                          <option key={d.slug} value={d.slug}>
                            {d.title.replace(/[\u2013\u2014]/g, "-")}
                          </option>
                        ))}
                      </select>
                    )}
                    <span className="ev-grade-pill ev-grade-P">[P] Peer-Reviewed: {activeDoc.evidence_counts.peer_reviewed_P}</span>
                    <span className="ev-grade-pill ev-grade-C">[C] Plant/Vendor: {activeDoc.evidence_counts.company_report_C}</span>
                    <span className="ev-grade-pill ev-grade-I">[I] Inference: {activeDoc.evidence_counts.inference_I}</span>
                  </div>
                </div>
                <StructuredInteractiveDocument doc={activeDoc} plantData={plantData} />
              </>
            ) : (
              <p className="muted">No documents match your search query.</p>
            )}
          </article>
        </div>
      )}

      {tab === "plant" && (
        <div className="kb-plant-explorer">
          <div className="plant-provenance-banner">
            <div>
              <strong>PUBLIC REFERENCE RUNNING-PLANT ARCHIVE : {pr.plant}</strong>
              <p className="muted" style={{ margin: "0.2rem 0 0" }}>
                Citation: {pr.citation} | Mendeley DOI: {pr.mendeley_doi} | Licence: {pr.licence} | Evidence class:{" "}
                <b>public_reference</b> (measured industrial sensors 2013-01-01 to 2016-05-18; not this customer&apos;s plant; not live).
              </p>
            </div>
            <a href={`${API}/industrial-data/export.csv?limit=1000`} download className="primary-btn" style={{ padding: "0.45rem 0.85rem", whiteSpace: "nowrap" }}>
              Download 1,000-Row Plant CSV
            </a>
          </div>

          <div className="grid" style={{ marginBottom: "1rem" }}>
            <div className="card">
              <span>Running-Plant Sensor Hours</span>
              <strong>{pr.hourly_rows.toLocaleString()} hrs (3.38 yrs)</strong>
              <small className="muted">
                On-wind (&gt;1000 m³/min): {pr.on_wind_hours.toLocaleString()} hrs ({pr.on_wind_pct}%) | Zero-blast: {pr.zero_blast_hours} hrs
              </small>
            </div>
            <div className="card">
              <span>Cast Lab Silicon Analyses</span>
              <strong>{pr.cast_silicon_analyses.toLocaleString()} casts</strong>
              <small className="muted">
                Persistence RMSE: {pr.silicon_persistence_rmse_wt_pct} wt% | Lag-1 autocorr: {pr.silicon_lag1_autocorr} (n_eff ~ {pr.effective_independent_blocks})
              </small>
            </div>
            <div className="card">
              <span>Pressure Balance dPu + dPl = dP</span>
              <strong>{pr.pressure_identity_median_residual} median err</strong>
              <small className="muted">
                95th percentile abs residual: {pr.pressure_identity_p95_residual} kgf/cm² across 29,602 hours
              </small>
            </div>
            <div className="card">
              <span>Circumferential Wall Asymmetry</span>
              <strong>{pr.circumferential_tp_median_spread_c} degC spread</strong>
              <small className="muted">
                {pr.circumferential_tp_gt150c_pct}% of on-wind hours exceed 150 degC azimuthal Tp1-Tp10 spread
              </small>
            </div>
          </div>

          {/* Circumferential Stave Profile Tp1..Tp10 */}
          <div className="card" style={{ marginBottom: "1.1rem" }}>
            <h3 style={{ marginBottom: "0.25rem" }}>Azimuthal Peripheral Gas Temperature Profile (Tp1 to Tp10 across 28,032 On-Wind Hours)</h3>
            <p className="muted">
              Real plant insight: probes Tp4 and Tp5 run ~400 degC median while probes Tp8 to Tp10 run ~195 degC across the campaign, proving persistent circumferential gas flow asymmetry that single-point shaft averages miss.
            </p>
            <div className="plant-stave-bars">
              {(plantData.stave_azimuthal_profile || []).map((st) => {
                const widthPct = Math.min(100, Math.max(8, (st.median / 520) * 100));
                return (
                  <div key={st.tag} className="plant-stave-row">
                    <b className="mono">{st.tag}</b>
                    <div className="plant-stave-track">
                      <div className="plant-stave-fill" style={{ width: `${widthPct}%` }} />
                    </div>
                    <span className="mono">
                      P10: {st.p10}°C | <b>Median: {st.median}°C</b> | P90: {st.p90}°C
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Workbook 2 Labeled Regimes */}
          <h3>Workbook 2 : 8 Labeled Blast-Furnace Operating States (Plant Demonstration Dictionary)</h3>
          <div className="kb-table-wrap" style={{ marginBottom: "1.2rem" }}>
            <table>
              <thead>
                <tr>
                  <th>Labeled Furnace Regime</th>
                  <th>Hours</th>
                  <th>Representative Timestamp</th>
                  <th>Fb (m³/min)</th>
                  <th>Fo (m³/h)</th>
                  <th>Th (°C)</th>
                  <th>dP (kgf/cm²)</th>
                  <th>CO2 (%)</th>
                  <th>R (t/t)</th>
                  <th>Tp Spread (°C)</th>
                </tr>
              </thead>
              <tbody>
                {(plantData.labeled_furnace_regimes || []).map((r) => (
                  <tr key={r.state}>
                    <td><b>{r.state}</b></td>
                    <td>{r.count}</td>
                    <td className="mono">{r.t}</td>
                    <td>{Math.round(r.Fb)}</td>
                    <td>{Math.round(r.Fo)}</td>
                    <td>{Math.round(r.Th)}</td>
                    <td>{r.dP.toFixed(2)}</td>
                    <td>{r.CO2.toFixed(2)}</td>
                    <td>{r.R.toFixed(2)}</td>
                    <td>{r.tp_spread}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Full 28-Tag Sensor Distribution & Span Audit */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", marginBottom: "0.4rem" }}>
            <h3 style={{ margin: 0 }}>All 28 Running-Plant Sensor Distributions &amp; Instrument Span Audit</h3>
            <input
              type="text"
              placeholder="Filter tag, role, or zone..."
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
              style={{ width: "260px" }}
            />
          </div>
          <div className="kb-table-wrap" style={{ marginBottom: "1.2rem" }}>
            <table>
              <thead>
                <tr>
                  <th>Tag</th>
                  <th>Description &amp; Unit</th>
                  <th>Role / Zone</th>
                  <th>P05</th>
                  <th>Median</th>
                  <th>P95</th>
                  <th>Raw Min / Max</th>
                  <th>Instrument Span</th>
                  <th>Out-of-Span Sentinels</th>
                </tr>
              </thead>
              <tbody>
                {filteredPlantTags.map((t) => (
                  <tr key={t.tag}>
                    <td className="mono"><b>{t.tag}</b></td>
                    <td>{t.label} <small className="muted">({t.unit})</small></td>
                    <td><span className="badge">{t.role}</span> <small className="muted">{t.zone}</small></td>
                    <td className="mono">{t.p05}</td>
                    <td className="mono"><b>{t.median}</b></td>
                    <td className="mono">{t.p95}</td>
                    <td className="mono">{t.raw_min} / {t.raw_max}</td>
                    <td className="mono">{t.instrument_span ? `${t.instrument_span[0]} to ${t.instrument_span[1]}` : "n/a"}</td>
                    <td className={t.span_violations > 0 ? "down mono" : "ok mono"}>
                      {t.span_violations} ({t.violation_pct}%)
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Sample Plant Records */}
          <h3>Sample Running-Plant Sensor &amp; Cast Records (EVRAZ ZSMK)</h3>
          <div className="kb-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Fb</th>
                  <th>Fo</th>
                  <th>Th</th>
                  <th>Pt</th>
                  <th>dPu</th>
                  <th>dPl</th>
                  <th>dP</th>
                  <th>CO2</th>
                  <th>H2</th>
                  <th>R</th>
                  <th>Tt1</th>
                  <th>Tp4</th>
                  <th>Tp9</th>
                  <th>Cast [Si]</th>
                </tr>
              </thead>
              <tbody>
                {(plantData.sample_plant_records || []).map((row) => (
                  <tr key={row.dt} className="mono">
                    <td>{row.dt}</td>
                    <td>{row.Fb}</td>
                    <td>{row.Fo}</td>
                    <td>{row.Th}</td>
                    <td>{row.Pt}</td>
                    <td>{row.dPu}</td>
                    <td>{row.dPl}</td>
                    <td><b>{row.dP}</b></td>
                    <td>{row.CO2}</td>
                    <td>{row.H2}</td>
                    <td>{row.R}</td>
                    <td>{row.Tt1}</td>
                    <td>{row.Tp4}</td>
                    <td>{row.Tp9}</td>
                    <td><b>{row.Si}</b></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "exceptions" && (
        <div className="kb-exceptions-pane">
          <h3>Explicit Engineering Exceptions, Data Boundaries &amp; TRL 7-9 Prerequisites</h3>
          <p className="muted">
            Per CLAUDE.md, a confident wrong claim is worse than an honest boundary. Below is every active exception in this deployment, how the software enforces it, and what plant artifact clears it during Phase A to D commissioning.
          </p>
          <div className="kb-exception-grid">
            {(kb.exceptions || []).map((ex) => (
              <div key={ex.id} className="kb-exception-card">
                <div className="kb-ex-head">
                  <span className="govern-phase-badge">{ex.id}</span>
                  <span className="badge">{ex.category}</span>
                  <span className="golden-badge golden-badge-below_golden" style={{ marginLeft: "auto" }}>
                    {ex.status}
                  </span>
                </div>
                <h4>{ex.title}</h4>
                <p className="muted">{ex.detail}</p>
                <div className="kb-ex-unblock">
                  <b>Required to clear:</b> {ex.unblock_requirement}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
