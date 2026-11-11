# Hearthline Patent Filing Package

This folder is an attorney-ready technical drafting package, not a filed patent application and not legal advice.

## Recommended invention title

**Lag-Aware Advisory Digital Twin for Diagnosing Blast-Furnace Production Shortfalls**

This title has 10 words and fits the Indian Patent Office preference that a title normally contain no more than 15 words.

## Package contents

| File | Purpose |
|---|---|
| `US_PROVISIONAL_SPECIFICATION_DRAFT.md` | Written description for a US provisional application under 35 U.S.C. 111(b), including best mode, examples, alternatives, figures, and a claim appendix. |
| `INDIA_COMPLETE_SPECIFICATION_FORM2_DRAFT.md` | India Form 2 complete-specification body with industrial-process framing intended to address Section 3(k). |
| `US_CLAIMS_DRAFT.md` | Narrow US method, system, and dependent claim set for counsel review. |
| `INDIA_CLAIMS_DRAFT.md` | India-specific industrial process and apparatus claims, avoiding computer-program-per-se wording. |
| `PRIOR_ART_VALIDATION_MATRIX.md` | Closest references and element-by-element distinction. |
| `PATENT_DRAWINGS.html` | Print-ready black-and-white line drawings with reference numerals (FIGS. 1-8). |
| `FILING_CHECKLIST_US.md` | USPTO provisional and nonprovisional filing checklist. |
| `FILING_CHECKLIST_INDIA.md` | Indian Patent Office provisional/complete filing checklist and forms. |
| `INVENTOR_APPLICANT_INTAKE.md` | Missing inventor, ownership, residency, and correspondence information needed before filing. |

## DRAFT PDF exports (attorney handoff)

All PDFs carry a diagonal **DRAFT** watermark (except the drawings sheet, which is print-ready line art).

| PDF | Source |
|---|---|
| `US_Provisional_Draft.pdf` | US provisional written description |
| `India_Form2_Complete_Draft.pdf` | India Form 2 complete specification |
| `US_Claims_Draft.pdf` / `India_Claims_Draft.pdf` | Claim sets |
| `Prior_Art_Validation_Matrix.pdf` | Closest references + distinctions |
| `Patent_Drawings_FIG1_to_FIG8.pdf` | FIGS. 1–8 line drawings |
| `Filing_Checklist_US.pdf` / `Filing_Checklist_India.pdf` | Filing checklists |
| `Inventor_Applicant_Intake.pdf` | Inventor / ownership intake |
| `Patentability_And_Disclosure.pdf` | High-level patentability memo |

## Independent Auto-mode validation

See `INDEPENDENT_VALIDATION_AUTO.md` (and PDF siblings in this folder). That file completes the specialized-model review that hit a usage limit: US §§101/102/103/112, India §3(k)/CRI 2025/§39, prior-art confirmation against TCS / Caterpillar / Daicel families, and ordered counsel next steps.

## Current validation verdict

### Potentially patentable nucleus

The strongest defensible combination is:

1. classifying blast-furnace tags into mutually exclusive causal roles;
2. generating target-production-conditioned Golden Bands from a permeability-qualified historical cohort;
3. convolving each tag with its own metallurgical transport/residence-time kernel;
4. diagnosing a production shortfall during an interval in which manipulated inputs remain inside their target-conditioned bands, using lag-active deviations of disturbances and furnace responses against both the Golden Band and a prior rolling baseline;
5. computing counterfactual recovery through a zero-drift sensor-anchored hybrid twin with derivative-preserving soft saturation; and
6. blocking routine advice outside a joint Mahalanobis envelope or a physical productivity ceiling, while generating a management-of-change dossier.

### Claims that should not be filed broadly

- A generic digital twin containing physics and machine-learning blocks.
- Generic blast-furnace intelligent control or neural-network optimization.
- Generic root-cause analysis from digital-twin residuals.
- Generic use of residence time to align manufacturing process data.
- Generic sensor-bias correction.
- Generic use of Mahalanobis distance as an anomaly or operating-envelope metric.
- The RAFT, Rist, or Ergun equations themselves.

Those elements have substantial prior art. The claim must recite the furnace-specific combination above.

## Critical public-disclosure warning

The project was published publicly on GitHub and GitHub Pages on **10 November 2026**.

- **United States:** An inventor-originated disclosure may fall within the AIA 35 U.S.C. 102(b)(1) one-year grace period. File no later than **10 November 2027**, but immediate filing is strongly recommended.
- **India and many non-US jurisdictions:** Absolute-novelty rules may make the public disclosure damaging unless a valid earlier priority filing exists or a statutory exception applies. A registered Indian patent agent must evaluate this immediately.
- If any inventor is resident in India, Section 39 of the Indian Patents Act may require filing in India first and waiting six weeks, or obtaining foreign-filing permission on Form 25, before a US/PCT filing.

## What is still required from the inventor

Complete `INVENTOR_APPLICANT_INTAKE.md`, confirm ownership/employer obligations, and engage registered US and Indian patent professionals. The drafts intentionally retain bracketed placeholders that cannot be guessed.

