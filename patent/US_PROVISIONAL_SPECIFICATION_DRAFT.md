# UNITED STATES PROVISIONAL PATENT APPLICATION DRAFT

## Title of the invention

**Method of Identifying an Unmeasured Cause of a Blast-Furnace Production Shortfall**

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

### Example 4: Zero-change identity and derivative-preserving saturation

Across sampled qualified historical hours, a simulation with no input change returns no response drift. Pressure-drop split remains exact: total pressure drop equals upper-furnace pressure drop plus lower-furnace pressure drop.

The preferred saturation operator, with nominal interval `[L, U] = [1.20, 1.70]` and softness `s = 0.08*(U-L) = 0.040`, was compared with hard clipping:

| Unsaturated value | Hard-clip output | Hard-clip derivative | Soft-saturation output | Soft-saturation derivative |
|---|---:|---:|---:|---:|
| 1.70 (at upper bound) | 1.7000 | 1.0000 | 1.7000 | 1.0000 |
| 1.72 | 1.7000 | 0.0000 | 1.7185 | 0.7864 |
| 1.74 | 1.7000 | 0.0000 | 1.7305 | 0.4200 |
| 1.78 | 1.7000 | 0.0000 | 1.7386 | 0.0707 |

Hard clipping extinguishes the local derivative immediately above the bound. The soft operator retains a positive derivative in the same neighbourhood, so a counterfactual move that crosses a nominal model bound still produces a nonzero downstream response.

### Example 5: Preferred lag constants

In the best mode presently known, tag-specific exponential kernels use these prior time constants, which are replaced by plant-calibrated delays when those delays are identified: top pressure 0.6 h; blast moisture 0.8 h; blast volume and oxygen 1.0 h; hot-blast temperature 1.5 h; pulverized-coal injection 2.5 h; sinter RDI 4.5 h; ore/coke ratio and burden iron 6.0 h; charged coke rate 6.5 h; coke CSR 7.0 h; alkali and zinc inputs 12 h. The rolling reference used for shortfall comparison is a window ending before the most recent hours, so a developing event does not define its own baseline.

## 10. Alternative embodiments

The invention can be applied to other counter-current moving-bed or delayed industrial reactors. The lag kernel can be learned, configured, or hybrid. The operating envelope can use kernel density, one-class support-vector methods, conformal scores, normalizing flows, or convex-hull methods instead of Mahalanobis distance, while retaining a joint-density and local-trust concept. The audit can use another tamper-evident hash or append-only ledger. The system can be deployed on premises, in an industrial DMZ, or in a segregated cloud tenant.

## 11. Abstract

A read-only advisory system diagnoses blast-furnace production shortfalls when operator settings appear unchanged. Furnace tags are partitioned into manipulated inputs, disturbances, state responses, outcomes, and latent states. For a required hot-metal rate, qualified historical periods generate a production-conditioned operating band for each tag. Each tag is evaluated using a furnace-transport lag kernel and compared with both the operating band and a preceding rolling baseline. Ranked deviations identify hidden causes and estimated production loss. A hybrid reduced-order physics and learned-residual model is anchored to current sensor values using a fixed reconciliation bias and smooth saturation that preserves response derivatives. Counterfactual recovery actions are checked against a joint-density operating envelope, local trust region, causal-identifiability status, and multiple physical productivity ceilings. Unsupported actions are withheld and converted into a management-of-change trial dossier. Operator decisions are stored in a tamper-evident audit chain separately from later plant-execution confirmation.

## 12. Claim appendix

Claims are not required to obtain a US provisional filing date. The claims below are included so this disclosure expressly supports the anticipated nonprovisional scope. Bracketed inventor and applicant fields above must be completed before Patent Center submission. This draft is not legal advice and is not a filed application.

## What is claimed is:

1. **A method for identifying an unmeasured physical cause of a hot-metal production shortfall in an iron blast furnace while operator-set inputs remain inside a production-conditioned band, the method comprising:**

   receiving, through a historian interface restricted to read operations, time-series records from a plurality of sensors associated with the blast furnace;

   assigning each of a plurality of furnace tags represented in the time-series records to one of a plurality of mutually exclusive causal roles comprising a manipulated input, a disturbance, a furnace state response, an outcome, or a derived latent state;

   receiving a required hot-metal production rate;

   for each of at least a subset of the furnace tags, generating a production-conditioned operating band by:

   (a) selecting, from historical qualified on-wind periods, a cohort having a production measure within a production tolerance of the required hot-metal production rate and having a pressure-drop measure below a permeability criterion,

   (b) determining lower, center, and upper empirical values from the cohort, and

   (c) shifting at least one of the empirical values according to a physical production-intensity sensitivity and a difference between the required hot-metal production rate and a production measure of the cohort;

   at a query time, generating a lag-active value for each of the subset of furnace tags by applying a respective temporal kernel parameterized by a physical transport delay of the corresponding furnace tag;

   detecting an unchanged-input production-shortfall interval in which a production value is below at least one of the required hot-metal production rate or a preceding rolling production reference while a selected plurality of the manipulated inputs remain within corresponding production-conditioned operating bands;

   during the unchanged-input production-shortfall interval, identifying an unmeasured furnace condition as the cause of the production shortfall by ranking a measured disturbance or furnace state response whose lag-active value deviates from both (i) its production-conditioned operating band and (ii) a preceding rolling tag reference, the unmeasured furnace condition comprising at least one of an alkali or zinc accumulation, a burden-permeability loss, a cohesive-zone shift, a circumferential gas maldistribution, or a hearth-drainage restriction;

   generating a counterfactual recovery trajectory for at least one candidate manipulated-input vector with a reduced-order blast-furnace material-and-energy calculation reconciled to the sensors, wherein generating the counterfactual recovery trajectory comprises:

   computing an additive anchor bias at a baseline state as a difference between a measured furnace response and a free-running output of the reduced-order blast-furnace physics model,

   holding the additive anchor bias fixed while evaluating the candidate manipulated-input vector, and

   enforcing a pressure conservation identity in which a simulated total pressure drop equals a sum of an upper-furnace pressure drop and a lower-furnace pressure drop;

   determining whether the candidate manipulated-input vector is inside a joint-density operating envelope and a trust region and satisfies a plurality of physical blast-furnace productivity ceilings; and

   responsive to determining that the candidate manipulated-input vector is inside the joint-density operating envelope and the trust region and satisfies the plurality of physical blast-furnace productivity ceilings, outputting the candidate manipulated-input vector as the safety-gated operator advisory, and otherwise withholding the candidate manipulated-input vector as a routine advisory and generating an engineering-trial dossier.

2. The method of claim 1, wherein the historian interface permits one or more of an HTTP GET operation, an OPC-UA Read service, an OPC-UA HistoryRead service, or reading an immutable file, and rejects historian writes, OPC method calls, SQL mutation operations, and actuator setpoint writes.

3. The method of claim 1, wherein the physical transport delay is selected from a first gas-phase delay for blast flow or oxygen, a second injectant delay for pulverized-coal injection, a third burden-descent delay for charged coke or ore, and a fourth accumulation delay for alkali or zinc.

4. The method of claim 1, wherein the temporal kernel is an exponential moving-average kernel over an interval extending from the query time minus at least twice the physical transport delay to the query time.

5. The method of claim 1, wherein the preceding rolling tag reference excludes a recent interval immediately preceding the query time to prevent a developing event from contaminating the reference.

6. The method of claim 1, wherein the reduced-order blast-furnace physics model includes at least three selected from raceway adiabatic flame temperature, tuyere oxygen/carbon stoichiometry, bosh-gas volume, Rist operating-line quantity, upper and lower packed-bed pressure drop, top-gas utilization, cohesive-zone geometry, volatile condensation load, hot-metal temperature, silicon response, or a production ceiling.

7. The method of claim 1, further comprising confirming a zero-change identity in which, when the candidate manipulated-input vector equals a current manipulated-input vector, each anchored simulated response equals the corresponding measured baseline response within a numerical tolerance.

8. The method of claim 7, wherein the learned residual model used for the counterfactual recovery trajectory is restricted to features that are not descendants of the production outcome, and wherein a manipulated input classified as not identifiable is excluded from the safety-gated operator advisory.

9. The method of claim 1, wherein the reduced-order blast-furnace physics model applies a continuously differentiable monotonic saturation operator outside a nominal physical interval so that a response derivative remains nonzero outside the nominal physical interval.

10. The method of claim 1, wherein a forecast residual used to predict a future outcome is permitted to use information known at forecast time, and a separate decision residual used to score the candidate manipulated-input vector is restricted to causal-parent features of the outcome.

11. The method of claim 1, wherein the joint-density operating envelope comprises a regularized Mahalanobis ellipsoid fitted to historical qualified on-wind manipulated-input vectors and the trust region comprises a Mahalanobis step distance from a current manipulated-input vector.

12. The method of claim 1, wherein the plurality of physical blast-furnace productivity ceilings comprises at least three of a tuyere stoichiometry ceiling, a packed-bed permeability ceiling, a gas flooding or fluidization ceiling, a top-gas thermal or dewpoint ceiling, or a hearth drainage ceiling, and the method further comprises reporting a lowest ceiling as a binding ceiling.

13. The method of claim 1, further comprising storing an operator acceptance or rejection of the safety-gated operator advisory in a hash-chained append-only record and storing later confirmation that a plant action occurred in a separate post-hoc execution field that does not alter the hash of the operator acceptance or rejection.

14. **A system for identifying an unmeasured physical cause of a hot-metal production shortfall in an iron blast furnace, the system comprising:**

   a historian interface configured to receive time-series records from furnace sensors while lacking a write path to a plant historian, programmable logic controller, distributed control system, or furnace actuator;

   one or more processors; and

   memory storing instructions that, when executed by the one or more processors, cause the system to:

   classify furnace tags into mutually exclusive causal roles comprising manipulated inputs, disturbances, furnace state responses, outcomes, and derived latent states;

   form, for a required hot-metal production rate, respective target-conditioned operating bands from a permeability-qualified historical production cohort;

   transform values of the furnace tags into lag-active values using tag-specific temporal kernels representing physical transport delays within the blast furnace;

   detect a production shortfall during an interval in which selected manipulated inputs remain within the respective target-conditioned operating bands;

   attribute the production shortfall to an unmeasured furnace condition inferred from one or more lag-active disturbances or furnace state responses that have left their target-conditioned operating bands;

   anchor a reduced-order blast-furnace material-and-energy calculation to current measured sensor responses and use that anchored calculation to test a candidate recovery;

   evaluate the candidate recovery advisory against a joint historical operating-density envelope, a local trust region, and multiple physical blast-furnace productivity ceilings; and

   selectively output the candidate recovery advisory or an engineering-trial dossier according to the evaluation.

15. The system of claim 14, wherein the system is configured to output, for each attributed cause, a furnace tag, a tag-specific lag, a lag-active value, a target-conditioned operating band, an estimated production-loss contribution, and a physical mechanism.

16. The system of claim 14, wherein the system includes a capability classifier configured to classify a result as measured-anchored, physics-estimated, assumption-dependent, response-only, not-qualified, not-identifiable, or not-testable.

17. The system of claim 16, wherein the capability classifier withholds an absolute value of a derived latent state while permitting a differential counterfactual response when required measured inputs are absent.

18. The system of claim 14, wherein the system is configured to suppress the candidate recovery advisory during at least one of off-wind operation, banking, blow-in, shutdown, maintenance, stale-source operation, severe instability, or an unqualified regime.

19. The system of claim 14, wherein the system is configured to publish server-sent events containing monotonic sequence numbers, a model version, a regime status, an operating-envelope status, and a target-band compliance value.

20. The system of claim 14, further comprising a role-based audit service configured to permit acceptance or rejection by an operator role, calibration sign-off by a metallurgist role, and read-only inspection by an auditor role, while maintaining a cryptographic hash chain across audit events.
