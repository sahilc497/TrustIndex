# TRUST Index Validation — Provenance & Leakage Audit

## 1. Executive Summary

- **Final Audit Status**: **CLEAN WITH LIMITATIONS**
- **Recommendation**: **FREEZE WITH DISCLOSED LIMITATIONS**

This audit evaluates the provenance, test-set integrity, potential data leakage, and reproducibility of the 130-case validation benchmark used to evaluate the TRUST Index verification layer. 

The evaluation is classified as **CLEAN WITH LIMITATIONS** rather than unconditionally clean because:
1. **Historical Benchmark Overlap**: 88 of the 130 validation cases (67.7%) originated directly from the earlier 77-item development benchmark ([`data/eval_dataset.json`](file:///d:/T-index/data/eval_dataset.json)), which historically informed the Phase 1 heuristic refinement of numeric diffing and entity category rules in September 2026.
2. **Strict Test-Time Isolation**: No detector rules, thresholds, models, or formulas were altered, tuned, or retrofitted on or after the 130-case benchmark was constructed.
3. **Generalization Subset Integrity**: The benchmark incorporates 42 instances (32.3%)—comprising 11 novel out-of-taxonomy held-out entity cases and 31 newly constructed multi-clause and irrelevant-evidence cases—that were entirely unseen during rule development.
4. **Reproducibility**: The evaluation is 100% deterministic and reproduces published metrics bit-for-bit via a single CLI command.

---

## 2. Dataset Composition

- **Total Cases**: $N = 130$
- **Case-Type Distribution**:
  - `Case Type 1: Correct + Supported`: 30 cases (23.1%)
  - `Case Type 2: Incorrect + Unsupported`: 14 cases (10.8%)
  - `Case Type 3: Contradictory`: 12 cases (9.2%)
  - `Case Type 4: Partially Supported`: 12 cases (9.2%)
  - `Case Type 5: Irrelevant Evidence`: 10 cases (7.7%)
  - `Case Type 6: Negation Error`: 12 cases (9.2%)
  - `Case Type 7: Numerical Error`: 20 cases (15.4%)
  - `Case Type 8: Entity Substitution`: 20 cases (15.4%)
- **Support-Tier Breakdown**:
  - **Supported**: 30 cases (23.1%)
  - **Partially Supported**: 12 cases (9.2%)
  - **Unsupported**: 24 cases (18.5%)
  - **Contradictory**: 64 cases (49.2%)
- **Provenance Origins**:
  - `original_77` ([`data/eval_dataset.json`](file:///d:/T-index/data/eval_dataset.json)): **88 cases** (67.7%)
  - `held_out_10` ([`data/held_out_eval_dataset.json`](file:///d:/T-index/data/held_out_eval_dataset.json)): **11 cases** (8.5%)
  - `newly_constructed` (Synthesized for Types 2, 3, 4, 5): **31 cases** (23.8%)
  - `unknown`: **0 cases** (0.0%)

---

## 3. Dataset Overlap

Programmatic cross-comparison against existing project datasets reveals:

### Exact Duplicates
- **Total Exact (Query, Evidence, Answer) Duplicates**: **99 cases**
  - **24 cases**: Exact match to `correct_answer` entries from the 77-item benchmark (evaluated under Case Type 1).
  - **64 cases**: Exact match to `hallucinated_answer` entries from the 77-item benchmark (evaluated under Case Types 2, 3, 6, 7, 8).
  - **6 cases**: Exact match to `correct_answer` entries from the 10-item held-out benchmark.
  - **5 cases**: Exact match to `hallucinated_answer` entries from the 10-item held-out benchmark.

### Likely / Semantic Duplicates
- **Likely Duplicates**: **0 cases**
- The remaining 31 cases are newly constructed compound sentences, unevidenced additions, or cross-section passage pairings that do not duplicate previous test pairs.

### Internal Query/Evidence Multiplexing
- Within the 130 cases, **35 unique (Query, Evidence) pairs** are evaluated under multiple distinct answer conditions (76 total cases involved).
- *Methodological Rationale*: Evaluating the exact same context under both an authentic answer (Case 1) and a corrupted answer (Cases 6–8) tests whether the detector's score shift is caused by the answer's factual content rather than retrieval or topical bias.

---

## 4. Ground Truth Provenance

For all 130 cases, ground-truth labels were established independently:
1. **Source Corpus Grounding**: Every expected status (`Trusted`, `Uncertain`, `Hallucinated`) was directly verified against the raw policy text in `hr_policy_leave.txt`, `hr_policy_reimbursement.txt`, `hr_policy_wfh.txt`, or `it_security_policy.txt`.
2. **Zero Circular Labeling**: No labels were generated or validated using TRUST Index detector outputs. 
3. **Explicit Operational Definition**:
   - `Trusted` / `Supported`: Every propositional clause is fully entailed by the cited passage.
   - `Uncertain` / `Unsupported`: The answer asserts unevidenced claims that are neither entailed nor explicitly contradicted, or presents a compound statement with one supported and one unevidenced clause.
   - `Hallucinated` / `Contradictory`: The answer makes assertions that directly conflict with numerical limits, explicit negative prohibitions, or designated authority slots in the text.

---

## 5. Detector Development Contamination

| Aspect | Historical Status | Post-Validation Changes | Contamination Assessment |
|---|---|---|---|
| **Classification Thresholds** | Fixed at $\ge 80$ (Trusted) and $\ge 50$ (Uncertain) on 14-09-2026 | None | **NO** (Pre-established operational baseline) |
| **Contradiction Rules** | Layer 1a (Numeric) and Layer 1b (Entity) implemented 14-09-2026 | None | **YES for 88 historical cases**; **NO for 42 unseen cases** |
| **Model Selection** | SBERT (`all-MiniLM-L6-v2`) and `roberta-large-mnli` selected 14-09-2026 | None | **NO** |
| **Scoring Formula** | Normalized graph consensus $[-1, 1] \to [0, 100]$ implemented 14-09-2026 | None | **NO** |
| **Claim Aggregation** | Weakest-link $\min()$ implemented 14-09-2026 | None | **NO** |

**Evidence from Repository Timestamps**:
All core detector files ([`src/detector.py`](file:///d:/T-index/src/detector.py), [`src/contradiction.py`](file:///d:/T-index/src/contradiction.py), [`src/trust_score.py`](file:///d:/T-index/src/trust_score.py), [`src/similarity.py`](file:///d:/T-index/src/similarity.py), [`src/evidence_graph.py`](file:///d:/T-index/src/evidence_graph.py)) carry filesystem modification timestamps of **14 September 2026**. Zero modifications were made to detector logic during the execution of this 130-case validation phase.

---

## 6. Circularity Assessment

### 1. Error Taxonomy Alignment
The benchmark evaluates 8 specific case types (numeric substitutions, negations, entity swaps, causal distortions, unevidenced additions). The detector was architected with modular components (Layer 1a for numbers, Layer 1b for entities, Layer 2 for NLI/negation).
- **Assessment**: This alignment is a deliberate design feature of targeted unit-testing and component ablation (demonstrating what happens when individual layers are disabled). 
- **Methodological Limitation**: If presented as a completely blind open-domain evaluation, this structural alignment would be circular. However, as an architectural ablation study on targeted enterprise policy failure modes, it isolates component contributions.

### 2. Label Independence
- Labels were not determined by threshold fitting or model consensus. Ground-truth rationales document the explicit factual basis in the raw text for every individual case.

---

## 7. Source Corpus Overlap

- All 130 validation items are situated within four enterprise policy text documents:
  - `hr_policy_leave.txt`
  - `hr_policy_reimbursement.txt`
  - `hr_policy_wfh.txt`
  - `it_security_policy.txt`

### Distinguishing Leakage vs. Shared Corpus:
- **Acceptable (Shared Domain Corpus)**: Evaluating new test cases (e.g. Case 4 compound statements, Case 5 irrelevant passages) within the same domain knowledge corpus is standard methodology for domain-specific RAG verification.
- **Potential Leakage (Instance Reuse)**: 88 cases reuse the exact query and answer instances from the development set. These 88 cases cannot be claimed as an independent out-of-sample evaluation.
- **Strong Leakage (Detector Retrofitting)**: **Absent**. No heuristics or rules were added or modified to accommodate failures on the 130-case validation set.

---

## 8. Reproducibility Audit

- **Execution Command**:
  ```powershell
  python run_trust_validation.py
  ```
- **Audit Verification Result**: **PASS**
  - All dependencies are listed in [`requirements.txt`](file:///d:/T-index/requirements.txt).
  - The script executes end-to-end on CPU without external API keys or network dependencies.
  - Verification run reproduces all metrics in [`results/trust_validation/metrics.json`](file:///d:/T-index/results/trust_validation/metrics.json) bit-for-bit:
    - 3-Way Overall Accuracy: **0.846**
    - Binary Verification Accuracy: **0.977**
    - Binary Supported Precision: **1.000**
    - Binary Detection Recall: **1.000**
    - Kruskal-Wallis Statistic: $H = 100.5568, p = 1.18 \times 10^{-21}$

---

## 9. Risks & Limitations for Academic Reporting

1. **Disclosure of Development Set Re-use**: The thesis/paper must explicitly state that the 130-case validation set includes 88 instances from the initial development benchmark. Authors should report metrics on the full 130 cases alongside a disaggregated breakdown of the 42 strictly unseen cases (11 novel entity + 31 newly constructed cases).
2. **Curated Slot Taxonomy vs. Open-Domain NER**: Layer 1b entity matching relies on pre-defined domain categories. Performance on open-domain corpora will require dynamic Named Entity Recognition.
3. **Weakest-Link Edge Conservatism**: In Case Types 2, 4, and 5 (expected `Uncertain`), answers containing arbitrary numerical parameters frequently trigger Layer 1a numeric mismatch, escalating predictions from `Uncertain` (50.0) to `Hallucinated` (0.0). While binary classification remains 100% correct (`Unsupported`), multi-class precision for `Uncertain` reflects this conservative shift.

---

## 10. Final Recommendation

### **FREEZE WITH DISCLOSED LIMITATIONS**

**Rationale**:
The detector implementation, thresholds, and experimental outputs are fully frozen, deterministic, and verifiable. Because 88 cases overlap with early developmental testing while 42 cases are strictly unseen, scientific transparency requires that the thesis/paper report the results with full disclosure of benchmark provenance rather than claiming an entirely independent blind evaluation. No further model or dataset tuning should be performed.
