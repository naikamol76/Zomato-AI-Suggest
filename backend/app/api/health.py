from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(request: Request) -> dict:
    repo = getattr(request.app.state, "repository", None)
    data_loaded = repo is not None and repo.is_loaded

    body: dict = {
        "status": "ok",
        "data_loaded": data_loaded,
    }

    if data_loaded:
        body["restaurant_count"] = repo.row_count
        body["load_duration_ms"] = repo.load_duration_ms
        body["message"] = "API and restaurant data are ready."
    else:
        body["message"] = (
            "API is running but restaurant data is not loaded. "
            "Run ingest and restart, or check DATA_PATH."
        )

    return body
