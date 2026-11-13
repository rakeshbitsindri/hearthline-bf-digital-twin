# THE PATENTS ACT, 1970

# COMPLETE SPECIFICATION

## [See Section 10 and Rule 13]

## Title

**METHOD OF IDENTIFYING AN UNMEASURED CAUSE OF A BLAST-FURNACE PRODUCTION SHORTFALL**

## Applicant(s)

`[FULL LEGAL NAME, NATIONALITY, AND COMPLETE ADDRESS OF EACH APPLICANT]`

## Inventor(s)

`[FULL LEGAL NAME, NATIONALITY, AND COMPLETE ADDRESS OF EACH ACTUAL INVENTOR]`

## Preamble

**The following specification particularly describes the invention and the manner in which it is to be performed.**

---

## 1. Field of the invention

The invention relates to sensor-based monitoring and diagnosis of iron blast furnaces. More particularly, it relates to an industrial monitoring apparatus and method that receives read-only furnace measurements, detects and explains production shortfalls during intervals in which operator-manipulated settings remain substantially unchanged, computes a physically constrained recovery advisory, and prevents unsupported advice from being issued outside a validated multi-parameter operating envelope.

## 2. Background and problem addressed

A blast furnace is a counter-current moving-bed chemical reactor. Solid burden moves downward over several hours while gas generated at the tuyeres moves upward in minutes. Important internal conditions, including radial gas distribution, cohesive-zone position, burden degradation, coke-bed permeability, alkali and zinc recirculation, and hearth drainage, are not directly measured.

In practice, hot-metal output can fall while hourly blast volume, oxygen flow, hot-blast temperature, top pressure, and burden ratio appear similar to a prior high-production period. Ordinary threshold alarms and same-hour statistical attribution do not account for different transport delays. A predictive model trained on operator-controlled history can also confuse an operator response with a furnace cause.

Known blast-furnace control systems acquire online process data, apply expert rules or predictive models, and provide control guidance. Known digital-twin platforms combine physics and learning, estimate non-measurable variables, diagnose performance dips, and recommend corrective measures. Known manufacturing systems use residence time to align process variables, and known statistical systems use Mahalanobis distance to identify abnormal operation. These technologies do not provide the particular blast-furnace combination described below.

## 3. Objects of the invention

An object is to diagnose a physical production shortfall during an interval in which manipulated blast-furnace settings remain within operating bands associated with a required production rate.

Another object is to prevent incorrect same-hour attribution by aligning each furnace tag with its physical gas, injectant, burden, thermal, or inventory delay.

Another object is to create an operating band that changes with required hot-metal output instead of applying one static alarm range at every production rate.

Another object is to anchor a reduced-order physical furnace model to actual sensors without eliminating counterfactual response sensitivity at model limits.

Another object is to reject routine operational advice that is outside a historically observed multi-variable operating density, outside a local trust region, unsupported by causal identifiability, or above a physical productivity ceiling.

Another object is to provide read-only industrial deployment in which no historian-write, OPC-method, PLC, DCS, or actuator path is present.

## 4. Statement of technical advancement and technical effect

The claimed subject matter is not a computer program per se, mathematical method per se, or presentation of information. It is an industrial furnace monitoring and diagnosis process coupled to physical furnace sensors and a hardware/protocol-restricted read-only historian interface.

The technical advancement is the coordination of:

1. production-target-conditioned multi-sensor bands formed from qualified furnace operation;
2. furnace-residence-time alignment of heterogeneous physical variables;
3. sensor-anchored conservation-consistent counterfactual furnace simulation;
4. preservation of a non-zero physical response derivative at nominal model bounds;
5. detection of hidden physical degradation while manipulated inputs remain in band; and
6. joint-density and physical-ceiling suppression of unsupported recovery actions.

The resulting technical effects include fewer false physical-cause assignments, preservation of pressure-balance identity, detection of otherwise hidden gas-flow and burden-state changes, prevention of extrapolated out-of-envelope advisories, and improved reliability of read-only blast-furnace operational diagnosis.

## 5. Summary of the invention

The invention provides a read-only blast-furnace advisory apparatus having a sensor interface, one or more processors, and memory.

The apparatus assigns each furnace tag to exactly one causal role selected from manipulated input, material disturbance, furnace state response, outcome, and derived latent state.

For a required hot-metal production rate, the apparatus selects historical qualified on-wind periods near the required rate and below a permeability criterion. It derives lower, center, and upper empirical values for each tag and shifts the values by a physical production-intensity sensitivity when the cohort production differs from the required rate.

At a query time, each tag is transformed by a temporal kernel based on its physical transport or residence time. A production shortfall is compared with the required rate and a prior rolling production baseline. When manipulated inputs remain within their target-conditioned bands, disturbances and state responses leaving their bands or shifting adversely from their rolling references are ranked as causes.

A hybrid digital twin computes a recovery trajectory. A free-running reduced-order physical state is reconciled to measured sensors with a fixed baseline bias. A smooth monotonic limiting function preserves response derivatives beyond a nominal bound. A learned residual is permitted only within a decision feature set of causal parents.

Before an advisory is shown, the candidate manipulated vector is tested against a joint historical density envelope, a local trust region, and physical ceilings including tuyere stoichiometry, permeability, flooding or fluidization, top-gas thermal condition, and hearth drainage. A candidate failing the test is withheld and converted to an engineering-trial dossier.

## 6. Brief description of the accompanying drawings

- **FIG. 1** shows the overall read-only blast-furnace advisory apparatus.
- **FIG. 2** shows the shortfall-diagnosis method.
- **FIG. 3** shows causal-role partition and data flow.
- **FIG. 4** shows operating bands conditioned on required production.
- **FIG. 5** shows heterogeneous transport-lag alignment.
- **FIG. 6** shows sensor anchoring and zero-change identity.
- **FIG. 7** shows joint-density envelope, trust region, and physical-ceiling gating.
- **FIG. 8** shows role-based audit and separate confirmation of plant execution.

The drawings are provided in `PATENT_DRAWINGS.html` and shall be exported to compliant black-and-white PDF sheets before filing.

## 7. Detailed description of the invention

### 7.1 Industrial sensor interface

The apparatus receives furnace and laboratory records using a read-only industrial interface. The interface may use PI Web API HTTP GET, OPC-UA Read and HistoryRead, or an immutable file drop. The software and network profile omit write, history-update, OPC Call, SQL mutation, PLC, DCS setpoint, and actuator services.

Records preferably include event time, availability time, source identifier, revision identifier, engineering unit, and quality flag. Raw records are maintained append-only.

### 7.2 Role classification

Each tag is stored in a registry with one role:

```text
manipulated
disturbance
state_response
outcome
derived_latent
```

Examples of manipulated inputs are blast volume, hot-blast temperature, oxygen, top pressure, PCI, coke rate, and charging program. Disturbances include coke CSR, sinter RDI, burden moisture, chemistry, alkali, and zinc. State responses include pressure-drop split, top gas, and stave temperatures. Outcomes include hot-metal tonnes, hot-metal temperature, and silicon.

### 7.3 Regime qualification

The apparatus identifies whether the furnace is on wind, reduced blast, or off wind. Banking, blow-in, shutdown, severe instability, maintenance, stale source, and unqualified periods are excluded from routine advisory generation.

### 7.4 Required-production-conditioned operating bands

For required production `P*`, a cohort is formed:

```text
H(P*) = {t : qualified(t),
             |P(t) - P*| <= tolerance,
             dP(t) <= permeability_criterion}
```

For tag `x_i`, empirical lower, center, and upper values can be percentiles 18, 50, and 82 of the cohort. When the cohort median differs from `P*`, a physical sensitivity shifts the values:

```text
L_i(P*) = Q18_i + s_i*(P* - P_cohort)/1000
C_i(P*) = Q50_i + s_i*(P* - P_cohort)/1000
U_i(P*) = Q82_i + s_i*(P* - P_cohort)/1000
```

The percentile values, cohort tolerance, sensitivity, and minimum band width can be configured and are not limiting.

### 7.5 Physical delay alignment

Each tag has a physical time constant or delay. The active value can be:

```text
x_tilde_i(t) = EMA(x_i[t-2*tau_i:t], span=tau_i)
```

Blast and oxygen can use approximately one hour, PCI approximately 1.5 to 3 hours, charged coke approximately 5 to 8 hours, hot-metal temperature greater than 8 hours, and alkali or zinc inventory multiple days. Plant-calibrated delays override literature priors.

### 7.6 Detection of the unchanged-input shortfall

The apparatus determines:

```text
shortfall_target = max(0, P* - P(t))
shortfall_reference = max(0, median(P[t-84h:t-12h]) - P(t))
```

An unchanged-input shortfall is present when the shortfall exceeds a threshold while selected manipulated inputs remain in their required-production-conditioned bands or below a change tolerance.

For each disturbance and response tag, the apparatus compares the lag-active value against its band and the earlier rolling reference. An estimated physical production impact or bounded local learned sensitivity ranks the candidate causes.

### 7.7 Reduced-order physics and learned correction

The physical state can include flame temperature, tuyere oxygen/carbon balance, bosh gas, Rist relation, pressure-drop split, top-gas utilization, cohesive-zone proxy, condensation load, hot-metal temperature, silicon, and physical production ceilings.

A forecast residual may use features known at forecast time. A decision residual is restricted to causal parents approved for setpoint analysis. The decision residual is disabled if the effect is not identifiable.

### 7.8 Sensor anchoring and derivative preservation

At baseline:

```text
b0 = y_measured - f_physics(u0)
y_counterfactual = f_physics(u0 + delta_u) + b0
```

The bias remains constant over the counterfactual, maintaining agreement with the sensor baseline while preserving a physics-derived response.

A smooth limit may be:

```text
S(x) = U + s*tanh((x-U)/s), x > U
S(x) = L - s*tanh((L-x)/s), x < L
S(x) = x,                    otherwise
```

Pressure balance is reconciled such that total pressure drop equals upper plus lower pressure drop. With zero input change, the simulated output equals the baseline.

### 7.9 Joint-density envelope and physical ceilings

A regularized covariance is fitted on qualified historical manipulated vectors. The candidate distance is:

```text
D_M(u) = sqrt((u-mu)^T * inverse(Sigma_reg) * (u-mu))
```

The candidate must also satisfy a local Mahalanobis step distance from the current point. The apparatus evaluates at least three physical ceilings selected from tuyere stoichiometry, pressure-drop permeability, gas flooding, top-gas thermal/dewpoint, and hearth drainage. The lowest is reported as binding.

### 7.10 Withholding and engineering-trial dossier

If a candidate is outside the envelope, trust region, causal-identifiability status, freshness requirement, or physical ceiling, no routine setpoint is output. Instead, the apparatus produces a management-of-change dossier containing moved variables, distances, threshold, binding ceiling, evidence class, model version, and required human sign-offs.

### 7.11 Audit and later execution confirmation

An acceptance, rejection, note, calibration sign-off, or dossier action is stored in an append-only cryptographic hash chain. Confirmation that a plant later executed an accepted action is stored in a separate field and does not change the original hash.

## 8. Example implementation

The method has been demonstrated on a public running-plant blast-furnace archive containing 29,602 hourly sensor rows and 16,589 cast silicon analyses. The archive is used to demonstrate time alignment, pressure identity, circumferential wall-temperature asymmetry, operating-regime qualification, and walk-forward model validation. The public series lacks measured hot-metal tonnes, PCI, coke rate, top-gas CO, and hot-metal temperature; those absent quantities are therefore marked unavailable, assumption-dependent, response-only, or not-testable and are not represented as measured.

At a qualified on-wind hour, a combined increase in blast, oxygen, and hot-blast temperature can exceed the regularized Mahalanobis envelope. In that case, the apparatus blocks routine advisory output and produces an engineering-trial dossier. With no manipulated-input change, sampled records show zero simulated drift and exact pressure-split reconciliation.

A comparative test of the saturation function on a nominal pressure-drop interval of 1.20 to 1.70, with softness equal to 0.08 times that interval, showed that hard clipping sets the local derivative to zero at 1.72, while the claimed saturation returns 1.7185 with a local derivative of about 0.79. At 1.74 the soft output is 1.7305 with a local derivative of about 0.42, whereas hard clipping remains 1.7000 with derivative zero. This is the technical effect relied on for non-zero response sensitivity at a furnace operating limit.

Preferred transport-delay priors, replaced by plant-calibrated delays when identified, are: top pressure 0.6 hour; blast moisture 0.8 hour; blast volume and oxygen 1.0 hour; hot-blast temperature 1.5 hours; pulverized coal 2.5 hours; sinter reduction-degradation index 4.5 hours; ore/coke ratio and burden iron 6.0 hours; charged coke rate 6.5 hours; coke strength after reaction 7.0 hours; and alkali and zinc inputs 12 hours.

## 9. Best method of performing the invention

The best method known at filing is:

1. receive immutable read-only historian records;
2. enforce one causal role per tag;
3. exclude unqualified furnace regimes;
4. form target bands from qualified P18/P50/P82 cohorts;
5. apply exponential kernels using plant-calibrated delays;
6. step reduced-order physics and bounded causal-parent residuals;
7. hold a measured baseline anchor constant;
8. apply monotonic soft saturation;
9. enforce conservation identities;
10. apply a 99-percent regularized Mahalanobis envelope and local trust region;
11. arbitrate among five physical ceilings; and
12. record the advisory and human decision in a cryptographic audit chain.

## 10. Industrial applicability

The invention is applicable to iron and steel plants operating blast furnaces and can be installed in an industrial DMZ with read-only access to the plant historian. It can improve reliability of physical shortfall diagnosis, reduce unsupported setpoint trials, and support shadow-mode process improvement without creating a plant control path.

## 11. Claims

The following claims are the claims of this complete specification. Bracketed applicant and inventor fields on the cover must be completed, and a registered Indian patent agent must settle Forms 1, 3, 5, and 26, before filing. This draft is not legal advice and is not a filed application.

## I/We claim:

1. **A method for identifying an unmeasured physical cause of a hot-metal production shortfall in an iron blast furnace, performed by a furnace-monitoring apparatus coupled to a plurality of blast-furnace sensors, the method comprising:**

   receiving, through an industrial historian interface restricted to read services, time-series physical measurements comprising manipulated furnace inputs, material disturbances, furnace state responses, and hot-metal production or quality outcomes;

   assigning each physical measurement to one mutually exclusive causal role comprising manipulated input, disturbance, furnace state response, outcome, or derived latent state;

   for a required hot-metal production rate, selecting a historical cohort of qualified on-wind furnace intervals having production within a tolerance of the required hot-metal production rate and pressure drop below a permeability criterion, and generating from the historical cohort a lower operating value, center operating value, and upper operating value for each of a plurality of furnace tags;

   shifting at least one of the lower, center, or upper operating values according to a physical furnace sensitivity and a difference between the required hot-metal production rate and production represented by the historical cohort, thereby producing a production-conditioned operating band;

   converting each of the plurality of furnace tags at a query time into a lag-active physical value by applying a respective temporal kernel representing a gas-flow delay, injectant delay, descending-burden delay, thermal delay, or accumulated-inventory delay within the blast furnace;

   detecting an unchanged-input shortfall in which a measured or reconciled production value is below the required hot-metal production rate or below a preceding rolling production reference while a selected plurality of manipulated inputs remain within their corresponding production-conditioned operating bands;

   in response to the unchanged-input shortfall, identifying an unmeasured furnace condition as the physical cause by a deviation of the lag-active physical value of a measured disturbance or furnace state response from both its production-conditioned operating band and a preceding rolling reference of the corresponding furnace tag, the unmeasured furnace condition being at least one of an alkali or zinc accumulation, a burden-permeability loss, a cohesive-zone shift, a circumferential gas maldistribution, or a hearth-drainage restriction;

   testing a candidate recovery with a reduced-order blast-furnace material-and-energy calculation, including calculating an additive anchor bias between a measured sensor response and a free-running physical-model output at a baseline state, holding said additive anchor bias fixed during the test, and enforcing a physical identity in which a simulated total furnace pressure drop equals an upper-furnace pressure drop plus a lower-furnace pressure drop;

   evaluating the counterfactual recovery trajectory against a joint multi-parameter historical operating-density envelope, a step trust region, and a plurality of physical blast-furnace productivity ceilings; and

   displaying, through an operator advisory interface, either (i) a recovery advisory when the counterfactual recovery trajectory remains within said envelope, trust region, and productivity ceilings, or (ii) an engineering-trial dossier while withholding the recovery advisory when at least one of said envelope, trust region, or productivity ceilings is violated.

2. The method as claimed in claim 1, wherein the industrial historian interface permits only an HTTP read operation, an OPC-UA Read service, an OPC-UA HistoryRead service, or reading an immutable historian-export file, and rejects historian write, OPC method-call, SQL mutation, programmable-logic-controller write, distributed-control-system setpoint, and furnace-actuator operations.

3. The method as claimed in claim 1, wherein, when the counterfactual recovery trajectory uses a manipulated-input vector equal to a current manipulated-input vector, each anchored simulated response equals the corresponding measured baseline response within a numerical tolerance.

4. The method as claimed in claim 1, wherein the reduced-order blast-furnace physical model applies a monotonic continuously differentiable saturation function outside a nominal physical interval, thereby retaining a non-zero response sensitivity at a furnace operating limit.

5. The method as claimed in claim 1, wherein the joint multi-parameter historical operating-density envelope is a regularized Mahalanobis ellipsoid fitted to qualified on-wind manipulated-input vectors and the step trust region is a Mahalanobis distance from a current manipulated-input vector.

6. The method as claimed in claim 1, wherein the plurality of physical blast-furnace productivity ceilings includes at least three selected from tuyere oxygen-carbon stoichiometry, packed-bed pressure-drop permeability, bosh-gas flooding or fluidization, top-gas thermal or acid-dewpoint condition, and hearth coke-bed drainage, and wherein a lowest ceiling is displayed as a binding ceiling.

7. The method as claimed in claim 1, further comprising classifying each generated result as measured-anchored, physics-estimated, assumption-dependent, response-only, not-qualified, not-identifiable, or not-testable, and withholding an absolute latent-state value while continuing to display a differential response when a required sensor is unavailable.

8. The method as claimed in claim 1, further comprising storing an operator acceptance or rejection in an append-only cryptographic hash chain stamped with a model version and storing a later indication of plant execution in a separate post-hoc field without altering the operator acceptance or rejection.

9. **A blast-furnace advisory apparatus comprising:**

   a plurality of industrial data inputs receiving physical blast-furnace sensor measurements;

   a read-only historian interface configured to receive said measurements while lacking a write service to a historian, programmable logic controller, distributed control system, or furnace actuator;

   one or more processors; and

   a memory storing executable instructions configured to cause the apparatus to perform the method of any one of claims 1 to 8.

10. The blast-furnace advisory apparatus as claimed in claim 9, further comprising a regime gate configured to suppress a recovery advisory during off-wind operation, banking, blow-in, shutdown, maintenance, stale-source operation, severe instability, or an unqualified regime.

## 12. Abstract

An industrial read-only advisory apparatus diagnoses blast-furnace production shortfalls when operator settings appear unchanged. Sensor tags are partitioned into manipulated inputs, disturbances, furnace responses, outcomes, and latent states. For a required hot-metal rate, qualified historical periods form a production-conditioned operating band for each tag. Tag values are convolved with respective furnace transport-delay kernels and compared with both the operating bands and preceding rolling references. Ranked deviations identify hidden physical causes and estimated production loss. A reduced-order physics and learned-residual twin is anchored to measured sensor values using a fixed bias and smooth saturation preserving response sensitivity. Candidate recovery actions are tested against a joint-density operating envelope, a local trust region, causal-identifiability status, and multiple physical productivity ceilings. Unsupported actions are withheld and converted into an engineering-trial dossier. Human decisions and later plant execution are recorded separately in a tamper-evident audit chain.

