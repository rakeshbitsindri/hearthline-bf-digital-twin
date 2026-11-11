# THE PATENTS ACT, 1970

# COMPLETE SPECIFICATION

## [See Section 10 and Rule 13]

## Title

**LAG-AWARE ADVISORY DIGITAL TWIN FOR DIAGNOSING BLAST-FURNACE PRODUCTION SHORTFALLS**

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

Claims for India are provided in `INDIA_CLAIMS_DRAFT.md` and shall be inserted here after review by a registered Indian patent agent.

## 12. Abstract

An industrial read-only advisory apparatus diagnoses blast-furnace production shortfalls when operator settings appear unchanged. Sensor tags are partitioned into manipulated inputs, disturbances, furnace responses, outcomes, and latent states. For a required hot-metal rate, qualified historical periods form a production-conditioned operating band for each tag. Tag values are convolved with respective furnace transport-delay kernels and compared with both the operating bands and preceding rolling references. Ranked deviations identify hidden physical causes and estimated production loss. A reduced-order physics and learned-residual twin is anchored to measured sensor values using a fixed bias and smooth saturation preserving response sensitivity. Candidate recovery actions are tested against a joint-density operating envelope, a local trust region, causal-identifiability status, and multiple physical productivity ceilings. Unsupported actions are withheld and converted into an engineering-trial dossier. Human decisions and later plant execution are recorded separately in a tamper-evident audit chain.

