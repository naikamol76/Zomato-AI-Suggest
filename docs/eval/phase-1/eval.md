# Phase 1 Evaluation — Data Ingestion & Restaurant Store

**Goal:** Hugging Face dataset → cleaned Parquet; repository loads at FastAPI startup.

**References:** [Implementation plan § Phase 1](../../implementationPlan.md#phase-1-data-ingestion--restaurant-store) · [Architecture §3.1–3.2](../../architecture.md#31-data-ingestion-pipeline)

---

## Prerequisites

- Phase 0 complete  
- Network access for first HF download (or cached dataset)  

---

## Pass criteria (summary)

Parquet exists, repository loads on startup, metadata methods return sensible data for major cities.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A1.1 | Ingest succeeds | `python -m scripts.ingest` exit code 0 | ☐ |
| A1.2 | Parquet exists | `data/processed/restaurants.parquet` present | ☐ |
| A1.3 | Row count | After ingest: 40k–55k rows (document actual count) | ☐ |
| A1.4 | Required columns | `restaurant_id`, `name`, `city`, `rating`, `budget_band`, `cuisines` present | ☐ |
| A1.5 | Startup load | API logs `Loaded N restaurants` with N > 0 | ☐ |
| A1.6 | Repository unit test | `pytest tests/` for load/list (if written) | ☐ |

---

## Manual evaluation

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| M1.1 | `list_cities()` | Includes **Bangalore** and **Delhi** (or documented canonical names) | ☐ |
| M1.2 | Bangalore subset | Query/filter by Bangalore returns **> 0** rows | ☐ |
| M1.3 | Ratings range | Spot-check: ratings in [0, 5] | ☐ |
| M1.4 | Budget bands | Only `low`, `medium`, `high` (or documented enum) | ☐ |
| M1.5 | `dataSchema.md` | Column mapping from raw HF → processed documented | ☐ |
| M1.6 | Missing Parquet | Rename file → startup fails with clear error (DATA-11) | ☐ |

---

## Data quality metrics (record)

| Metric | Value |
|--------|-------|
| Raw rows downloaded | |
| Rows after clean | |
| % dropped | |
| Distinct cities | |
| Load time (ms) | |

---

## Edge cases to verify

| ID | Verify |
|----|--------|
| DATA-01 | Simulate or document behavior on HF failure |
| DATA-03 | Dropped null name/city/rating |
| DATA-11 | Missing Parquet → fail fast |
| REPO-01 | Empty file handling (if testable) |

---

## Sign-off

| Field | Value |
|-------|--------|
| Evaluator | |
| Date | |
| Result | ☐ Pass · ☐ Fail |
| Notes | |

**Previous:** [Phase 0](../phase-0/eval.md) · **Next:** [Phase 2](../phase-2/eval.md)
