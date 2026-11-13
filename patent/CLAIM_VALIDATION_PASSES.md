# Four-Pass Claim Validation Log

**Date:** 11 November 2026  
**Documents reviewed:** `US_CLAIMS_DRAFT.md`, `INDIA_CLAIMS_DRAFT.md`, both specifications, `PRIOR_ART_VALIDATION_MATRIX.md`, `CLAIM_SUPPORT_AND_ENABLEMENT_MATRIX.md`, and the working implementation in `apps/api/bf_twin/`.  
**Result:** Claims were amended after the passes below and then copied into the US provisional and the India Form 2 complete specification so each filing document is self-contained.

This log is a technical filing review. It is not a legal opinion, a freedom-to-operate opinion, or a substitute for a registered patent attorney or Indian patent agent.

---

## Pass 1 — Clarity and antecedent basis

Checked every independent and dependent claim for missing antecedents, inconsistent names, and claim-dependency errors.

| Finding | Action |
|---|---|
| US claim 1 generated a counterfactual without requiring the fixed sensor anchor or the pressure identity that the specification calls the technical core. | Those three limitations were moved into independent claim 1. Old claims 7 and 8 were rewritten so they no longer repeat the same limitation. |
| India claim 1 reconciled the model to sensors but left the fixed bias and pressure identity only in a dependent claim. | The same three limitations were moved into India claim 1. Dependent claims 3 and 4 were rewritten. |
| “Decision residual” in former US claim 10 could be read as requiring three causal estimators (backdoor, g-computation, and double machine learning) that are specified but not all deployed. | US claim 10 now separates a forecast residual from a decision residual and does not recite those three estimators as implemented. |
| India title is 9 words, within the usual 15-word preference. India abstract is 141 words, within the 150-word limit. | Left unchanged. |
| India claim 9 is an apparatus claim that performs the method of claims 1 to 8. That omnibus style is ordinary Indian practice and is supported by the apparatus description. | Kept. |

No remaining claim refers to a term that was not introduced earlier in that claim or in the claim it depends on.

## Pass 2 — Written description and enablement

Each limitation in the amended independent claims was checked against a section of the specification and a function that actually runs.

| Limitation now in both independent method claims | Support |
|---|---|
| Read-only historian | `connector.py` rejects non-read operations |
| Five mutually exclusive causal roles | Parameter catalog and capability classifier |
| Production-conditioned band from a permeability-qualified on-wind cohort, then shifted by a physical sensitivity | `compute_golden_ranges` |
| Tag-specific temporal kernel | `LAG_TAU_HOURS` and lag-active exponential average |
| Shortfall while manipulated inputs stay inside their bands | `attribute_historical_shortfall` |
| Dual comparison: band and preceding rolling reference | Golden-band status plus excluded-recent rolling window |
| Fixed additive anchor bias | `physics_bias` held constant across the counterfactual |
| Pressure identity `dP = dPu + dPl` | Physics state reconciliation |
| Joint-density envelope, trust region, and physical ceilings | `evaluate_density_envelope` and ceiling arbiter |
| Advisory withheld and replaced by an engineering-trial dossier | Management-of-change gate |

A numerical best-mode example was added to both specifications. On the interval 1.20 to 1.70 with softness 0.040, hard clipping at 1.74 has derivative 0 and output 1.7000. The soft operator has output 1.7305 and derivative about 0.42. Preferred lag priors (0.6 h through 12 h) are listed as configuration, not as universal constants.

**Remaining enablement limit, disclosed on purpose:** a full backdoor / g-computation / double-machine-learning decision residual is described as a later embodiment. The claims do not require it.

## Pass 3 — Novelty and obviousness

The amended independent claims were challenged again against the closest references in `PRIOR_ART_VALIDATION_MATRIX.md`: TCS industrial and blast-furnace monitoring (including EP4154105B1 and US12026047B2), CN122654903A, Caterpillar US11899527B2, Daicel US12321163B2, Shanghai Jiao Tong CN109918702A, and AspenTech WO2021076760A1.

No single reference was found that teaches all of the following together:

1. a required-production band built from a permeability-qualified blast-furnace cohort;
2. a shortfall diagnosed only while manipulated inputs remain inside those bands;
3. a separate physical lag kernel per tag, compared with both the band and a prior rolling reference;
4. a counterfactual whose sensor anchor bias is frozen and whose pressure split is conserved; and
5. routine advice blocked by a joint-density envelope, a local trust step, and named furnace productivity ceilings, with an engineering-trial dossier instead.

**Risk that remains:** an examiner can still argue that items 1–5 are an obvious combination of known blast-furnace root-cause tools, residence-time alignment, sensor calibration, and multivariate envelopes. The claims are narrowed to that combination because a broader “digital twin plus machine learning” claim is not defensible. Mahalanobis distance, the Ergun, Rist, and raceway-flame equations, and generic digital twins are not claimed by themselves.

## Pass 4 — US eligibility and India Section 3(k)

**United States.** The independent method is a concrete industrial diagnosis tied to furnace sensors, a conservation identity, and a physical productivity ceiling. It is not a claim to the equations alone and it does not claim closed-loop control of the furnace. That is the practical-application framing counsel should use under 35 U.S.C. 101. Eligibility is not guaranteed.

**India.** Claim 1 is drafted as a method performed by a furnace-monitoring apparatus coupled to blast-furnace sensors, with a stated technical effect: non-zero response sensitivity at an operating limit, preservation of the pressure balance, and detection of a shortfall while manipulated inputs stay in band. That is the Section 3(k) / CRI Guidelines 2025 framing. It is not a claim to a computer program per se. Allowance is not guaranteed.

**Section 39.** If any inventor is resident in India, do not file in the United States first unless Form 25 permission has been obtained or an Indian application was filed at least six weeks earlier and no secrecy direction was issued.

## Public disclosure

The repository and GitHub Pages site were public on 10 November 2026.

- United States: an inventor-originated disclosure may fall in the one-year grace period of 35 U.S.C. 102(b)(1). File a provisional no later than 10 November 2027, and sooner if possible.
- India, the EPO, and most PCT states: that disclosure is a serious absolute-novelty problem. Indian counsel must decide whether any filing is still available before these documents are treated as ready to file there.

## What is submission-formatted, and what is still blocked

Ready for counsel to file after the identity block is filled:

- `US_PROVISIONAL_SPECIFICATION_DRAFT.md` and `US_Provisional_Draft.pdf`, including FIGS. description, best mode, worked numbers, and all 20 claims.
- `INDIA_COMPLETE_SPECIFICATION_FORM2_DRAFT.md` and `India_Form2_Complete_Draft.pdf`, Form 2 preamble, technical advancement, best method, all 10 claims, and a 141-word abstract.
- `Patent_Drawings_FIG1_to_FIG8.pdf`.
- Filing checklists and the inventor intake form.

Still required before any office will accept the application:

- Every inventor’s legal name, residence, citizenship, and address.
- Applicant name, address, and the assignment or employment basis.
- India residence answer and, if required, Form 25.
- A registered practitioner’s signature, fee, entity status, and the official form set (US PTO/SB/16 or ADS; India Forms 1, 2, 3, 5, and 26 as applicable).
- Counsel’s own prior-art search. This package is not that search.

Do not post a newer enabling draft to a public repository while a filing decision is open. The copies already on GitHub Pages are enough to count as a disclosure; adding another public revision does not help the filing.
