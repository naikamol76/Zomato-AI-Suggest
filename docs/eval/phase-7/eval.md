# Phase 7 Evaluation — MVP Sign-Off (Hardening & Full Stack)

**Goal:** Submission-ready system: tests green, grounding verified, documentation complete, P0 edge cases covered.

**References:** [Implementation plan § Phase 7](../../implementationPlan.md#phase-7-testing-documentation--evaluation) · [edgecase.md](../../edgecase.md)

---

## Prerequisites

- Phases 0–6 complete  
- `docs/evalQueries.md` created (or use tables below)  

---

## Pass criteria (summary)

MVP is **shipped** when all **P0** edge cases are handled, pytest passes, ≥5 golden queries evaluated, and a new developer can run the stack in <15 minutes using README.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A7.1 | Full test suite | `cd backend && pytest` — 100% pass | ☐ |
| A7.2 | Coverage (optional) | Critical paths: filter, validator, orchestrator, API | ☐ |
| A7.3 | Frontend build | `npm run build` in `frontend/` | ☐ |
| A7.4 | Lint (optional) | `ruff check` passes | ☐ |
| A7.5 | No secrets | `git grep -i sk-` / review — no keys in history | ☐ |

---

## Golden query evaluation (manual)

Run each via **UI** and/or **API**. For each: verify names and ratings against `restaurants.parquet`.

| # | Query | # results | Grounded? | Explanation OK? | Pass? |
|---|-------|-----------|-----------|-----------------|-------|
| GQ-1 | Bangalore, medium, North Indian, ≥4.0 | | ☐ | ☐ | ☐ |
| GQ-2 | Delhi, low, Chinese, ≥3.5 | | ☐ | ☐ | ☐ |
| GQ-3 | Bangalore, high, Italian, ≥4.5 | | ☐ | ☐ | ☐ |
| GQ-4 | FakeCity, medium, Italian, ≥3.0 | 0 expected | ☐ N/A | ☐ | ☐ |
| GQ-5 | Bangalore, medium, North Indian, ≥4.9 | 0 or few | ☐ | ☐ | ☐ |
| GQ-6 | Bangalore, medium, North Indian, ≥4.0 + notes "quiet, family" | | ☐ | ☐ | ☐ |
| GQ-7 | Mumbai (or valid city), medium, Cafe, ≥4.0 | | ☐ | ☐ | ☐ |

**Minimum to pass:** GQ-1, GQ-4, and **any 3 others** (5 total).

---

## End-to-end edge cases (P0)

| ID | Scenario | Pass? |
|----|----------|-------|
| E2E-01 | Golden query returns real venues | ☐ |
| E2E-02 | Names exist in Parquet for city | ☐ |
| E2E-03 | Explanations mention user criteria | ☐ |
| E2E-05 | Impossible combo → no fabricated restaurants | ☐ |

---

## Documentation & onboarding

| # | Check | Pass? |
|---|--------|-------|
| D7.1 | README: ingest, backend, frontend, env vars | ☐ |
| D7.2 | `.env.example` for backend and frontend | ☐ |
| D7.3 | Architecture + implementation plan linked | ☐ |
| D7.4 | New dev dry-run: clone → run in <15 min | ☐ |

---

## Fresh developer dry-run

| Step | Time (min) | Pass? |
|------|------------|-------|
| Clone + venv + pip install | | ☐ |
| `python -m scripts.ingest` (or use committed Parquet) | | ☐ |
| Start backend | | ☐ |
| Start frontend | | ☐ |
| Golden query in UI | | ☐ |

---

## Known limitations (document)

| Limitation | Accepted for MVP? |
|------------|-----------------|
| No user auth | ☐ Yes |
| LLM latency 2–15s | ☐ Yes |
| City name normalization incomplete | ☐ Yes / ☐ No |
| | |

---

## Final sign-off

| Field | Value |
|-------|--------|
| Evaluator | |
| Date | |
| pytest count | passed / total |
| Golden queries passed | /7 |
| MVP result | ☐ **Shipped** · ☐ Not ready |
| Notes | |

**Previous:** [Phase 6](../phase-6/eval.md)
