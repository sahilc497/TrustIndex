# TRUST Index — Research-Grade Verification Dashboard

The **TRUST Index Verification Dashboard** is a desktop-first research-grade interface designed to evaluate and explain factual reliability in Retrieval-Augmented Generation (RAG) systems.

It visualizes the full post-generation verification lifecycle:
```text
Retrieve → Generate → Extract Claims → Verify Evidence → Detect Contradictions → Trust Scoring → Explain
```

---

## Key Features

1. **Top Horizontal Pipeline:**
   - 6-stage verification progress tracker (`Retrieval` → `Generation` → `Claim Extraction` → `Evidence Matching` → `Contradiction Analysis` → `Trust Scoring`).

2. **Weakest-Link Trust Score Radial Gauge:**
   - Visual speedometer gauge with explicit thresholds (`≥ 80.0` Trusted, `50.0–79.9` Uncertain, `< 50.0` Hallucinated).
   - Real-time weakest-link decision rationale banner.

3. **Generated Answer with Interactive Claim Highlights:**
   - Inline color-coded highlights for atomic propositions (Supported, Uncertain, Contradiction).
   - Hover tooltips and click synchronization with the Evidence Graph and Evidence Inspector.

4. **Bipartite Consensus Evidence Graph (Centerpiece):**
   - Interactive SVG bipartite visualization linking Atomic Claims to Retrieved Passages.
   - Directed alignment edges: `SUPPORTS` (Solid Emerald), `CONTRADICTS` (Dashed Crimson), and `NEUTRAL` (Dotted Slate).
   - Canvas controls: Zoom in/out, pan drag, reset view, and sub-graph hover isolation.

5. **Claim-by-Claim Verification Cards:**
   - Granular claim breakdown with consensus scores (`+1.00`, `0.00`, `-1.00`), trust score pills, and diagnostic reasons.

6. **Evidence Alignment Inspector:**
   - Detailed inspection drawer showing verbatim source passages, SBERT cross-similarity bars, and NLI diagnosis.

7. **Empirical Findings Tab:**
   - Dedicated dashboard displaying frozen Chapter 4 experimental results:
     - RAG Intervention Invariance (Conditions A–E, exact McNemar $p = 1.0000$)
     - Full Controlled Benchmark ($N = 130$, 97.7% binary accuracy, 100% recall)
     - Isolated Unseen Partition ($N = 42$, 100% binary accuracy, 100% precision)
     - Asymmetric Safety Invariant ($0/100$ and $0/36$ false trust violations = 0.0%)
     - Kruskal-Wallis score separation ($H = 100.56, p = 1.18 \times 10^{-21}$)

8. **Professor 2-Click Demonstration Scenarios:**
   - **Demo 1 (Supported - 100%):** Annual Leave Entitlement
   - **Demo 2 (Unsupported - 50%):** Wellness & Remote Equipment Stipend
   - **Demo 3 (Contradiction - 0%):** Alcohol Travel Reimbursement

---

## Getting Started

### 1. Start the Backend API (FastAPI)
From the repository root (`d:\T-index`):
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start the Frontend Dev Server
From `frontend/`:
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.
