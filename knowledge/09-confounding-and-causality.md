# Confounding: the optimiser will learn the operator

A model fit to blast furnace history estimates P(production | blast volume), the association in the log. The quantity a recommendation needs is P(production | do(blast volume)), the effect of changing the blast. They differ because operators move the blast, the PCI, the moisture, and the coke *in response to* the furnace and the raw materials. The fitted surface is the plant and the control policy added together. Inverting it recommends the policy.

This is the constraint on Phase 7. Ignore it and the optimiser will tell the operator to do what the operator already does on the good days, including the parts that were reactions rather than causes.

## 1. The demonstration to reproduce before trusting a recommendation

Caers and Eskanlou, *Minerals Engineering*, on a public iron-ore reverse-flotation record (the Kaggle set in [10-datasets-and-benchmarks.md](10-datasets-and-benchmarks.md)). 737,453 rows at 20 seconds, aggregated to 4,097 hourly records. Causal discovery with process-knowledge constraints, PC and DirectLiNGAM agreeing, recovered a circuit graph. Then:

- A gradient-boosted predictor says pulp pH is inert. Partial dependence −0.01 percentage points per standard deviation, interval includes zero.
- Backdoor adjustment, g-computation, and double machine learning return −0.08 and −0.10 percentage points, intervals exclude zero, in the direction reverse-flotation practice predicts. The paired difference is negative in all 200 block-bootstrap resamples of 24-hour blocks. Three regime shifts with balanced feed assays confirm the sign.
- The disagreement is a lag of about one hour. A same-hour attribution has nothing to attach to.
- The amine-collector effect is reported as **not identifiable**, because dosing responds to ore mineralogy the routine assays do not measure. The paper prints that verdict instead of a number.
- Aeration has the largest identified effect, and it is carried by one of seven columns. The bank-average column hides it.
- Letting the iron concentrate assay in as a feature lifts held-out R² from 0.36 to 0.78. The assay is a descendant of the outcome. A pipeline scored only on held-out error accepts it.

Source: [Minerals Engineering, flotation causal study](https://www.sciencedirect.com/science/article/abs/pii/S0892687526008666).

Build this test into the decision-model suite. If the code cannot recover "pH is real, amine is not identifiable, concentrate assay is leakage" on that dataset, it is not allowed to rank a blast furnace setpoint.

## 2. Formal results

- **Adjustment under a fixed control law.** [arXiv 2211.05613](https://arxiv.org/abs/2211.05613) gives an adjustment for control confounding when the controller is fixed, by estimating the disturbance the controller is cancelling and conditioning on it. Feedforward and feedback both covered. The fixed-law assumption breaks at a practice change. Split the record on those dates.
- **Sign reversal.** Causal Newton Optimization (IJCAI 2026) states the failure directly: a past state or an external disturbance affects both the current control move and the future output, so the apparent effect can have the wrong sign and a naive optimiser walks the wrong way. The remedy they use is a known graph, backdoor-adjusted gradients, and additive interventions rather than absolute setpoints. [IJCAI 2026 proceedings](https://ijcai.org/proceedings/2026/710).
- **The recommender contaminates its own training set.** Recovering Markov models from closed-loop data (Automatica 2019) is the case where a decision-support tool biases the log that trains the next model. Background: Forssell and Ljung 1999, Van den Hof and Schrama 1995, on closed-loop identification.
- **Offline reinforcement learning.** Conservative Q-learning (NeurIPS 2020) shows off-policy methods assign optimistic values to actions outside the data, and the policy then prefers those actions because it maximises Q. A steel flatness controller (Information Sciences 2023) combines an ensemble Q with a behaviour-cloning penalty so the policy stays near observed actions.

## 3. Discovery methods, and their limits

PC, FCI, RFCI, LiNGAM, and NOTEARS have been compared on Tennessee Eastman. Agreement across algorithms is the practical confidence signal. In one study, 10 of 52 variables matched or beat the full set ([arXiv 2510.23817](https://arxiv.org/html/2510.23817)). Process-knowledge constraints come in four published categories and have been validated on a commercial FCC unit ([I&ECR 2022](https://pubs.acs.org/doi/full/10.1021/acs.iecr.2c01326)).

Blast-furnace-specific work exists as Granger causality fused with expert knowledge, hierarchical lag search, and confidence-scored propagation paths (patent CN122654903A), plus a knowledge-constrained graph network for root cause (Process Safety and Environmental Protection 2022). Use discovery to propose edges. Accept an edge into the decision model only when process knowledge, an intervention, or a natural experiment agrees. The constitution in [../CLAUDE.md](../CLAUDE.md) already says this. Do not let a discovered edge become a recommendation on its own.

## 4. Remedies, in the order to build them

1. **Identifiability audit, per manipulated variable, before any recommendation ships.** Output is one of: identifiable, not identifiable, identifiable only inside a named regime. Non-identifiable is a result. The amine verdict is the template. Print it on the optimiser page.
2. **Two model families.** A predictive model may use anything known at prediction time, including descendants, because the job is to forecast the next cast. A decision model may use only causal parents of the target. The concentrate-assay result is why a single model cannot serve both jobs.
3. **Adjust for the disturbance the operator is answering.** Raw-material chemistry, coke CSR, sinter FeO and RDI, moisture, and upstream sinter and pellet quality are the backdoor set. Anything the operator sees and the log does not — a visual read of the tuyeres, a shift handover, an unlogged coke pile — remains an unmeasured confounder and bounds the claim.
4. **Require agreement.** Backdoor adjustment, g-computation, and double machine learning, with block-bootstrap intervals. Block length at least the decorrelation time. Twenty-four hours is the published choice on the flotation record. On hot metal temperature, start from the 8–12 hour time constant and test longer.
5. **Mine natural experiments.** Regime changes, campaign boundaries, furnace-to-furnace contrast, equipment outages. Keep a contrast only when the covariates balance across it. Several furnaces are the advantage single-furnace studies do not have.
6. **Put the lag in before the attribution.** A same-hour SHAP on this process misses the burden entirely and assigns the effect to whatever moved recently, which is usually the blast. SHAP on the predictive model is an explanation of the fit. It is not a cause. Say that next to every beeswarm plot.
7. **Plan a small deliberate excitation** for the setpoints the plant most wants to optimise. No observational fix fully replaces a scheduled, randomised, modest dither. This platform does not apply it. It can propose a design for a metallurgist to approve.
8. **Treat the recommendation as offline policy learning.** Penalise distance from the historical behaviour policy. Use ensemble disagreement as the uncertainty. Hard-filter actions outside the operating envelope and outside a trust region around the current point.

## 5. Envelope

A box drawn from the historical min and max of each variable admits corners that never occurred. Tata's NSGA-II study used that box and reported up to 5% improvement on the surrogate. Replace the box with a density threshold or a convex hull in the joint manipulated-variable space, and shrink a trust region around the current operating point when the predicted gain is inside the noise. Recommendations outside the hull are blocked, or marked as requiring an engineering trial. They are not shown as a setpoint.

## 6. Wording the UI is allowed to use

Allowed: "Periods with this combination of blast, PCI, and coke were followed by production in this range. The association is adjusted for measured raw-material quality. It is not an estimate of the effect of moving the blast on an otherwise identical furnace, except where the identifiability audit says the effect is identified."

Not allowed: "Set blast volume to this value to obtain 10,000 t/day."

When the audit says not identifiable, the page says which unmeasured confounder blocks it, and what measurement would unblock it. That sentence is more useful than a fabricated setpoint.
