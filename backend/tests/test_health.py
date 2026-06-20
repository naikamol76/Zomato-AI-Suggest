def test_health_returns_ok_with_data_loaded(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data_loaded"] is True
    assert body["restaurant_count"] >= 3


def test_openapi_docs_available(client) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "Restaurant Recommendation API" in response.json()["info"]["title"]
