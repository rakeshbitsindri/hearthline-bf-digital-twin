# Patentability Assessment and Provisional Patent Disclosure

## 1. Executive Verdict: Can We File a Patent for This Use Case?

**Yes, with properly scoped method and system claims.** While you cannot patent textbook blast-furnace physics equations (such as AIST/Geerdes flame temperature, Rist mass balance, or Ergun pressure drop) or generic machine-learning prediction of hot-metal silicon, **you CAN patent the specific computer-implemented diagnostic, sensor-reconciliation, and safety-gating architecture** we built to solve the **"Unchanged-Operating-Sheet Production Shortfall"** use case.

In patent law (United States 35 U.S.C. 101 *Alice/Mayo* framework, European Patent Convention Art. 52(2)/(3), and India Patent Act Sec. 3(k)), a software-implemented method is **patent-eligible** when it is tied to a concrete industrial process and produces a **specific technical effect** (such as isolating hidden physical state degradation across multi-hour transport lags, reconciling sensor drift while preserving conservation identities, or hardware/protocol-blocking unsafe out-of-envelope setpoints).

### Critical Public-Disclosure Timing Notice

1. **United States (12-Month Grace Period)**: Under 35 U.S.C. 102(b)(1) (AIA), an inventor has **12 months from the first public disclosure** (such as publishing a public GitHub repository or web demo) to file a US Provisional or Non-Provisional Patent Application. Since the public repository was pushed on **10 November 2026**, the US filing deadline is **10 November 2027**.
2. **International / PCT / EPO / India / China (Absolute Novelty)**: Most non-US jurisdictions require filing **before** public disclosure. If you intend to file outside the US (or via PCT), you should:
   - File a **US Provisional Patent Application** immediately (costs $65-$160 USPTO micro/small-entity fee) to lock in today's priority date, **and**
   - Temporarily switch the GitHub repositories (`rakeshbitsindri.github.io` and `hearthline-bf-digital-twin`) to **Private** until the provisional patent number is issued.

---

## 2. Prior-Art Landscape and How Hearthline Differentiates

To survive USPTO / EPO examination under 35 U.S.C. 102 (novelty) and 103 (non-obviousness), claims must distinguish over four categories of existing prior art:

| Prior Art Category | Representative Systems / Patents | What Prior Art Does | How Hearthline Is Structurally Different (Our Novelty) |
|---|---|---|---|
| **1. OEM Rule-Based & Heat/Mass Balance Expert Systems** | Paul Wurth BFXpert, Primetals VAiron, Thyssenkrupp THYBAS, Nippon Steel VENUS [C] | Compute static Rist/heat balances and trigger threshold alarms on individual tags. | Prior systems use static alarm bands and open-loop physics. They do not dynamically shift a 41-tag Golden Range cohort by required daily tonnage combined with lag-convolved historical root-cause attribution when manipulated setpoints are constant. |
| **2. Pure ML / Deep Learning Silicon & Tonnage Predictors** | Published LSTM, XGBoost, and PINN papers (2018-2025) [P] | Predict next-cast silicon `[Si]` or HMT using raw lagged sensor windows and explain fits with same-hour SHAP. | Same-hour SHAP on predictive models attributes credit to whichever input moved last (blast) and learns operator feedback confounding. Hearthline separates predictive vs. causal decision models and convolves each parameter by its physical residence-time kernel before attributing shortfalls. |
| **3. Granger-Causal & Graph Root-Cause Patents** | CN122654903A (Granger causality + expert graph for BF) [P] | Proposes statistical Granger-causality edges between furnace sensors to trace anomalies. | Does not perform baseline-anchored bias reconciliation with derivative-preserving soft saturation, does not condition Golden Ranges on target tonnage, and does not gate inverse setpoints via a joint Mahalanobis ellipsoid + 5-ceiling arbiter that auto-generates an MoC trial dossier. |
| **4. Multivariate Statistical Monitoring** | JFE Steel PCA Q-statistic / Hotelling T2 hanging predictors [P] | Flags correlation-breakdown anomalies 1 to 2.5 hours before a slip/hang. | Detects that correlation broke, but does not quantify per-parameter tonnes/day production risk against a target-conditioned Golden Band or solve for constrained recovery setpoints. |

---

## 3. Four Core Patentable Inventions in Hearthline

### Invention 1 (Primary Independent Claim): Lag-Convolved Multi-Role Observability and Target-Conditioned Golden-Band Attribution Engine

- **Industrial Problem Solved**: When daily hot-metal production drops while all operator-manipulated setpoints (`Fb`, `Th`, `Fo`, `Pt`, `R`) remain unchanged, conventional trend screens show "normal operation" and standard ML feature-attribution misidentifies the cause because furnace transport lags span three orders of magnitude (`0.6h` top pressure, `1.0h` blast/oxygen, `2.5h` PCI, `6.5h` charged coke, `12h+` alkali recirculation).
- **Technical Mechanism**:
  1. **Strict Causal Role Partitioning**: Every sensor tag is assigned to one of five mutually exclusive causal classes: `manipulated`, `disturbance`, `state_response`, `outcome`, or `derived_latent`.
  2. **Target-Tonnage-Conditioned Golden Band Synthesis**: Given a desired production rate $P^*$, the engine filters historical on-wind operating hours where permeability resistance stayed below the 85th percentile and output fell within $P^* \pm \Delta P$, extracts empirical inter-quantile bounds $[Q_{0.18}, Q_{0.82}]$, and shifts them by a stoichiometric/Ergun sensitivity vector $\mathbf{s}_i \cdot (P^* - P_{\text{cohort}})$ to form a live Golden Band $[L_i(P^*), U_i(P^*)]$ for all 41 tags.
  3. **Lag-Kernel Convolution**: For any query timestamp $t$ (live or historical), each parameter $x_i$ is convolved over $[t - 2\tau_i, t]$ using an exponential residence-time filter parameterized by its physical transport delay $\tau_i$ to yield an active effective value $\tilde{x}_i(t)$.
  4. **Dual-Reference Shortfall Attribution & 7-Gate Protocol**: Each parameter's lag-active value $\tilde{x}_i(t)$ is evaluated simultaneously against $[L_i(P^*), U_i(P^*)]$ and a preceding 72-hour rolling furnace baseline $[t-84\text{h}, t-12\text{h}]$, converting excursions into directional production-loss estimates ($\text{tHM/day}$) and stepping through a 7-gate observability decision tree that isolates hidden disturbances and azimuthal wall asymmetry (`Tp1..Tp10`) when manipulated inputs are invariant.

### Invention 2: Sensor-Anchored Bias-Preserving Hybrid Digital Twin with Derivative-Preserving Soft Saturation

- **Industrial Problem Solved**: First-principles furnace equations exhibit systematic offset bias relative to plant instruments (for example, uncalibrated Ergun pressure drop over-predicting measured $\Delta P$ by 20-25%), while standard numerical clamping (`clip(x, min, max)`) forces partial derivatives to zero at clip boundaries, severing cross-parameter coupling during high-load operation.
- **Technical Mechanism**:
  1. **Monotone Hyperbolic-Tangent Soft Saturation**: All internal state equations replace hard boundary clipping with a $C^\infty$-smooth saturation operator:
     ```
     S(x; L, U, s) = U + s * tanh((x - U) / s)   for x > U
                   = L - s * tanh((L - x) / s)   for x < L
                   = x                           for L <= x <= U
     ```
     This guarantees $\partial S / \partial x > 0$ everywhere, preserving live cross-parameter sensitivity even when a state approaches its thermal or flooding limit.
  2. **Baseline Sensor Reconciliation with Exact Conservation Identities**: At baseline state $\mathbf{x}_0$, the engine computes free-running physics outputs $\mathbf{f}_{\text{phys}}(\mathbf{x}_0)$, calculates the per-sensor anchor bias $\mathbf{b}_0 = \mathbf{y}_{\text{meas}}(t_0) - \mathbf{f}_{\text{phys}}(\mathbf{x}_0)$ across all measured response channels, and applies $\mathbf{b}_0$ invariant to counterfactual states $\mathbf{f}_{\text{phys}}(\mathbf{x}_0 + \Delta\mathbf{x}) + \mathbf{b}_0$ while enforcing exact additive conservation identities ($\Delta P = \Delta P_u + \Delta P_l$ and $\Delta P_h = \Delta P + \Delta P_t$).
  3. **Zero-Drift Identity**: Guarantees by construction that $\|\mathbf{y}_{\text{sim}}(\Delta\mathbf{u}=0) - \mathbf{y}_{\text{base}}\| = 0$ across all 41 tags while blending physics deltas with lag-aligned Ridge residual Jacobians for non-zero moves.

### Invention 3: Confounding-Proof Inverse Setpoint Optimizer with Mahalanobis Density Ellipsoid, 5-Ceiling Arbiter, and Automated MoC Dossier Generation

- **Industrial Problem Solved**: Inverting a regression model trained on historical blast-furnace logs recommends the operator's reactive control policy rather than causal setpoints, and optimizing inside a simple min/max hypercube drives the furnace into unobserved, unsafe multi-parameter corners.
- **Technical Mechanism**:
  1. **Dual-Model Causal Separation**: Enforces a structural separation between the predictive forecast model (permitted to consume outcome descendants such as top-gas ratios and prior cast silicon) and the decision model (restricted to causal parents).
  2. **Joint Mahalanobis Ellipsoid & Step Trust Region**: Fits a regularized precision matrix $\boldsymbol{\Sigma}_{\text{reg}}^{-1}$ on historical on-wind manipulated vectors and constrains candidate setpoint vectors $\mathbf{u}$ to satisfy both $(\mathbf{u} - \boldsymbol{\mu})^\top \boldsymbol{\Sigma}_{\text{reg}}^{-1} (\mathbf{u} - \boldsymbol{\mu}) \le \chi^2_{p, 0.99}$ and step-norm $(\mathbf{u} - \mathbf{u}_0)^\top \boldsymbol{\Sigma}_{\text{reg}}^{-1} (\mathbf{u} - \mathbf{u}_0) \le r_{\text{trust}}^2$.
  3. **Five-Ceiling Binding Arbiter & MoC Dossier Trigger**: Evaluates candidate moves against five concurrent physical ceilings (tuyere oxygen stoichiometry, Ergun permeability $\Delta P$, bosh-gas flooding factor, top-gas acid dewpoint, and hearth coke-bed drainage). Whenever a target requires stepping outside the Mahalanobis ellipsoid or fails causal identifiability, the engine blocks routine setpoint issuance and automatically generates a SHA-256 hash-chained **Management-of-Change (MoC) engineering trial dossier**.

### Invention 4: Epistemic Capability Classifier & Operating-Regime Suppression Gate

- **Industrial Problem Solved**: Showing absolute flame temperature (`RAFT`) or hot-metal temperature (`HMT`) when injectant/moisture sensors are missing—or during banked/reduced-wind hours—misleads operators with fabricated numbers.
- **Technical Mechanism**:
  1. Dynamically evaluates the blast-wind fraction $F_b(t) / \text{median}(F_b)$ and the dependency graph `PHYSICS_REQUIRES[k]` at every timestamp.
  2. Classifies each output into `measured_anchored`, `physics_estimated`, `assumption_dependent`, `response_only`, or `not_qualified`.
  3. Automatically withholds absolute display (`not computable`) while continuing to serve differential counterfactual deltas ($\Delta y$) when in `response_only` mode.

---

## 4. Draft Independent Claims (Ready for Patent Counsel Review)

### Claim 1 (Computer-Implemented Method for Blast Furnace Shortfall Diagnosis and Advisory Control)

A computer-implemented method for diagnosing production shortfalls and generating safety-gated operational advisories in an metallurgical shaft furnace, the method comprising:
1. ingesting, via a hardware-enforced read-only historian interface that rejects write, remote-procedure-call, and query-mutation operations, a plurality of time-series sensor channels from a blast furnace and partitioning said channels into distinct causal roles comprising manipulated inputs, material disturbances, furnace state responses, outcome metrics, and derived latent states;
2. generating, for a specified target hot-metal production rate, a production-conditioned golden operating band for each channel of the plurality of sensor channels by extracting an empirical inter-quantile distribution from a historical cohort of on-wind furnace hours satisfying a permeability ceiling near the specified target hot-metal production rate and shifting said distribution by a coupled stoichiometric and packed-bed pressure-drop sensitivity gradient;
3. convolving each channel over a trailing temporal window using a channel-specific residence-time kernel parameterized by a physical transport delay of that channel within the blast furnace, wherein said transport delays span from sub-hour gas-phase transit to multi-hour burden-descent and multi-day alkali-recirculation time constants;
4. in response to detecting a production shortfall during an interval in which the manipulated inputs remain within their respective production-conditioned golden operating bands, attributing the production shortfall across the material disturbances and furnace state responses by comparing their lag-convolved values against both the production-conditioned golden operating bands and a rolling multi-day baseline window; and
5. computing a counterfactual recovery trajectory using a hybrid physics-and-residual simulator anchored to current sensor measurements via an additive reconciliation bias vector and a continuously differentiable soft-saturation operator, and gating issuance of any recommended setpoint change by evaluating a joint Mahalanobis density ellipsoid and five concurrent physical productivity ceilings.

### Claim 2 (System Claim with Tamper-Evident Split Execution Ledger)

The system of Claim 1, further comprising a role-based cryptographic audit ledger configured to:
- record operator acceptance or rejection of a generated advisory in an append-only SHA-256 hash-chained table stamped with an active model version;
- maintain a physically and logically separated post-hoc plant execution field that is updated only upon subsequent historian reconciliation; and
- automatically suppress routine setpoint issuance and generate a Management-of-Change (MoC) engineering trial dossier whenever a proposed manipulated input vector exceeds a threshold Mahalanobis distance from the historical on-wind operating distribution.

---

## 5. Recommended Filing Roadmap

1. **Step 1 (Immediate - Week 1)**: File a **US Provisional Patent Application** attaching this disclosure, `PHYSICS_MODEL_DESIGN.md`, `OBSERVABILITY_DESIGN.md`, `ML_ARCHITECTURE.md`, and the codebase diagrams. This establishes a priority date for 12 months at minimal cost (~$160 small entity / $80 micro entity).
2. **Step 2 (Before Pilot Meetings - Weeks 2-4)**: Use the "Patent Pending" designation on the Hearthline pitch deck and technical handouts when presenting to steel producers.
3. **Step 3 (During Phase A-C Plant Trial - Months 6-10)**: Gather real shadow-mode incident casebook data from the customer furnace to include as additional empirical examples in the **Non-Provisional Utility Patent & PCT International Application** filed before the 12-month provisional anniversary.
