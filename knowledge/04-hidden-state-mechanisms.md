# Why production falls while the blast sheet looks the same

The hourly log is a boundary-condition record: blast volume, temperature, pressure, oxygen, PCI, moisture, burden weights, top gas. The internal state is a set of slow latent variables: radial gas distribution, cohesive-zone geometry, alkali inventory, deadman porosity, wall accretion, hearth liquid level. Two periods with the same boundary conditions can sit on different internal states. The 1970s dissection studies exist because that state cannot be read off the operating log.

This file is the domain spine of the mystery protocol in `../prompts/06-phase6-observability-mystery.md`. Each section is a gate input: mechanism, signature, time scale, and how sure the literature is.

## 1. Burden and gas distribution

Gas permeability of a coke layer is far higher than an ore layer, so the radial ore/coke profile sets the gas flow. Ore heat capacity is about four times coke, so the same shift moves the thermal profile. Mixed layers at the coke/ore interface have lower voidage than either layer alone ([Steel Research Int. 2022](https://doi.org/10.1002/srin.202200290)).

Identical chute setpoints do not produce identical distribution. Burden aggregates with a longer chute and disperses with a higher stockline or a larger chute angle ([Steel Research Int. 2020](https://onlinelibrary.wiley.com/doi/10.1002/srin.202000262)). Fines concentrate at the end of hopper discharge, so the same matrix segregates differently after a different fill ([Steel Research Int. 2024](https://doi.org/10.1002/srin.202400306)). Pellets roll to the centre. Coarse particles report to the wall and the sub-centre. Without a centre-coke dump, ore rolls inward, central ore/coke rises, and peripheral ore/coke falls.

**Signature.** Above-burden radial temperature, and the per-second fluctuation ΔT/Δt, which peaks at the centre-coke / ore interface where small coke fluidises ([ISIJ Int. 55(10) 2015](https://www.jstage.jst.go.jp/article/isijinternational/55/10/55_ISIJINT-2015-161/_html/-char/en)). Tata Steel's radar "sounding ore by coke" gives a continuous wall ore/coke and tracks wall heat load ([ISIJ Int. 63(1) 2023](https://www.jstage.jst.go.jp/article/isijinternational/63/1/63_ISIJINT-2022-246/_html/-char/en)). Centre ore/coke can be estimated from probe transients ([Saxén and Nikus, ISIJ Int. 42, 115](https://doi.org/10.2355/isijinternational.42.115)).

Gas accelerates in the hot centre and draws gas in from the colder intermediate region, so a probe reading is not a stockline reading.

**Time scale.** Minutes for a layer. Hours for the gas pattern. Days for a drifting matrix to show up as lost production.

## 2. Alkali and zinc circulation

K and Na enter as silicates in ore, sinter, and coke ash. Zinc enters mainly with sinter and recycled dust. Both reduce and vaporise low in the furnace, rise, recondense in the cohesive zone and stack, and come down again with the burden. Dissections give 4–8 circulations through the cohesive zone. Potassium is retained about twice as strongly as sodium. About 80–100% of what leaves, leaves in the slag ([alkali behaviour review](https://www.bindingsolutions.uk/wp-content/uploads/2025/09/ON-Na2O-AND-K2O-BEHAVIOUR-IN-BLAST-FURNACE-OPERATION-paper126.pdf)).

Quenched furnaces: alkali peaks about 7 m above the tuyeres, K₂O at 3.5× and Na₂O at 1.7× the charged value. Recirculating alkali on six Japanese furnaces was estimated at 13–24 kg/t against about 3 kg/t input. One study reports belly maxima near 50× charge for K and Na and near 80× for Zn ([Ironmaking & Steelmaking 2016](https://doi.org/10.1080/03019233.2016.1210913)).

Alkali and zinc vapour catalyse coke solution loss, lower the in-furnace CSR, open macropores, and make fines ([ISIJ Int. 59(10) 2019](https://www.jstage.jst.go.jp/article/isijinternational/59/10/59_ISIJINT-2019-140/_html/-char/en)). Rising alkali load makes lower-zone reactions more endothermic and can reach a point where hearth heat cannot carry both the alkali cycle and burden preheat.

**Load limits in practice.** Na₂O + K₂O under 2.5 kg/tHM is a common standard. Attributed coke-rate penalties per unit of accumulated load: Na 13.99, K 6.25, Zn 3.63, Pb 0.02 kg/tHM (same 2016 paper).

**Signature.** Input minus slag-plus-dust output. A persistent gap *is* the inventory. Rising K₂O/Na₂O in top-gas dust. A slag-basicity change that flushes alkali. More coke fines at tuyere level.

**Time scale.** Days to weeks to build. Weeks to flush. This is the usual reason an instantaneous sheet cannot explain a slow production loss: the variable is an integral, and the daily balance is the only place it appears.

## 3. Scaffolds and wall build-up

Fines, condensed alkali (often kalsilite or KCN), and ZnO stick to the shaft wall and sinter into a scab. Middle-stack deposits 1.2–4.6 m thick, sometimes a full ring, have been documented. Wall dust from such a furnace assayed about 60% K₂O ([ORNL refractory wear report](https://www.osti.gov/servlets/purl/7348573)). Mineralogy: [ISIJ Int. 9 (1969) 413](https://doi.org/10.2355/isijinternational1966.9.413).

The effect is a smaller effective cross-section. The same blast volume passes a smaller area, local velocity rises, and gas goes somewhere else. Blast volume and pressure can look normal.

**Signature.** Stave temperature level, fluctuation, and spatial gradient, plus cooling-water heat flux. Nippon Steel estimates thickness from two thermocouples at different depths, assuming one-dimensional steady conduction and an assumed scaffold conductivity. The assumption is explicit ([NSC report 123-15](https://www.nipponsteel.com/en/tech/report/pdf/123-15.pdf)). Shougang BF2 deliberately holds 30–50 mm. Tata's stave excursion index is `(duration / count) × peak temperature`, per hour, per level. The Higashida No. 1 case located the deposit with heat flux plus 16 drill holes, removed 300–500 mm by blasting, and replaced cyclic slipping with smooth descent ([Tetsu-to-Hagané 52(9) 1966](https://doi.org/10.2355/tetsutohagane1955.52.9_1395)). CSN BF2's multi-year scaffold history was driven by zinc ([ABM proceedings](https://abmproceedings.com.br/en/article/control-of-the-scaffold-formation-in-the-csns-blast-furnace-2)).

**Time scale.** Weeks to months to grow. A scab falling off is an abrupt heat-load spike and a slip.

## 4. Deadman and hearth coke

The deadman is a stagnant-to-slow coke column. Porosity is heterogeneous and unmeasured. Radioactive tracer: coke at the periphery is consumed in 2–3 days, consistent with a hearth carbon balance. The core takes weeks ([Processes 8(11) 1335, 2020](https://www.mdpi.com/2227-9717/8/11/1335)).

Iron is about 2.5 times as dense as slag. Buoyancy against burden weight, gas drag, and raceway length decides whether the deadman sits (low liquid level, coke fills the hearth) or floats (high level, a coke-free zone opens). A coke-free zone changes drainage directly only if it reaches the taphole, but even partial floating changes liquid level and the taphole pressure loss.

At high PCI, unburnt char and soot collect in the bird's nest between raceway and deadman and around the cohesive-zone root. Voidage falls, pressure drop rises, gas fluctuates, and wall heat load rises ([IEA CCC-116](https://www.sustainable-carbon.org/wp-content/uploads/dlm_uploads/reports/Combustion/use-of-pci-in-blast-furnaces-ccc-116.pdf)). At 1600–2000 °C roughly a third of volatile mass can become soot; some authors say 20%. An IJmuiden 6BF trial with 42% VM coal above 240 kg/tHM doubled sludge carbon from 3–4 to 7–8 kg/tHM and was stopped after two weeks.

**Signature.** Falling hearth-bottom temperature with rising sidewall temperature: deteriorating deadman permeability, and the path to elephant-foot erosion. Inverse heat-conduction models give a weekly hearth-volume state (clogged, clogging, opening, open). The deadman cleanliness index uses departure of tapped iron from carbon saturation plus a slag-superheat term ([Nightingale, Wollongong](https://ro.uow.edu.au/theses/1522)). Hot metal carbon and sulphur move together: low carbon and high sulphur mean metal bypassed the coke core.

**Time scale.** A tap cycle for floating. Days at the periphery. Weeks in the core. The core is the longest memory in the furnace.

## 5. Hearth liquid level

Incomplete drainage fills coke-bed voids. Cold models plus CFD: the gas region shrinks as melt accumulates, velocity near the tuyere rises, and pressure drop climbs rapidly once the mean liquid level is within about 1 m of the tuyere. The published response is to cut blast and raise tapping rate immediately ([Tetsu-to-Hagané 110(10) 2024](https://www.jstage.jst.go.jp/article/tetsutohagane/110/10/110_TETSU-2024-053/_pdf/-char/en)). Sustained high level raises blast pressure, slows descent, increases heat loss, and can flood a tuyere.

A dry tap does not happen. Slag remains. The residual ratio tracks the flow-out coefficient and rises when deadman permeability falls, drainage rate rises, or slag viscosity rises. Taphole erosion changes the effective drill diameter during a cast. Switching a multi-taphole furnace from alternating to one-sided casting changes the gap and the peak level ([Metall. Mater. Trans. B 2020](https://link.springer.com/article/10.1007/s11663-020-01857-1)).

**Signature.** Production minus discharge, ideally with a time-varying voidage. Blast pressure rising at constant blast volume. Slower descent. Slag-breakthrough timing drifting. Levels can differ between tapholes when the deadman is uneven, so opening the taphole where the level is higher can stabilise the furnace.

**Time scale.** Hours per tap. A deficit compounds over days.

## 6. Cohesive zone

In the softening-melting region, liquid soaks into the ore layer, voidage collapses, and gas has to cross through coke slits. The zone is an inverted V, a W, or asymmetric. A lower inverted V raises central voidage and concentrates gas in the centre. A thinner zone and a steeper slope shorten the slit and improve permeability ([ISIJ Int. 55(6) 1232](https://www.jstage.jst.go.jp/article/isijinternational/55/6/55_1232/_html/-char/en)).

**The identical-recipe trap.** Softening and melting depend on how the components interact, not only on the percentages. More mixing between sinter and pellets generates liquid in the cohesive zone and hurts permeability ([Ironmaking & Steelmaking 2022](https://doi.org/10.1080/03019233.2022.2099699)). A constant 70/20/10 recipe with a drifted sinter softening curve is a different furnace.

The geometry effect is well established. The claim that routine sinter-plant drift at constant recipe is a *frequent* cause of unexplained loss is mechanistically sound and not tied, in the sources read, to one named unexplained-loss case. Label it that way.

**Signature.** Where the shaft pressure drop concentrates. Cohesive-zone root height from stave-temperature models. Wall heat load. Tata links a lower root to higher heat loss because the bosh and belly use high-conductivity copper staves.

**Time scale.** Hours to reshape. Days for a sinter-quality shift to arrive.

## 7. Raw material quality the BF log does not hold

**Coke.** Inter-laboratory CRI/CSR scatter can reach about ±2 points, so one certificate must not move the coke rate ([Metals, PMC8771692](https://pmc.ncbi.nlm.nih.gov/articles/PMC8771692/)). CSR is a restricted lab test. In-furnace degradation depends on strength and on the mechanical field inside the furnace ([ISIJ Int. 43, 44](https://doi.org/10.2355/isijinternational.43.44)). Tuyere coke is about 50% smaller than charged coke (reported 52–58%), worse at higher PCI. Fines under 3 mm reach 10–15% at the raceway tip and shorten the raceway. Regression: about 0.2 mm size loss per 1% DI and about 0.4 mm per 1% CSR, so CSR dominates on large furnaces. A coke-plant average from days earlier can match while the coke in the furnace does not, because residence time, PCI, and alkali load changed.

**Sinter.** +2% FeO can improve RDI by several points and still raise coke rate through worse reducibility. Log FeO, RDI, and RI together.

**Pellets.** Swelling and clustering are iron-whisker growth at the wüstite stage. Alkali in the burden promotes it. A cited limit for pellet alkali is Na₂O + K₂O at or below 0.15%. This couples to section 2: alkali accumulation causes swelling, swelling hurts permeability, permeability cuts the driving rate.

**Gangue at constant Fe.** Higher Al₂O₃ raises slag viscosity and liquidus. Drainage rate falls as Al₂O₃ rises. MgO restores it. Same %Fe, different alumina, different achievable wind.

**Fines.** Charge −5 mm and screen efficiency are rarely logged per charge and set the bed voidage directly.

## 8. Circumferential asymmetry

Averages hide it. On Krivorozhstal's 5000 m³ BF9, nonuniform blast across tuyeres produced nonuniform flame temperature, gas yield, and energy flux around the hearth. Smoothness, productivity, coke rate, and hot metal quality all moved. Blast flow-rate nonuniformity had the largest influence ([Steel in Translation 2018](https://doi.org/10.3103/s0967091218030087)).

Bustle-pipe CFD on a 2500 m³ furnace: circumferential uniformity got *worse* as blast flow rose, because drag losses rose. Tuyere diameter mattered. Tuyere length barely did. The practical fix was enlarging one or two off-average tuyeres, not all of them ([ISIJ Int. 62(3) 2022](https://www.jstage.jst.go.jp/article/isijinternational/62/3/62_ISIJINT-2021-371/_html/-char/en)).

A 3-D model with circumferentially nonuniform ore/coke produces an inclined cohesive zone, nonuniform liquid flow, and almost no movement in average top gas temperature or tuyere pressure ([Monash asymmetric BF model](https://research.monash.edu/en/publications/numerical-simulation-of-the-3d-asymmetric-inner-states-of-an-iron/)). The asymmetry reinforces itself: sinter RDI and coke gasification intensify on the high ore/coke side. Deliberate unequal PCI, used to even out the thermal profile, saved 3.9% and 4.7% coke on two DMK furnaces.

**Signature.** Per-tuyere flow and kinetic energy. Blocked, eroded, or protruding tuyeres. Per-lance PCI. Circumferential stave temperature variance, not the mean. Per-taphole Si, S, C, and temperature. Azimuthal shaft-pressure asynchrony. This last item is what the JFE Q-statistic measures.

**Time scale.** Immediate on a tuyere event. Days to weeks for the permeability split to reinforce.

## 9. Weather and season

Natural blast humidity is often 8–10 g/Nm³ and moves with the season and the hour. Steam dissociation is endothermic, cuts RAFT, and raises bosh-gas hydrogen. A Japanese dehumidification study: annual mean absolute humidity 12 g/Nm³, August peak about 23, daily spread up to 4. Ten g/Nm³ of dehumidification raised tuyere-front temperature 60–70 °C and was credited with about 10 kg/t coke including stability ([Tetsu-to-Hagané 64(13) 1978](https://www.jstage.jst.go.jp/article/tetsutohagane1955/64/13/64_13_1926/_pdf/-char/en)). The opposite result also exists: +10 g/Nm³ humidity raised production 3.5–4.5% and cut coke 1.5% *when blast temperature paid for the dissociation*. The proviso is the result. Tata Steel has run 60–80 g/Nm³ on purpose to hold RAFT down for low-silicon iron.

Cooler, denser inlet air changes blower mass flow at the same volumetric reading. Barometric pressure moves the Nm³ conversion. "Constant blast volume" in normalised units is not constant velocity.

**The rainy-season case.** Tata Steel traced instability to pellet moisture. Top gas temperature fell, the cohesive-zone root dropped, heat loss rose, gas hit the bottom wall, lower-furnace resistance rose, slag FeO rose, and wall ore/coke read *high* because wet pellets roll less toward the centre ([ISIJ Int. 63(1) 2023, case 2](https://www.jstage.jst.go.jp/article/isijinternational/63/1/63_ISIJINT-2022-246/_html/-char/en)). The blast log would not have shown it.

**Time scale.** Diurnal and seasonal. Stockyard moisture lasts days after rain.

## 10. Thermal and inventory inertia

| Action | Time to become active |
|---|---|
| Blast volume, temperature, oxygen | within about 1 hour |
| PCI | 1.5–3 hours, and a separate ~10 minute hydrocarbon peak |
| Charged coke | 5–8 hours |
| Burden, top to hearth | about 6 hours |
| Hot metal temperature | time constant above 8 hours |
| Deadman core, alkali inventory | days to weeks |

An identical snapshot can hide three differences: the coke at the hearth was charged under different conditions, the alkali or char inventory differs, and the derivative differs. Rate of change and accumulated history carry information the level does not. Compute active coke and active coal over their lag windows. The table and the estimation methods are in [08-lag-reference.md](08-lag-reference.md).

## 11. Instruments lying

Orifice-plate wear changes the discharge coefficient and biases blast flow. Type K thermocouples can be poisoned above 600 °C and thereafter read low. Pressure transmitters drift at zero. Gas analysers drift between calibrations and take η_CO, and every balance that uses it, with them.

A live blast furnace data-reconciliation system enforcing Fe, C, N, O, and H balances produced consistent production-rate estimates, found gross errors in the online gas analyser, and estimated unmeasured top-gas flow, moisture, and calorific value ([Asia-Pac. J. Chem. Eng. 2021](https://doi.org/10.1002/apj.2628)). Gross-error detection has to run *before* reconciliation, or the bad sensor contaminates the good ones. Steady-state reconciliation averages slow drift away. That is the failure mode here. A dynamic or Kalman reconciliation is the alternative.

Tata accepts a hearth thermocouple pair only when the two same-level couples have r² above 0.8 *and* their rates of change have r² above 0.8.

**Signature.** Reconciled-minus-measured residual trending for weeks. Mass-balance closure error growing in one direction. A frozen tag. A KPI drifting while every input looks stable.

**Time scale.** Weeks to months. Long enough that operators adopt the drifted reading as normal.

## 12. The tonne figure, and the furnace not being the cause

Three production routes, which rarely agree:

1. Torpedo weighbridge, full minus empty, allocated to a cast. Visual split of a ladle poured from two furnaces has been the weak link; RFID and GPS ladle tracking exists because of that.
2. Iron balance from burden charged. Sensitive to coke moisture, which runs 0.5–5% and is often sampled about three times a day.
3. Sum of cast weights.

A cast crossing a shift boundary, or a change in metal sitting in the ladle fleet, moves tonnes between periods with no change in the furnace.

**External throttling.** Hot metal has to go somewhere. A documented cascade is caster slows, BOF holds heats, blast furnace cuts wind, and the furnace is banking within about two hours. Torpedo and locomotive availability constrain continuity (modelled as such at Fos-sur-Mer). A slag-granulation outage stops tapping. An oxygen, power, or gas-network limit stops driving. Published guidance under a supply constraint: dropping top pressure 50–100 kPa is preferable to cutting oxygen enrichment 5–8%, while holding total pressure drop at its established value.

**Signature, and the first test.** Reconcile the three routes. Check ladle-fleet inventory at both ends of the period. Check delay minutes by reason code against blast-off time. If the blast cut was commanded, the furnace was not the constraint. Test that before any latent-state hypothesis. It is the cheapest one to falsify.

## 13. How sure is each mechanism?

**Established in the peer-reviewed or plant literature.** Radial ore/coke controls gas flow (1). Alkali and zinc recirculate 4–8× and catalyse coke degradation, with the ~2.5 kg/tHM convention (2). Scaffolds reach metres and are visible in stave heat flux (3). Deadman floating versus sitting, 2–3 day periphery, weeks-long core (4). Pressure drop rising sharply within about 1 m of the tuyeres (5). Cohesive-zone geometry governing permeability (6). CSR not predicting in-furnace size, ~50% loss by the tuyere (7). Tuyere-flow nonuniformity as the largest circumferential driver, and averages staying normal under asymmetry (8). Blast-moisture physics and the Tata rainy-season pellet case (9). The lag hierarchy (10). Reconciliation catching a gas-analyser gross error on a live furnace (11). The JFE Q-statistic detecting slow permeability loss that conventional indices miss.

**Mechanistically sound, not documented as a named cause of an unexplained loss.** Routine sinter softening drift at constant recipe (6). Screen-efficiency drift interacting with hopper segregation (1, 7). Period-boundary and torpedo-inventory artifacts as the sole cause of an apparent loss (12). The pieces are documented. A paper that attributes one plant's unexplained loss to accounting alone was not found.

**Not a term of art.** "Unexplained production loss blast furnace" and "blast furnace latent state estimation" return almost nothing under those phrases. The real literature is inner-state estimation, soft sensing, permeability diagnosis, and factor analysis of productivity. Search those.

## 14. What to compute every hour

These are the discriminators. They are mostly derived from tags a plant already has.

| Discriminator | Role in the mystery protocol | Needs |
|---|---|---|
| Three-way production reconciliation residual | Gate 0 | Weighbridge, burden Fe, cast weights |
| Fe, C, N, O, H balance closure | Gate 0 and instrument gate | Analyses plus flows |
| Commanded vs forced blast-cut flag | Gate 0 | Delay reason codes |
| Active coke and active PCI | Gate 1 | Charging weights, lags from [08-lag-reference.md](08-lag-reference.md) |
| Within-hour std, min, max, excursion count | Gate 1 | Historian aggregate, see [../DATA_REQUEST.md](../DATA_REQUEST.md) |
| Circumferential stave-temperature std | Gate 1 and 3 | Per-stave tags |
| Per-tuyere flow std | Gate 1 and 3 | Per-tuyere tags |
| Coke CSR/CRI, sinter RDI/FeO, ore Al₂O₃, burden moisture | Gate 2 | Certificates joined on charge time |
| Blast humidity vs ambient dew point | Gate 2 | Weather or hygrometer |
| Upper/lower ΔP, permeability variant, η_CO, shaft efficiency | Gate 3 | Shaft taps, gas analysis |
| Heat loss per tonne, stave excursion index, burden descent index | Gate 3 | Water ΔT, radar |
| PCA Q-statistic on the pressure and temperature arrays | Gate 3 | Distributed sensors |
| Alkali and zinc inventory ledger | Gate 4 | Input analyses, slag and dust analyses |
| Unburnt-char proxy, hearth liquid level, deadman cleanliness | Gate 4 | PCI, VM, tap weights, HM carbon |
| Model residual, and its autocorrelation, shift pattern, and sector pattern | Gate 5 | The prediction model |
