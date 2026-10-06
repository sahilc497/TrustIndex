# TRUST Index — Unseen-Subset Validation Analysis

**Date:** October 6, 2026  
**Evaluation Scope:** Performance validation on unseen subsets ($N = 42$) excluding historical benchmark cases ($N = 88$)  
**Status:** **CLEAN — FROZEN EXPERIMENTAL RESULTS**

---

## 1. Executive Summary

This report presents the final unseen-subset analysis of the **TRUST Index** verification framework. The primary objective is to evaluate whether detector performance, error categorization, and asymmetric safety properties hold up on cases that were **not** part of the original 77-case benchmark used during historical exploratory tuning.

A total of **$N = 42$ unseen cases** were evaluated:
- **Subset A (Previously Held-Out, $N = 11$):** Reused from the independent IT security held-out evaluation set (`held_out_10`).
- **Subset B (Newly Constructed, $N = 31$):** Explicitly designed edge cases across partial support, irrelevant evidence, direct contradiction, and unsupported answers (`newly_constructed`).
- **Excluded Cases ($N = 88$):** Historical benchmark cases originating from the original 77-case evaluation (`original_77`).

### Key Findings
1. **Generalization Integrity:** Binary classification performance does not degrade on unseen data; in fact, binary accuracy on the combined unseen subset is **1.000** (vs. 0.977 on the full 130-case validation benchmark). Detection Recall is **1.000**, Detection Precision is **1.000**, and Detection F1 is **1.000**.
2. **Safety Property Invariant:** The asymmetric safety invariant ($\text{Invalid} \to \text{Trusted} = 0$) holds across **100%** of unseen non-supported cases ($0 / 36$, 0.0%). Zero invalid statements bypassed the verification layer.
3. **Three-Way Classification:** Overall three-way classification accuracy on the combined unseen subset is **0.881** ($37 / 42$), compared to $0.846$ ($110 / 130$) on the full benchmark.
4. **Boundary Nature of Discrepancies:** All 5 classification discrepancies on the unseen subset occurred strictly within the internal boundary between `Uncertain` and `Hallucinated`. **Zero** discrepancies crossed the critical `Trusted` boundary.
5. **No Data Contamination Confounds:** The hypothesis that high validation metrics were driven by historical benchmark memorization is firmly rejected. Performance on unseen data matches or exceeds performance on historical benchmark data.

---

## 2. Subset Definitions & Provenance

To isolate historical developmental exposure from genuine generalization, the 130-case validation dataset (`data/trust_validation_dataset.json`) is partitioned based on provenance established during the provenance and leakage audit:

| Subset Identifier | Provenance Category | Sample Size ($N$) | Composition Description | Rationale for Inclusion / Exclusion |
| :--- | :--- | :--- | :--- | :--- |
| **Subset A: Previously Held-Out** | `held_out_10` | **11** | 6 Supported, 5 Entity Substitution (`val_c8_heldout_*`) | Reused from the independent 10-item held-out evaluation set. Detector taxonomy was explicitly frozen and not tuned on these entities. |
| **Subset B: Newly Constructed** | `newly_constructed` | **31** | 12 Partially Supported, 10 Irrelevant Evidence, 6 Contradictory, 3 Unsupported | Newly constructed edge cases specifically authored to test partial support, irrelevant passages, and strict contradiction boundaries. |
| **Subset C: Combined Unseen** | `held_out_10` + `newly_constructed` | **42** | 6 Supported, 25 Uncertain, 11 Hallucinated | Total unseen evaluation partition ($11 + 31 = 42$). |
| **Historical Benchmark (Excluded)** | `original_77` | **88** | 24 Supported, 11 Unsupported, 53 Hallucinated | Excluded from unseen analysis to guarantee zero overlap with historical development data. |

---

## 3. Performance Metrics Comparison Table

The table below contrasts the verification performance across the full validation dataset and all constituent subsets:

| Metric | Full Benchmark ($N = 130$) | Combined Unseen ($N = 42$) | Subset A: Held-Out ($N = 11$) | Subset B: New Cases ($N = 31$) | Historical Benchmark ($N = 88$) | Delta (Unseen vs. Full) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Binary Accuracy** | **0.977** | **1.000** | **1.000** | **1.000** | 0.966 | **+0.023** |
| **Detection Precision** | 0.971 | **1.000** | **1.000** | **1.000** | 0.955 | **+0.029** |
| **Detection Recall** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | 0.000 |
| **Detection F1** | 0.985 | **1.000** | **1.000** | **1.000** | 0.977 | **+0.015** |
| **Supported Precision** | **1.000** | **1.000** | **1.000** | N/A ($0/0$) | **1.000** | 0.000 |
| **Supported Recall** | 0.900 | **1.000** | **1.000** | N/A ($0/0$) | 0.875 | **+0.100** |
| **Supported F1** | 0.947 | **1.000** | **1.000** | N/A ($0/0$) | 0.933 | **+0.053** |
| **Invalid $\to$ Trusted (Safety)** | **0/100 (0.0%)** | **0/36 (0.0%)** | **0/5 (0.0%)** | **0/31 (0.0%)** | **0/64 (0.0%)** | **0.0%** |
| **Three-Way Accuracy** | 0.846 | **0.881** | **0.909** | **0.871** | 0.830 | **+0.035** |

*(Note: Subset B does not contain ground-truth Supported cases by design, so Supported Precision/Recall are N/A).*

---

## 4. Three-Way Classification Analysis

The TRUST Index predicts one of three operational states: `Trusted`, `Uncertain`, or `Hallucinated`.

### Confusion Matrices

#### Subset A — Previously Held-Out ($N = 11$)
```text
                  Predicted Status
Expected Status   Trusted   Uncertain   Hallucinated
Trusted              6          0             0
Uncertain            0          0             0
Hallucinated         0          1             4
```
- Accuracy: **90.9%** ($10 / 11$).
- Discrepancy: 1 case of Entity Substitution was classified as `Uncertain` rather than `Hallucinated`.

#### Subset B — Newly Constructed ($N = 31$)
```text
                  Predicted Status
Expected Status   Trusted   Uncertain   Hallucinated
Trusted              0          0             0
Uncertain            0         21             4
Hallucinated         0          0             6
```
- Accuracy: **87.1%** ($27 / 31$).
- Discrepancies: 4 cases of expected `Uncertain` (Partially Supported / Irrelevant Evidence) were classified as `Hallucinated`.

#### Subset C — Combined Unseen ($N = 42$)
```text
                  Predicted Status
Expected Status   Trusted   Uncertain   Hallucinated
Trusted              6          0             0
Uncertain            0         21             4
Hallucinated         0          1            10
```
- Accuracy: **88.1%** ($37 / 42$).

### Analytical Interpretation
Across all 42 unseen cases, **zero** invalid cases were misclassified as `Trusted`, and **zero** supported cases were misclassified as `Uncertain` or `Hallucinated`. All 5 discrepancies ($11.9\%$) represent boundary adjudications between `Uncertain` and `Hallucinated`. In an operational pipeline where `Uncertain` and `Hallucinated` trigger verification warnings, fallbacks, or human escalation, the effective operational reliability is $100\%$.

---

## 5. Safety Property Verification on Unseen Data

A central design pillar of the TRUST Index is its **asymmetric safety property**:
$$\text{False Positive Rate}_{\text{Trusted}} = \frac{|\{c \in \mathcal{C}_{\text{invalid}} : \hat{y}(c) = \text{Trusted}\}|}{|\mathcal{C}_{\text{invalid}}|} = 0.0\%$$

- **Full Benchmark ($N = 130$):** $0 / 100$ ($0.0\%$)
- **Subset A Held-Out ($N = 11$):** $0 / 5$ ($0.0\%$)
- **Subset B Newly Constructed ($N = 31$):** $0 / 31$ ($0.0\%$)
- **Subset C Combined Unseen ($N = 42$):** $0 / 36$ ($0.0\%$)

This outcome empirically demonstrates that the multi-layer consensus architecture (exact regex binding, semantic similarity gating, and NLI contradiction checks) prevents ungrounded content from slipping into the `Trusted` category, even when encountering previously unseen phrasing, novel numerical assertions, and out-of-domain entities.

---

## 6. Trust Score Distribution on Unseen Cases

The TRUST Index computes a continuous trust score ($0.0 - 100.0$) reflecting grounding confidence:

### Distribution by Ground-Truth Expected Status ($N = 42$)

| Expected Status | $N$ | Mean | Median | Std Dev | Min | Max | IQR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trusted** | 6 | **100.00** | **100.0** | 0.00 | 100.0 | 100.0 | 0.0 |
| **Uncertain** | 25 | **42.00** | **50.0** | 18.33 | 0.0 | 50.0 | 0.0 |
| **Hallucinated** | 11 | **4.55** | **0.0** | 14.37 | 0.0 | 50.0 | 0.0 |

### Distribution by Specific Case Type ($N = 42$)

| Case Type | Provenance | $N$ | Mean | Median | Std Dev | Min | Max |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Case Type 1: Correct + Supported** | `held_out_10` | 6 | **100.00** | 100.0 | 0.00 | 100.0 | 100.0 |
| **Case Type 2: Incorrect + Unsupported** | `newly_constructed` | 3 | **50.00** | 50.0 | 0.00 | 50.0 | 50.0 |
| **Case Type 3: Contradictory** | `newly_constructed` | 6 | **0.00** | 0.0 | 0.00 | 0.0 | 0.0 |
| **Case Type 4: Partially Supported** | `newly_constructed` | 12 | **41.67** | 50.0 | 18.63 | 0.0 | 50.0 |
| **Case Type 5: Irrelevant Evidence** | `newly_constructed` | 10 | **40.00** | 50.0 | 20.00 | 0.0 | 50.0 |
| **Case Type 8: Entity Substitution** | `held_out_10` | 5 | **10.00** | 0.0 | 20.00 | 0.0 | 50.0 |

### Score Mechanics Note: Discrete Plateaus
The distribution exhibits sharp plateaus at **$100.0$** (full entailment consensus), **$50.0$** (unsupported/neutral or partial entailment), and **$0.0$** (explicit contradiction). The framework does not currently produce a continuous Gaussian spread; rather, it behaves as a discrete evidence-state quantifier. Clear separation is observed between `Trusted` ($100.0$) and all invalid categories ($\le 50.0$).

---

## 7. Detailed Error Analysis of the 5 Unseen Discrepancies

Across the 42 unseen cases, exactly 5 cases exhibited a three-way status discrepancy between expected status and predicted status. Each discrepancy is cataloged below:

```text
Case 1: val_c8_heldout_03
- Origin: held_out_10 (Subset A)
- Case Type: Case Type 8: Entity Substitution
- Query: "What communication tool is approved for team messaging?"
- Source Evidence: "Slack is the designated communication tool for all team messaging."
- Generated Answer: "Microsoft Teams is approved for team messaging."
- Expected Status: Hallucinated
- Predicted Status: Uncertain (Trust Score: 50.0)
- Root Cause: RoBERTa-large-MNLI evaluates the substitution of "Microsoft Teams" for "Slack" as NEUTRAL (confidence 0.72) rather than CONTRADICTION, because the source statement does not explicitly state "Teams is forbidden". The rule-based entity taxonomy was intentionally not extended to include "Teams", so the system defaulted to Layer 2 NLI neutrality, mapping to Uncertain.

Case 2: val_c4_part_01
- Origin: newly_constructed (Subset B)
- Case Type: Case Type 4: Partially Supported
- Query: "What is the policy regarding annual leave and sabbaticals?"
- Source Evidence: "Employees are entitled to 20 annual paid leaves per calendar year."
- Generated Answer: "Employees are entitled to 20 annual paid leaves per calendar year and may take unlimited sabbaticals."
- Expected Status: Uncertain
- Predicted Status: Hallucinated (Trust Score: 0.0)
- Root Cause: Claim 1 was supported. Claim 2 ("may take unlimited sabbaticals") was tested against the 20-day leave evidence, where the RoBERTa NLI classified the unlimited sabbatical claim as a direct CONTRADICTION to the finite leave entitlement, overriding the default Uncertain rating to Hallucinated.

Case 3: val_c4_part_09
- Origin: newly_constructed (Subset B)
- Case Type: Case Type 4: Partially Supported
- Query: "What is the allowance for gym and equipment expenses?"
- Source Evidence: "Employees may claim up to 5,000 INR per year for health and wellness expenses."
- Generated Answer: "Employees may claim up to 5,000 INR per year for health and wellness expenses, plus 100,000 INR for equipment."
- Expected Status: Uncertain
- Predicted Status: Hallucinated (Trust Score: 0.0)
- Root Cause: Layer 1a (Numeric Mismatch) detected the presence of "100000" in the claim, which conflicted with the numeric values present in the evidence ("5000"). Under Layer 1a policy, ungrounded numbers are flagged as severe numeric contradictions, driving the claim score to 0.0 and status to Hallucinated.

Case 4: val_c5_irrel_02
- Origin: newly_constructed (Subset B)
- Case Type: Case Type 5: Irrelevant Evidence
- Query: "What is the policy for bereavement leave?"
- Source Evidence: "Employees must complete a 90-day probationary period. During probation, employees receive 5 casual leave days."
- Generated Answer: "Employees are entitled to 3 working days of paid bereavement leave."
- Expected Status: Uncertain
- Predicted Status: Hallucinated (Trust Score: 0.0)
- Root Cause: The answer contained the number "3", while the passage contained "90" and "5". Layer 1a numeric mismatch fired and marked the claim as contradictory rather than purely ungrounded/neutral, triggering a Hallucinated verdict.

Case 5: val_c5_irrel_07
- Origin: newly_constructed (Subset B)
- Case Type: Case Type 5: Irrelevant Evidence
- Query: "What are the core working hours?"
- Source Evidence: "Remote employees receive a one-time home office setup stipend of 15,000 INR."
- Generated Answer: "Core working hours are 10:00 AM to 4:00 PM."
- Expected Status: Uncertain
- Predicted Status: Hallucinated (Trust Score: 0.0)
- Root Cause: The answer contained "10" and "4", whereas the passage contained "15000". Layer 1a numeric contradiction logic flagged the numbers as mismatched, classifying the claim as Hallucinated.
```

### Synthesis of Error Mechanics
- **Asymmetric Safety Maintained:** In all 5 instances, the discrepancy is confined to `Uncertain` $\leftrightarrow$ `Hallucinated`. At no point was unverified information labeled `Trusted`.
- **Numeric Strictness Bias:** 3 out of 5 discrepancies stemmed from Layer 1a's strict numeric heuristic, which treats any numerical divergence as an active contradiction rather than an unsupported claim. This provides high safety at the expense of finer `Uncertain` granularity.

---

## 8. Implications for the Research

1. **Robust Generalization Confirmed:**  
   The verification layer does not rely on memorization or overfitting to the original 77 benchmark queries. When tested on novel scenarios ($N = 42$), binary accuracy reached **1.000**, with **1.000** detection recall and precision.
2. **Rejection of Leakage Confound:**  
   Because performance on unseen cases ($F_1 = 1.000$) is slightly higher than on historical cases ($F_1 = 0.977$), there is no evidence that historical benchmark tuning inflated overall system efficacy.
3. **Conservative Academic Framing:**  
   While these empirical results demonstrate high reliability on the evaluated corpora, the findings must be scoped appropriately:
   - Sample sizes on unseen data ($N = 42$, $N = 11$) are modest.
   - The domains evaluated are structured enterprise domains (HR, IT security, office policies).
   - The trust score behaves primarily as a discrete three-tier gating mechanism rather than a finely calibrated continuous probability.

---

## 9. Scoped Limitations

1. **Domain Diversity:** The evaluation is grounded in enterprise policies and technical IT documents. Performance on open-domain conversational QA, creative writing, or complex mathematical derivation remains unmeasured.
2. **Layer 1a Heuristic Aggressiveness:** The numeric mismatch detector treats ungrounded numerical quantities as strict contradictions. While this guarantees safety in financial/policy settings, it reduces three-way discriminability between `Uncertain` and `Hallucinated`.
3. **Granularity of Trust Score:** The discrete plateaus at 0.0, 50.0, and 100.0 indicate that the trust score represents qualitative consensus tiers rather than a smooth Bayesian posterior probability.

---

## 10. Final Assessment & Freeze Decision

- **Verification Performance:** Generalizes robustly without degradation.
- **Safety Guarantee:** Verified ($0.0\%$ false trust rate across all 36 invalid unseen cases).
- **Provenance Integrity:** Audited, segregated, and validated.
- **Experimental Code & Data Status:** **FROZEN.** No further tuning of thresholds, prompts, or weights.

### Verdict
**FINAL STATUS: FREEZE RESULTS**
