# Executive Summary — TRUST Index Research Findings

---

## Problem

Retrieval-Augmented Generation (RAG) systems frequently generate factually inaccurate, ungrounded, or contradictory responses despite retrieving reference text. This study investigated whether retrieval- and prompting-level interventions (dense re-ranking, explicit citation prompting, conciseness constraints) can reliably mitigate generation-time hallucinations, and whether an independent post-generation verification framework—the **TRUST Index**—can reliably identify invalid responses across atomic claims without intervening in the generation model.

---

## Experiment 1 — RAG Generation Interventions

Five controlled RAG conditions (Conditions A–E) were tested using a frozen generator (`TinyLlama-1.1B`) on 77 enterprise-policy queries. Neither dense Sentence-BERT re-ranking ($27.3\%$ hallucination, $p = 0.4531$) nor strict citation prompting ($22.1\%$ hallucination, $p = 1.0000$) produced a statistically significant reduction in hallucinations compared to the baseline ($23.4\%$). When a strict 1–2 sentence constraint was imposed in Condition E, the claim-count confound was resolved (mean claims dropped from $1.53$ to $1.16$, truncation dropped from $1.3\%$ to $0.0\%$), yet the hallucination rate remained essentially unchanged at $24.7\%$ ($p = 1.0000$). Generation-stage interventions failed to resolve factual distortions within the evaluated setting.

---

## Experiment 2 — TRUST Index Verification

An independent verification layer combining exact numeric/date heuristics, Sentence-BERT semantic similarity gating, RoBERTa-large-MNLI cross-examination, bipartite graph consensus, and weakest-link score aggregation was evaluated across a 130-case controlled validation benchmark. The framework achieved a binary classification accuracy of **0.977**, Detection Precision of **0.971**, Detection Recall of **1.000**, and an asymmetric safety violation rate of **0.0%** ($0/100$ invalid cases labeled Trusted). On an isolated unseen validation partition of $N = 42$ cases (excluding all 88 historical benchmark cases), binary accuracy reached **1.000** with **0/36** safety violations.

---

## Strongest Evidence (Top 5 Numerical Findings)

1. **RAG Intervention Invariance:** Reducing atomic claim volume from $1.53$ to $1.16$ claims/answer yielded an identical hallucination rate ($23.4\%$ in Condition A vs. $24.7\%$ in Condition E, exact McNemar $p = 1.0000$).
2. **Binary Verification Detection:** Across the full 130-case validation benchmark, the verifier achieved **0.977** binary accuracy, **1.000** detection recall, and **0.985** detection F1.
3. **Asymmetric Safety Invariant:** Across both the full benchmark ($N = 130$) and the unseen subset ($N = 42$), **0.0%** of invalid outputs were classified as `Trusted` ($0/100$ full, $0/36$ unseen).
4. **Unseen Subset Generalization:** On the $N = 42$ unseen partition, binary accuracy was **1.000**, detection precision was **1.000**, and three-way classification accuracy was **0.881**.
5. **Significant Score Separation:** Kruskal-Wallis analysis confirmed highly significant separation of continuous trust scores across ground-truth support categories ($H = 100.56, p = 1.18 \times 10^{-21}, \eta^2 = 0.7743$).

---

## Main Contribution

This research provides a rigorous empirical evaluation demonstrating that post-generation verification serves as an effective, explainable safeguard for RAG systems where generation-stage interventions fail to eliminate factual errors. By decomposing generated responses into atomic claims, constructing bipartite evidence graphs, and enforcing weakest-link aggregation, the TRUST Index delivers an explainable trust score and guarantees zero false-trust acceptances on invalid claims within the evaluated benchmark, offering a practical blueprint for defense-in-depth AI architectures.

---

## Main Limitation

The evaluation is bounded by a single enterprise-policy corpus, a small-scale 1B parameter generator, and a 130-case validation dataset where 88 cases share provenance with historical exploratory benchmarks. Furthermore, the remaining unseen evaluation cohort is modest ($N = 42$), the trust score concentrates at discrete plateaus ($0, 50, 100$) rather than acting as a continuously calibrated probability, and the primary remaining classification ambiguity occurs at the boundary between `Uncertain` and `Hallucinated` claims.

---

## Final Research Claim

Within the evaluated experimental setup, retrieval- and prompting-level interventions did not reliably reduce hallucination in the tested RAG configuration. In contrast, the TRUST Index provided an independent post-generation verification layer that reliably identified unsupported or contradictory outputs, including on previously unseen validation cases. These results support the use of verification as a complementary layer for improving the reliability of RAG-based generation, rather than implying that retrieval or prompting alone is universally insufficient.
