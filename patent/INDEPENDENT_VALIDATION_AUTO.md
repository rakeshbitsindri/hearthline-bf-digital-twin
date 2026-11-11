# Independent Patentability & Filing-Readiness Validation (Auto Mode)

**Date:** 10 November 2026  
**Scope:** US (35 U.S.C. §§ 101 / 102 / 103 / 112) and India (Sections 2(1)(j), 3(k), 10, 39; CRI Guidelines 2025)  
**Status:** Technical counsel-prep validation. **Not legal advice.** Not a filed application.

This document replaces the unfinished specialized-model review that hit a usage limit. Validation was performed against live web sources (USPTO MPEP, Indian CRI Guidelines 2025, *Ferid Allani*, TCS ironmaking / root-cause families) and the local drafting package in `patent/`.

---

## 1. Overall verdict

| Question | Answer |
|---|---|
| Is a filing worth pursuing? | **Yes**, as a **narrow** industrial method/system. |
| Is a broad “BF digital twin + ML + RCA” claim viable? | **No.** Anticipated / obvious over TCS, Central South Univ., Caterpillar, Daicel, SJTU, AspenTech. |
| US §101 eligibility (Alice/Mayo)? | **Survivable** if claims stay tied to physical furnace diagnosis, conservation identities, soft saturation at operational limits, and envelope/ceiling gating — not abstract “optimize a plant with ML.” |
| India §3(k)? | **Survivable** if framed as industrial monitoring apparatus/process with concrete technical effect (pressure-drop identity preservation, channeling/shortfall detection during unchanged manipulated inputs, non-zero limit sensitivity). Follow CRI 2025 + *Ferid Allani*. |
| Filing readiness of drafts? | **Attorney-ready technical package** with DRAFT PDFs. Inventor intake, ownership, and Section 39 residency still required. |

---

## 2. US track — validated points

### 2.1 §101 (subject matter)
- Stronger when claims recite transforming blast-furnace sensor streams into a gated advisory output that respects physical ceilings and a density envelope, with sensor-anchor bias held fixed across counterfactuals.
- Weaker if claims reduce to “collect data → run model → display recommendation.”
- Cite practical-application framing analogous to *Diamond v. Diehr* / industrial process transformation; avoid pure mathematical claim of RAFT/Rist/Ergun.

### 2.2 §102 / §103 (novelty / obviousness)
Closest art confirmed in this Auto pass:

1. **TCS ironmaking / cyber-physical family** — e.g. ironmaking plant optimization (BFSI, KPI forecast, physics + data-driven models, diagnostics) and **US12026047B2** causal-map root-cause identification (FTRCI). Also academic *metafur* BF digital twin papers by TCS authors.
2. **CN122654903A** — BF root-cause with expert physics, hierarchical lags, Granger / causal paths.
3. **US11899527B2 (Caterpillar)** — reduced-order twin residual + fault-model RCA.
4. **US12321163B2 (Daicel)** — residence-time alignment of explanatory vs response variables.
5. Hybrid BF optimization (e.g. CN109918702A) and AspenTech automated model/MPC families.

**Required distinguishing combination** (must appear together in independent claims):

1. mutually exclusive causal roles;  
2. target-production–conditioned Golden Bands on a permeability-qualified cohort;  
3. per-tag metallurgical lag kernels;  
4. shortfall attribution **during unchanged-manipulated-input** intervals vs Golden Band **and** excluded-recent rolling baseline;  
5. fixed baseline sensor-anchor bias + exact conservation / zero-drift identities;  
6. derivative-preserving soft saturation;  
7. Mahalanobis (or equivalent joint-density) envelope **plus** named physical ceilings, with MoC dossier + separate execution-confirmation ledger when blocked.

### 2.3 §112 (written description / enablement)
- Package maps claim elements to `simulator.py`, `connector.py`, `db.py`, FIGS. 1–8, and tests (see `CLAIM_SUPPORT_AND_ENABLEMENT_MATRIX.md`).
- **Gap to disclose honestly to counsel:** full backdoor / g-computation / DML decision-residual triad is architected but not all three estimators are deployed; do not claim that triad as currently implemented without additional enablement.

### 2.4 Public disclosure / grace period
- Public GitHub + Pages push ~**10 Nov 2026** is treated as an inventor-originated disclosure candidate.
- **US AIA 35 U.S.C. §102(b)(1):** file **on or before 10 Nov 2027**. Immediate provisional strongly recommended.
- USPTO provisional guidance explicitly warns that pre-filing disclosure protected in the US **may preclude** patenting abroad.
- Making repos private **now does not erase** the prior public disclosure.

### 2.5 Filing package completeness (US)
Present: provisional spec PDF, claims PDF, drawings PDF, prior-art matrix, checklist, inventor intake.  
Still needed from inventor: legal names, citizenship, assignments, correspondence, best-mode confirmation, disclosure log dates/URLs.

---

## 3. India track — validated points

### 3.1 Section 3(k) / CRI 2025
- *Ferid Allani*: computer-program–based inventions are not barred solely for being software if they show **technical effect / technical contribution**.
- CRI Guidelines **2025** (IPO, Jul 2025) reinforce technical-effect examination for AI/ML CRIs and allow system **and** method independent claims when supported.
- Drafts correctly avoid “computer program per se” wording and recite furnace monitoring apparatus + industrial process effects.

### 3.2 Absolute novelty risk
- India generally lacks a US-style one-year grace period for this disclosure pattern.
- Public GitHub/Pages content may destroy absolute novelty for India/PCT/EPO unless counsel identifies a statutory exception or an earlier priority filing.
- **Action:** Indian patent agent triage **immediately**.

### 3.3 Section 39
- If any inventor is resident in India, foreign filing may require India-first filing + six-week wait **or** Form 25 foreign-filing permission before US/PCT.

### 3.4 Filing package completeness (India)
Present: Form 2 complete-spec draft PDF, India claims PDF, checklist, drawings.  
Still needed: Forms 1/3/5/18/25/26 as applicable, inventor residency determination, Hindi/English formalities per agent instruction.

---

## 4. Claim strategy confirmed

**File:** the multi-step shortfall diagnosis + sensor-anchored soft-sat twin + dual envelope/ceiling gating + MoC/audit separation.  
**Do not file broadly:** generic digital twin, generic BF expert system, textbook physics equations alone, generic Mahalanobis anomaly detection, generic residence-time alignment alone.

Dependent claims should lock: specific lag kernels (0.6 / 1.0 / 2.5 / 6.5 h priors), five causal roles, five named ceilings, SHA-256 hash-chained audit, read-only connector verb rejection.

---

## 5. Recommended next actions (ordered)

1. Complete `INVENTOR_APPLICANT_INTAKE.md` / PDF.  
2. Engage registered **US** and **Indian** patent professionals with this folder.  
3. File **US provisional** immediately (today–this week if possible).  
4. Parallel India counsel decision on novelty salvage / Form 25 / India complete or provisional.  
5. Log every public URL, commit SHA, and Pages deploy timestamp in the intake disclosure table.  
6. After provisional number issues, counsel may advise limiting further enabling public detail; privacy of repos does not undo past disclosure.

---

## 6. Artifacts produced in this Auto completion

| Artifact | Path |
|---|---|
| US provisional DRAFT PDF | `patent/US_Provisional_Draft.pdf` |
| India Form 2 DRAFT PDF | `patent/India_Form2_Complete_Draft.pdf` |
| Claims PDFs | `patent/US_Claims_Draft.pdf`, `patent/India_Claims_Draft.pdf` |
| Drawings PDF | `patent/Patent_Drawings_FIG1_to_FIG8.pdf` |
| Prior-art matrix PDF | `patent/Prior_Art_Validation_Matrix.pdf` |
| Checklists / intake / memo PDFs | `patent/Filing_Checklist_*.pdf`, `Inventor_Applicant_Intake.pdf`, `Patentability_And_Disclosure.pdf` |
| This validation | `patent/INDEPENDENT_VALIDATION_AUTO.md` |

---

*End of Auto-mode independent validation.*
