def test_debug_candidates_endpoint(client) -> None:
    response = client.get(
        "/api/v1/debug/candidates",
        params={
            "city": "Bangalore",
            "budget": "medium",
            "cuisine": "North Indian",
            "min_rating": 4.0,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    assert body["preferences"]["city"] == "Bangalore"
    assert len(body["candidates"]) == body["count"]


def test_debug_candidates_empty_city(client) -> None:
    response = client.get(
        "/api/v1/debug/candidates",
        params={
            "city": "Zanzibar",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 3.0,
        },
    )
    assert response.status_code == 200
    assert response.json()["count"] == 0
