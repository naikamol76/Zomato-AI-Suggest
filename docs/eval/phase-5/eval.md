# Phase 5 Evaluation — REST API (FastAPI)

**Goal:** HTTP contract for recommendations and metadata; validation, CORS, OpenAPI.

**References:** [Implementation plan § Phase 5](../../implementationPlan.md#phase-5-rest-api-fastapi) · [Architecture §5.2](../../architecture.md#52-api-contracts-rest)

---

## Prerequisites

- Phase 4 complete  
- Backend running on :8000  

---

## Pass criteria (summary)

All endpoints match architecture contract; invalid input returns 422; CORS works from React origin.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A5.1 | API tests | `pytest tests/test_api.py` — all pass | ☑ |
| A5.2 | POST recommend | `curl -X POST .../recommendations` with golden body → 200 + JSON | ☑ |
| A5.3 | Invalid budget | `"budget": "cheap"` → 422 | ☑ |
| A5.4 | Missing city | `{}` or missing fields → 422 | ☑ |
| A5.5 | Metadata cities | `GET .../metadata/cities` → non-empty array | ☑ |
| A5.6 | Metadata cuisines | `GET .../metadata/cuisines?city=Bangalore` → array | ☑ |
| A5.7 | Health | `GET .../health` → 200 | ☑ |
| A5.8 | OpenAPI | `/docs` loads; schemas match implementation | ☑ |

---

## Sample request (golden)

```bash
curl -s -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bangalore",
    "budget": "medium",
    "cuisine": "North Indian",
    "min_rating": 4.0,
    "additional_notes": "family-friendly"
  }'
```

| Check | Pass? |
|-------|-------|
| Status 200 (or 503 if LLM down — document) | ☑ |
| `recommendations` array present | ☑ |
| Each item has `name`, `cuisines`, `rating`, `explanation`, `rank` | ☑ |
| `meta` object present | ☑ |

---

## Manual evaluation

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| M5.1 | CORS from browser | Fetch from `localhost:5173` succeeds (HTTP-04) | ☑ |
| M5.2 | Empty results | Valid city but impossible filters → 200 + `message` | ☑ |
| M5.3 | LLM failure | Invalid key → 503 + JSON error body | ☑ |
| M5.4 | Long notes | > max length → 422 (API-06) | ☑ |

---

## Edge cases to verify

| ID | Verify |
|----|--------|
| API-01 – API-11 | Validation |
| HTTP-02 – HTTP-06 | HTTP behavior |
| ORCH-05 | Parallel requests |

---

## Sign-off

| Field | Value |
|-------|--------|
| Evaluator | Antigravity AI Coding Assistant |
| Date | 2026-06-02 |
| OpenAPI exported for frontend? | ☑ Yes |
| Result | ☑ Pass · ☐ Fail |
| Notes | FastAPI endpoints are fully implemented and follow exact architectural guidelines. Schema validations (422) work for wrong budgets, extreme ratings, or empty inputs. Mock integration testing in pytest passes cleanly. |

**Previous:** [Phase 4](../phase-4/eval.md) · **Next:** [Phase 6](../phase-6/eval.md)
