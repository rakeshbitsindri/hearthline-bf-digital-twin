# Derived indices and KPIs

Formulas plant engineers actually compute. Several indices share a name and do not share a formula. The configuration page must record which variant is in force, and every chart title must repeat it. A trend inside one plant is meaningful. A comparison of absolute permeability numbers across plants is not.

Symbol notes: HM is hot metal mass, V_w is working volume, Q is a gas flow, ΔP is a pressure difference. Units sit next to each formula.

## Productivity and rates

| Index | Formula | Typical target | Notes |
|---|---|---|---|
| Productivity | P = HM / V_w | 2.0–2.5 t/(m³·day) on working volume. Chinese super-large furnaces report 1.8–2.7 on *inner* volume. Japanese "tapping ratio" 1.7–2.1. | Name the volume. Shougang Jingtang No.1 reported 2.551 t/m³/day and above 15,000 t/day monthly average in 2022. |
| Hearth driving rate | DR = HM / A_hearth | about 40–65 t/(m²·day). Shougang Jingtang has reported 78 t/(m²·day). | US legacy form used coke burned per unit hearth area per day. Do not mix them. |
| Coke rate | CR = m_coke / HM | 280–340 kg/tHM low-fuel. A review put the minimum near 330 and the mean near 363 for 3000–3800 m³. | IJmuiden has *claimed* 250 kg/tHM coke with 250 kg/tHM PCI. That is a vendor figure [C]. |
| Fuel rate | coke + PCI + nut coke + coke-equivalent of oil, gas | 470–530 kg/tHM. Best quoted near 460. Shougang Jingtang 496 with coke 263 and PCI 196. | Say whether injectants are actual mass or coke-equivalent. |
| Reducing agent rate | coke + injectant actual mass | 470–500 kg/tHM. Mean of 19 large Chinese furnaces 2011–14 was 511. | |
| PCI replacement ratio | Δ coke / Δ coal | Theoretical 0.8–1.0 kg/kg. About 0.9 at 150 kg/tHM. Falls below theory above ~150. | "Corrected RR" also removes blast-temperature and other balance shifts. State which. |
| Specific blast volume | V_blast / HM | about 1,000–1,200 Nm³/tHM | |

Productivity sources: [J. Metall. Mater. Eng. 2020](https://doi.org/10.30544/414), [Shougang Jingtang, AIST Transactions 22(10)](https://onepetro.org/ist/article/22/10/168/804875/Development-and-Progress-on-Green-and-Low-Carbon), [ISIJ Int. 2015-353 on 19 Chinese furnaces](https://doi.org/10.2355/isijinternational.isijint-2015-353).

## Gas utilisation

```
η_CO = CO2 / (CO + CO2)          volume fraction, dry analysis
η_H2 = H2O / (H2 + H2O)
```

η_CO of 0.48–0.525 is a normal modern band. Platform-plus-funnel charging has been reported at 50.5–52.5%, central-coke charging at 46.5–48.5%. International "advanced" figures of 52–54% are quoted against a Chinese large-furnace fleet that mostly sat under 50% in 2011–14.

Equilibrium η_CO in the thermal reserve zone is about 35% at 800 °C and about 29% at 1000 °C. Actual utilisation is shaft efficiency times that equilibrium. Shaft efficiency above 0.90 is good. 1.00 is the thermodynamic ceiling.

Hydrogen utilisation of 0.35–0.50 is quoted and poorly pinned. Treat it as plant-specific.

Geerdes rule of thumb, constant blast volume: +1% η_CO is worth about −7 kg/tHM coke. Confirm against [11-pending-validation.md](11-pending-validation.md) PV-01 before showing it as a recommendation.

## Permeability: four variants, two directions

| Variant | Formula | Direction | Who |
|---|---|---|---|
| v1 | K = Q_blast / ΔP_total | higher is better | Common operating index. Units Nm³·min⁻¹·kPa⁻¹. Track the trend. |
| v2 | K = (Q1 + Q2) / ΔP_total | higher is better | [JIEM 3(4) 2025](https://doi.org/10.62517/jiem.202503407), cold blast flow in m³/s over kPa. |
| Resistance | R = ΔP / Q | lower is better | Inverse of v1. Weekly reports. |
| Shaft K | K = RGV / [(p1 − p_top)^1.7 · A1] | **lower is better** | thyssenkrupp Schwelgern. RGV is bosh gas volume, A1 is shaft area. Easy to code backwards. |
| Ergun coefficient | ΔP/L = K · ρ · G^1.7 / μ^0.3 | lower resistance is better | Turbulent packed-bed form. [ISIJ Int. 57(9)](https://doi.org/10.2355/isijinternational.isijint-2016-224). |
| Circumferential index | standard deviation of gas temperatures about 5 m below the stockline | lower is better | JFE control limit at or below 120 °C (patent US12624404). |

Upper share of total pressure drop is often 0.25–0.35. A rising upper share points at shaft fines. A rising lower share points at the cohesive zone, bird's nest, or liquid holdup.

Nippon Steel channeling factor CF = ΔP / σ_yy. CF above 1 outside the raceway means theoretical channeling. Design target is CF below 1 ([NSC report 123-16](https://www.nipponsteel.com/en/tech/report/pdf/123-16.pdf)).

## Flame temperature

Empirical Nippon Steel form, °C:

```
T_f = 1524 + 60·R_O2 + 0.84·T_b − 2.7·R_coal − 6.3·M_b
```

R_O2 is enrichment in vol%, T_b blast temperature in °C, R_coal PCI in kg/tHM, M_b moisture in g/Nm³.

AIST/Geerdes form, the one to implement first:

```
RAFT = 1489 + 0.82·BT − 5.705·BM + 52.778·OE
       − 18.1·(Coal/WC)·100 − 43.01·(Oil/WC)·100
       − 27.9·(Tar/WC)·100 − 50.66·(NG/WC)·100
```

BT °C, BM g/m³ STP, OE = %O₂ − 21, injectant rates kg/tHM dry, WC wind consumption in m³ STP/tHM. Stated for RAFT roughly 1900–2300 °C. It is a linearisation of a raceway enthalpy balance. It is not valid far outside conventional blast.

Acceptable operating band often quoted: 1900–2250 °C, with many furnaces held at 2000–2200 °C.

Geerdes sensitivities at constant blast volume:

| Change | Δ flame temperature | Δ top gas temperature |
|---|---|---|
| Blast temperature +100 °C | +65 °C | — |
| Coal +10 kg/tHM | −30 °C | +9 °C |
| Oxygen +1% | +45 °C | −15 °C |
| Moisture +10 g/m³ STP | −50 °C | +9 °C |

The rigorous alternative is an adiabatic enthalpy balance on a tuyere control volume: enthalpy in (blast, oxygen, moisture, injectant, coke arriving at raceway temperature) equals enthalpy out (CO, H₂, N₂ at flame temperature). Prefer that once species enthalpies are coded and tested. Recalibrate every empirical form on the plant. Do not transplant coefficients. The uncited `1615 + 0.76·HBT − 5.75·H + 53.3·E` variant stays off. See PV-09.

Sources: [Mousa, Metall. Mater. Eng. 25(2) 2019](https://metall-mater-eng.com/index.php/home/article/download/414/333), [IJERA 7(4)](https://ijera.com/papers/Vol7_issue4/Part-3/I0704035762.pdf).

## Bosh gas

Each O₂ molecule at the tuyere yields two CO, so a first estimate is:

```
V_bosh = V_N2 + 2·V_O2     plus hydrogen from moisture and injectants
```

Geerdes example: 6500 m³ STP/min at 25.6% O₂ gives 8164 m³ STP/min at about 59% N₂ and 41% CO.

Specific bosh gas volume is often 1400–1650 Nm³/tHM. A design study put the flooding/fluidisation ceiling near 1445 m³/t. Bosh gas index (volume per hearth area per time) is often 54–67 Nm³/(min·m²); TISCO No. 5 was operated in that band.

Bosh gas hydrogen is a few percent and rises quickly with PCI, natural gas, moisture, or hydrogen injection.

## Raceway and blast energy

Nakamura raceway depth ([Tetsu-to-Hagané 73(15) 1980](https://www.jstage.jst.go.jp/article/tetsutohagane1955/73/15/73_15_1980/_article/-char/en)):

```
D_R = 5.00 · D_t · u_t · sqrt(P_b + 1) / [ρ_c · d_p · (T_b + 273)]
```

D_R and D_t in m, u_t in m/s, P_b in kgf/cm² gauge, ρ_c in kg/m³, d_p in m, T_b in °C. Large furnaces near 1.4 m. Fine-coke deposition rises sharply above about 1.3 m.

Geometry power laws ([ISIJ Int. 26 (1986) 107](https://doi.org/10.2355/isijinternational1966.26.107)):

```
D_R / D_T = 0.315 · RF^0.587
W_R / D_T = 2.631 · (D_R / D_T)^0.331
V_R = 0.53 · D_R · H_R · W_R
```

Blast "kinetic energy" is published as both:

- momentum per tuyere, (Q_t/60) · ρ · v, in kg·m/s. Chinese super-large furnaces quote 10,000–15,000 per tuyere.
- power per tuyere, ½ ṁ v², in kW. MMK 2000 m³ furnaces quoted an optimum near 90–100 kW.

Store the convention on the series. A later reader cannot recover it from the magnitude alone if both land in a similar numeric range after a unit error.

## Rist operating line

Axes used by Bailera et al. ([Open Research Europe 2021, 1:141](https://doi.org/10.12688/openreseurope.14275.1)):

```
X = (O + H2) / (C + H2)     gas oxidation state
Y = (O + H2) / Fe
Y = μ · X + Y_E
μ = (C + H2) / Fe           slope, specific reducing-gas requirement
```

Y_E is the intercept: oxygen and hydrogen that did not come from iron oxide (blast oxygen, moisture, injectant O and H). Direct reduction ratio r_d = y_d / Y_A, where y_d is the oxygen removed by direct reduction, read where X = 1. Typical r_d is 0.20–0.40. Full coefficients are in [03-physics-equations.md](03-physics-equations.md).

Shaft efficiency is the distance of the real operating point from the wüstite equilibrium point, as a fraction of the ideal distance. Thermal reserve zone temperature is the plateau in the burden temperature profile, commonly 950–1000 °C. Lowering it moves the equilibrium toward higher η_CO and a lower reductant rate.

## Slag

```
B2 = CaO / SiO2                         1.05–1.30
B3 = (CaO + MgO) / SiO2                 1.40–1.60
B4 = (CaO + MgO) / (SiO2 + Al2O3)       0.95–1.10
```

Weight percent. Typical BF slag is about CaO 40, MgO 10, SiO₂ 36, Al₂O₃ 10, and those four oxides are about 96% of the slag.

Viscosity target is under 1 Pa·s at tap temperature, often 0.3–0.8 at 1500 °C. Implement Urbain, Riboud, and the NPL optical-basicity model. Equations and coefficients are in [03-physics-equations.md](03-physics-equations.md). Iida stays pending (PV-06).

BF slags are short slags: viscosity rises abruptly near a critical temperature. Drainage logic should key off `T_slag − T_liquidus`, not viscosity alone. The liquidus polynomial is PV-07.

Sulphur partition:

```
L_S = (mass% S in slag) / (mass% S in metal)
```

Geerdes operating guide: to cut hot metal sulphur by 5%, cut sulphur input by 5%, or raise B3 by 0.02, or raise hot metal silicon by 0.06%. The capacity equations are in the physics file.

## Heat loss, residence, flooding

Heat loss per tonne is the sum of `ṁ · c_p · ΔT` over cooling circuits, divided by hot metal rate. A working band is 0.2–1.1 GJ/tHM, worth roughly 10–55 kg coke/tHM depending on the equivalence used. Geerdes quotes +10 GJ/h of cooling loss as about +1.2 kg/tHM coke. Confirm PV-01.

```
τ_solids = H_eff / v_descent     6–8 hours
τ_gas    = H_eff / u_superficial 6–12 seconds (4–5 s on the centre line)
```

The ratio is about 2000:1. A burden change takes a shift to reach the tuyeres. A blast change is felt in the raceway immediately and in the hot metal over the thermal time constant.

Fluidisation check, from the packed-bed force balance:

```
g · [ρ_s · (1 − ε) + ρ_l · h_t]  >  ΔP / ΔL
```

If the right side wins, the bed can lift. Classic Japanese work concluded coke-bed fluidisation often starts before slag flooding, because slag is more than 2.5 times as dense as coke. A 2008 model study on very light versus heavy particles concluded flooding could be what occurs in the lower furnace. The disagreement is genuine. Report both checks. See PV-04.

## Thermal equivalence, constant blast volume

Geerdes Annex III, reconstructed. Show these as rules of thumb with the constant-blast-volume label, not as optimiser gradients, until PV-01 is signed.

| Change | Coke-rate adjustment |
|---|---|
| Hot metal Si +0.1% | +4 kg/tHM |
| Blast moisture +10 g/m³ STP | +6 |
| Top pressure +0.1 bar | −1.2 |
| Coal +10 kg/tHM | −9 |
| Oil +10 kg/tHM | −11 |
| Oxygen +1% | +1 |
| Blast temperature +100 °C | −9 |
| Slag volume +10 kg/tHM | +0.5 |
| Cooling losses +10 GJ/h | +1.2 |
| η_CO +1% | −7 |

Other plants quote −20 to −30 kg/tHM per +100 °C of blast temperature. Both can be right under different conventions: at constant production the coke rate moves more, because productivity is not allowed to absorb the extra heat. The screen must say which convention it used.

## Driving rate

Production is set by oxygen through the tuyeres and by the carbon burned there:

```
P (tHM/day) = [O2 through tuyeres (kmol/day) · 2 · 12] / C_burned_at_tuyeres (kg C / tHM)
```

Geerdes example: holding tuyere carbon burn at 300 kg/tHM and moving 10 kg/tHM from coke to coal cuts production about 6.5%, because production follows the coke burn, not total carbon. Flame temperature in that example fell 32 °C.

Oxygen enrichment raises productivity until top gas temperature hits the floor near 100 °C, below which burden moisture stops evaporating and the effective furnace height shrinks.

A productivity claim has to clear five ceilings, not one:

1. Tuyere oxygen and carbon stoichiometry.
2. Bed permeability and channeling (CF below 1 outside the raceway).
3. Slag flooding or coke fluidisation in the dripping zone.
4. Minimum top gas temperature.
5. Hearth drainage capacity.

The Donetsk/Ramm permeability-constrained form is in [03-physics-equations.md](03-physics-equations.md).
