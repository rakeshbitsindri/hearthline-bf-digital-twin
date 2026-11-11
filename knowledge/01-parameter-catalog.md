# Measured blast furnace parameters

Reference basis: a modern large furnace, 3000–5500 m³ working volume, 32–42 tuyeres, 13.5–16 m hearth diameter, roughly 8,000–13,000 t/day. Ranges marked with a warning vary widely by plant or rest on a single source. Role codes are defined in [README.md](README.md).

## 1. Blast and hot blast

| Tag | Quantity | SI | Plant unit | Typical range | Instrument | Role |
|---|---|---|---|---|---|---|
| `CBF` / `VB` | Cold blast flow | m³/s STP | Nm³/min | 6,000–8,500 | Venturi or orifice in the cold blast main | manipulated |
| `HBT` | Hot blast temperature | K | °C | 1,100–1,250, max about 1,280 | Thermocouple in the hot blast main | manipulated |
| `HBP` | Blast pressure | Pa | bar(g) | 3.8–5.5 | Transmitter on the bustle main | state_response (often saturates against a limit) |
| Blast moisture | Humidity | kg/m³ | g/Nm³ | 8–30 natural; up to 40 with steam; some plants run 60–80 deliberately | Dew cell or chilled mirror | manipulated if steam-trimmed, else disturbance |
| Steam addition | Flow | kg/s | t/h | 0–8 | Orifice or vortex | manipulated |
| O₂ enrichment | Volume fraction | — | vol% above 21, or total O₂% | +2 to +8 (total 23–29) | Zirconia cell plus oxygen flow | manipulated |
| Blower discharge | Pressure, temperature, flow | Pa, K | bar, °C | 4.5–6.5 bar, 180–230 °C | Turbo-blower instruments | state_response |
| Per-tuyere blowpipe pressure | Pressure | Pa | kPa | Balance check | Tap at the blowpipe | state_response |
| Tuyere count | Count | — | — | 32–42 | Design | disturbance (configuration) |
| Tuyere nose diameter | Length | m | mm | 120–150 | Measured at replacement | disturbance (configuration) |
| Tuyere nose velocity | Velocity | m/s | m/s | 200–280 | Derived | derived_latent |

One review quotes blowpipe velocity of 100–200 m/s ([doi 10.30544/414](https://doi.org/10.30544/414)). That is the larger-bore blowpipe, not the tuyere nose. Keep the two tags separate.

Also log blower inlet temperature, barometric pressure, and whether blast volume is stored as Nm³ or actual m³. The conversion moves with weather, and "constant blast volume" in one convention is not constant velocity in the other. See [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) section 9.

## 2. Injectants

| Parameter | Plant unit | Typical range | Instrument | Role |
|---|---|---|---|---|
| PCI rate | kg/tHM | 90–120 Japanese practice; 150–200 high-PCI; burnout limit near 190–230 | Loss-in-weight cells, Coriolis | manipulated |
| PCI loading | g coal / Nm³ blast | about 150 | Derived | derived_latent |
| Natural gas | kg/tHM | 0–150 (North America) | Orifice and mass flow | manipulated |
| Coke oven gas | Nm³/tHM | 0–120 | Orifice | manipulated |
| Oil or tar | kg/tHM | 0–60, now uncommon | Coriolis | manipulated |
| Hydrogen | kg H₂/tHM | Trials 0.6–1.0; theoretical ceiling cited near 28 | Thermal mass flow | manipulated |
| Lance configuration | — | single, coaxial, oxy-coal | Design | disturbance (configuration) |
| Per-tuyere coal split | % deviation | target about ±5% | Per-line Coriolis | state_response |

Sources: [IEA CCC-116](https://www.sustainable-carbon.org/wp-content/uploads/dlm_uploads/reports/Combustion/use-of-pci-in-blast-furnaces-ccc-116.pdf), [thyssenkrupp BF9 hydrogen trial](https://www.thyssenkrupp-steel.com/en/newsroom/press-releases/thyssenkrupp-steel-concludes-first-test-phase-successfully.html).

Per-tuyere distribution is more informative than the furnace-average PCI rate. See asymmetry in [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) section 8.

## 3. Burden and charging

| Parameter | Unit | Typical range | Instrument | Role |
|---|---|---|---|---|
| Sinter / pellet / lump split | wt% of ferrous | Regional. Europe often 60–75 / 10–25 / 10–15. Some plants 100% pellet. | Hopper load cells | manipulated |
| Total ferrous burden | kg/tHM | about 1,550–1,650 | Load cells | derived_latent |
| Coke rate | kg/tHM | 280–340 low-fuel; up to about 390 | Load cells | manipulated |
| Nut coke | kg/tHM | 20–85 | Load cells | manipulated |
| Flux (limestone, dolomite, quartzite) | kg/tHM | 0–60 when most flux is already in sinter | Load cells | manipulated |
| Ore/coke ratio | t/t | 4.5–5.5; Shougang Jingtang has reported above 6.0 | Derived | derived_latent |
| Ore batch weight | t | 80–180 per charge | Load cells | manipulated |
| Charges per hour | 1/h | 8–14 | Counter | manipulated |
| Charging sequence | — | example C-C-O-O, platform-plus-funnel, central coke | Program | manipulated |
| Bell-less top chute tilt | deg | about 10 ring positions, often 20–50° | Chute encoder | manipulated |
| Rings and rotations per charge | — | 10–14 rings typical | Program | manipulated |
| Stockline | m below zero | 1.0–2.0 | Stockrod, radar, profilometer | manipulated setpoint, state_response actual |
| Burden descent rate | m/min | 0.10–0.13, mean near 0.117 | Stockrod or radar derivative | state_response |
| Slips | count/day | target 0. Tata Steel: a step above 100 mm on radar is a slip; about 50 mm is a drop | Radar | state_response |
| Hangs | count/day | target 0. No radar change over a set window | Radar | state_response |

Sources: [ISIJ Int. 55(6) 1146](https://www.jstage.jst.go.jp/article/isijinternational/55/6/55_1146/_pdf), [Saxén stockrod analysis](https://www.jstage.jst.go.jp/article/isijinternational1989/41/2/41_2_142/_pdf/-char/en), [Tata Steel soft sensors, ISIJ Int. 63(1)](https://www.jstage.jst.go.jp/article/isijinternational/63/1/63_ISIJINT-2022-246/_html/-char/en).

Identical chute setpoints do not guarantee identical burden distribution. Hopper fill history changes where the fines land. Log the program *and* a realised-distribution proxy (above-burden probe, profilometer, or a radar ore-by-coke soft sensor).

## 4. Raw material quality

These are disturbances. They are often measured at the coke plant or sinter plant days before the material reaches the tuyeres, and the blast furnace hourly log frequently omits them. Ask for them explicitly. See [../DATA_REQUEST.md](../DATA_REQUEST.md).

### Coke

| Property | Unit | Target on a large high-PCI furnace | Method |
|---|---|---|---|
| CSR | % | 60–70, prefer at least 65. Below 60 is commonly rejected. | ISO 18894 |
| CRI | % | 20–30, prefer at most 25. High-PCI guidance often wants CRI below 29. | ISO 18894 |
| M40 / M25 | % | M40 above 80–88; M25 at least 88–90 | ISO 556 |
| M10 | % | at most 6–7 | ISO 556 |
| Ash, dry basis | % | 10–13, prefer at most 11 | ISO 1171 |
| Volatile matter | % | below 1.2 | ISO 562 |
| Sulphur | % | 0.5–0.8 | ISO 19579 |
| Moisture | % | 1–6 wet quench; below 1 for CDQ. Stability within ±0.5 matters as much as the level. | ISO 579 |
| Size | mm | mean 45–60; +80 mm under 5%; −25 mm under 5% | ISO 728 |
| Alkali in ash | % | as low as practical | XRF |

CSR is a laboratory index. Inter-laboratory scatter can reach about ±2 points, and tuyere-level coke is roughly half the charged size. See [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) section 7.

Sources: [mesteel coke parameters](https://mesteel.com/product-info/base-materials/coke/coke-quality-parameters), [Lviv Polytechnic review 2025](https://science.lpnu.ua/sites/default/files/journal-paper/2025/oct/40503/fulltext1388.pdf).

### Sinter

RDI 22–32 (lower is better; plant optima differ). RI often 65–75. Tumbler index around 69 ± 6. Abrasion index at most about 5%. Basicity CaO/SiO₂ commonly 1.6–2.1, practice near 1.7. FeO 8–10% is a frequent window; Tata Steel Kalinganagar has reported 10.4–10.8% as the joint optimum for fuel rate and permeability on that plant. −5 mm at most about 5%. MgO near 2.5% is often cited as a fluidity aid. SFCA as the dominant bonding phase.

A rise in FeO can improve RDI and hurt reducibility at the same time. Log both.

Sources: [MECON sinter notes](https://www.meconlimited.co.in/writereaddata/mist_2016/sesn/tech_2/6.pdf), [JSW FeO study](https://doi.org/10.1179/1743281211y.0000000080).

### Pellets and ore

Pellets: tumbler 85–95%, abrasion 3–7%, free swelling target under 20% (clustering risk above). Cold crushing strength is often quoted near 200–250 daN/pellet; that figure was not confirmed in the sources read for this catalog.

Ore and burden chemistry: Fe 58–62%, SiO₂ 3–6%, Al₂O₃ 1–3%, P 0.03–0.09%, crystal water and LOI 1–8%. Two ores at the same Fe grade and different alumina do not drain the same way. A spinel phase has been reported between 15 and 17 wt% Al₂O₃ in slag, after which viscosity and liquidus rise quickly ([Can. Metall. Q. 2022](https://doi.org/10.1080/00084433.2022.2144595)).

Contaminant input limits used in practice:

- Alkali Na₂O + K₂O: commonly at most 2.5–3.0 kg/tHM. Some plants have run higher and then cut back after a collapse.
- Zinc: 100–150 g/tHM is a widely cited band. Plant standards differ by an order of magnitude in the Chinese literature, so use the plant's own limit.

Sources: [alkali behaviour paper](https://www.bindingsolutions.uk/wp-content/uploads/2025/09/ON-Na2O-AND-K2O-BEHAVIOUR-IN-BLAST-FURNACE-OPERATION-paper126.pdf), [METAL 2022 zinc](https://doi.org/10.37904/metal.2022.4386).

## 5. Top gas

| Parameter | Unit | Typical range | Instrument | Role |
|---|---|---|---|---|
| CO | vol% dry | 20–25, span 20–28 | IR or mass spec | state_response |
| CO₂ | vol% dry | 20–24, span 17–25 | IR | state_response |
| H₂ | vol% dry | 2–7, rises with PCI, natural gas, moisture, and water leaks | Thermal conductivity | state_response |
| N₂ | vol% dry | 45–55 | By difference | state_response |
| CH₄ | vol% | at most about 0.2 | GC or mass spec | state_response |
| Top gas temperature | °C | 100–200 normal; spikes toward 600 on channeling | Thermocouple array; acoustic tomography | state_response |
| Top pressure | bar(g) | 1.5–2.5. Example: voestalpine BFA 2.3. | Transmitter | manipulated |
| Top gas flow | Nm³/tHM | 1,200–2,000 | Usually derived from blast plus carbon balance | derived_latent |
| Dust rate | kg/tHM | 8–15 is a common band; some plants cite 5–10 g/Nm³ and others 10–40 g/Nm³ | Dust catcher or isokinetic sample | state_response |
| Radial temperature and gas profile | °C, vol% | Edge often near 120 ± 50; centre near 450 ± 150 | Above-burden probe | state_response |

Gas utilisation ηCO = CO₂ / (CO + CO₂) is derived. Platform-plus-funnel charging has been reported at 50.5–52.5%, central-coke charging at 46.5–48.5%, a gap worth about 20 kg/tHM of fuel. See [02-derived-indices.md](02-derived-indices.md).

Top gas H₂ above a hydrogen balance is a water-leak signature (Ternium Brasil). Do not treat a high H₂ reading as "more injectant" until the balance is closed.

Sources: [IspatGuru BF gas](https://www.ispatguru.com/blast-furnace-gas-its-characteristics-and-safety-requirements/), [ISIJ Int. 59(3)](https://www.jstage.jst.go.jp/article/isijinternational/59/3/59_ISIJINT-2018-591/_html/-char/en).

## 6. Furnace body

| Parameter | Unit | Typical | Instrument | Role |
|---|---|---|---|---|
| Shaft pressure at several elevations | kPa | Monotone fall from bustle to top | Purged shell taps | state_response |
| Total pressure drop, blast minus top | kPa | 150–220 | Derived | state_response |
| Upper pressure drop | kPa | 30–70 | Derived | state_response |
| Lower pressure drop | kPa | 90–160 | Derived | state_response |
| Stave and cooling-plate temperature | °C | 50–250, zone dependent | Embedded thermocouples | state_response |
| Shell temperature | °C | below 150 in normal operation | Surface thermocouples | state_response |
| Cooling-water flow per circuit | m³/h | pipe velocity often 1.5–2.5 m/s | Magnetic flow meter | state_response |
| Cooling-water temperature rise | K | inlet 25–35 °C, outlet 35–60 °C | Matched RTDs | state_response |
| Stave heat flux | kW/m² | about 20 normal; low 30s has been used as a severe-erosion alarm | q = N · ṁ · cₚ · ΔT / A | derived_latent |
| In-burden probe temperature | °C | 200–1,000 radial profile | Water-cooled probe | state_response |
| Hearth and bottom thermocouples | °C | 1,150 °C isotherm tracked for wear | Multi-depth nests | state_response |

The diagnostic content is in the *array*, not the average. Store every stave, every elevation, and every tuyere. Circumferential standard deviation and the loss of correlation between gauges are first-class features. See [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) sections 3 and 8, and the JFE Q-statistic in [07-ml-literature.md](07-ml-literature.md).

A vendor note listing stave cooling-water pressure at 33–45 bar is implausible. Realistic bands are a few bar, or roughly 6–10 bar on high-pressure circuits. Treat 33–45 bar as a likely decimal error.

Sources: [AIP Advances hearth heat flux](https://pubs.aip.org/aip/adv/article/10/2/025308/21861/Monitoring-the-safety-status-of-a-blast-furnace), [Nippon Steel stave report](https://www.nipponsteel.com/en/tech/report/pdf/123-15.pdf).

## 7. Hot metal and slag

| Parameter | Unit | Typical range | Role |
|---|---|---|---|
| Production | t/day, t/h | 8,000–13,000 t/day; 330–540 t/h on this size class | outcome |
| Hot metal temperature | °C | 1,480–1,530, control band often ±15 K | outcome |
| Si | wt% | 0.30–0.60 modern low-Si practice; 0.7–1.0 older practice | outcome |
| S | wt% | 0.020–0.040. Above about 0.05 has been tied to hearth scabbing. | outcome |
| P | wt% | 0.05–0.10, span 0.01–0.15 | outcome |
| Mn | wt% | 0.20–0.80 | outcome |
| C | wt% | 4.3–4.8, near saturation. Departure from saturation is a deadman cleanliness signal. | outcome |
| Ti | wt% | 0.03–0.15; raised toward 0.10–0.20 on purpose for hearth protection | manipulated via burden, outcome as analysis |
| Slag volume | kg/tHM | 250–350 typical; 150–165 best reported (SSAB Luleå 164, Oxelösund 155). An older EU mean was about 254. | derived_latent |
| Slag CaO / SiO₂ / Al₂O₃ / MgO | wt% | 38–45 / 33–37 / 11–16 / 6.5–10 | outcome |
| Slag FeO | wt% | 0.3–0.6. A rise points at worse reduction or a colder bosh. | outcome |
| Slag S | wt% | 1.0–1.8 | outcome |
| Slag temperature | °C | 1,480–1,550 | outcome |
| Slag viscosity at 1,500 °C | Pa·s | 0.3–0.8, target under 1.0 | derived_latent |

Production is usually *derived*. Three routes exist and they disagree: torpedo weighbridge, iron balance from burden charged, and summed cast weights. Record which route a column came from, the allocation rule for casts that cross an hour boundary, and the moisture correction. See Gate 0 in [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) section 12.

Sources: [SSAB slag paper](https://www.pyrometallurgy.co.za/MoltenSlags2000/pdfs/105.pdf).

## 8. Cast house

| Parameter | Unit | Typical range | Role |
|---|---|---|---|
| Taphole count | — | 2 on hearths up to about 10 m; 4 on hearths from about 14 m | disturbance (configuration) |
| Taphole length | m | 2.5–4.0, often SPC-controlled near 3.1. Older small furnaces 1.8–2.0. | manipulated |
| Drill diameter | mm | 38–50 common; up to 70 on very high rate | manipulated |
| Taphole wear rate | mm/s | about 5.6×10⁻⁴; poor clay near 1×10⁻³ | state_response |
| Tapping rate | t/min | 5–7 hot metal; liquid velocity near 5 m/s | state_response |
| Cast duration | min | 90–240. Tap-to-tap gap 0–20 on multi-taphole furnaces. | state_response |
| Dry hearth time | min | target 0–15. A truly dry hearth does not occur; slag remains. | state_response |
| Clay volume per closure | L | 100–120 for a stable mushroom; 10–300 when rebuilding | manipulated |
| Clay consumption | kg/tHM | about 0.5–0.9. Weak single-source support. | state_response |
| Slag breakthrough | fraction of cast | often 60–75% | state_response |

Sources: [SAIMM taphole](https://saimm.co.za/Journal/v116n05p465.pdf), [Geyer, ArcelorMittal tapping](http://www.saimm.co.za/Conferences/FurnaceTapping/097-Geyer.pdf).

## 9. What to store that a typical hourly sheet drops

These columns are the ones that separate "parameters look the same" from "the furnace is the same".

1. Within-hour standard deviation, minimum, maximum, and excursion count for every high-rate tag the historian can emit. Slips, hangs, and pressure spikes do not survive an hourly mean.
2. Per-tuyere blast flow, PCI flow, and cooling-water differential, not only the furnace total.
3. Per-stave temperature, not a zone average. Store the circumferential standard deviation as its own series.
4. Per-taphole hot metal temperature, Si, S, and C.
5. Coke, sinter, and pellet certificates joined on the *charging* timestamp, with the lab timestamp kept beside them.
6. Ambient dew point, barometric pressure, blower inlet temperature, and stockyard moisture.
7. Delay and downtime minutes with a reason code, and a flag for whether a blast cut was commanded or forced.
8. Which production route produced the tonne figure, and the torpedo-fleet inventory at period boundaries.
9. Calibration events for the blast flow meter, gas analysers, thermocouples, and weighers.

## 10. Uncertainty flags

1. Productivity denominators differ by region: working volume, inner volume, and hearth area. A quoted 2.2 t/(m³·day) is not comparable across Europe, Japan, and China until the denominator is named.
2. "Blast kinetic energy" is published both as momentum (kg·m/s) and as power (kW). See [02-derived-indices.md](02-derived-indices.md).
3. Slag volume spans 150–350 kg/tHM almost entirely because of burden gangue. Targets do not transfer between plants.
4. Taphole clay consumption and stave cooling-water pressure are the weakest numbers in this catalog.
