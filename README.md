# AI-Powered Restaurant Recommendations (Zomato Use Case)

Hybrid **filter + LLM** recommendation service: FastAPI backend, React frontend, Zomato-style dataset from Hugging Face.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**

## Project structure

```text
zomato/
├── backend/          # FastAPI API
├── frontend/         # React (Vite + TypeScript)
├── data/processed/   # Parquet after ingest (Phase 1)
├── docs/             # Architecture, implementation plan, eval
├── prompts/          # LLM templates (Phase 3)
└── scripts/          # Data ingest (Phase 1)
```

## Quick start

### 1. Ingest restaurant data (once)

From the **repository root**:

```bash
pip install -e "./backend[dev]"   # if not already installed
python -m scripts.ingest
# or: make ingest
```

Writes `data/processed/restaurants.parquet` (~50k rows; requires network on first run).

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Startup logs: `Loaded N restaurants from ...`

- API: http://localhost:8000  
- Health: http://localhost:8000/api/v1/health  
- OpenAPI: http://localhost:8000/docs  

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env   # Windows
# cp .env.example .env

npm run dev
```

- UI: http://localhost:5173  

Use **Ping backend** on the home page to verify CORS and the health endpoint.

### 4. Tests

```bash
cd backend
pytest
```

## Environment variables

| Location | Variable | Description |
|----------|----------|-------------|
| `backend/.env` | `LLM_API_KEY` | OpenAI-compatible key (Phase 3+) |
| `backend/.env` | `DATA_PATH` | Path to `restaurants.parquet` (Phase 1) |
| `frontend/.env` | `VITE_API_BASE_URL` | Backend URL (default `http://localhost:8000`) |

## Documentation

- [Problem statement](docs/problemStatement.md)
- [Architecture](docs/architecture.md)
- [Implementation plan](docs/implementationPlan.md)
- [Edge cases](docs/edgecase.md)
- [Phase 0 evaluation](docs/eval/phase-0/eval.md)

## Implementation status

| Phase | Status |
|-------|--------|
| 0 — Foundation | Done |
| 1 — Data ingest | Done |
| 2 — Filter service | Done |
| 3+ | Pending |

**Metadata API (Phase 1):** `GET /api/v1/metadata/cities`, `GET /api/v1/metadata/cuisines?city=`

**Filter debug (Phase 2):** `GET /api/v1/debug/candidates?city=Bangalore&budget=medium&cuisine=North%20Indian&min_rating=4.0`

```bash
python -m scripts.filter_smoke   # or: make filter-smoke
```
