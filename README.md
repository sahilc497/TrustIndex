# TRUST INDEX: Explainable Trust Verification Framework for RAG Systems

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646cff.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Research Prototype & Thesis Demonstration**  
> An explainable post-generation verification framework for Retrieval-Augmented Generation (RAG) systems. Given a user query, a generated answer, and retrieved evidence passages, TRUST Index decomposes the response into atomic propositions, constructs a bipartite consensus graph against retrieved evidence, and computes an audited, mathematically grounded **Trust Score** ($0 - 100$).

---

## Key Research Findings

1. **RAG Interventions Do Not Eliminate Hallucination**:
   Across a 2×2 controlled factorial ablation study and hybrid retrieval experiments on 77 real queries (Conditions A–E), neither semantic re-ranking nor citation-forced prompting produced a statistically significant reduction in hallucination over naive baselines (**McNemar exact paired test: $p = 1.0000$**). Hallucination rates remained bounded between **20.7% and 31.2%**.
2. **Post-Generation Verification is Essential**:
   Because prompting-level and retrieval-level interventions cannot prevent generative language models from producing unsupported assertions, an independent post-generation verification layer is mathematically and operationally required.
3. **TRUST Index Validation**:
   On the audited 130-case validation benchmark, the TRUST Index verification layer achieves:
   - **97.7% Binary Classification Accuracy**
   - **98.5% Hallucination Detection F1-Score**
   - **100% Unseen Subset Accuracy** ($n=31$ novel cases)
   - **0 / 100 False Acceptance Rate** (Zero invalid answers misclassified as `Trusted`)

---

## System Architecture

```text
                       [ User / Academic Evaluator ]
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │       React + Vite + Tailwind Academic Frontend        │
        │   • 4-Stage Conceptual Workflow                        │
        │   • 1-Click Canned Benchmark Scenarios                 │
        │   • Document Q&A Inline Claim Highlighting             │
        │   • Bipartite Consensus Graph (SVG Interactive)        │
        │   • Empirical Research Results & Findings Panel        │
        └────────────────────────────┬───────────────────────────┘
                                     │
                                     ▼ HTTP REST (Port 8000)
        ┌────────────────────────────────────────────────────────┐
        │                 FastAPI Backend Service                │
        │   • POST /verify         -> Single verification pipeline│
        │   • POST /verify/batch   -> Batch evaluation           │
        │   • POST /simulate-rag   -> Generation + Verification  │
        │   • GET  /health         -> Health check & metadata    │
        └────────────────────────────┬───────────────────────────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │            TRUST Index Verification Engine             │
        │                                                        │
        │  1. Claim Extraction (src/claim_extraction.py)         │
        │     • Splits generated answers into atomic claims      │
        │                                                        │
        │  2. Semantic Similarity Alignment (src/similarity.py)  │
        │     • Sentence-BERT (all-MiniLM-L6-v2) cosine weights  │
        │                                                        │
        │  3. Contradiction & Entailment (src/contradiction.py)  │
        │     • Layer 1: Deterministic regex numeric/date/negation│
        │     • Layer 2: RoBERTa-large-MNLI neural inference     │
        │                                                        │
        │  4. Bipartite Evidence Graph (src/evidence_graph.py)   │
        │     • Builds consensus edges [-1.0, +1.0]              │
        │                                                        │
        │  5. Weakest-Link Trust Scoring (src/trust_score.py)    │
        │     • Min-aggregation: catches isolated hallucinations │
        └────────────────────────────────────────────────────────┘
```

---

## Core Mathematical Formulations

### 1. Bipartite Graph Consensus Formula
For each atomic claim $c$ connected to retrieved evidence passages $\{e_1, \dots, e_m\}$:
$$\text{Consensus}(c) = \frac{\sum_{e \in \text{ENTAIL}} \text{Sim}(c, e) - \sum_{e \in \text{CONTRADICT}} \text{Sim}(c, e)}{\sum_{e \in \text{ALL}} \text{Sim}(c, e) + \epsilon} \in [-1.0, +1.0]$$

The claim-level score rescales consensus to $[0, 100]$:
$$\text{Score}(c) = \frac{\text{Consensus}(c) + 1}{2} \times 100$$

### 2. Weakest-Link ($\min$) Aggregation
Rather than taking the arithmetic mean across claims, the answer-level Trust Score is governed by:
$$\text{Trust Score} = \min_{c \in \text{claims}} \text{Score}(c)$$

In high-stakes compliance and policy QA, trustworthiness is non-compensatory: an answer with three true claims and one critical contradiction must fail verification.

### 3. Classification Thresholds
- **$80 - 100$**: `Trusted` — Fully substantiated by retrieved passages.
- **$50 - 79$**: `Uncertain` — Incomplete, ambiguous, or unverified claims.
- **$0 - 49$**: `Hallucinated` — Direct contradiction or factual mutation detected.

---

## Academic Demonstration UI

The frontend is specifically designed for academic defense, viva evaluations, and executive demos:

1. **Four-Stage Conceptual Workflow**:
   $$\text{Retrieve} \longrightarrow \text{Generate} \longrightarrow \text{Verify} \longrightarrow \text{Trust}$$
2. **Quick 1-Click Demo Bar**:
   - **Supported Example** (Green) — Reimbursable meals up to $75
   - **Unsupported Example** (Amber) — Ergonomic home-office keyboards
   - **Contradiction Example** (Red) — Alcohol reimbursement claim
3. **Synchronized Evidence Triangulation**:
   - Clicking any highlighted sentence in the **Generated Answer** selects the corresponding claim, isolates its consensus edge in the **Evidence Graph**, and surfaces the source passage in the **Evidence Explanation**.
4. **Empirical Research Results Tab**:
   - Live inspection of the frozen 2×2 ablation, McNemar tests, and 130-case validation metrics.

---

## Empirical Evaluation Summary

### 1. Detector Validation (Audited 130-Case Benchmark)

| Metric | Result | Description |
|---|---|---|
| **Total Evaluation Cases** | **130** | Benchmark across 4 policy domains |
| **Binary Classification Accuracy** | **97.7%** | $127 / 130$ cases correctly classified |
| **Hallucination Detection Precision** | **97.1%** | $100 / 103$ flagged claims are true hallucinations |
| **Hallucination Detection Recall** | **100.0%** | Zero hallucinations missed ($100 / 100$) |
| **Detection F1-Score** | **98.5%** | Harmonic mean of precision and recall |
| **Unseen Cases Accuracy** | **100.0%** | $31 / 31$ cases with novel vocabulary / entities |
| **Invalid $\to$ Trusted (False Acceptance)** | **0 / 100** | Strict safety guarantee |

### 2. Five-Condition RAG Factorial Ablation ($N = 77$)

| Condition | Description | Mean Trust | % Trusted | % Hallucinated | McNemar vs A |
|---|---|---|---|---|---|
| **Condition A** | Naive Lexical + Standard Prompt | **56.9** | 31.2% | **23.4%** | Baseline |
| **Condition B** | Dense SBERT Re-ranking + Std Prompt | 49.8 | 10.4% | 27.3% | $p = 0.4531$ (Not Sig) |
| **Condition C** | Naive Lexical + Citation Prompt | 56.6 | 23.4% | 22.1% | $p = 1.0000$ (Not Sig) |
| **Condition D** | Dense Re-ranking + Citation Prompt | 49.5 | 9.1% | 31.2% | $p = 0.2863$ (Not Sig) |
| **Condition E** | Hybrid RRF + Concise Grounding | 54.9 | 16.9% | 24.7% | $p = 1.0000$ (Not Sig) |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/sahilc497/TrustIndex.git
cd TrustIndex
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger API Documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

> **Note**: The frontend includes built-in fallback data. Even if the backend Python server is offline, selecting any scenario from the **Demo Examples** bar will render authentic, pre-verified results.

---

## Reproducing Research Results

Run the validation suite to re-verify all 130 benchmark cases:
```bash
python run_trust_validation.py
```
This produces complete statistical tables and diagnostic reports in `results/trust_validation/`.

To inspect the McNemar paired significance tests:
```bash
python scratch/mcnemar_test.py
```

---

## Project Structure

```text
TrustIndex/
├── api/
│   ├── __init__.py
│   ├── main.py                   # FastAPI REST endpoints
│   ├── models.py                 # Pydantic request & response schemas
│   └── service.py                # Pipeline execution service
├── data/
│   ├── eval_dataset.json         # 77-query primary RAG benchmark
│   ├── held_out_eval_dataset.json# 10 novel entity test pairs
│   ├── trust_validation_dataset.json # 130-case validation benchmark
│   └── hr_policy_*.txt           # Knowledge base documents
├── frontend/
│   ├── src/
│   │   ├── components/           # UI components (Graph, Gauge, Answer, etc.)
│   │   ├── data/demoScenarios.js # Pre-verified benchmark demo scenarios
│   │   ├── App.jsx               # Main application view & state
│   │   └── index.css             # Soft academic design tokens
│   ├── package.json
│   └── vite.config.js
├── results/
│   ├── trust_validation/         # Audited reports, figures & metrics
│   ├── rag_comparison.json       # Conditions A-D raw predictions
│   ├── condition_e_comparison.json # Condition E raw predictions
│   ├── FINAL_RESULTS_AND_DISCUSSION.md
│   └── RESEARCH_FINDINGS_SUMMARY.md
├── src/
│   ├── claim_extraction.py       # Atomic proposition parser
│   ├── contradiction.py          # Dual-layer NLI & rule diffing
│   ├── detector.py               # Main verification pipeline
│   ├── evidence_graph.py         # Bipartite consensus graph
│   ├── rag_hybrid_retrieval.py   # Reciprocal Rank Fusion retrieval
│   ├── similarity.py             # Sentence-BERT cosine matcher
│   └── trust_score.py            # Weakest-link aggregation
├── run_trust_validation.py       # Benchmark validation runner
├── requirements.txt              # Backend dependencies
└── README.md
```

---

## REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/verify` | `POST` | Decomposes and scores answer claims against provided evidence. |
| `/verify/batch` | `POST` | Batch verification over multiple query-answer pairs. |
| `/simulate-rag` | `POST` | Executes retrieval, generates response, and runs TRUST Index. |
| `/health` | `GET` | Health check endpoint returning model version and status. |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
