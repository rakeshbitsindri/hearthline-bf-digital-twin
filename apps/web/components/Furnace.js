"use client";

function heatColor(value) {
  const t = Math.min(1, Math.max(0, (value - 120) / 520));
  const r = Math.round(70 + t * 185);
  const g = Math.round(92 + t * 40);
  const b = Math.round(110 - t * 70);
  return `rgb(${r}, ${g}, ${b})`;
}

export function Furnace({ frame, blast, temperature }) {
  const probes = frame?.tp || Array(10).fill(180);
  const flow = Math.max(0.35, Math.min(2.4, blast / 2800));
  const flame = Math.max(0.25, Math.min(1, (temperature - 700) / 500));
  return (
    <svg className="furnace" viewBox="0 0 440 620" role="img" aria-label="Blast furnace cross-section driven by the selected hour">
      <defs>
        <linearGradient id="shell" x1="0" x2="1">
          <stop offset="0" stopColor="#2a241c" />
          <stop offset="0.5" stopColor="#3c342a" />
          <stop offset="1" stopColor="#221c16" />
        </linearGradient>
        <radialGradient id="flame" cx="50%" cy="60%" r="60%">
          <stop offset="0" stopColor={`rgba(255, ${180 + flame * 60}, 80, ${0.35 + flame * 0.55})`} />
          <stop offset="1" stopColor="rgba(224, 122, 61, 0)" />
        </radialGradient>
      </defs>
      <path d="M150 36 H290 L330 150 L338 360 L300 470 L250 560 H190 L140 470 L102 360 L110 150 Z" fill="url(#shell)" stroke="#8fbfb6" strokeWidth="2" />
      <ellipse cx="220" cy="500" rx="70" ry="28" fill="url(#flame)" />
      {[0, 1, 2, 3, 4].map((band) => (
        <rect key={band} className="burden" x="150" y={70 + band * 62} width="140" height="18" rx="3" style={{ animationDelay: `${band * -0.7}s`, animationDuration: `${7 / flow}s` }} />
      ))}
      {probes.map((value, index) => {
        const left = index < 5;
        const slot = left ? index : index - 5;
        const y = 80 + slot * 70;
        const x = left ? 78 : 338;
        return (
          <g key={index}>
            <rect x={x} y={y} width="24" height="48" rx="3" fill={heatColor(value)} stroke="#efe6d6" strokeOpacity="0.35" />
            <text x={left ? 70 : 368} y={y + 28} textAnchor={left ? "end" : "start"} className="probe-label">
              {Math.round(value)}
            </text>
          </g>
        );
      })}
      {[150, 220, 290].map((x) => (
        <g key={x}>
          <circle className="gas" cx={x} cy="460" r={4 + flame * 3} style={{ animationDuration: `${2.8 / flow}s` }} />
        </g>
      ))}
      <text x="220" y="24" textAnchor="middle" className="probe-label">measured wall temperatures, index order</text>
      <text x="220" y="600" textAnchor="middle" className="probe-label">
        blast {Math.round(blast)} m³/min · hot blast {Math.round(temperature)} °C
      </text>
    </svg>
  );
}
