# Phase 0 Evaluation — Project Foundation

**Goal:** Runnable FastAPI backend and React frontend skeleton with configuration and health check.

**References:** [Implementation plan § Phase 0](../../implementationPlan.md#phase-0-project-foundation) · [Architecture §4](../../architecture.md#4-proposed-repository-layout)

---

## Prerequisites

- Python 3.11+ and Node 18+ installed  
- Virtual environment created for backend  

---

## Pass criteria (summary)

Phase 0 is **complete** when all **P0** items below pass. No business logic required yet.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A0.1 | Backend starts | `cd backend && uvicorn app.main:app --reload` | ☐ |
| A0.2 | Health endpoint | `curl http://localhost:8000/api/v1/health` → 200 + JSON body | ☐ |
| A0.3 | pytest runs | `cd backend && pytest` (≥0 tests, exit 0) | ☐ |
| A0.4 | Frontend dev server | `cd frontend && npm run dev` → :5173 | ☐ |
| A0.5 | Settings load | App starts with `.env.example` copied to `.env` (dummy values OK) | ☐ |

---

## Manual evaluation

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| M0.1 | Folder layout | `backend/app/`, `frontend/src/`, `docs/`, `prompts/`, `scripts/`, `tests/` exist | ☐ |
| M0.2 | `.gitignore` | Excludes `.env`, `venv/`, `node_modules/`, `__pycache__/`, `data/raw/` | ☐ |
| M0.3 | CORS configured | Browser console shows no CORS error on health fetch from React (optional stub fetch) | ☐ |
| M0.4 | README | Documents Python version, ports 8000/5173, how to run both apps | ☐ |
| M0.5 | No secrets in repo | `git status` / search shows no real API keys committed | ☐ |

---

## Edge cases to verify

From [`edgecase.md`](../../edgecase.md):

| ID | Verify |
|----|--------|
| SEC-01 | `.env` not tracked; `.env.example` present |
| HTTP-01 | Health behavior documented if data not loaded yet |

---

## Sign-off

| Field | Value |
|-------|--------|
| Evaluator | |
| Date | |
| Result | ☐ Pass · ☐ Fail |
| Notes | |

**Next phase:** [Phase 1 — Data](../phase-1/eval.md)
