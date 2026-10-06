# Chapter 4 — Experimental Results and Discussion

---

## 4.1 Experimental Overview

This investigation addresses two complementary research questions concerning factual reliability in retrieval-augmented generation (RAG) systems:

1. **Generation-Stage Interventions:** Can retrieval-level enhancements (dense semantic re-ranking) and prompting-level constraints (explicit citation demands, conciseness constraints) reliably mitigate hallucination rates during the generation phase?
2. **Post-Generation Verification:** Can an independent verification layer—the **TRUST Index**—reliably detect unsupported, factual-distorting, or contradictory claims in generated responses without modifying the underlying generation architecture?

These two evaluations operate at distinct stages of the RAG information-processing pipeline:

```text
Knowledge Retrieval / Generation Stage
                 ↓
            RAG Output
                 ↓
    TRUST Verification Stage (Independent)
                 ↓
     Trust Score + Evidence Graph + Operational Status
```

Crucially, the TRUST Index is evaluated strictly as an **independent post-generation verification framework**. It does not intervene during token autoregression, nor does it claim to prevent generation-time hallucinations. Instead, it serves as an analytical guardrail that inspects candidate answers, decomposes them into atomic verifiable claims, aligns them against retrieved passage context, tests for semantic contradiction and support, and produces an interpretable trust score ($0.0 - 100.0$) alongside a three-way categorical verdict (`Trusted`, `Uncertain`, `Hallucinated`).

---

## 4.2 RAG Generation Experiments

To investigate generation-stage grounding, a controlled series of five experimental conditions (Conditions A–E) was executed using an enterprise policy corpus comprising human resources, travel reimbursement, and remote work regulations. All conditions shared an identical generator backbone—`TinyLlama/TinyLlama-1.1B-Chat-v1.0`—with generation bounded by `max_new_tokens = 110`. Across all 77 evaluated evaluation queries, the generator architecture remained frozen to guarantee zero model-discrepancy confounds.

The tested RAG conditions are defined as follows:

- **Condition A (Baseline RAG):** Standard sparse lexical retrieval (TF-IDF, Top-2 passages) paired with a standard zero-shot instructional system prompt.
- **Condition B (Re-Ranking Only):** Two-stage retrieval pairing initial TF-IDF candidate selection with Sentence-BERT (`all-MiniLM-L6-v2`) cross-entropy re-ranking, presented with the baseline prompt.
- **Condition C (Citation Prompting Only):** Baseline TF-IDF retrieval paired with a strict citation prompt instructing the model to ground every claim with explicit section citations (`[Section X]`) and refuse ungrounded queries.
- **Condition D (Combined Intervention):** The full dual intervention combining Sentence-BERT re-ranking with strict citation prompting.
- **Condition E (Conciseness-Constrained RAG):** Baseline TF-IDF retrieval paired with an explicit conciseness constraint instructing the model to generate concise 1–2 sentence factual answers, specifically targeting output length inflation and claim-multiplication confounds.

### Summary of RAG Experimental Results ($N = 77$)

The table below reports the empirical performance across all five frozen conditions evaluated on the benchmark:

| Condition | Retrieval Method | Prompting Strategy | Mean Trust Score | Claims / Answer | Truncation Rate (%) | Hallucination Rate (%) | McNemar vs. Baseline ($p$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Condition A** | TF-IDF (Top-2) | Standard Instructional | 56.90 | 1.53 | 1.3% | 23.4% ($18/77$) | — |
| **Condition B** | SBERT Re-ranking | Standard Instructional | 49.79 | 1.58 | 2.6% | 27.3% ($21/77$) | $p = 0.4531$ |
| **Condition C** | TF-IDF (Top-2) | Strict Citation Prompt | 56.57 | 1.68 | 1.3% | 22.1% ($17/77$) | $p = 1.0000$ |
| **Condition D** | SBERT Re-ranking | Strict Citation Prompt | 49.53 | 1.92 | 3.9% | 31.2% ($24/77$) | $p = 0.2863$ |
| **Condition E** | TF-IDF (Top-2) | 1–2 Sentence Concise | 54.85 | 1.16 | 0.0% | 24.7% ($19/77$) | $p = 1.0000$ |

---

## 4.3 RAG Statistical Results

To determine whether observed differences in hallucination rates reflected statistically meaningful improvements or stochastic variation, pairwise McNemar tests with Edwards continuity correction and exact binomial tests were executed across all paired binary outcomes ($\text{Hallucinated}$ vs. $\text{Not-Hallucinated}$).

### Key Pairwise Significance Tests ($N = 77$)

1. **Condition A vs. Condition B (Re-Ranking Effect):**
   - Hallucination rate shifted from $23.4\%$ ($18/77$) to $27.3\%$ ($21/77$).
   - Discordant pairs: $n = 7$ ($b = 2$, $c = 5$). $\chi^2 = 0.5714$, exact binomial $p = 0.4531$ (Not Significant).
2. **Condition A vs. Condition C (Citation Prompt Effect):**
   - Hallucination rate shifted from $23.4\%$ ($18/77$) to $22.1\%$ ($17/77$).
   - Discordant pairs: $n = 13$ ($b = 7$, $c = 6$). $\chi^2 = 0.0000$, exact binomial $p = 1.0000$ (Not Significant).
3. **Condition A vs. Condition D (Combined Intervention):**
   - Hallucination rate worsened from $23.4\%$ ($18/77$) to $31.2\%$ ($24/77$).
   - Discordant pairs: $n = 22$ ($b = 8$, $c = 14$). $\chi^2 = 1.1364$, exact binomial $p = 0.2863$ (Not Significant).
4. **Condition C vs. Condition D (Re-ranking under Citation Prompt):**
   - Discordant pairs: $n = 9$ ($b = 1$, $c = 8$). $\chi^2 = 4.0000$, exact binomial $p = 0.0391$ (**Statistically Significant Degradation**). SBERT re-ranking under citation prompting introduced 8 new hallucinated outputs while correcting only 1.
5. **Condition A vs. Condition E (Addressing the Scoring/Length Confound):**
   - In Conditions A–D, answers occasionally generated multiple sentences, raising concerns that higher claim counts artificially inflated per-query hallucination risk.
   - Condition E successfully reduced mean atomic claims per answer from **1.53 to 1.16** and eliminated token truncation entirely ($1.3\% \to 0.0\%$).
   - However, the observed hallucination rate was unchanged: **$23.4\%$ ($18/77$) in Condition A vs. $24.7\%$ ($19/77$) in Condition E**.
   - Discordant pairs: $n = 19$ ($b = 10$, $c = 9$). $\chi^2 = 0.0000$, exact binomial $p = 1.0000$ (Not Significant).
   - In the expanded 87-query cohort (`stats_87_combined`), hallucination was $20.7\%$ in A vs. $21.8\%$ in E ($p = 1.0000$).

### Methodological Distinction: Scoring Confound vs. Factual Behavior

It is critical to distinguish between the **scoring mechanics** and the **underlying hallucination behavior**:
- By enforcing conciseness in Condition E, the claim-multiplication confound was resolved: each response contained fewer surface propositions, reducing the surface area evaluated by the verifier.
- Despite this strict structural reduction, the frequency of generating factually unsupported or contradictory statements persisted at virtually identical levels.
- Therefore, the empirical evidence demonstrates that **reducing the claim-count/scoring confound did not produce a corresponding reduction in the observed hallucination rate**.

---

## 4.4 Interpretation of the RAG Results

In evaluating these findings, strict scientific restraint is necessary:

> **Within the evaluated experimental setup, retrieval- and prompting-level interventions did not reliably reduce hallucination.**

This finding must **not** be extrapolated beyond its empirical boundaries:
- It does **not** demonstrate that "RAG cannot be grounded."
- It does **not** prove that "retrieval augmentation is universally ineffective at reducing hallucinations."
- It does **not** characterize larger frontier language models (e.g., GPT-4, Gemini 1.5 Pro) or enterprise retrieval engines (e.g., ColBERT, dense hybrid indexes).

Rather, the result is specifically scoped to:
1. Small-scale instruction-tuned language models (1B parameter class) operating under strict generation bounds.
2. Dense policy documents where queries require exact numerical, temporal, and role boundary matching.
3. Standard retrieval (TF-IDF and bi-encoder SBERT) and prompting strategies (instructional, in-context citation, length constraints).

Within this operational regime, retrieval-level enhancements failed to suppress hallucinations because generation errors frequently arose from misattribution of retrieved numbers, conflation of eligibility rules across adjacent sections, or hallucinated details introduced in the absence of explicit passage knowledge. This outcome strongly **motivates an independent verification layer**: when generation-time interventions fail to prevent ungrounded outputs, post-generation detection becomes necessary to protect downstream systems.

---

## 4.5 TRUST Index Validation Dataset

To rigorously evaluate the TRUST Index verification layer independently of the RAG generation experiments, a controlled 130-case validation benchmark was compiled in `data/trust_validation_dataset.json`.

### Benchmark Composition ($N = 130$)

The dataset evaluates four fundamental support categories across nine explicit case types:
- **Supported ($N = 30$):** Fully grounded, factually accurate statements directly entailed by source policy passages (Case Type 1).
- **Partially Supported ($N = 12$):** Compound assertions containing one verified claim and one unsupported or speculative claim (Case Type 4).
- **Unsupported ($N = 24$):** Assertions neither confirmed nor directly contradicted by evidence, including ungrounded extrapolations and irrelevant evidence (Case Types 2 and 5).
- **Contradictory ($N = 64$):** Assertions directly conflicting with source passages, encompassing direct factual conflicts, numeric substitutions, date/tenure alterations, entity substitutions, and polarity inversions (Case Types 3, 6, 7, 8, and 9).

### Provenance Audit Disclosure

A full provenance and leakage audit (`results/trust_validation/PROVENANCE_AUDIT_REPORT.md`) examined all 130 cases:
- **Historical Benchmark Cases ($N = 88$):** Reused from the original 77-case evaluation dataset (`original_77`).
- **Previously Held-Out Cases ($N = 11$):** Originating from an independent 10-item held-out IT security evaluation set (`held_out_10`).
- **Newly Constructed Cases ($N = 31$):** Authoritatively created edge cases specifically targeting partial support, irrelevant context, and strict contradictions (`newly_constructed`).
- **Exact Duplicates:** 99 cases shared exact query, evidence, and answer text with historical benchmark entries.

**Critical Academic Note:** Because 88 of the 130 cases originated from historical benchmarks utilized during initial exploratory pipeline development, the full $N = 130$ benchmark **cannot and must not be characterized as an independent test set**. Its results represent a controlled verification benchmark subject to known provenance limitations, which are explicitly addressed through isolated unseen-subset evaluations (Section 4.10).

---

## 4.6 TRUST Index Full Validation Results

The TRUST Index was evaluated on the full 130-case validation benchmark under frozen hyperparameters ($T_{\text{trusted}} = 80.0$, $T_{\text{hallucinated}} = 30.0$).

### Three-Way Classification Performance ($N = 130$)

In three-way evaluation, the verifier assigns one of three operational states: `Trusted` (valid and fully grounded), `Uncertain` (insufficient evidence or partial grounding), or `Hallucinated` (demonstrably contradictory or ungrounded):

- **Overall Accuracy:** **0.846** ($110 / 130$)
- **Macro Precision:** **0.863**
- **Macro Recall:** **0.826**
- **Macro F1:** **0.840**

#### Per-Class Performance Breakdown

| Class | Support ($N$) | TP | FP | FN | TN | Precision | Recall | F1 | Specificity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trusted** | 30 | 27 | 0 | 3 | 100 | **1.000** | **0.900** | **0.947** | **1.000** |
| **Uncertain** | 36 | 23 | 7 | 13 | 87 | 0.767 | 0.639 | 0.697 | 0.926 |
| **Hallucinated** | 64 | 60 | 13 | 4 | 53 | 0.822 | 0.938 | 0.876 | 0.803 |

### Binary Detection Performance ($N = 130$)

When mapped to an operational binary gating task—distinguishing fully verified outputs (`Trusted`) from unverified or invalid outputs (`Uncertain` or `Hallucinated`):

- **Binary Classification Accuracy:** **0.977** ($127 / 130$)
- **Detection Perspective (Flagging Invalid Outputs):**
  - **Precision:** **0.971** ($100 / 103$)
  - **Recall:** **1.000** ($100 / 100$)
  - **F1 Score:** **0.985**
  - **Specificity:** **0.900** ($27 / 30$)
- **Supported Perspective (Passing Valid Outputs):**
  - **Precision:** **1.000** ($27 / 27$)
  - **Recall:** **0.900** ($27 / 30$)
  - **F1 Score:** **0.947**
  - **Specificity:** **1.000** ($100 / 100$)

### Asymmetric Safety Property

A paramount design requirement for enterprise deployment is that ungrounded or contradictory outputs must never receive an uncritical seal of approval:

$$\text{Safety Violation Rate} = \frac{\text{Invalid Outputs Predicted as Trusted}}{\text{Total Invalid Outputs}} = \frac{0}{100} = \mathbf{0.0\%}$$

Across all 100 non-supported cases in the benchmark, **zero** invalid outputs were classified as `Trusted`. All three binary classification errors were conservative false alarms (supported statements classified as `Uncertain`, score 50.0). In mission-critical enterprise environments, an asymmetric error profile where failures manifest as cautious escalations rather than silent acceptances of false claims is highly desirable.

---

## 4.7 Trust Score Analysis

The TRUST Index computes a continuous scalar score ($0.0 - 100.0$) aggregated across atomic claims.

### Score Distributions Across Ground-Truth Categories

| Support Category | Sample Size ($N$) | Mean Score | Median Score | Std Dev | Min | Max | IQR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Supported** | 30 | **95.00** | 100.0 | 15.26 | 50.0 | 100.0 | 0.0 |
| **Partially Supported** | 12 | **41.67** | 50.0 | 19.46 | 0.0 | 50.0 | 0.0 |
| **Unsupported** | 24 | **27.08** | 50.0 | 25.45 | 0.0 | 50.0 | 50.0 |
| **Contradictory** | 64 | **3.12** | 0.0 | 12.20 | 0.0 | 50.0 | 0.0 |

When examining the overall predicted status classes:
- **`Trusted` Class ($N = 27$):** Mean $= 100.0$
- **`Uncertain` Class ($N = 36$ aggregate):** Mean $= \mathbf{31.94}$
- **`Hallucinated` Class ($N = 64$ aggregate):** Mean $= \mathbf{3.12}$

### Discrete Plateaus and Calibration Caveat

Crucially, **the trust score does not behave as a smoothly calibrated Bayesian probability**. 
- A Shapiro-Wilk test strongly rejects score normality ($W = 0.7188, p = 1.82 \times 10^{-14}$).
- Instead, scores cluster sharply at discrete structural plateaus:
  - **$100.0$:** Complete entailment across all constituent claims.
  - **$50.0$:** Neutral NLI consensus, partial support, or ungrounded claims lacking explicit contradiction.
  - **$0.0$:** Flagged contradiction via Layer 1 heuristics or Layer 2 NLI models.
- Consequently, the metric represents **discrete evidence-state separation**, not continuous probabilistic calibration.

### Non-Parametric Separation Analysis

A Kruskal-Wallis $H$-test across the four support categories confirms massive global separation:
- **$H$-statistic:** **100.56**
- **$p$-value:** **$1.18 \times 10^{-21}$**
- **Effect Size ($\eta^2$):** **0.7743**

Post-hoc pairwise Mann-Whitney $U$ tests with Holm-Bonferroni family-wise error correction revealed significant separation across five of the six category pairs:
1. **Supported vs. Contradictory:** $U = 1914.0$, $p_{\text{adj}} = 3.73 \times 10^{-19}$ (Significant)
2. **Supported vs. Unsupported:** $U = 700.5$, $p_{\text{adj}} = 5.43 \times 10^{-10}$ (Significant)
3. **Partially Supported vs. Contradictory:** $U = 680.0$, $p_{\text{adj}} = 1.46 \times 10^{-09}$ (Significant)
4. **Supported vs. Partially Supported:** $U = 345.0$, $p_{\text{adj}} = 1.47 \times 10^{-07}$ (Significant)
5. **Unsupported vs. Contradictory:** $U = 1136.0$, $p_{\text{adj}} = 9.56 \times 10^{-07}$ (Significant)
6. **Partially Supported vs. Unsupported:** $U = 186.0$, $p_{\text{raw}} = 0.0943$, **$p_{\text{adj}} = 0.0943$ (NOT Statistically Significant)**.

**Scientific Disclosure:** The lack of statistical significance between Partially Supported and Unsupported ($p = 0.0943$) is a vital negative finding. Both categories hover predominantly around the neutral score plateau ($50.0$), showing that the current pipeline cannot reliably separate unsupported claims from partially supported claims based on continuous trust scores alone.

---

## 4.8 TRUST Index Ablation Study

To evaluate the structural contribution of each architectural layer, four controlled ablation variants were evaluated against the full pipeline on the 130-case benchmark:

1. **Ablation 1 (No Contradiction Detection):** Removal of Layer 1 (numeric/date heuristics) and Layer 2 (RoBERTa NLI contradiction testing).
2. **Ablation 2 (No Semantic Similarity):** Removal of Sentence-BERT semantic similarity gating.
3. **Ablation 3 (No Graph Consensus):** Removal of bipartite evidence graph propagation, using direct max-consensus heuristics instead.
4. **Ablation 4 (Alternative Claim-Score Aggregation):** Methodological clarification: rather than removing propagation, this variant replaces the conservative weakest-link bottleneck ($\min_{c} S_c$) with an arithmetic mean ($\frac{1}{M}\sum S_c$).

### Ablation Performance Summary ($N = 130$)

| Variant | Binary Accuracy | Binary Precision | Binary Recall | Binary F1 | Mean Trust Score | $\Delta$ Accuracy | $\Delta$ Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Pipeline** | **0.977** | **1.000** | **0.900** | **0.947** | **32.31** | — | — |
| **No Contradiction** | 0.969 | 0.964 | 0.900 | 0.931 | **60.77** | $-0.008$ | $+28.46$ |
| **No Similarity** | 0.977 | 1.000 | 0.900 | 0.947 | 30.77 | $0.000$ | $-1.54$ |
| **No Graph Consensus** | 0.977 | 1.000 | 0.900 | 0.947 | 32.15 | $0.000$ | $-0.16$ |
| **Mean Aggregation** | 0.977 | 1.000 | 0.900 | 0.947 | 35.19 | $0.000$ | $+2.88$ |

---

## 4.9 Statistical Interpretation of Ablations

When evaluated strictly by binary classification accuracy, the ablation variants show minimal surface changes (Accuracy shifts by at most $-0.008$). However, analyzing the continuous score distributions reveals deeper dynamics:

### Paired Statistical Tests (Ablation vs. Full Pipeline)

- **No Contradiction Detection:**
  - McNemar test: 1 discordant pair ($b = 1$, $c = 0$), $p = 1.0000$ (Not Significant).
  - Wilcoxon signed-rank test: $W = 0.0$, **$p = 2.10 \times 10^{-17}$** across 73 differing pairs (**Highly Significant**). Removing contradiction detection caused the mean score across contradictory cases to surge from $3.12$ to $60.77$, severely degrading distributional safety.
- **No Semantic Similarity:**
  - McNemar test: 0 discordant pairs, $p = 1.0000$.
  - Wilcoxon signed-rank test: $W = 0.0$, **$p = 0.0455$** across 4 differing pairs (**Statistically Significant**).
- **No Graph Consensus:**
  - McNemar test: 0 discordant pairs, $p = 1.0000$.
  - Wilcoxon signed-rank test: $W = 0.0$, $p = 0.3173$ across 1 differing pair (Not Significant).
- **Alternative Mean Aggregation:**
  - McNemar test: 0 discordant pairs, $p = 1.0000$.
  - Wilcoxon signed-rank test: $W = 0.0$, **$p = 0.0013$** across 12 differing pairs (**Statistically Significant**).

### Core Takeaway

> **Binary classification performance alone does not fully capture the contribution of individual verification components.**

The multi-layer architecture contains redundant protective layers: when one component is removed, secondary thresholds frequently prevent binary misclassification. However, continuous distributional metrics confirm that contradiction detection and score aggregation strategies are vital to maintaining distinct trust levels.

---

## 4.10 Unseen-Subset Validation

To address the provenance limitation identified in Section 4.5, an isolated analysis was conducted strictly on the **$N = 42$ unseen cases**—completely excluding all 88 historical benchmark cases:

- **Subset A (Previously Held-Out, $N = 11$):** IT security cases from `held_out_10`.
- **Subset B (Newly Constructed, $N = 31$):** Novel edge cases from `newly_constructed`.
- **Subset C (Combined Unseen, $N = 42$):** Subsets A + B.

### Unseen Performance vs. Full Benchmark

| Metric | Full Benchmark ($N = 130$) | Combined Unseen ($N = 42$) | Held-Out Set ($N = 11$) | New Cases ($N = 31$) |
| :--- | :---: | :---: | :---: | :---: |
| **Binary Accuracy** | 0.977 | **1.000** | **1.000** | **1.000** |
| **Detection Precision** | 0.971 | **1.000** | **1.000** | **1.000** |
| **Detection Recall** | 1.000 | **1.000** | **1.000** | **1.000** |
| **Detection F1** | 0.985 | **1.000** | **1.000** | **1.000** |
| **Supported Recall** | 0.900 | **1.000** | **1.000** | N/A ($0/0$) |
| **Invalid $\to$ Trusted (Safety)** | **0/100 (0.0%)** | **0/36 (0.0%)** | **0/5 (0.0%)** | **0/31 (0.0%)** |
| **Three-Way Accuracy** | 0.846 | **0.881** | **0.909** | **0.871** |

### Three-Way Confusion Matrix (Combined Unseen, $N = 42$)

```text
                  Predicted Status
Expected Status   Trusted   Uncertain   Hallucinated
Trusted              6          0             0
Uncertain            0         21             4
Hallucinated         0          1            10
```

### Nature of Unseen Discrepancies

Across all 42 unseen cases, exactly 5 cases ($11.9\%$) exhibited three-way classification discrepancies:
- **Zero** discrepancies crossed the critical `Trusted` boundary.
- **All 5 discrepancies occurred strictly between `Uncertain` and `Hallucinated`**:
  - 4 expected `Uncertain` cases were classified as `Hallucinated`.
  - 1 expected `Hallucinated` case was classified as `Uncertain`.
- In binary operational terms, detection accuracy on the unseen subset was **1.000** ($42 / 42$).

---

## 4.11 Unseen-Subset Interpretation

In interpreting the unseen validation results, disciplined academic restraint must be maintained:

> **The unseen-subset results provide additional evidence that the observed detection behavior is not solely attributable to reuse of the historical benchmark.**

Careful boundaries must be observed:
- We do **not** claim this "proves universal generalization."
- We do **not** claim this "completely eliminates data contamination."
- We do **not** claim this "rules out benchmark memorization across all possible domains."

The unseen sample size ($N = 42$) is modest. Nevertheless, the fact that detection performance remained at $1.000$ binary accuracy and $1.000$ detection recall confirms that the verifier functions effectively on novel queries and unencountered syntactic structures within the evaluated domain.

---

## 4.12 Error Analysis

Across the entire 130-case validation benchmark, exactly 20 cases exhibited three-way classification discrepancies (`results/trust_validation/error_analysis.json`).

### Error Categorization Breakdown

1. **False Alarms on Ground-Truth Supported Answers ($3$ Cases):**
   - Cases: `val_c1_reimb_07`, `val_c1_wfh_03`, `val_c1_wfh_08`.
   - Expected: `Trusted`; Predicted: `Uncertain` (Score: 50.0).
   - Mechanism: RoBERTa NLI returned low neutral confidence on valid claims involving complex negation or scope qualifiers (e.g., *"not available to employees on the standard hybrid arrangement"*), defaulting to neutral consensus.
2. **Strict Escalation of Unsupported Claims to Hallucinated ($11$ Cases):**
   - Cases: 7 historical unsupported cases, 2 partial support (`val_c4_part_01`, `val_c4_part_09`), and 2 irrelevant evidence cases (`val_c5_irrel_02`, `val_c5_irrel_07`).
   - Expected: `Uncertain`; Predicted: `Hallucinated` (Score: 0.0).
   - Mechanism: Layer 1a numeric mismatch flags any numerical divergence (e.g., claiming 100,000 INR when evidence states 5,000 INR) as an active contradiction rather than an unsupported claim. Similarly, RoBERTa NLI judged "unlimited sabbaticals" as directly contradictory to annual leave text.
3. **Under-Escalation of Contradictions to Uncertain ($6$ Cases):**
   - Cases: 5 historical causal/tenure distortions and 1 held-out entity substitution (`val_c8_heldout_03`).
   - Expected: `Hallucinated`; Predicted: `Uncertain` (Score: 50.0).
   - Mechanism: When entity swaps fall outside the rule-based keyword taxonomy (e.g., substituting "Microsoft Teams" for "Slack" in a negative prohibition), RoBERTa NLI evaluates the relationship as NEUTRAL rather than CONTRADICTION, resulting in a score of 50.0 instead of 0.0.

### Crucial Error Boundary Insight

> **The dominant remaining weakness of the TRUST Index is the boundary distinction between Uncertain and Hallucinated, rather than failure to detect invalid outputs as a whole.**

The system reliably separates valid outputs from invalid outputs. Its ambiguity lies in determining whether an invalid claim is merely ungrounded (`Uncertain`) or actively contradictory (`Hallucinated`).

---

## 4.13 Provenance and Validation Limitations

Full scientific transparency requires explicit disclosure of benchmark constraints:

1. **Substantial Historical Overlap:** 88 of the 130 validation cases ($67.7\%$) originated from the historical 77-case benchmark used during earlier exploratory phases. Furthermore, 99 cases shared exact textual matches with prior benchmark records.
2. **Unseen Sample Constraints:** Only 42 cases were fully unseen relative to historical tuning, with only 11 cases originating from an independent external held-out set.
3. **Benchmark-Mechanism Alignment:** The validation taxonomy deliberately incorporates error categories (numeric substitutions, date changes, entity swaps, negations) that align with mechanisms explicitly implemented in the multi-layer verifier. While essential for controlled unit evaluation, this alignment evaluates known defensive mechanisms rather than unconstrained open-domain failure modes.
4. **Independent Ground Truth:** The provenance audit confirmed that ground-truth labels were independently checked against source policy passages, with zero label errors identified.
5. **Frozen Development:** Thresholds, detector logic, and scoring formulas were strictly frozen prior to running the validation benchmark and remained unaltered throughout.

---

## 4.14 Discussion

The synthesis of generation and verification results yields six core findings:

- **Finding 1 (Retrieval/Prompting Limitation):** Within the evaluated setup, retrieval- and prompting-level interventions did not reliably reduce hallucination.
- **Finding 2 (Verification Effectiveness):** The TRUST Index detected unsupported and contradictory outputs with high binary accuracy ($0.977$ full, $1.000$ unseen).
- **Finding 3 (Asymmetric Safety):** Zero invalid outputs bypassed the verifier into the `Trusted` category ($0 / 100$ full, $0 / 36$ unseen).
- **Finding 4 (Unseen Consistency):** Identical binary detection efficacy was maintained on the 42 unseen cases.
- **Finding 5 (Adjudication Boundary):** The primary remaining classification ambiguity occurs at the `Uncertain` $\leftrightarrow$ `Hallucinated` boundary.
- **Finding 6 (Defense-in-Depth Architecture):** These findings strongly support a layered defense-in-depth architecture:

```text
       Knowledge Retrieval
                ↓
      Autoregressive Generation
                ↓
    Independent Verification Layer
                ↓
      Explainable Trust Score
                ↓
   Downstream Action / Human Escalation
```

Post-generation verification should not be viewed as an alternative to retrieval grounding, but as an indispensable complementary defense layer.

---

## 4.15 Final Research Findings

1. Retrieval- and prompting-level interventions did not reliably reduce hallucination within the evaluated RAG configuration.
2. Correcting the claim-count/scoring confound through conciseness constraints did not materially change the observed hallucination rate.
3. The TRUST Index provided strong binary detection performance for identifying ungrounded generation outputs.
4. No invalid output was classified as `Trusted` across the entire validation benchmark, satisfying the asymmetric safety invariant.
5. Strong detection performance was retained on the unseen $N = 42$ validation partition.
6. The principal remaining classification ambiguity occurred between `Uncertain` and `Hallucinated` verdicts.
7. Verification-layer detection provides a viable complementary mechanism for improving operational RAG reliability within the evaluated setting.

---

## 4.16 Research Claim — FINAL WORDING

> **Within the evaluated experimental setup, retrieval- and prompting-level interventions did not reliably reduce hallucination in the tested RAG configuration. In contrast, the TRUST Index provided an independent post-generation verification layer that reliably identified unsupported or contradictory outputs, including on previously unseen validation cases. These results support the use of verification as a complementary layer for improving the reliability of RAG-based generation, rather than implying that retrieval or prompting alone is universally insufficient.**

---

## 4.17 Limitations and Future Work

### Limitations
- **Model Scale:** The generation experiments evaluated a small-scale language model (`TinyLlama-1.1B`). Scaling behavior in larger parameter regimes remains uncharacterized.
- **Corpus Breadth:** Evaluation was restricted to a single enterprise policy domain (HR, travel, IT security).
- **Benchmark Overlap:** 88 of 130 validation cases share provenance with historical benchmarks, leaving a modest unseen sample ($N = 42$).
- **Taxonomy Alignment:** The validation taxonomy reflects designed detector mechanisms.
- **Three-Way Ambiguity:** Distinguishing neutral ungrounded claims from active contradictions remains challenging.
- **Discrete Scoring:** The trust score exhibits discrete plateaus (0, 50, 100) rather than a continuous probability density.
- **Model Dependencies:** The pipeline relies on off-the-shelf Sentence-BERT and RoBERTa-large-MNLI models, inheriting their inductive biases.

### Future Research Directions
- Investigating verification performance across frontier 70B+ parameter models.
- Evaluating external multi-domain benchmarks (e.g., HaluEval, RAGTruth).
- Incorporating continuous calibration techniques (e.g., conformal prediction, temperature scaling).
- Enhancing NLI sensitivity to fine-grained semantic entities and implicit negations.
