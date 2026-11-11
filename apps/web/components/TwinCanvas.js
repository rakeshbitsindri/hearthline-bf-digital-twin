"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Html, OrbitControls } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

function heatColorHex(value, min = 120, max = 680) {
  const t = Math.min(1, Math.max(0, (value - min) / (max - min + 1e-6)));
  const color = new THREE.Color().setHSL(0.08 - t * 0.08, 0.85, 0.30 + t * 0.32);
  return `#${color.getHexString()}`;
}

function Shell({ open, themeMeta }) {
  const geometry = useMemo(() => {
    const profile = [
      [2.85, 13.6],
      [3.25, 11.4],
      [4.05, 8.2],
      [5.05, 5.2],
      [5.35, 3.4],
      [4.45, 1.2],
      [4.15, -0.5],
      [4.15, -2.5],
    ].map(([x, y]) => new THREE.Vector2(x, y));
    return new THREE.LatheGeometry(profile, 64, 0.18, Math.PI * (0.68 + open * 1.22));
  }, [open]);

  const shellCol = themeMeta?.shellColor || "#243044";
  const bustleCol = themeMeta?.bustleColor || "#3b4f6b";

  return (
    <group>
      <mesh geometry={geometry}>
        <meshStandardMaterial color={shellCol} metalness={0.74} roughness={0.34} side={THREE.DoubleSide} />
      </mesh>
      {/* Bustle pipe ring around tuyere zone */}
      <mesh position={[0, -0.35, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[4.85, 0.24, 16, 48]} />
        <meshStandardMaterial color={bustleCol} metalness={0.65} roughness={0.35} />
      </mesh>
      {/* Top charging hopper / bell-less top housing */}
      <mesh position={[0, 14.35, 0]}>
        <cylinderGeometry args={[1.45, 2.2, 1.3, 28]} />
        <meshStandardMaterial color={shellCol} metalness={0.8} roughness={0.3} />
      </mesh>
    </group>
  );
}

function PeripheralWallRing({ simState, baseState, paramByTag, selectedTag, onSelectTag, showAllPins, anomalyPinsOnly }) {
  return Array.from({ length: 10 }, (_, idx) => {
    const num = idx + 1;
    const tag = `Tp${num}`;
    const value = Number(simState?.[tag] ?? 260);
    const baseVal = Number(baseState?.[tag] ?? value);
    const delta = value - baseVal;
    const gStatus = paramByTag?.[tag]?.simulated_golden_status || "in_golden";
    const isOut = gStatus !== "in_golden";
    const angle = idx * ((2 * Math.PI) / 10) + 0.25;
    const radius = 4.42;
    const y = 6.2;
    const pos = [Math.cos(angle) * radius, y, Math.sin(angle) * radius];
    const col = isOut ? (gStatus === "above_golden" ? "#f43f5e" : "#f59e0b") : heatColorHex(value, 140, 620);
    const isSel = selectedTag === tag;
    const shouldShowLabel = anomalyPinsOnly ? isOut || isSel : showAllPins || isSel || isOut || num % 2 === 1;

    return (
      <group key={tag} position={pos}>
        <mesh
          onClick={(e) => {
            e.stopPropagation();
            onSelectTag?.(tag);
          }}
        >
          <sphereGeometry args={[isSel ? 0.36 : isOut ? 0.30 : 0.22, 18, 18]} />
          <meshStandardMaterial color={col} emissive={col} emissiveIntensity={isSel ? 1.25 : isOut ? 0.95 : 0.55} />
        </mesh>
        {shouldShowLabel && (
          <Html position={[0, 0.42, 0]} distanceFactor={15} style={{ pointerEvents: "none" }}>
            <div className={`sensor-pin pin-${gStatus} ${isSel ? "selected" : ""}`}>
              <span>
                {tag} {isOut ? (gStatus === "below_golden" ? "LOW" : "HIGH") : ""}
              </span>
              <b>{Math.round(value)}°C</b>
              {Math.abs(delta) >= 0.5 && (
                <em className={delta > 0 ? "up" : "down"}>
                  {delta > 0 ? "+" : ""}
                  {delta.toFixed(0)}
                </em>
              )}
            </div>
          </Html>
        )}
      </group>
    );
  });
}

function TopOfftakeSensors({ simState, paramByTag, selectedTag, onSelectTag, anomalyPinsOnly }) {
  const coords = [
    ["Tt1", [2.35, 13.2, 2.0]],
    ["Tt2", [-2.35, 13.2, 2.0]],
    ["Tt3", [-2.35, 13.2, -2.0]],
    ["Tt4", [2.35, 13.2, -2.0]],
  ];
  return coords.map(([tag, pos]) => {
    const val = Number(simState?.[tag] ?? 150);
    const gStatus = paramByTag?.[tag]?.simulated_golden_status || "in_golden";
    const isOut = gStatus !== "in_golden";
    const col = isOut ? (gStatus === "above_golden" ? "#f43f5e" : "#f59e0b") : heatColorHex(val, 90, 260);
    const isSel = selectedTag === tag;
    const shouldShowLabel = !anomalyPinsOnly || isOut || isSel;
    return (
      <group key={tag} position={pos}>
        <mesh
          onClick={(e) => {
            e.stopPropagation();
            onSelectTag?.(tag);
          }}
        >
          <cylinderGeometry args={[0.22, 0.22, 0.9, 14]} />
          <meshStandardMaterial color={col} emissive={col} emissiveIntensity={isOut ? 0.9 : 0.45} />
        </mesh>
        {shouldShowLabel && (
          <Html position={[0, 0.65, 0]} distanceFactor={15} style={{ pointerEvents: "none" }}>
            <div className={`sensor-pin compact pin-${gStatus} ${isSel ? "selected" : ""}`}>
              <span>
                {tag} {isOut ? (gStatus === "below_golden" ? "LOW" : "HIGH") : ""}
              </span>
              <b>{Math.round(val)}°C</b>
            </div>
          </Html>
        )}
      </group>
    );
  });
}

function InternalProcessZones({ simState, kpis }) {
  const gas = useRef([]);
  const burden = useRef([]);
  const condParticles = useRef([]);
  const chuteRef = useRef(null);
  const clock = useRef(0);

  const blast = Number(simState?.Fb ?? 3500);
  const raft = Number(kpis?.RAFT ?? simState?.RAFT ?? 2080);
  const czHeight = Number(kpis?.CZHeight ?? simState?.CZHeight ?? 3.8);
  const condIdx = Number(kpis?.CondensationIdx ?? simState?.CondensationIdx ?? 25);
  const prod = Number(kpis?.Production ?? simState?.Production ?? 4450);

  const flow = Math.max(0.25, blast / 3200);
  const flame = Math.max(0.2, Math.min(1.0, (raft - 1850) / 420));
  const condAlpha = Math.min(0.68, Math.max(0.08, condIdx / 110));

  useFrame((_, delta) => {
    clock.current += delta;
    if (chuteRef.current) {
      chuteRef.current.rotation.y = clock.current * 1.1 * flow;
    }
    gas.current.forEach((mesh, index) => {
      if (!mesh) return;
      mesh.position.y += delta * (1.8 + flow * 2.6);
      if (mesh.position.y > 13.2) {
        mesh.position.y = -0.8;
        const angle = index * 0.65 + clock.current * 0.2;
        const r = 0.8 + (index % 5) * 0.48;
        mesh.position.x = Math.cos(angle) * r;
        mesh.position.z = Math.sin(angle) * r;
      }
    });
    burden.current.forEach((mesh, index) => {
      if (!mesh) return;
      const cycle = ((clock.current * 0.045 * flow) + index / 9) % 1;
      mesh.position.y = 12.2 - cycle * (12.2 - czHeight);
    });
    condParticles.current.forEach((mesh, index) => {
      if (!mesh) return;
      const a = index * 0.52 + clock.current * 0.45;
      const r = 3.25 + 0.35 * Math.sin(clock.current * 1.5 + index);
      mesh.position.x = Math.cos(a) * r;
      mesh.position.z = Math.sin(a) * r;
      mesh.position.y = 7.2 + 1.1 * Math.cos(clock.current * 0.9 + index);
    });
  });

  return (
    <group>
      {/* Rotating Bell-Less Top Chute */}
      <group ref={chuteRef} position={[0, 13.2, 0]}>
        <mesh position={[0.6, -0.35, 0]} rotation={[0, 0, -0.45]}>
          <boxGeometry args={[1.4, 0.14, 0.38]} />
          <meshStandardMaterial color="#d98a4e" metalness={0.6} roughness={0.3} />
        </mesh>
      </group>

      {/* Descending Alternating Ore & Coke Burden Layers */}
      {Array.from({ length: 9 }, (_, index) => (
        <mesh
          key={`b${index}`}
          ref={(node) => {
            burden.current[index] = node;
          }}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <ringGeometry args={[0.35, 2.55 - index * 0.06, 28]} />
          <meshStandardMaterial
            color={index % 2 === 0 ? "#5a4632" : "#8c6240"}
            transparent
            opacity={0.48}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}

      {/* Alkali & Zinc Condensation / Recirculation Band (Upper-Mid Shaft 750-950C) */}
      <mesh position={[0, 7.6, 0]}>
        <cylinderGeometry args={[3.65, 4.15, 2.1, 32, 1, true]} />
        <meshStandardMaterial
          color={condIdx > 45 ? "#d85a3a" : "#74b5a6"}
          emissive={condIdx > 45 ? "#b83c1c" : "#3a7d70"}
          emissiveIntensity={0.45}
          transparent
          opacity={condAlpha}
          side={THREE.DoubleSide}
        />
      </mesh>
      {Array.from({ length: 14 }, (_, idx) => (
        <mesh
          key={`cond${idx}`}
          ref={(node) => {
            condParticles.current[idx] = node;
          }}
        >
          <sphereGeometry args={[0.09 + condIdx / 600, 8, 8]} />
          <meshBasicMaterial color={condIdx > 45 ? "#ff7b54" : "#88e0d0"} transparent opacity={0.75} />
        </mesh>
      ))}

      {/* Cohesive Softening-Melting Zone (Inverted-V Root) */}
      <mesh position={[0, czHeight, 0]}>
        <coneGeometry args={[3.95, 2.35, 32, 1, true]} />
        <meshStandardMaterial
          color="#e07a3d"
          emissive="#c95b1e"
          emissiveIntensity={0.55}
          transparent
          opacity={0.34}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Ascending Bosh / Shaft Reducing Gas Stream */}
      {Array.from({ length: 34 }, (_, index) => (
        <mesh
          key={`g${index}`}
          ref={(node) => {
            gas.current[index] = node;
          }}
          position={[Math.cos(index) * 1.8, (index % 10) * 1.3, Math.sin(index) * 1.8]}
        >
          <sphereGeometry args={[0.08 + flame * 0.05, 8, 8]} />
          <meshBasicMaterial color={index % 3 ? "#f6c667" : "#8fd4c8"} transparent opacity={0.85} />
        </mesh>
      ))}

      {/* Tuyere Raceway Combustion Envelopes (6 radial plumes around bustle ring) */}
      {Array.from({ length: 6 }, (_, idx) => {
        const a = idx * (Math.PI / 3);
        return (
          <mesh key={`rw${idx}`} position={[Math.cos(a) * 2.55, -0.45, Math.sin(a) * 2.55]}>
            <sphereGeometry args={[0.48 + flame * 0.38, 18, 18]} />
            <meshBasicMaterial color="#ffb347" transparent opacity={0.42 + flame * 0.42} />
          </mesh>
        );
      })}

      {/* Deadman Coke Core Cone */}
      <mesh position={[0, -0.8, 0]}>
        <coneGeometry args={[2.1, 2.4, 24]} />
        <meshStandardMaterial color="#2b241d" roughness={0.9} transparent opacity={0.68} />
      </mesh>

      {/* Hearth Slag Layer + Molten Hot Metal Pool */}
      <mesh position={[0, -1.65, 0]}>
        <cylinderGeometry args={[3.8, 3.8, 0.42, 32]} />
        <meshStandardMaterial color="#b86b35" emissive="#6e3814" emissiveIntensity={0.45} transparent opacity={0.75} />
      </mesh>
      <mesh position={[0, -2.18, 0]}>
        <cylinderGeometry args={[3.85, 3.85, 0.65, 32]} />
        <meshStandardMaterial
          color="#ff9233"
          emissive="#e05310"
          emissiveIntensity={0.6 + Math.min(0.5, (prod - 3500) / 3000)}
        />
      </mesh>

      {/* Active Taphole Molten Iron Runner Stream */}
      <mesh position={[4.25, -2.25, 0.8]} rotation={[0, 0, -0.18]}>
        <cylinderGeometry args={[0.11, 0.16, 1.8, 12]} />
        <meshBasicMaterial color="#ffae42" />
      </mesh>
    </group>
  );
}

function KeyZoneCallouts({ simState, baseState, kpis, paramByTag, selectedTag, onSelectTag, anomalyPinsOnly }) {
  const callouts = [
    { tag: "R", pos: [0, 14.9, 0], label: "Ore/Coke Ratio", val: `${Number(simState?.R ?? 4.0).toFixed(2)} t/t`, delta: (simState?.R ?? 0) - (baseState?.R ?? 0) },
    { tag: "Pt", pos: [4.6, 11.4, 0], label: "Top Pressure Pt", val: `${Number(simState?.Pt ?? 1.4).toFixed(2)} kgf/cm²`, delta: (simState?.Pt ?? 0) - (baseState?.Pt ?? 0) },
    { tag: "CO2", pos: [-4.6, 11.4, 0], label: "Top Gas CO₂ / H₂", val: `${Number(simState?.CO2 ?? 21).toFixed(1)}% / ${Number(simState?.H2 ?? 6).toFixed(1)}%`, delta: (simState?.CO2 ?? 0) - (baseState?.CO2 ?? 0) },
    { tag: "CondensationIdx", pos: [4.9, 7.8, 0], label: "Alkali/Zn Condensation", val: `${Number(kpis?.CondensationIdx ?? 25).toFixed(1)} idx`, delta: (simState?.CondensationIdx ?? 0) - (baseState?.CondensationIdx ?? 0) },
    { tag: "dPu", pos: [-5.1, 8.1, 0], label: "Upper ΔPu", val: `${Number(simState?.dPu ?? 0.45).toFixed(2)} kgf/cm²`, delta: (simState?.dPu ?? 0) - (baseState?.dPu ?? 0) },
    { tag: "CZHeight", pos: [4.9, 4.1, 0], label: "Cohesive Zone Root", val: `${Number(kpis?.CZHeight ?? 3.8).toFixed(2)} m`, delta: (simState?.CZHeight ?? 0) - (baseState?.CZHeight ?? 0) },
    { tag: "dPl", pos: [-5.1, 3.4, 0], label: "Lower ΔPl (Total ΔP)", val: `${Number(simState?.dPl ?? 0.98).toFixed(2)} (${Number(simState?.dP ?? 1.43).toFixed(2)})`, delta: (simState?.dP ?? 0) - (baseState?.dP ?? 0) },
    { tag: "Th", pos: [5.5, 0.3, 0], label: "Hot Blast Th / RAFT", val: `${Math.round(simState?.Th ?? 1100)}°C / ${Math.round(kpis?.RAFT ?? 2080)}°C`, delta: (simState?.Th ?? 0) - (baseState?.Th ?? 0) },
    { tag: "Fb", pos: [5.5, -1.2, 0], label: "Blast Fb / Ph", val: `${Math.round(simState?.Fb ?? 3500)} m³/m | ${Number(simState?.Ph ?? 2.85).toFixed(2)}`, delta: (simState?.Fb ?? 0) - (baseState?.Fb ?? 0) },
    { tag: "Fo", pos: [-5.4, -0.8, 0], label: "O₂ Flow / PCI", val: `${Math.round(simState?.Fo ?? 18000)} m³/h | ${Math.round(simState?.PCI ?? 115)} kg/t`, delta: (simState?.Fo ?? 0) - (baseState?.Fo ?? 0) },
    { tag: "Si", pos: [-3.2, -3.2, 1.5], label: "Hot Metal [Si] & HMT", val: `${Number(simState?.Si ?? 0.47).toFixed(3)}% | ${Math.round(kpis?.HMT ?? 1498)}°C`, delta: (simState?.Si ?? 0) - (baseState?.Si ?? 0) },
    { tag: "Production", pos: [3.4, -3.2, 1.5], label: "Hot Metal Production", val: `${Math.round(kpis?.Production ?? 4450)} t/day`, delta: (simState?.Production ?? 0) - (baseState?.Production ?? 0) },
  ];

  return callouts.map((c) => {
    const isSel = selectedTag === c.tag;
    const gStatus = paramByTag?.[c.tag]?.simulated_golden_status || "in_golden";
    const isOut = gStatus !== "in_golden";
    if (anomalyPinsOnly && !isOut && !isSel) return null;
    return (
      <Html key={c.tag} position={c.pos} distanceFactor={15}>
        <button
          type="button"
          className={`sensor-tag clickable pin-${gStatus} ${isSel ? "selected" : ""}`}
          onClick={() => onSelectTag?.(c.tag)}
        >
          <span>
            {c.label} {isOut ? (gStatus === "below_golden" ? "[LOW]" : "[HIGH]") : ""}
          </span>
          <b>{c.val}</b>
          {Math.abs(c.delta) > 0.005 && (
            <em className={c.delta > 0 ? "up" : "down"}>
              Δ {c.delta > 0 ? "+" : ""}
              {Math.abs(c.delta) < 1 ? c.delta.toFixed(3) : c.delta.toFixed(1)}
            </em>
          )}
        </button>
      </Html>
    );
  });
}

function Scene({ simState, baseState, kpis, paramByTag, open, selectedTag, onSelectTag, showAllPins, anomalyPinsOnly, themeMeta }) {
  const temp = Number(simState?.Th ?? 1100);
  const bg = themeMeta?.canvasBg || "#070b12";
  const lightCol = themeMeta?.lightColor || "#e2f1ff";
  return (
    <>
      <color attach="background" args={[bg]} />
      <ambientLight intensity={0.48} />
      <directionalLight position={[9, 15, 8]} intensity={1.38} color={lightCol} />
      <pointLight position={[0, -1, 2.5]} intensity={7 + (temp - 900) / 70} color="#ff9636" distance={14} />
      <Shell open={open} themeMeta={themeMeta} />
      <PeripheralWallRing
        simState={simState}
        baseState={baseState}
        paramByTag={paramByTag}
        selectedTag={selectedTag}
        onSelectTag={onSelectTag}
        showAllPins={showAllPins}
        anomalyPinsOnly={anomalyPinsOnly}
      />
      <TopOfftakeSensors
        simState={simState}
        paramByTag={paramByTag}
        selectedTag={selectedTag}
        onSelectTag={onSelectTag}
        anomalyPinsOnly={anomalyPinsOnly}
      />
      <InternalProcessZones simState={simState} kpis={kpis} />
      <KeyZoneCallouts
        simState={simState}
        baseState={baseState}
        kpis={kpis}
        paramByTag={paramByTag}
        selectedTag={selectedTag}
        onSelectTag={onSelectTag}
        anomalyPinsOnly={anomalyPinsOnly}
      />
      <OrbitControls enablePan={false} minDistance={9} maxDistance={28} target={[0, 5.2, 0]} />
    </>
  );
}

export default function TwinCanvas({
  simState,
  baseState,
  kpis,
  paramByTag,
  open,
  selectedTag,
  onSelectTag,
  showAllPins,
  anomalyPinsOnly,
  themeMeta,
}) {
  return (
    <Canvas camera={{ position: [12.5, 7.2, 16.5], fov: 39 }} dpr={[1, 1.75]}>
      <Scene
        simState={simState}
        baseState={baseState}
        kpis={kpis}
        paramByTag={paramByTag}
        open={open}
        selectedTag={selectedTag}
        onSelectTag={onSelectTag}
        showAllPins={showAllPins}
        anomalyPinsOnly={anomalyPinsOnly}
        themeMeta={themeMeta}
      />
    </Canvas>
  );
}
