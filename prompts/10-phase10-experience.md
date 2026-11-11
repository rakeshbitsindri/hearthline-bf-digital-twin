# 10 — Experience

Read `CLAUDE.md`, `knowledge/16-twin-commissioning-and-acceptance.md`, and `UX_DESIGN.md`. This phase finishes the workplaces on APIs that exist. A missing API gets an empty state that names the phase. It does not get a fake number.

Use the project design skill. Do not restyle into a generic dashboard.

## Workspaces

**Observe.** Command center: production when the capability allows, otherwise the capability status; silicon and hot-blast temperature when present; fuel rates when present; active gate; forecast interval; alarm count. EVRAZ shows the public-reference banner and the 2013–2016 clock.

**Investigate.** Sensor search by role. Trend, band, quality class, dispersion if present. 2D scaled cross-section is the quantitative view. Circumferential map for `Tp1`–`Tp10` on EVRAZ, with the statement that angles were not in the file, so the map is an index order unless positions are configured. Pressure profile. Interactive Rist when the balance ran. Mystery board from phase 6.

**Decide.** What-if and the optimiser from phases 4 and 8. Scenario studio states: draft, validate, run, review, share, accept, reject, archive. Completed runs are immutable. Branches keep the parent id. Watermark on scenario views. Path from the simulator, not only the end point.

**Govern.** Model cards, capability matrix, audit log, mapping, geometry versions. Accept and reject write the audit table. They do not write to a plant.

## 3D

Progressive cutaway after the 2D view has painted. Staves and tuyeres only at configured positions. Zones as zones. Estimated motion uses the estimated style and the uncertainty. Every 3D mark has a 2D or table equivalent. No WebGL: 2D remains complete. Context loss returns to 2D. Reduced tier targets 30 frames per second. Full tier targets 60 on the named reference machine.

## Collaboration

Investigation owner, comments tied to furnace, time, tag, and view, shift handover summary, immutable deep link, PDF and CSV export. Exports include timestamps, units, versions, uncertainty, origin, and author. None of these call a historian write API.

## Accessibility and displays

WCAG 2.2 AA as far as automated checks plus a documented keyboard pass. Visible focus, non-colour provenance, reduced motion, 200% zoom. Control-room and laptop layouts. A tablet summary. No hover-only critical control. Selected furnace and time stay fixed while scrolling.

## Performance

Record device, browser, window, p75, and p95 for shell time, simulation time, and frame time. Run the soak in `knowledge/16-twin-commissioning-and-acceptance.md` or document why it was not run.

## Exit

`docs/ui.md` maps pages to endpoints. A test fails if a page contains a numeric literal for production, silicon, or temperature other than an axis bound. Playwright, or the closest scripted browser available, covers: public banner, stale timestamp, replay not labelled live, blocked setpoint on EVRAZ, and the no-WebGL path.
