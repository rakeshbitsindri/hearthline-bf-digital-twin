# Data request for the blast furnace extract

Send this to the historian and the ironmaking process team before the extract is built. Hourly means alone cannot answer "production fell and every parameter looks the same". Several of the columns below are cheap to add at extract time and expensive to reconstruct later.

Please provide a sample of one furnace for one month first, with a data dictionary, so mapping can be checked before the full 3–4 year pull.

## 1. Identity and time

For every file:

- Furnace id, plant, campaign id if one exists.
- Timestamp in a named timezone, not a local wall time without the zone. Say whether the stamp is the start or the end of the hour.
- The aggregation rule per tag: raw sample nearest the hour, hourly mean, hourly median, or last value. A mean and a snapshot behave differently and must not share a column type.
- Units as recorded, and the reference conditions for any Nm³ (temperature, pressure, wet or dry basis).
- A flag when the tag was substituted, frozen, or bad-quality in the historian.

## 2. The column that changes the project

For every tag that exists faster than hourly, add four hourly companions:

| Column | Definition |
|---|---|
| `<tag>__std` | Standard deviation inside the hour |
| `<tag>__min` | Minimum inside the hour |
| `<tag>__max` | Maximum inside the hour |
| `<tag>__exc` | Count of samples that crossed a stated threshold |

State the threshold rule next to `__exc` (absolute, or outside mean ± k·σ). Priority tags: blast pressure, top pressure, shaft pressures, hot blast temperature, stockline or radar level, stave temperatures, top gas temperature, differential pressure.

If the historian cannot emit these, say so explicitly. Absence is a scope limit the model must disclose. Please do not silently drop them.

## 3. Tags by role

Use the names the plant already has. The standard concepts are in `knowledge/01-parameter-catalog.md`. Map later. Do not rename tags in the extract.

**Manipulated.** Blast volume (state whether Nm³ or actual), hot blast temperature, oxygen enrichment and oxygen flow, steam or moisture setpoint, PCI and other injectant flows, coke rate and nut coke, burden recipe and batch weights, charging program and chute angles, top pressure setpoint, taphole length and drill diameter.

**Disturbances, including ones that usually live outside the BF historian.**

- Coke: CSR, CRI, ash, moisture, sulphur, size, M40/M10, alkali in ash. Lab timestamp and the time the coke was charged, separately.
- Sinter and pellets: RDI, RI, FeO, basicity, −5 mm, tumble and abrasion, swelling. Same two timestamps.
- Ore and flux: Fe, SiO₂, Al₂O₃, MgO, P, moisture, LOI.
- Alkali and zinc input by material, kg/tHM or the analyses needed to compute it.
- Ambient: dew point or absolute humidity, barometric pressure, blower inlet temperature, stockyard or charge moisture, a rain flag if one exists.

**State response, stored disaggregated.**

- Per tuyere: blast flow or a blowpipe pressure, PCI flow, cooling-water flow in and out, temperature in and out.
- Per stave and per elevation: temperature. Do not send only a zone average.
- Shaft pressures at each elevation and each available azimuth.
- Top gas CO, CO₂, H₂, N₂, CH₄, temperature, pressure, dust rate. Radial probe or acoustic tomography if it exists.
- Cooling-water flow and ΔT per circuit.
- Stockline, radar or stockrod, at the fastest rate you will export, plus the hourly stats from section 2.
- Hearth and bottom thermocouples at each depth.

**Outcomes.**

- Hot metal production by all three routes you have: torpedo weighbridge, iron balance from burden, summed cast weights. Say which column is which.
- Cast table: taphole, start, end, hot metal weight, slag weight or a granulation total, temperature, Si, S, P, Mn, C, Ti.
- Slag analysis: CaO, SiO₂, Al₂O₃, MgO, FeO, S, and alkali if analysed.
- Per-taphole chemistry where samples are taken per taphole rather than per day.

**Events.**

- Delay and downtime intervals with a reason code.
- A flag, or a reason-code family, that distinguishes a commanded blast cut (steel shop, ladles, granulation, oxygen, power) from a cut forced by furnace pressure or hanging.
- Tuyere changes, taphole clay type, stove changes, calibration events on the blast meter, gas analysers, weighers, and thermocouples.
- Burden-material batch ids so certificates join to charges.

## 4. Production provenance

Please answer these in a short note with the sample, not only in column names.

1. Which system creates the official daily tonne figure?
2. How is a cast that crosses an hour boundary split across hours?
3. Are tonnes wet or dry, and is scrap or skull corrected?
4. How often is coke moisture sampled, and is the charging weight wet or dry?
5. Can torpedo-fleet inventory be exported at day boundaries?

## 5. Format

- Parquet preferred, CSV acceptable for the one-month sample. One furnace per file, or an explicit furnace column.
- UTF-8. Decimal point, not a thousands separator inside numbers.
- Missing as null, not as 0, not as a blank that becomes 0 on import.
- A sidecar data dictionary: tag, description, unit, range the instrument can physically produce, sample rate, aggregation, quality flag rules.

## 6. What this extract is for

The first use is a paired comparison. Find periods where blast, oxygen, PCI, coke rate, and top pressure match, and production does not, then test whether variance, circumferential spread, raw-material certificates, alkali balance, or the production-accounting route explains the gap. Columns that only exist as a daily average still help. Columns that are dropped because they "look constant" are often the ones that matter. Please include them.

## 7. Geometry and sensor positions

The twin cannot place a sensor without a position. Please add a sheet, one row per station:

- Profile station, elevation from the tuyere centreline, internal diameter.
- Tuyere index, angle, nose diameter, protrusion.
- Stave index, elevation, circumferential angle.
- Pressure-tap elevation and azimuth.
- Top-gas and peripheral thermocouple positions.
- Hearth thermocouple depth and angle.
- Which engineering drawing and revision the coordinates came from.

## 8. Clocks, campaigns, and authority

- For each source system: NTP or PTP source, typical clock skew, and whether the timestamp is the instrument, the server, or the archive.
- Campaign id, start, end, and whether the hearth was emptied.
- Instrument replacements and calibration intervals with `valid_from`.
- Which system is authoritative for process tags, analyses, casts, delays, geometry, and calibration. The platform will not overwrite those systems.

## 9. Historian connection, when you are ready

This is optional until the file extract is understood. It is read-only.

- Historian product and whether we may use a replica or an export node in the industrial DMZ.
- A least-privilege identity limited to named read operations. No write, no method call, no ad hoc query.
- Network path, certificate authority, and the vault where the secret will live.
- Retention available for backfill. Please do not trim to three years if older history exists.
- Whether minute samples, or at least within-hour standard deviation, minimum, maximum, and excursion counts, can be read continuously after backfill.

The file extract remains useful if the connector is refused. Say which of these you cannot provide.

## 10. Acquisition priority

If the full catalog in section 3 cannot be delivered at once, send the critical group first: geometry, blast volume, hot-blast temperature, oxygen, injectant rates, coke rate, ferrous weights with Fe, and every production route you have. Hot-metal temperature and silicon are both needed. They do not replace each other. Within-hour statistics on blast pressure, shaft pressures, and stockline are the next most useful addition.
