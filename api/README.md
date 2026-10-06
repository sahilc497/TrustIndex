# TRUST Index API

FastAPI service exposing the TRUST Index explainable verification layer for RAG systems.

## Run Instructions

From the repository root (`d:\T-index`):

```bash
# Start the FastAPI server locally
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Example API Requests

### 1. Health Check (`GET /health`)

```bash
curl -X GET http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Verify an Answer (`POST /verify`)

#### Example A: Trusted Answer
```bash
curl -X POST http://127.0.0.1:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many annual paid leaves do employees get?",
    "answer": "Employees are entitled to 20 annual paid leaves per calendar year.",
    "retrieved_documents": [
      {
        "doc": "hr_policy_leave.txt",
        "text": "Employees are entitled to 20 annual paid leaves per calendar year."
      }
    ]
  }'
```

#### Example B: Hallucinated Answer (Numeric substitution)
```bash
curl -X POST http://127.0.0.1:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many annual paid leaves do employees get?",
    "answer": "Employees are entitled to 30 annual paid leaves per calendar year.",
    "retrieved_documents": [
      {
        "doc": "hr_policy_leave.txt",
        "text": "Employees are entitled to 20 annual paid leaves per calendar year."
      }
    ]
  }'
```

#### Example C: Uncertain Answer (Uncorroborated addition)
```bash
curl -X POST http://127.0.0.1:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the rules for probation leave?",
    "answer": "Employees on probation get 5 paid leaves and are eligible for 1 day of remote work with manager approval.",
    "retrieved_documents": [
      {
        "doc": "hr_policy_leave.txt",
        "text": "Employees on probation (first 90 days of employment) are entitled to 5 paid leaves only."
      }
    ]
  }'
```

---

### 3. Simulate RAG Pipeline (`POST /simulate-rag`)

```bash
curl -X POST http://127.0.0.1:8000/simulate-rag \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many annual leaves do employees get?",
    "force_hallucination": false
  }'
```
