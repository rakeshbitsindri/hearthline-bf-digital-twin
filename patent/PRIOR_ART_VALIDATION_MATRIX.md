# Prior-Art Validation Matrix

This is a technical landscape review, not a legal opinion or a substitute for a professional patentability/FTO search. Google Patents status labels are not legal conclusions. Dates and family status must be confirmed in official registers.

## 1. Executive validation result

The original broad proposition, “blast-furnace digital twin combining physics and ML to diagnose root cause and recommend corrective action,” is **not novel enough to claim broadly**.

The strongest references are:

- **EP4154105A1 / EP4154105B1 (Tata Consultancy Services)**: self-organizing cyber-physical industrial plant monitoring with hybrid physics/data models, time-lag identification, regime analysis, real-time root-cause analysis, hidden-variable soft sensors, and corrective actions, including steel and blast-furnace examples.
- **CN122654903A (Central South University)**: blast-furnace root-cause analysis combining expert physical knowledge, causal structure, hierarchical lag estimation, Granger causality, and confidence-scored causal paths.
- **US11899527B2 (Caterpillar)**: reduced-order digital-twin anomaly detection and root-cause identification by comparing measured data with fault models.
- **US12321163B2 / US20230057291A1 (Daicel)**: causal production-facility prediction using historical process data and residence-time alignment for explanatory and response variables.
- **CN109918702A (Shanghai Jiao Tong University)**: blast-furnace hybrid neural-network/mechanistic mass/heat constrained multi-objective optimization.

Accordingly, a defensible filing should emphasize the **specific combination and sequence**, not its generic components:

1. required-production-conditioned empirical/physical Golden Bands;
2. physical lag-active comparison against both those bands and an excluded-recent-window rolling reference;
3. detection specifically during an unchanged-manipulated-input interval;
4. fixed baseline sensor-anchor bias plus exact conservation identities and zero-change identity;
5. derivative-preserving soft saturation;
6. candidate gating by both a joint-density envelope/local trust region and multiple named furnace production ceilings; and
7. automatic conversion of a blocked candidate into an MoC trial dossier and separate execution-confirmation ledger.

Even this combination faces a **material obviousness/inventive-step risk** because an examiner can combine TCS, Central South University, Daicel, AspenTech, and known Mahalanobis techniques.

## 2. Closest patent and non-patent references

| Ref. | Publication / source | Priority / publication | Applicant | Relevant disclosure | Risk |
|---|---|---|---|---|---|
| R1 | [EP4154105A1](https://patents.google.com/patent/EP4154105A1/en), granted as EP4154105B1 | priority 19 May 2020; A1 29 Mar 2023; B1 2 Jul 2025 | Tata Consultancy Services Ltd | Industrial cyber-physical/digital-twin platform; physics, ML, and hybrid models; time-lag identification; regime shifts; hidden variables; real-time root-cause analysis; operator guidance and corrective actions; steel/blast-furnace use cases. | **Very high** |
| R2 | [CN122654903A](https://eureka.patsnap.com/patent/CN122654903A) | filed 4 Jun 2026; published 28 Aug 2026 | Central South University | Blast-furnace abnormal-condition root cause using expert physical knowledge, Granger causality, adaptive group lasso, hierarchical lag search, physical lag priors, path search, and confidence scoring. | **Very high** |
| R3 | [US11899527B2](https://patents.google.com/patent/US11899527B2/en) / US20230168961A1 | priority 30 Nov 2021; A1 1 Jun 2023; B2 13 Feb 2024 | Caterpillar Inc. | Sensor-fed reduced-order digital twin; anomaly from model/measured residual; multiple fault models; select closest fault output as root cause. | High |
| R4 | [US12321163B2](https://patents.google.com/patent/US12321163B2/en) / US20230057291A1 | filed 4 Feb 2021; A1 23 Feb 2023; B2 3 Jun 2025 | Daicel Corporation | Causality information in a production-facility prediction model; positive/negative direction; timing alignment using residence time; optimum manufacturing conditions. | High |
| R5 | [CN111831719A](https://patents.google.com/patent/CN111831719A/zh) | priority 22 Jul 2020; published 27 Oct 2020 | Shandong Iron and Steel Co. | Blast-furnace online data, operation/raw-material division, digital/mechanistic model corrected by association analysis, deep learning and genetic-algorithm control. | High |
| R6 | [CN109918702A](https://patents.google.com/patent/CN109918702A/zh) | priority 3 Jan 2019; published 21 Jun 2019 | Shanghai Jiao Tong University | Blast-furnace burden/operation hybrid neural + mass/heat constrained multi-objective optimization for fuel, emissions, cost, and metal quality. | High |
| R7 | [WO2021076760A1](https://patents.google.com/patent/WO2021076760A1/en) | priority 18 Oct 2019; published 22 Apr 2021 | Aspen Technology Inc. | Automated model development from historical plant tags; informative moves; multivariable predictive control; model growth/calibration; steady-state optimization. | Medium-high |
| R8 | [EP4567667A1](https://patents.google.com/patent/EP4567667A1/en) | priority 5 Dec 2023; published 11 Jun 2025 | British Telecommunications PLC | Modular digital twin with learning and differentiable physics blocks, residual block, sensor data, explanations, and control output. | High for generic hybrid twin |
| R9 | [WO2024141260A1](https://patents.google.com/patent/WO2024141260A1/en) | priority 27 Dec 2022; published 4 Jul 2024 | Siemens Schweiz AG | Real-time sensor-based digital-twin calibration using error gradient and candidate parameter optimization. | Medium-high |
| R10 | [US20170286572A1](https://patents.google.com/patent/US20170286572A1/en) | priority 31 Mar 2016; published 5 Oct 2017 | General Electric Co. | General digital twin of a twinned physical system using sensor/operating data. | Medium |
| R11 | [US20240337486A1](https://patents.google.com/patent/US20240337486A1/en) | publication 10 Oct 2024 | — | Learned rules for sensor-reading correction and missing-data enhancement. | Medium |
| R12 | [US6486661B2](https://patents.google.com/patent/US6486661B2/en) | priority 14 Feb 2001; expired | — | Generic sensor bias-drift compensation. | Low-medium |
| R13 | [US9799110B2](https://patents.google.com/patent/US9799110B2/en) / US20160148365A1 | JP priority 29 Jul 2013; A1 26 May 2016; B2 24 Oct 2017 | JFE Steel Corp. | Blast-furnace abnormality detection from multiple tuyere images using PCA and distance from normal subspace. | Medium |
| R14 | [CN1403593A](https://patents.google.com/patent/CN1403593A/en), granted CN1224720C | priority 17 Oct 2002; published 19 Mar 2003 | Zhejiang University | Online blast-furnace data, expert intelligent control, fault charts, foreman guidance, best thermal-state operation. | High for broad BF expert-system claims |
| R15 | [CN1038146C](https://patents.google.com/patent/CN1038146C/zh) | older Chinese BF expert-system family | — | Sensor collection, fuzzy expert knowledge, furnace-state and abnormal-condition prediction/control. | High for broad BF diagnosis |
| R16 | [US20060230018A1](https://patents.google.com/patent/US20060230018A1/en) | priority 8 Apr 2005; published 12 Oct 2006; abandoned | Caterpillar Inc. | Mahalanobis distance and genetic algorithm for variable selection and separation of normal/abnormal data. | Medium for generic Mahalanobis claims |
| R17 | [US20180283815A1](https://patents.google.com/patent/US20180283815A1/en) / US10663238B2 | priority 28 Mar 2017; A1 4 Oct 2018 | Honeywell UOP LLC | Historical/current plant data, operating boundaries, relationships among operating parameters, target optimization, maldistribution detection. | Medium-high |
| R18 | [US10935962B2](https://patents.google.com/patent/US10935962B2/en) / US20170153630A1 | priority 30 Nov 2015 | National Cheng Kung University | Two-phase production yield-loss root-cause ranking by process tool/stage and parameters. | Medium |
| R19 | Caers and Eskanlou, reverse-flotation causal study cited in `knowledge/09-confounding-and-causality.md` | 2026 | Academic paper | Demonstrates predictive/causal disagreement, backdoor, g-computation, DML, lag, and non-identifiability. | High for generic causal-audit concepts |
| R20 | Blast-furnace causality by convergent cross mapping, DOI [10.1080/03019233.2022.2065447](https://doi.org/10.1080/03019233.2022.2065447) | 2022 | Academic paper | Causal relationship analysis and blast-furnace state prediction. | Medium-high |

## 3. Element-by-element challenge of proposed independent claim

| Proposed element | Closest teaching | Anticipated examiner position | Proposed distinction |
|---|---|---|---|
| Read-only sensor/historian acquisition | R1, R5, R7, R14 | Routine plant data acquisition; read-only choice may be obvious security design. | Retain as safety architecture, but do not rely on it alone for novelty. |
| Mutually exclusive causal-role assignment | R4 causal explanatory/response variables; R1 model types and plant variables | Variable classification is known. | Require five roles and use the roles to control attribution, absolute-value withholding, and decision-model feature eligibility. |
| Production-target-conditioned empirical bands | R17 operating boundaries; R4 setting/management ranges; R7 steady-state targets | Historical target ranges are known. | Require permeability-qualified blast-furnace cohorts plus physics sensitivity shifting for requested hot-metal tonnage across all roles. Still medium risk. |
| Per-tag physical lag convolution | R1 time-lag identification; R2 hierarchical lag with physical priors; R4 residence-time alignment | Lags in process plants and blast furnaces are known. | Require heterogeneous gas/injectant/burden/inventory kernels and dual comparison against Golden Band plus excluded-recent rolling reference during an unchanged-input interval. |
| Detect shortfall while manipulated inputs stay in band | R1 performance dip/root cause; R2 abnormal furnace root cause | Broad performance-dip diagnosis is known. | Central narrowing feature. Explicitly require unchanged manipulated inputs and rank disturbance/state-response deviations. |
| Sensor-anchor bias held fixed over counterfactual | R3 residual anomaly; R9 real-time calibration; R11 sensor correction | Sensor/model reconciliation is known. | Require fixed baseline additive anchor, exact pressure-conservation identity, and zero-change output identity. Do not claim generic calibration. |
| Smooth saturation preserving nonzero derivative | Generic numerical methods; R8 differentiable physics | Soft clipping and differentiability are known mathematically. | Claim only in combination with fixed anchor and conservation-consistent blast-furnace counterfactual. Avoid standalone claim. |
| Predictive vs causal decision residual | R4 causal model; R19 causal-estimation literature | Causal feature restriction is known. | Treat as dependent limitation; not likely a standalone inventive concept. |
| Mahalanobis envelope and local trust region | R16; widespread multivariate process control | Mahalanobis anomaly envelopes are old. | Require simultaneous joint-density envelope, local step distance, and five physical furnace ceilings, leading to automatic MoC dossier rather than controller output. |
| Five-ceiling binding arbiter | BF physics and optimization prior art such as R6 | Individual physical constraints are known. | Claim explicit lowest-ceiling arbitration combined with density/trust and unchanged-sheet attribution. |
| MoC dossier and audit/execution split | Governance/audit techniques | Likely administrative/business-method objection. | Keep as dependent claim. Tie to technical suppression and model/envelope evidence. |

## 4. Validation of four proposed invention families

### Family A: Lag-convolved target-band attribution

**Status: AMBER / potentially patentable only when narrowly combined.**

R1 and R2 are severe references because they teach industrial/blast-furnace root-cause analysis, time lag, physical knowledge, regime analysis, and corrective guidance. R4 teaches residence-time alignment and causal direction in a production facility. The likely defensible distinction is not “lag-aware root cause” alone, but the sequence of:

- target-production-conditioned permeability-qualified cohort bands;
- unchanged manipulated-input interval;
- per-tag physical convolution;
- dual Golden-Band and prior rolling-reference comparison; and
- production-loss attribution by causal role.

### Family B: Sensor-anchored derivative-preserving hybrid twin

**Status: AMBER-GREEN / strongest technical nucleus if experimental effects are documented.**

R3, R8, R9, R11, and R12 cover digital-twin residuals, physics/learning blocks, calibration, and sensor correction. None identified in this search expressly teaches the fixed baseline anchor held invariant across a counterfactual together with zero-change identity, exact pressure-split conservation, and smooth nonzero-derivative saturation in a blast furnace.

An application should include comparative experiments:

- hard clip versus soft saturation response near a limit;
- free-running versus anchored pressure-drop error;
- zero-change drift before and after the method; and
- conservation residual before and after reconciliation.

### Family C: Envelope/ceiling/MoC gate

**Status: AMBER / obviousness risk.**

Mahalanobis envelopes, MPC constraints, blast-furnace hybrid optimization, and physical constraints are known separately. The narrow combination of two Mahalanobis tests, five named BF ceilings, causal-identifiability status, and automatic conversion from routine advisory to a technical trial dossier may survive as a dependent or second-family claim, but a generic optimization-envelope claim is weak.

### Family D: Evidence/capability classifier

**Status: RED-AMBER / likely abstract, obvious, or presentation-of-information risk alone.**

Claim only as a technical dependent limitation that physically suppresses computation/output of unsupported absolute latent states while retaining differential response. Do not lead with labels or user-interface presentation.

## 5. Public-disclosure risk

The source repository and interactive demonstration were public on **10 November 2026**.

- The USPTO states an inventor-originated public disclosure can fall within the one-year AIA grace period. The factual authorship/derivation of the disclosure must be documented.
- The USPTO also warns such pre-filing disclosure may preclude foreign patenting.
- India generally applies absolute novelty, subject to narrow statutory exceptions that must be analyzed by Indian counsel. Public GitHub availability is a serious India/PCT risk.
- If any inventor is resident in India, Section 39 and Form 25 must be considered before an outside-India filing.

## 6. Search limitations

This review used keyword and classification-oriented searches of Google Patents, public patent aggregators, official USPTO/IP India materials, and project literature. It is not:

- a professional classification/subclassification search;
- a prosecution-history or claim-construction opinion;
- a freedom-to-operate opinion;
- a legal-status opinion;
- a search of unpublished applications; or
- a substitute for searches in USPTO Patent Public Search, Espacenet, WIPO Patentscope, Indian Patent Advanced Search System, CNIPA, KIPRIS, J-PlatPat, and commercial semantic databases.

