# Physics equations for implementation

Every equation below is intended to be coded and unit-tested on its own. Symbols are defined at first use. Reference temperature is 25 °C and 1 atm unless a formula says otherwise. Items in [11-pending-validation.md](11-pending-validation.md) are interfaces, not formulas.

Primary numerical sources:

- Geerdes et al., *Modern Blast Furnace Ironmaking*, for balances, the standard-coke split, and Annex III.
- Bailera, Lisbona, Peña, Romeo, Open Research Europe 2021, 1:141, [DOI 10.12688/openreseurope.14275.1](https://doi.org/10.12688/openreseurope.14275.1), for Rist coefficients.
- IspatGuru chemistry summary for the 298 K enthalpies, cross-checked against Geerdes where both state a number.
- Aalto thesis *Viscosity models for molten slags* for Urbain, Riboud, and NPL coefficients.

## 1. Mass balances

Steady state, per tonne of hot metal, for each element j:

```
Σ_i (m_in,i · x_in,i,j) = Σ_k (m_out,k · x_out,k,j)
```

Inputs: sinter, pellets, lump, coke, nut coke, PCI, other injectants, flux, dry blast, injected oxygen, blast moisture. Outputs: hot metal, slag, top gas, flue dust and sludge.

### Iron

```
m_ore · w_Fe,ore · (1 − L) + m_coke · w_Fe,coke
    = 1000 · w_Fe,HM + m_slag · w_Fe,slag + m_dust · w_Fe,dust
```

L is the iron fraction lost to dust, typically 0.01–0.03 from catcher and scrubber samples. w_Fe,HM is about 0.94–0.945 once carbon (~4.5%), Si, Mn, P, and S are subtracted. A first ore estimate is `m_ore = 1000 · 0.94 / w_Fe,ore`. Replace it with the full balance as soon as dust and slag analyses exist.

### Carbon

Geerdes split, expressed as standard coke at 87.5% C:

```
C_total = C_carburisation + C_direct_reduction + C_gasified_at_tuyeres
```

Worked reference case: coke 300 kg/tHM plus coal 200 kg/tHM at replacement ratio 0.85 contributes 170 kg standard coke, total 470. Of that, carburisation 50, direct reduction 120, tuyere burn 300 (coal 170, coke 130). The plant certificate overrides 87.5% C.

### Oxygen and nitrogen

```
O_blast + O_moisture + O_enrichment + O_injectant + O_from_ore
    = O_in_topgas (CO + CO2 + H2O) + O_in_slag
```

Oxygen per iron atom in the burden, Y_A: 1.50 for Fe₂O₃, 1.33 for Fe₃O₄, 1.05 for wüstite Fe₀.₉₅O.

Nitrogen is the blast-volume check, because it is effectively inert:

```
N2_topgas = N2_in_dry_blast (after the enrichment correction) + N2_from_carrier_gas
```

Close this balance before trusting a top-gas flow that was back-calculated from the analyser.

### Sulphur

```
S_in (coke + coal + ore + flux) = S_slag + S_HM + S_gas
```

Gas-phase sulphur is usually under 5%. With the partition ratio L_S from section 7:

```
[%S] = S_in / (1000 · 10⁻³ + m_slag · 10⁻³ · L_S)
```

Check the percent-versus-fraction scaling in the unit test. This line is where implementations silently drop a factor of ten.

### Alkali

```
K2O_in + Na2O_in = K2O_slag + Na2O_slag + K2O_dust + Na2O_dust + Δinventory
```

Removal is 80–100% via slag once the furnace is at steady elimination. The recirculating load is about `1 / f_elim`. FactSage values at 1500 °C from the Binding Solutions review: at B3 = 1.22, f_elim(K) = 18.9% and f_elim(Na) = 38.7% (5.3 and 2.6 recirculations). At B3 = 1.32 those fall to 14.5% and 32.1% (6.9 and 3.1 recirculations). Higher basicity holds more alkali inside the loop.

A persistent positive Δinventory is the scaffold and coke-degradation mechanism in [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md). Compute it. Do not wait for a model to discover it.

Input limits used as operating standards: total alkali 2.5 kg/tHM, or Geerdes' K₂O band of 1.0–1.5 kg/tHM. Zinc 100–150 g/tHM. A sensitivity quoted in Ironmaking & Steelmaking 2019: +0.1 B2 raises K and Na enrichment by 5.3 and 1.6 kg/tHM.

### Slag mass and flux

For each of SiO₂, CaO, MgO, Al₂O₃ (about 96% of the slag):

```
m_j = Σ_i m_i · (1 − loss_i) · w_i,j
    + m_coke · ash_coke · w_ash,j
    + m_PCI · ash_PCI · w_ash,j
m_slag = (m_SiO2 + m_CaO + m_MgO + m_Al2O3) / 0.96
```

Flux to hit a target binary basicity:

```
m_flux = (B2_target · ΣSiO2 − ΣCaO) / (w_CaO,flux − B2_target · w_SiO2,flux)
```

Iterate. Added flux costs heat, which raises coke rate, which adds coke ash, which moves the slag. Geerdes Table 6.1 is a fully worked numeric case (coke 300, coal 200, sinter 1000, pellets 500, lump 80 kg/tHM). Use it as a regression fixture.

## 2. Heat balance

```
Σ Q_in = Σ Q_out + Q_loss
```

Inputs that belong in the balance:

- Tuyere carbon to CO: 110,458 kJ/kmol of C (IspatGuru; Geerdes quotes 111 kJ/mol). Full combustion to CO₂ is 394 kJ/mol and does not happen in the raceway.
- Blast sensible heat: `V_blast · ρ · c_p · (T_blast − 25)`, or the integral of real gas heat capacities.
- Slag-formation enthalpy. The constant 196.7×10⁴ from ISIJ Int. 51(7) 2011 is PV-02. Leave it configurable and off.
- Indirect reduction steps that are exothermic. `FeO + CO → Fe + CO₂` is −16,108 kJ/kmol (IspatGuru) or −17.45 kJ/mol in other tabulations. Pin one source in the test.

Outputs:

- Hot metal sensible heat, fusion, and carburisation. `Q_HM = 1000 · [c_p · (T_HM − 25) + ΔH_fusion + ΔH_carb]`.
- Slag sensible heat from composition, not from a single heat capacity. Bailera computes it from SiO₂, Al₂O₃, CaO, MgO.
- Top gas sensible heat.
- Moisture decomposition: `H2O + C → CO + H2`, +131,378 kJ/kmol.
- Direct reduction: `FeO + C → Fe + CO`, +156,482 kJ/kmol (IspatGuru) or +155.15 kJ/mol. This is the large endothermic term.
- Cooling loss, measured: `Q_loss = ṁ_water · c_p · ΔT`, summed over circuits. Often 0.2–0.5 GJ/tHM, with a wider plant span of 0.2–1.1.

Solve the lower zone (tuyere to the 900–1000 °C isotherm) for coke rate. That is the Ramm/Rist heat-balance coke rate. Geerdes requires the upper zone (top down to 900 °C) and the lower zone to close together. If they do not, show the imbalance. Do not force a coke rate.

Thermal equivalence factors are in [02-derived-indices.md](02-derived-indices.md) and are gated by PV-01.

## 3. Rist operating line

Source: Bailera et al. 2021, Table 1 and Table 2. Axes and slope:

```
X = (O + H2) / (C + H2)
Y = (O + H2) / Fe
Y = μ · X + Y_E
μ = (C + H2) / Fe
```

Equilibrium polyline. ω is the equilibrium gas oxidation fraction, n_CO2/(n_CO+n_CO2) on the carbon system and n_H2O/(n_H2+n_H2O) on the hydrogen system.

| Point | Phase | X | Y |
|---|---|---|---|
| F | Fe | X_W | 0 |
| W | Wüstite Fe₀.₉₅O | Eq. below | 1.05 |
| W2 | Wüstite Fe₀.₈₉O | X_M | 1.12 |
| M | Magnetite | Eq. below | 1.33 |
| M2 | Magnetite | 2 | 1.33 |

```
X_W = 1 + (1 − x_h) · ω_WC + x_h · ω_WH
X_M = 1 + (1 − x_h) · ω_MC + x_h · ω_MH
x_h = (H2 + H2O) / (CO + CO2 + H2 + H2O)
ω(T) = a0 + a1·T + a2·T² + a3·T³ + a4·T⁴ + a5·T⁵
```

T is in °C, valid 500–1100 °C. T is the thermal reserve zone temperature, normally 800–1000 °C.

Coefficients for T > 565 °C, copied so they can be unit-tested. The a0 column is the constant term.

| ω | a0 | a1 | a2 | a3 | a4 | a5 |
|---|---|---|---|---|---|---|
| ω_WC | 0.40894101 | 3.8856440×10⁻³ | −1.3778206×10⁻⁵ | 1.7924558×10⁻⁸ | −1.0465659×10⁻¹¹ | 2.3054702×10⁻¹⁵ |
| ω_MC | −0.78765294 | 3.6286637×10⁻³ | −0.2811151×10⁻⁵ | 0.0772069×10⁻⁸ | 0 | 0 |
| ω_WH | −0.04957779 | −0.5074581×10⁻³ | 0.4367340×10⁻⁵ | −0.6744924×10⁻⁸ | 0.4402173×10⁻¹¹ | −1.0668513×10⁻¹⁵ |
| ω_MH | −21.536181 | 0.11554294 | −2.4611536×10⁻⁴ | 2.6555149×10⁻⁶ | −1.4341369×10⁻⁸ | 3.0845286×10⁻¹¹ |

The source prints a0 with a power-of-ten shift (a0·10, a0·10²). The table above is the expanded value. Add a fixture that recomputes ω at one published temperature before trusting the expansion. If the fixture fails, the shift was copied wrong and the coefficient stays pending.

For T < 565 °C the equilibrium is Fe–magnetite:

- ω_C: a0 = 0.63672662, a1 = −0.2230216×10⁻³, higher terms 0
- ω_H: a0 = −0.14558633, a1 = 0.6611511×10⁻³, higher terms 0

Confirm those two expansions against Table 2 the same way.

Chemical reserve zone, real furnace. r is chemical efficiency, typically about 0.92.

```
X_R = 1 + r · (X_W − 1)
Y_R = Y_A + r · (Y_A − Y_W)
```

Point P is the elaboration-zone enthalpy balance per mole of Fe, referenced to T_R. The source writes it in kcal/mol Fe. Keep that unit inside the Rist module and convert at the boundary, so the published q coefficients are not silently rescaled.

```
q_c·y_v + q_v·y_v + q_iw·Y_W + δ
    = q_g·(y_d − y_e) + q_k·y_k + q_e·y_e + Σ q_j·y_j + δ′
    + q_Si·y_Si + q_Mn·y_Mn + q_P·y_P + q_γ·γ + q_f·φ + q_l + q_p
```

Left side: incomplete combustion of carbon, blast sensible heat, wüstite reduction heat, chemical non-ideality. Right side: CO₂ dissociation in direct reduction, coke hydrogen, blast moisture, injectants, hydrogen non-ideality, Si/Mn/P reduction, carburisation, losses.

Closure:

```
μ = (Y_R − Y_P) / (X_R − X_P)
Y_E = Y_R − μ · X_R
```

Direct reduction: the operating line at X = 1 gives y_d, the oxygen removed by direct reduction. y_i = Y_A − y_d. r_d = y_d / Y_A. A typical furnace sits near one third direct reduction.

## 4. Reduction enthalpies at 298 K

From IspatGuru, *Chemistry of the ironmaking by blast furnace process*. Pin these in tests. Where a second source disagrees by ~1 kJ/mol, record both and pick one in config.

| Reaction | ΔH, kJ/kmol |
|---|---|
| 2C + O₂ → 2CO | −110,458 per mole of C |
| CO₂ + C → 2CO (Boudouard) | +172,590 |
| H₂O + C → CO + H₂ | +131,378 |
| FeO + CO → Fe + CO₂ | −16,108 |
| FeO + C → Fe + CO | +156,482 |
| 3Fe₂O₃ + H₂ → 2Fe₃O₄ + H₂O | −7,100 |
| Fe₃O₄ + H₂ → 3FeO + H₂O | +62,900 |
| FeO + H₂ → Fe + H₂O | +25,104 (the same page also prints 30.2 kJ; do not average them) |
| CO₂ + H₂ → H₂O + CO | +41,200 |

Water-gas shift equilibrium constant `(p_H2O · p_CO) / (p_H2 · p_CO2)` equals 1 near 825 °C. Use that as an anchor test.

Boudouard: above about 1100 °C, CO₂ in contact with coke goes to CO, so the bosh gas is CO, H₂, and N₂. Below about 500 °C, CO can decompose to carbon plus CO₂. Gas utilisation:

```
η_CO = %CO2 / (%CO + %CO2)
η_H2 = %H2O / (%H2 + %H2O)
η_CO,actual = shaft_efficiency · η_CO,equilibrium(T_reserve)
```

Hydrogen reduction is faster than CO reduction at blast furnace temperatures, and the hydrogen steps are less exothermic or outright endothermic. Adding hydrogen changes the heat balance even when the total reductant rate is held constant. Top gas temperature and RAFT both have floors under hydrogen injection; see the hydrogen row in [05-failure-mode-catalog.md](05-failure-mode-catalog.md).

## 5. RAFT, Ergun, raceway, residence

The AIST/Geerdes RAFT formula, Nakamura depth, and the raceway power laws are in [02-derived-indices.md](02-derived-indices.md). Implement them there as specified, with a test vector.

Ergun, non-spherical particles, d_sv = d_p / φ:

```
ΔP/H = 150 · μ · U · (1−ε)² / (d_sv² · ε³)
     + 1.75 · ρ_g · U² · (1−ε) / (d_sv · ε³)
```

ΔP in Pa, H in m, μ in Pa·s, U superficial velocity in m/s, ε voidage, ρ_g in kg/m³. Friction form: f* = 150/Re* + 1.75.

Blast-furnace form with the gas-law correction (Roy, NPTEL ironmaking lecture 11):

```
ΔP = ψ · H · (1−ε)/ε³ · (G0² / (d · ρ0)) · (T/T0) · (P0/P)
```

G0 is mass flux at NTP. Reynolds numbers run from about 800 at the belly to about 3500 at the top. A typical pressure gradient is about 10 mm water per cm of bed at ε = 0.25.

Irrigated bed: replace ε with ε − h_l, treating liquid holdup as extra packing ([Tetsu-to-Hagané 66(13) 1980](https://www.jstage.jst.go.jp/article/tetsutohagane1955/66/13/66_13_1947/_article/-char/en)).

Gas residence (Geerdes §2.3.6):

```
t = ε · V_working / Q_gas
t_corrected = t · (P/P0) · (273 / (273+T)) · (V_bosh / V_top)
```

Fixture: 3800 m³, ε = 0.30, 8164 m³ STP/min gives about 8 s uncorrected and about 6 s corrected.

Burden residence:

```
V_dot = Σ(dump volumes) / Δt          over one charging cycle
w(z) = V_dot / A(z)
t_res = V_working / V_dot
t_to_tuyere = ∫ dz / w(z)             stockline to tuyere
```

A(z) grows from throat to belly, so descent slows. Belly diameter is typically 1.4–1.5 times throat diameter, area more than doubles, and layer thickness halves. A Japanese rule of thumb wants at least 18 cm of coke at the belly. Modern residence time is about 6 hours, so one 2-hour cast is about a third of the furnace contents.

## 6. PCI replacement ratio

Geerdes, against standard coke at 87.5% C:

```
RR = 2·C% + 2.5·H% − 2·moisture% − 86 + 0.9·ash%
```

Keep carbon, hydrogen, and ash on one consistent basis and say which. The positive ash term is a heat-balance correction, not a benefit of ash.

Other published fits, via the CoalTech replacement-ratio note:

```
RR = −0.6395 + 0.04 · SE_coal(daf, MJ/kg)      Hutny, Price, Gransden 1990
RR = 1.14 − 0.014·Ash − 0.007·VM               European 1996, both percent dry
```

Brouwer and Toxopeus 1991 is the Hoogovens form and is PV-08. Leave the adapter empty.

Replacement ratio sits at 0.8–1.0 in theory, a bit above theory at moderate rates, and below theory above about 150 kg/tHM as heat loss and unburnt char rise. It falls 0.01–0.05 per extra 1% ash. At 500 kg/tHM total reductant, 1% less coal ash is about 6 kg/tHM coke (Poveromo 2004, cited in IEA CCC/116).

Raceway transit time is 20–30 ms. Unburnt char that escapes into the coke bed lowers voidage. Published PCI ceilings from burnout criteria are 190–210 kg/tHM (ISIJ Int. 51(7) 2011) and about 180 kg/tHM (Tamura). Practical blast oxygen is often 22–27% depending on the coal rate. Oil or natural gas: about 1.2 t coke replaced per tonne injected, consistent with Geerdes' −11 kg coke per +10 kg oil.

## 7. Silicon and sulphur

Silicon path ([Ironmaking & Steelmaking 2022, FeO paper](https://doi.org/10.1080/03019233.2022.2027135)):

1. `SiO2 + CO → SiO(g) + CO2` in the raceway, silica from coke and coal ash, above about 2000 °C.
2. `SiO(g) + [C] → [Si] + CO` into dripping metal.
3. `[Si] + 2FeO → SiO2 + 2Fe` re-oxidation in the dripping zone.

Higher RAFT raises Si. Higher total pressure slows SiO formation. A taller dripping zone and a higher liquid level increase contact and raise Si. Higher slag basicity pushes SiO back to SiO₂ and lowers Si. There is no universal coefficient set. PV-05: fit on the plant, and keep the prediction labelled as a fit.

Sulphur capacity, lime-equivalent form, Total Materia compilation, 1575–1650 °C, R = 0.99, σ = 0.044 on log C_S:

```
log10(C_S) = 3.44 · (N_CaO + 0.1·N_MgO − 0.8·N_Al2O3 − N_SiO2) − 9894/T + 2.05
log10(L_S) = 3.44 · Σ(K_i N_i) − log10(wt% O) − 10980/T + 3.50
```

T in kelvin. Optical basicity form from the same source:

```
log10(C_S) = 14.20·Λ − 9894/T − 7.55
Λ = Σ (x_i · n_i · Λ_i) / Σ (x_i · n_i)
```

Optical basicity values: CaO 1.00, MgO 0.78, Al₂O₃ 0.60, SiO₂ 0.48, K₂O 1.40, Na₂O 1.15, FeO 1.00, MnO 1.00, TiO₂ 0.61, CaF₂ 1.20 (Aalto thesis, Table 7).

Slovic form:

```
log10(L_S) = log10(C_S) + log10(f_S) − log10(a_O) − 935/T + 1.375
```

Unit-test the two L_S expressions against one published slag before either is allowed to drive a recommendation. If they disagree beyond the stated σ, show both and mark the screen pending.

## 8. Slag viscosity

Basicity definitions and the short-slag warning are in [02-derived-indices.md](02-derived-indices.md).

### Urbain

```
μ (poise) = A · T · exp(1000 · B / T)
−ln A = 0.29 · B + 11.57
B = B0 + B1·X_G + B2·X_G² + B3·X_G³
B_i = a_i + b_i·α + c_i·α²
α = X_M / (X_M + X_A)
```

Mole-fraction groups: X_G = SiO₂ + P₂O₅. X_M = CaO + MgO + FeO + MnO + CrO + NiO + Na₂O + K₂O + Li₂O + 2 TiO₂ + 2 ZrO₂ + 3 CaF₂. X_A = Al₂O₃ + Fe₂O₃ + B₂O₃ + Cr₂O₃. Normalise by (1 + X_CaF₂ + X_TiO₂ + X_ZrO₂).

Original CaO–Al₂O₃–SiO₂ coefficients:

```
B0 = 13.8 + 39.9355·α − 44.049·α²
B1 = 30.481 − 117.1505·α + 139.9978·α²
B2 = −40.9429 + 234.0486·α − 300.04·α²
B3 = 60.7619 − 153.9276·α + 211.1616·α²
```

Cation-specific sets (a, then b, then c, each as four numbers for B0..B3):

- Ca: a = 13.2, 30.5, −40.4, 60.8; b = 41.5, −117.2, 232.1, −156.4; c = −45.0, 130.0, −298.6, 213.6
- Mg: b = 15.9, −54.1, 138, −99.8; c = −18.6, 33.0, −112.0, 97.6
- Mn: b = 20.0, 26, −110.3, 64.3; c = −25.6, −56.0, 186.2, −104.6

Mg and Mn share the Ca `a` vector in the Aalto write-up. Confirm against the thesis table in the first unit test, using a published CaO–SiO₂–Al₂O₃–MgO slag with a measured viscosity.

### Riboud

μ in dPa·s (watch the unit):

```
μ = A · T · exp(B / T)
A = exp(−19.81 + 1.73·X_CaO + 5.82·X_CaF2 + 7.02·X_Na2O − 35.76·X_Al2O3)
B = 31140 − 23896·X_CaO − 46356·X_CaF2 − 39159·X_Na2O + 68833·X_Al2O3
```

Grouped mole fractions: "SiO₂" includes P₂O₅, TiO₂, ZrO₂. "CaO" includes MgO, FeO, Fe₂O₃, MnO, NiO, CrO, ZnO, Cr₂O₃. "Al₂O₃" includes B₂O₃. "Na₂O" includes K₂O and Li₂O. Riboud cannot tell MgO from CaO. That is a known weakness on blast furnace slag. Report it next to the number.

### NPL (Mills and Sridhar)

Corrected optical basicity: reduce the mole fractions of the basic oxides by the amount spent charge-balancing AlO₄⁻, consuming the highest-Λ oxides first.

```
B/1000 = −1.77 + 2.88 / Λ_corr
ln A = −232.69·Λ_corr² + 357.32·Λ_corr − 144.17
μ (Pa·s) = A · exp(B / T)
```

Ray and Pal variant, Weymann–Frenkel, μ in poise:

```
−ln A = 0.2056·B + 12.492
B = 297.14·Λ² − 466.69·Λ + 196.22
μ = A · T · exp(1000·B / T)
```

Run all three models. If they spread by more than a stated tolerance on a slag inside their calibration, show the spread and withhold a single "the viscosity".

## 9. Productivity ceilings

Stoichiometric driving rate:

```
P = O2_kmol_per_day · 2 · 12 / C_tuyere_kg_per_tHM
```

Permeability-constrained form (Donetsk / Ramm, RWTH note):

```
P = P0 · (v_g0 / v_g) · [ (d0 · Θ0 · γ0) / (d · Θ · γ) ]^0.5
d = (L · v_b/v_c + 1) / (v_b/v_c + 1)
```

P in t/day, Θ mean gas temperature in K, v_g wet top gas volume per kg hot metal, γ mean gas density, v_b/v_c burden-to-coke volume ratio, L a pressure-drop ratio, 0 the base case.

Return the minimum of the five ceilings in section 11 of [02-derived-indices.md](02-derived-indices.md), and name which ceiling bound the answer. An infeasible production target gets that ceiling and the slack on the other four, not a forced setpoint.
