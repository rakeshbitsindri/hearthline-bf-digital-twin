# Plant cases, benchmarks, and existing systems

Evidence grades: **[P]** paper or regulatory report, **[C]** company or vendor, **[T]** trade press, **[I]** inference. Benefit numbers on vendor pages are unaudited. Use the detection signatures. Do not copy the savings claims into a model card.

## 1. Cases with a published cause and a usable signature

| Plant | What happened | Published cause | Signature to copy | Source |
|---|---|---|---|---|
| SSAB Raahe BF2, Jan 2019 | Minor hearth breakout. ~8 week stop, ~SEK 200 m in Q1. | Hearth wall penetration. Maintenance pulled forward. [C] | The breakout itself, then a condition survey. | [SSAB](https://www.ssab.com/en/news/2019/02/ssab-europe-carries-out-repairs-and-brings-forward-maintenance-work-at-blast-furnace-2-in-raahe) |
| Dofasco No. 4, 1994 | Taphole breakout. | Coke quality, productivity, casting, and leaking cooling members driving hearth temperature fluctuations. [P] | Hearth thermocouple fluctuation. | [OSTI 577458](https://www.osti.gov/biblio/577458) |
| US Steel BF14, 2016–18 | Hearth wall temperature up under all three tapholes. | Water from tuyere-nose circuits ate the protective skull. Extreme case oxidises hearth carbon. [P] | Per-tuyere nose-circuit flow imbalance. | [AISTech 377/055](https://doi.org/10.33313/377/055) |
| Port Talbot BF5, Nov 2001 | Explosion, 3 killed, 12 injured. Furnace top lifted. | Official account: water met hot material. [T] | Catastrophic. Not an early-warning dataset. | [BBC](https://www.bbc.co.uk/news/articles/c8vdq6y56v0o) |
| Burns Harbor BF D, 16 Jul 2020 | Hot-blast stove dome separated. ~$22 m damage. | CSB: an improper weld repair. Shell thinned from 1 in to ~0.1 in by oxidation. Repair plate 0.25 in against 0.56 in required. 36 psi ran the crack. [P] | Shell-thickness inspection that was not effective. | [CSB](https://www.csb.gov/assets/1/6/incident_reports_volume_4_2026-02-18.pdf) |
| ArcelorMittal Dunkirk, ARIA 60812 | Restart after an emergency stop. Mass CO release. | Hearth was cold. Liquid below the taphole had frozen. Could not reach gas-network pressure. Started on 8 tuyeres because 10–12 would have made too much liquid at once. [P] | Cannot reach network pressure. Cold hearth. | [ARIA 60812](https://www.aria.developpement-durable.gouv.fr/accident/60812_en/?lang=en) |
| thyssenkrupp Schwelgern BF1 vs BF2, ~6 weeks in 2021 | Same raw-material crisis, different outcome. | Weighted coke CSR fell to ~63 with large swings. Sinter basicity swung 1.9–2.1. BF2: wall heat load, hanging, channeling. BF1 on SIP held. [C] | η_CO from >49% to ~47%. RAR 510 → 530. Blast acceptance limited by hot blast pressure. BF2 at ~85% capacity, BF1 at 100% and ~509 kg/tHM. | [SEAISI / SIP paper](https://www.seaisi.org/storage/event_agendas/uOYu6jJdpiP6sTSCjjIgLflcM1sD7InBzlvErMcg.pdf) |
| Masteel A# 4000 m³, 4 Jan 2019 | Hearth carbon-brick temperature spike. | Late-campaign erosion. Point B2 jumped 142 °C to 684 °C. [P] | Single-point step change 1.5 m below a taphole. | [Hanspub](https://pdf.hanspub.org/meng20190300000_63717205.pdf) |
| Fangda Special Steel No. 4 | Forced stop, hearth cracking. | Zn erosion, then Na, poor carbon brick, Pb penetration, water on the slag-notch side. [P] | Multiple hearth cracks. | Chinese journal abstract. |
| Baotou No. 4 | Hearth/bottom wear after 18 years. | Elephant foot at the hearth/bottom junction, found by dissection. [P] | Post-campaign, not online. | Rare Earth Steel 2019. |
| Ansteel 2580 m³ | Restart after 31 days with burden in place. | Unplanned long stop. [P] | Hearth temperature decay, tuyere slagging risk. Full wind at 45 h, design capacity in 5 days, 2.0 t/m³/day, HM heat above 1450 °C. | Ansteel practice paper. |
| Masteel BF B, Jul–Aug 2012 | Weak centre, inactive hearth. | Charging and tapping. [P] | Low central gas flow. O/C raised 3.90 → 4.40 after central coke. | CNKI abstract. |
| CSN BF2 | Repeated skulls across the 5th campaign. | First large scaffold attributed to zinc. Returned after the Hot Stove 3 accident in 2002. [P] | Skull identification during the campaign. | [ABM](https://abmproceedings.com.br/en/article/control-of-the-scaffold-formation-in-the-csns-blast-furnace-2) |
| Ternium Brasil BF1 and BF2 | Stave displacement and copper deformation. | Campaign damage. 6 replacements on BF2, 1 on BF1. [P] | Shell heat, uneven descent, stops to remove water. A top-gas hydrogen balance separated cooling-water ingress from process H₂. | [ABM stave paper](https://abmproceedings.com.br/en/article/setima-troca-de-staves-altos-fornos-ternium-brasil), [H2 balance](https://abmproceedings.com.br/en/article/balanco-de-hidrogenioh2-aplicado-para-avaliar-o-estado-termico-de-alto-forno) |
| Tata Jamshedpur H BF | Hanging, channeling, scaffolding at low coke. | Coke rate pushed 450 → 350 kg/tHM, PCI toward 200, high-alumina ore, high coke ash. [C] | Channeling model, slag viscosity outside range. Reported three years with zero hangs. | [WASET abstract](https://publications.waset.org/abstracts/74931/achieving-process-stability-through-automation-and-process-optimization-at-h-blast-furnace-tata-steel-jamshedpur) |
| Tata Jamshedpur, monsoon | Instability. | Wet pellets roll less to the centre. Wall O/C rises. [P] | Top temperature down, CZ root down, heat loss up, slag FeO up. | [ISIJ 2022-246](https://doi.org/10.2355/isijinternational.isijint-2022-246) |
| Tata Jamshedpur, pellet share | Heat load after a burden change. | Pellets 35% → 46% of burden. [P] | Wall heat load 100 → 170 MJ/h. Stave excursion index rose with wall O/C. | same |
| Koverhar | Chronic hearth clogging, skimmer blockage. | HM S held 0.06–0.10% plus oil at 1.9–2.8% S. CaS scab. [P] | S above ~0.05%. | [Aalto thesis](https://aaltodoc.aalto.fi/handle/123456789/2134) |
| Gerdau Açominas BF1 | Drainage degradation. | Pneumatic drills, taphole length outside 3000–3200 mm. [P] | Length trend, cracked casts. Hydraulic drills recovered the length. | [doi 10.5151/2594-357x-12778](https://doi.org/10.5151/2594-357x-12778) |
| China Steel No. 2 | Channeling. | Uneven gas, rapid resistance change. [P] | L7 shaft-pressure RMSD > 0.15 kg/cm² and AGE opening > 60%. 10–15 min lead. | [CSC Tech Report 25](https://www.csc.com.tw/csc/ts/ena/pdf%5Cno25%5C4--Development%20of%20a%20Channeling%20Prediction%20System%20for%20a%20Blast.pdf) |
| Danieli Corus, 33 furnaces, 17 years | Chilled hearths. | Classified minor to very severe. ~5 of ~600 furnaces per year. [P] | Loss of tuyere connection. All but one recovery back to full production inside 200 h. | [ABM recovery paper](https://abmproceedings.com.br/en/article/download-pdf/experience-in-recovery-of-chilled-blast-furnaces) |
| IJmuiden BF6/BF7 | Five salamander taps in ten years. | Planned blowdown, not a failure. [P] | Thermocouple-grid wear line used to site the hole. Keeping blast pressure on to help drainage never worked. | [borrarna.se](https://www.borrarna.se/salamander-tapping/) |

The thyssenkrupp pair is the cleanest published natural experiment in this set: nearly the same raw materials, different technology and operating point, different production. The USS BF14, Dofasco 1994, and Fangda cases share one chain [I]: an undetected water leak degrades the hearth skull, the thermocouples then look like refractory wear, and the leak is missed.

No operational-problem papers turned up in open sources for Emirates Steel, Tosyalı, Erdemir, NLMK, or Severstal. Kobe's published contribution is the centre-coke principle rather than a named incident. Gent, Bremen, Tubarão, and Indiana Harbor show up in reline records more than in failure analyses.

## 2. Benchmark operating points

| Furnace | Year | Size | Productivity | Coke | PCI | Fuel | Other | Grade |
|---|---|---|---|---|---|---|---|---|
| Shougang Jingtang No. 1 | 2022 | 5500 m³ | 2.551 t/m³/day; >15,000 t/day monthly; hearth 78 t/m²/day | 263 kg/t | 196 | 496 | Blast 1230 °C monthly, O₂ 7–8%, O/C > 6, pellet > 55% | [P] |
| Schwelgern BF2 | 2012 / 2021 | 5513 m³, 14.9 m hearth, 42 tuyeres, 4 tapholes | ~12,000 t/day | — | 140–170 in the 2021 crisis | 530 in the crisis | η_CO < 47% in the crisis | [C] |
| Schwelgern BF1 with SIP | 2021–22 | 4416 m³, 13.6 m hearth | best hour +87 t/h over a reference | — | 140–170 | ~500–509 | median η_CO 49.1–51.1% | [C] |
| IJmuiden BF6/BF7 | ~2019 | BF7 14 m hearth, 3 tapholes | 3.5 t/m³ working volume/day claimed; availability > 98% | claimed 250 | claimed 250 | — | O₂ claimed 15% | [C] |
| Danieli Corus portfolio records | — | up to 6095 m³ inner | claimed > 4 t/m³ working volume/day | — | claimed > 250 | — | longest campaign claimed 37 years | [C] |
| SSAB Luleå BF3 | design | 2540 m³ WV, 11.4 m hearth, 32 tuyeres | 2.08 t/m³/day; 65.7 t/m²/day; average 6700 t/day | — | — | — | top 1.50 barg, blast 3.50 barg | [C] |
| Baosteel No. 4, 19-furnace comparison | 2011–14 | No. 4 is 4747 m³; fleet average 4539 m³ | fleet 2.15 t/m³/day | No. 4 coke 340, the lowest of the 19 | No. 4 PCI 156 | fleet RAR 511 | most of the 19 under 50% CO utilisation | [P] |
| POSCO Gwangyang No. 1 | 2016 | 6000 m³ | ~5.65 Mt/year | — | site record 225.5 in Aug 2005; site average 204 in 2005 | — | — | [C] / [T] |
| POSCO Gwangyang No. 3 | 2020 | 4600 → 5500 m³ | +25% claimed, 4.6 Mt/year | — | — | — | — | [C] |
| Nippon Steel Muroran No. 2 | 1998 | — | 2.14 t/m³/day | — | PCR 191 with high-Al₂O₃ sinter | — | — | [P] |
| Masteel A# | 2018 | 4000 m³, 36 tuyeres, 4 tapholes | 2.20 t/m³/day | — | 152 | 517 | — | [P] |
| JSW Vijayanagar BF3 | design, upgrade commissioning cited 2026 | 4019 m³, 36 tuyeres | ~8000 t/day, 3.0 → 4.5 Mt/year upgrade | — | — | — | blast 1250 °C, top 2.5 bar | [C] |
| Hyundai Dangjin BF1/2/3 | 2010–2013 | 4525 m³ each | 4.08 / 4.08 / 4.28 Mt/year | — | — | — | — | [T] |
| Raahe BF1 | ~2001 | ~1000 m³ WV | 3500 t/day | 330–350 | 80–100 oil | — | — | [P] |
| Review optimum | 2020 | best specific productivity at 2700–3700 m³ WV | max about 2.5 t/m³/day | min about 330, average about 363 | stable ~200 with coke under 300; RR ~1.0 up to 200, then declining | — | — | [P] |

Slag volume context, not in the table: SSAB Luleå 164 kg/tHM, Oxelösund 155, an older EU mean about 254. Fuel-rate "world best" near 460 kg/tHM is quoted in reviews. Treat anything below 480 as exceptional and check the denominator and the injectant convention.

## 3. Systems already running

Copy the split of labour. Do not copy the brochure.

| System | What it actually does | Published result | Grade |
|---|---|---|---|
| SMS / Paul Wurth BFXpert, on the SACHEM knowledge base | Level-2 guidance, phenomena detection, short and medium Si and hot-metal-temperature prediction, fuel-rate advice, permeability, raw-material tracking. | "Several kilograms" of coke at many customers. No error bars. Kardemir BF5 accepted May 2023. | [C] |
| Paul Wurth time-series translation | Treats each plant's sensors as a dialect. Builds a virtual sensor from another plant's history. | A Brazilian furnace's hot metal temperature, using German data, within 20 °C. | [C] |
| Primetals VAiron | Closed-loop expert system plus chemistry, permeability, and quality models. Active coke is a 5–8 h sum. Active coal is a 1.5–3 h sum. | Claims −5 kg/tHM coke, −10% quality standard deviation, +5% productivity, ~6 month payback. | [C] |
| Nippon Steel 3D-VENUS and Blast Brain | Stave and shaft-pressure imaging, scaffold thickness from two-depth couples, cohesive-zone root from stave time-change, JIT and tree models for hot metal temperature. ~500 stave couples at Nagoya, second-by-second. | Local linear models suffice under 4 h. Nonlinear models needed after that. No single headline error. | [C] |
| JFE cyber-physical system | 2-D transient model, PCA Q-statistic on shaft pressure and top-gas temperature, coke size at charging. | Hot metal temperature 8–12 h ahead from the physical model. σ from 15.9 to 14.0 °C when operators follow guidance (−13%). A CNN of operator behaviour cut a further 1.5 °C at Kurashiki No. 2. Q-statistic detected channeling 2.5 h before the operator. Fleet deployment. | [C], with a methods paper behind the Q-statistic |
| JFE NMPC, ISIJ Int. 59(9) 2019 and Metals 2022 | Nonlinear MPC, pulverised-coal rate as the manipulated variable, 8–10 h horizon. | Variance −1.9 °C and about 70% operator approval in guidance mode. Fully automatic: mean control error −4.6 °C, RMS −3.4 °C, inside ±20 °C, RAR −2.3 kg/t, CO₂ −20 kt/year claimed. | [P] |
| POSCO AI furnace | Deep learning on >1000 standardised types, five furnace-state variables, self-assessed input quality. | Taphole closing time: skip-dense CNN above 90% within ±30 min, deployed since Jan 2018. [P] Company claim +240 t/day and KRW 250 bn over 4 years. [C] | mixed |
| Baosteel closed-loop expert system, 2012 | Seven modules: temperature, airflow, burden, stoves. | Fuel ratio 488.9 → 485.4 kg/t. | [P], Chinese journal |
| Baosteel + Huawei furnace model | Foundation model, ~5000 dimensions, on No. 4 since Aug 2024. | Temperature 10 minutes ahead. ~2 kg/tHM fuel claimed. | [T] |
| ArcelorMittal MOGADOR and ZAP | 2-D steady model. Both compute cohesive-zone shape. | Agreed with probes. One model predicted the disturbance that followed an operating change. | [P] |
| Danieli Corus | Cooling and lining design, operating advice, chilled-hearth recovery. | 33 recoveries in 17 years. See the table above. | [P] for the recovery count |
| Hatch | Tuyere-nose leak soft sensor. Digital-twin language in their writing is mostly about electric arc furnaces. | USS BF14, 34 tuyeres, 2018. | [P] |
| Tata iMonitor | Burden descent index, stave excursion index, sounding ore-by-coke, cohesive zone, hearth level, remnant thickness from two insertion depths. | Ore-by-coke checked against a profilometer. The paper warns that a wrong thermocouple gives a wrong decision and needs continuous validation. | [P] |
| Åbo Akademi / Saxén | Hearth liquid level with drift correction, multi-taphole drainage, inverse-heat-conduction wear, stockrod interpretation. | Reproduced IJmuiden BF7 outflow and indicated a sitting deadman. Wear model over ~4 years on a two-taphole furnace. S leads sump depth by weeks. | [P] |
| LKAB experimental furnace, Luleå | 8-week campaigns, nitrogen quenched, excavated, hearth cores at centre, mid-radius, and wall. | K up to 30% of deadman coke ash. CSR cannot see recirculating alkali. This is ground truth, not a product. | [P] |

## 4. What "good" looks like when a system is actually closed around the furnace

JFE's published control results are the honest benchmark for value: a few degrees of hot metal temperature, a few kilograms per tonne of reductant, and about 70% operator agreement when the system is still in guidance mode. A projected gain an order of magnitude above that is a modelling artefact until a walk-forward test on this plant says otherwise.

Kokura No. 2 in 1977, with an adaptive model and oil injection as the manipulated variable, lowered hot metal temperature 15 °C and fuel rate 4 kg/t ([Tetsu-to-Hagané 67(3)](https://www.jstage.jst.go.jp/article/tetsutohagane1955/67/3/67_3_528/_article/-char/en)). The magnitude has been available for fifty years. The open problem is knowing *why* a period missed it.
