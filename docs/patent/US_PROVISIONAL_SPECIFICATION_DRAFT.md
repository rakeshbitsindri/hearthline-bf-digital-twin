# UNITED STATES PROVISIONAL PATENT APPLICATION DRAFT

## Title of the invention

**Lag-Aware Advisory Digital Twin for Diagnosing Blast-Furnace Production Shortfalls**

## Inventor(s)

`[FULL LEGAL NAME, RESIDENCE CITY/STATE/COUNTRY, CITIZENSHIP FOR EACH ACTUAL INVENTOR]`

## Applicant / assignee

`[APPLICANT OR ASSIGNEE LEGAL NAME AND ADDRESS; VERIFY EMPLOYMENT/IP-ASSIGNMENT OBLIGATIONS]`

## Correspondence address

`[ADDRESS, EMAIL, PHONE, CUSTOMER NUMBER IF ANY]`

---

## 1. Technical field

The present disclosure relates to monitoring, diagnosis, simulation, and safety-gated operational guidance for metallurgical shaft furnaces. More particularly, it concerns a read-only advisory digital twin for an iron blast furnace that identifies hidden physical causes of hot-metal production loss when operator-manipulated settings appear substantially unchanged, by combining production-target-conditioned multivariate operating bands, furnace-transport lag convolution, sensor-anchored reduced-order physics, causal-role-separated learned residuals, and a joint-density operating-envelope gate.

## 2. Background

An iron blast furnace is a tall counter-current moving-bed reactor. Solid burden descends from the top while reducing gas generated at tuyere level ascends through coke and ore layers. A limited set of external measurements is available even though important internal states, including radial gas distribution, cohesive-zone geometry, alkali and zinc recirculation, burden degradation, coke-bed permeability, and hearth drainage state, evolve over time.

A recurring industrial problem is that hot-metal production decreases while an operating sheet shows substantially unchanged blast flow, oxygen enrichment, hot-blast temperature, top pressure, burden ratio, and fuel settings. Conventional trend screens commonly compare same-hour values or fixed alarm thresholds. Such comparisons do not account for the fact that different inputs and disturbances affect the furnace after different transport delays. Blast and top pressure act in approximately sub-hour to one-hour windows; pulverized-coal injection may act over approximately one to three hours; charged burden and coke may require approximately five to eight hours to descend; and volatile alkali or zinc inventories may accumulate over days.

Pure machine-learning models trained on closed-loop operator-controlled history may learn a control policy rather than a causal furnace response. An operator often changes blast, moisture, fuel, or charging in response to furnace observations that are incompletely logged. A same-hour attribution can therefore assign apparent causality to whichever variable moved most recently rather than to a slow disturbance that initiated the event.

Physics-only models also have limitations. Empirical coefficients can have plant-specific offsets. A free-running packed-bed pressure-drop model may disagree with the instrument baseline. Further, conventional hard numerical clipping sets model derivatives to zero at a limit, causing a counterfactual response to disappear exactly where an operator most needs it.

Known systems separately provide blast-furnace expert rules, digital-twin anomaly detection, hybrid physics/learning blocks, plant-historical model development, causal regression based on residence time, and Mahalanobis anomaly scoring. A need remains for a furnace-specific system that:

1. defines a required-production-dependent safe band for each furnace tag;
2. evaluates each tag at its physical delay;
3. diagnoses hidden response and disturbance changes during an unchanged-input interval;
4. anchors counterfactual physics to current measured sensors without eliminating the derivative;
5. separates predictive and decision models to reduce closed-loop confounding;
6. gates advice by the joint historical operating density and multiple physical production ceilings; and
7. generates a governed engineering-trial dossier instead of a routine setpoint when a proposal is unsupported.

## 3. Summary of the invention

In one aspect, a computer-implemented advisory method receives read-only time-series furnace records through a historian interface and assigns each tag to one mutually exclusive causal role: manipulated input, material or environmental disturbance, furnace state response, production or quality outcome, or derived latent state.

For a required hot-metal production rate, the method identifies a historical cohort of qualified on-wind furnace periods near the required rate, optionally excluding periods having excessive pressure drop or an unqualified regime. For each tag, empirical quantiles from the cohort are combined with a physical sensitivity for production intensity to form a target-conditioned Golden Band.

At a query time, each tag is transformed into a lag-active value using a tag-specific temporal kernel based on a transport or residence time. A shortfall is detected relative to the required rate and/or a preceding rolling production baseline. When manipulated inputs remain substantially within their target-conditioned bands, the method ranks disturbance and state-response tags whose lag-active values leave their target-conditioned bands or shift adversely relative to the preceding rolling baseline.

The method computes a counterfactual recovery trajectory using a hybrid digital twin. The reduced-order physics portion can include flame-temperature, carbon/oxygen balance, packed-bed pressure-drop, top-gas-utilization, condensation-load, cohesive-zone, and productivity-ceiling relations. At the current baseline, each measured response is reconciled to the corresponding physics output using an additive anchor bias. The same bias is held fixed across a counterfactual so that the absolute value agrees with the sensor while the change remains a physics response. A smooth monotonic soft-limit operator replaces hard clipping to preserve a nonzero response derivative beyond a nominal bound.

The candidate input vector is then evaluated against a joint density operating envelope, such as a regularized Mahalanobis ellipsoid, and a trust region around the current point. A ceiling arbiter evaluates multiple physical constraints, including tuyere oxygen stoichiometry, permeability pressure drop, gas flooding or fluidization, top-gas thermal or dewpoint constraint, and hearth drainage. If the candidate is outside the joint-density envelope, beyond the trust region, non-identifiable, stale, or missing a required site-approved limit, the system withholds a routine setpoint and produces a management-of-change engineering-trial dossier.

## 4. Brief description of the drawings

The drawings referred to below are provided in `PATENT_DRAWINGS.html`.

- **FIG. 1** is a system architecture showing the blast furnace, read-only historian interface, causal-role registry, lag engine, physics model, learned residual, observability engine, envelope gate, operator interface, and tamper-evident audit ledger.
- **FIG. 2** is a method flow for diagnosing a production shortfall during an unchanged-input interval.
- **FIG. 3** illustrates mutually exclusive tag-role classification and direction of causal flow.
- **FIG. 4** illustrates target-conditioned Golden Bands at different required production rates.
- **FIG. 5** illustrates tag-specific lag kernels and alignment of input, disturbance, and output records.
- **FIG. 6** illustrates baseline sensor anchoring and zero-drift counterfactual simulation.
- **FIG. 7** illustrates the joint Mahalanobis operating envelope, trust region, physical-ceiling arbiter, and management-of-change gate.
- **FIG. 8** illustrates the role-based, hash-chained audit record and separate post-hoc confirmed-execution field.

## 5. Reference numerals

| Numeral | Element |
|---|---|
| 100 | blast furnace advisory system |
| 102 | blast furnace |
| 104 | plant sensors and laboratory records |
| 106 | read-only historian or DMZ replica interface |
| 108 | source/time/provenance processor |
| 110 | tag registry and causal-role classifier |
| 112 | operating-regime gate |
| 114 | target-conditioned Golden-Band generator |
| 116 | tag-specific lag convolution engine |
| 118 | reduced-order physics engine |
| 120 | learned forecast residual |
| 122 | causal-parent decision residual |
| 124 | sensor-anchor reconciler |
| 126 | hidden-state shortfall attribution engine |
| 128 | joint-density envelope and trust-region gate |
| 130 | physical productivity-ceiling arbiter |
| 132 | operator advisory interface |
| 134 | management-of-change dossier generator |
| 136 | role-based tamper-evident audit ledger |
| 138 | separate confirmed-execution store |

## 6. Definitions

**Qualified operating period** means an interval classified as suitable for steady or quasi-steady advisory analysis, excluding at least off-wind, banking, blow-in, shutdown, maintenance, stale-source, severe-instability, or unqualified-regime intervals.

**Manipulated input** means a parameter intentionally set or adjusted by an operator or control system, for example blast volume, hot-blast temperature, oxygen enrichment, top pressure, fuel injection, coke rate, or charging pattern.

**Disturbance** means a physical input not treated as the advisory setpoint, for example coke CSR/CRI, sinter RDI or FeO, burden moisture, raw-material chemistry, ambient condition, alkali input, or zinc input.

**State response** means a measured response of the furnace, for example pressure-drop split, top-gas composition, stave temperature, top-gas temperature, cooling heat loss, or burden descent.

**Outcome** means a production or quality result, for example hot-metal tonnes, hot-metal temperature, silicon, sulphur, or fuel rate.

**Derived latent state** means a computed quantity not directly measured, for example raceway adiabatic flame temperature, cohesive-zone root height, condensation load, alkali inventory, or hearth liquid level.

**Unchanged-input interval** means an interval in which one or more selected manipulated inputs remain within corresponding target-conditioned Golden Bands and/or within a specified change tolerance, while production decreases relative to a required rate or rolling reference.

## 7. Detailed description

### 7.1 Read-only data acquisition and immutable provenance

The read-only interface 106 can acquire records from an OSIsoft/AVEVA PI Web API through GET operations, from an OPC-UA server through Read and HistoryRead services, or from an immutable Parquet, CSV, or spreadsheet drop zone. The interface excludes write, history-update, OPC-method-call, SQL-mutation, setpoint-push, actuator, and PLC paths.

Each raw record can include an event time, receipt time, revision time, source identity, unit, quality status, and evidence class. Records are stored append-only. A laboratory value is not made available to an online model before its recorded availability time. When only hourly means exist, the system identifies slips, hangs, pressure spikes, tuyere events, and channeling precursors as below the sampling interval unless within-hour standard deviation, minimum, maximum, or excursion-count companion values are available.

### 7.2 Causal-role partition

The classifier 110 assigns every tag to exactly one role. The assignment can originate from a plant configuration, parameter registry, expert-approved graph, or rule set. The system prevents an outcome descendant from being used in the decision residual 122 even if the descendant improves prediction accuracy.

In a preferred embodiment, the role vector is:

```text
R(x_i) in {manipulated, disturbance, state_response, outcome, derived_latent}
```

The forecast residual 120 may use information known at prediction time. The decision residual 122 uses only expert-approved causal parents and is disabled when an identifiability audit returns non-identifiable.

### 7.3 Regime qualification

The regime gate 112 determines whether the furnace is on wind and qualified. One example uses blast flow as a fraction of a campaign on-wind median:

```text
q(t) = Fb(t) / median_on_wind(Fb)
on_wind when q(t) >= alpha
reduced_blast when beta <= q(t) < alpha
off_wind when q(t) < beta
```

Values of `alpha` and `beta` can be plant configured. An unqualified interval suppresses routine recommendations and absolute values of unobserved latent states.

### 7.4 Production-conditioned Golden-Band generation

Given required hot-metal production `P*`, the generator 114 forms a qualified cohort:

```text
H(P*) = { t :
          regime(t) is qualified,
          |P(t) - P*| <= epsilon_P,
          dP(t) <= Q_0.85(dP_on_wind) }
```

For tag `i`, an empirical center and lower/upper values are:

```text
C_i = Q_0.50(x_i | H(P*))
L_i^emp = Q_0.18(x_i | H(P*))
U_i^emp = Q_0.82(x_i | H(P*))
```

When the available cohort is sparse or does not exactly reach `P*`, a physics-derived production-intensity sensitivity `s_i` shifts the band:

```text
delta_P = (P* - median(P | H)) / 1000
L_i(P*) = L_i^emp + s_i * delta_P
C_i(P*) = C_i + s_i * delta_P
U_i(P*) = U_i^emp + s_i * delta_P
```

The band can be subject to plant-approved engineering limits and a minimum width based on instrument resolution. For an unmeasured latent state, a physics equilibrium point can provide the center, while the evidence class is marked assumed or simulated rather than measured.

### 7.5 Tag-specific lag convolution

The lag engine 116 applies a tag-specific delay or time constant. In one embodiment:

```text
x_tilde_i(t) = EMA(x_i[t - 2*tau_i : t], span=tau_i)
```

Alternative kernels include a pure transport delay, finite impulse response, Erlang, gamma-distributed residence time, data-estimated cross-correlation lag, or a mixture kernel for bimodal PCI transport.

Example prior ranges include:

- top pressure: approximately 0.6 hour;
- blast flow and oxygen: approximately 1 hour;
- PCI: approximately 1.5 to 3 hours;
- charged burden or coke: approximately 5 to 8 hours;
- hot-metal temperature: greater than 8 hours; and
- alkali or zinc inventory: multiple days.

### 7.6 Shortfall detection and dual-reference attribution

At time `t`, a shortfall magnitude can be:

```text
S_target(t) = max(0, P* - P(t))
S_roll(t) = max(0, median(P[t-84h:t-12h]) - P(t))
S_eff(t) = max(S_target(t), S_roll(t))
```

For each tag, the system compares `x_tilde_i(t)` with both its target-conditioned band and the prior rolling reference. Excursions can be converted to estimated production risk using a physics sensitivity, learned local slope, or bounded combined sensitivity. The attribution is ranked by estimated production loss and grouped by causal role and furnace region.

In an unchanged-input interval, manipulated inputs within their bands are not automatically identified as causes. Instead, the method prioritizes disturbance, state-response, and latent-state deviations, including circumferential temperature asymmetry and upper/lower pressure-drop split.

### 7.7 Seven-gate observability protocol

One embodiment performs:

1. verify that production loss is testable from a reconciled tonnage route;
2. verify identity and timing of manipulated inputs;
3. compare material and environmental disturbances;
4. compare measured furnace responses;
5. update slow accumulated inventories;
6. test multivariate residual and correlation structure; and
7. return a measurement gap when the cause is below the sampling interval or unobservable.

The output `inconclusive` or `not_testable` is permitted and prevents an unsupported cause from being asserted.

### 7.8 Reduced-order physical state

The physics engine 118 can include:

- oxygen and carbon stoichiometry at tuyere level;
- raceway adiabatic flame-temperature correlation;
- bosh-gas volume;
- Rist or equivalent carbon/oxygen operating-line quantities;
- upper and lower packed-bed pressure drop;
- gas utilization;
- cohesive-zone geometry proxy;
- alkali/zinc condensation load;
- hot-metal temperature and silicon response; and
- multiple productivity ceilings.

The invention is not limited to any named empirical coefficient or equation.

### 7.9 Derivative-preserving soft saturation

For nominal lower and upper bounds `L` and `U` and softness `s`, one embodiment uses:

```text
S(x) = U + s*tanh((x-U)/s), x > U
S(x) = L - s*tanh((L-x)/s), x < L
S(x) = x,                    L <= x <= U
```

Unlike a hard clip, the operator preserves a nonzero derivative outside the nominal interval, so a counterfactual change continues to propagate into downstream states near a physical limit.

### 7.10 Baseline sensor anchoring and zero-change identity

At baseline input state `u0`, free-running physical output is `f_phys(u0)` and measured response is `y_meas(t0)`. The reconciler 124 computes:

```text
b0 = y_meas(t0) - f_phys(u0)
y_hat(u0 + delta_u) = f_phys(u0 + delta_u) + b0
```

The anchor `b0` is held fixed across the counterfactual. Physical identities are then enforced, including:

```text
dP = dPu + dPl
Productivity = Production / working_volume
```

When `delta_u = 0`, the simulated state equals the measured baseline within a numerical tolerance, preventing phantom movement.

### 7.11 Learned residual and validation

Lag-aligned input features can be standardized and fitted to response residuals using regularized regression or gradient boosting. A silicon forecast can predict a change from the previous cast rather than the absolute value. Validation uses contiguous walk-forward folds and an embargo at least as long as the measured target decorrelation time. A persistence baseline remains visible and a learned model is not served unless it beats persistence.

### 7.12 Joint-density envelope and trust region

The system fits mean `mu` and a regularized covariance `Sigma_reg` over qualified historical manipulated-input vectors. Candidate `u` is evaluated by:

```text
D_M(u) = sqrt((u-mu)^T * inv(Sigma_reg) * (u-mu))
```

A candidate is outside the operating envelope when `D_M` exceeds a selected chi-square-derived threshold. A second distance from current input `u0` limits a single advisory step.

### 7.13 Physical ceiling arbiter

The arbiter 130 evaluates at least two and preferably all of:

1. tuyere oxygen/carbon stoichiometric ceiling;
2. packed-bed pressure-drop/permeability ceiling;
3. bosh-gas flooding or fluidization ceiling;
4. top-gas thermal or acid-dewpoint ceiling; and
5. hearth drainage/coke-bed ceiling.

The lowest ceiling is reported as binding. When a target exceeds the binding ceiling, the system reports the ceiling instead of fabricating a setpoint.

### 7.14 Capability and evidence classifier

For each result, the system evaluates whether required inputs are measured, assumed, stale, missing, outside a validated band, or unobservable. Example statuses include:

```text
measured_anchored
physics_estimated
assumption_dependent
response_only
not_qualified
not_identifiable
not_testable
```

An absolute value can be withheld while a response delta remains available.

### 7.15 Advisory, management-of-change, and audit

If a proposal is out of the joint envelope, outside the trust region, non-identifiable, stale, or missing a required site limit, the system generates a management-of-change dossier rather than a routine advisory. The dossier can contain proposed moves, reason for the block, required trial checks, model version, and sign-off requirements.

The audit ledger 136 can hash each event together with the preceding event hash. Operator acceptance or rejection is stored in the immutable event. Whether the plant later executed the accepted action is stored separately in the confirmed-execution store 138 and does not change the original event hash.

## 8. Best mode presently contemplated

The presently preferred implementation:

1. uses read-only PI Web API GET or OPC-UA Read/HistoryRead profiles;
2. archives raw records append-only;
3. assigns each tag one causal role in a configuration registry;
4. qualifies on-wind periods before model use;
5. builds target bands from qualified P18/P50/P82 cohorts near the requested production;
6. uses exponential lag filters with plant-calibrated time constants;
7. steps reduced-order physics and adds a bounded learned residual;
8. reconciles outputs with a fixed baseline sensor bias;
9. applies the smooth soft-limit operator;
10. checks a 99-percent joint Mahalanobis ellipsoid and a local trust region;
11. reports the lowest of five physical production ceilings; and
12. records operator decisions in a SHA-256 hash-chained audit ledger with a separate confirmed-execution field.

## 9. Worked examples

### Example 1: Circumferential hidden-state change

The public EVRAZ ZSMK series contains 29,602 hourly sensor records and 16,589 cast silicon analyses. Across qualified on-wind hours, peripheral probes show persistent azimuthal differences. A single average top-gas value does not expose that asymmetry. The system groups `Tp1` through `Tp10`, computes circumferential spread, and ranks a high wall-flow sector as a response change even when blast settings remain in band.

### Example 2: Low oxygen and blast shortfall

At a historical reference time, the lag-active oxygen and blast values can be below their target-conditioned bands while a prior 72-hour reference is higher. The engine assigns separate production-risk contributions to oxygen and blast, includes their one-hour lag, and proposes movement toward the band center. This example is a software demonstration because the public series does not contain reconciled cast tonnage; the production quantity is labelled estimated rather than measured.

### Example 3: Out-of-envelope proposal

At a qualified on-wind reference hour, increasing blast by approximately 800 m3/min, oxygen flow by approximately 8,000 m3/h, and hot-blast temperature by approximately 150 C can yield a joint Mahalanobis distance above the learned threshold. The proposal is not returned as a routine setpoint. The system generates an engineering-trial dossier containing the moved tags, distance, threshold, physical ceilings, and required sign-offs.

### Example 4: Zero-change identity

Across sampled qualified historical hours, a simulation with no input change returns no response drift. Pressure-drop split remains exact. A hot-blast-temperature change continues to affect flame temperature and downstream thermal responses even when one state is near a nominal limit because the soft-limit derivative remains nonzero.

## 10. Alternative embodiments

The invention can be applied to other counter-current moving-bed or delayed industrial reactors. The lag kernel can be learned, configured, or hybrid. The operating envelope can use kernel density, one-class support-vector methods, conformal scores, normalizing flows, or convex-hull methods instead of Mahalanobis distance, while retaining a joint-density and local-trust concept. The audit can use another tamper-evident hash or append-only ledger. The system can be deployed on premises, in an industrial DMZ, or in a segregated cloud tenant.

## 11. Abstract

A read-only advisory system diagnoses blast-furnace production shortfalls when operator settings appear unchanged. Furnace tags are partitioned into manipulated inputs, disturbances, state responses, outcomes, and latent states. For a required hot-metal rate, qualified historical periods generate a production-conditioned operating band for each tag. Each tag is evaluated using a furnace-transport lag kernel and compared with both the operating band and a preceding rolling baseline. Ranked deviations identify hidden causes and estimated production loss. A hybrid reduced-order physics and learned-residual model is anchored to current sensor values using a fixed reconciliation bias and smooth saturation that preserves response derivatives. Counterfactual recovery actions are checked against a joint-density operating envelope, local trust region, causal-identifiability status, and multiple physical productivity ceilings. Unsupported actions are withheld and converted into a management-of-change trial dossier. Operator decisions are stored in a tamper-evident audit chain separately from later plant-execution confirmation.

## 12. Claim appendix

Claims are not required for a US provisional application. Draft claims are provided in `US_CLAIMS_DRAFT.md` so the disclosure expressly supports the anticipated nonprovisional scope.

