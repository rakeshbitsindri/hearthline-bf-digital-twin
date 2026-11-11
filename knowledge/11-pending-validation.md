# Pending validation register

These items showed up in the literature search with coefficients that are ambiguous, image-only, OCR-damaged, paywalled, or plant-fitted without a primary citation. The physics module must expose each one as a documented interface with `status: pending_validation`. It must not invent a coefficient to fill the gap.

When a metallurgist confirms a value, record the person, the date, the source, and the validity range, and flip the status. Until then, any screen that would have used the number shows "not validated" instead of a fabricated result.

| ID | Item | What is wrong | What to do |
|---|---|---|---|
| PV-01 | Geerdes Annex III coke-rate adjustment table | Row pairing was reconstructed from reflowed PDF text. The blast-temperature line (−9 kg/tHM per +100 °C) is smaller than the often-quoted −20 to −30, because Geerdes holds blast volume constant and lets productivity absorb the change. The oxygen line is +1 kg/tHM per +1% at constant blast volume, not −4. | Ship the table as config. Default it off. Require a signed convention: constant blast volume or constant production. |
| PV-02 | Slag-formation heat, 196.7×10⁴ | Cited from ISIJ Int. 51(7) 2011 Eq. A-42. Units and basis were ambiguous in the text extraction. | Do not code the constant. Accept a measured cooling-loss term and a configurable slag-formation enthalpy. |
| PV-03 | Cohesive-zone permeability K as a function of shrinkage ratio | ISIJ Int. 57(9) 2017. The exponent structure is published. The K(Sr) coefficients were not readable. | Interface only. Use measured pressure drop until coefficients are copied from the printed paper. |
| PV-04 | Flooding-diagram density correction | The correction is real and behind a paywall. Literature also disagrees on whether fluidisation or slag flooding binds first. | Expose both criteria. Label the correction coefficient pending. Surface the disagreement in the UI instead of picking a side. |
| PV-05 | Hot metal silicon correlation | No universal closed form with coefficients was found. Published predictors are plant-fitted. Consistent variables: flame temperature, blowing pressure, coke rate, production rate, slag rate. | Site-fitted model only, trained after real data arrives. No default equation. |
| PV-06 | Iida slag viscosity, μ0i and αi table | Table 9 of the Aalto review was not recoverable from text extraction. Iida is family-calibrated and unreliable outside that family. | Implement Urbain, Riboud, and NPL, which have published coefficients. Leave Iida as an empty adapter. |
| PV-07 | Liquidus polynomial, ISIJ Int. 58(1) 2018 | Third-order polynomial in slag oxides, R² 0.91, stated validity C/S 0.5–1.4, Al₂O₃ 10–20%, MgO 0–15%, TiO₂ 0–5%. OCR mangled the coefficients. A 2019 Ironmaking & Steelmaking formula (average error 17.1 °C on 707 points) is paywalled. | Interface only. The companion `T_deform = 1.07 · T_liquidus − 177` can ship once T_liquidus itself is validated. |
| PV-08 | Brouwer and Toxopeus replacement-ratio coefficients | CoalTech document describes the form. The coefficients are an image. | Use the Geerdes RR formula, which is fully specified. Keep Brouwer as a named empty adapter. |
| PV-09 | RAFT variant `1615 + 0.76·HBT − 5.75·H + 53.3·E` | Circulates in plant blogs. No primary citation. The intercept is plant-fitted. | Default to the AIST/Geerdes linear form in [03-physics-equations.md](03-physics-equations.md). Any other form is config, off by default, and labelled uncited. |
| PV-10 | Absolute RAFT and hot metal temperature on the EVRAZ public reference | Validated over 500 on-wind hours. With the oxygen-enrichment definition corrected, the AIST/Geerdes form still returns RAFT ≈ 2380 °C (band 1900–2250) and HMT ≈ 1564 °C (band 1480–1530). The file has no PCI, natural-gas, blast-moisture, coke-rate or hot-metal-temperature column, so the inputs that set both intercepts are assumed, not measured. Russian furnaces of this era commonly injected natural gas rather than coal, and the natural-gas RAFT term (−50.66 per 100·NG/WC) is large enough to account for the whole offset. | Do not retune the intercept or the assumed PCI to move the number into band; that would fit a coefficient to make a screen look right. Both quantities are classified `response_only`: the absolute value is withheld and only the response to a change is served. Flip to `physics_estimated` when a furnace supplies injectant and hot-metal-temperature columns. |

## Conventions that must be chosen explicitly

These are not missing coefficients. They are choices that change the number a screen shows. The configuration page must force a choice and print it next to every result.

1. Productivity denominator: working volume, inner volume, or hearth area.
2. Permeability index variant. At least four are in plant use, and one of them (thyssenkrupp shaft K) is *lower-is-better*. See [02-derived-indices.md](02-derived-indices.md).
3. Blast kinetic energy: momentum in kg·m/s, or power in kW.
4. Thermal equivalence at constant blast volume or at constant production (PV-01).
5. RAFT empirical form. Recalibrate on the plant. Do not transplant Nippon Steel coefficients onto another furnace.
6. "Standard coke" carbon content. Geerdes uses 87.5% C. The plant's coke certificate overrides this.
