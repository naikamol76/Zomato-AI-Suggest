# Phase 2 Evaluation — Domain Models & Candidate Filtering

**Goal:** Deterministic filter from `UserPreferences` to ≤ `MAX_CANDIDATES` restaurants — **no LLM**.

**References:** [Implementation plan § Phase 2](../../implementationPlan.md#phase-2-domain-models--candidate-filtering) · [Architecture §3.3](../../architecture.md#33-candidate-filter-service)

---

## Prerequisites

- Phase 1 complete  
- `CandidateFilterService` implemented  

---

## Pass criteria (summary)

Filter applies all hard constraints; caps and sorts correctly; tests pass.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A2.1 | Filter tests | `pytest tests/test_filter.py` — all pass | ☐ |
| A2.2 | Golden filter | Bangalore + medium + North Indian + min 4.0 → 1–20 results | ☐ |
| A2.3 | Invalid city | Unknown city → `[]` | ☐ |
| A2.4 | Cap enforced | When many matches exist, `len(result) <= MAX_CANDIDATES` | ☐ |
| A2.5 | Sort order | First row rating ≥ last row rating (desc) | ☐ |

---

## Manual evaluation

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| M2.1 | Case-insensitive city | `bangalore` matches same as `Bangalore` | ☐ |
| M2.2 | Cuisine substring | `Indian` matches `North Indian` venues | ☐ |
| M2.3 | Strict rating | 3.9 excluded when min is 4.0 | ☐ |
| M2.4 | Budget mismatch | `low` budget excludes only-`medium` venues | ☐ |
| M2.5 | Impossible combo | e.g. fake city + strict filters → empty, no exception | ☐ |

---

## Test inputs (record results)

| city | budget | cuisine | min_rating | # candidates | Pass? |
|------|--------|---------|--------------|----------------|-------|
| Bangalore | medium | North Indian | 4.0 | | ☐ |
| Delhi | high | Chinese | 4.5 | | ☐ |
| Zanzibar | medium | Italian | 3.0 | 0 expected | ☐ |

---

## Edge cases to verify

| ID | Verify |
|----|--------|
| FILT-01 – FILT-08 | Per [edgecase.md](../../edgecase.md) §4 |
| REPO-04, REPO-05 | Trim / case |

---

## Sign-off

| Field | Value |
|-------|--------|
| Evaluator | |
| Date | |
| Result | ☐ Pass · ☐ Fail |
| Notes | |

**Previous:** [Phase 1](../phase-1/eval.md) · **Next:** [Phase 3](../phase-3/eval.md)
