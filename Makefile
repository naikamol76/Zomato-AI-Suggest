.PHONY: ingest test api frontend filter-smoke

ingest:
	python -m scripts.ingest

filter-smoke:
	python -m scripts.filter_smoke

test:
	cd backend && pytest

api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev
