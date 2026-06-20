def test_metadata_cities(client) -> None:
    response = client.get("/api/v1/metadata/cities")
    assert response.status_code == 200
    cities = response.json()["cities"]
    assert "Bangalore" in cities
    assert "Delhi" in cities


def test_metadata_cuisines_filtered_by_city(client) -> None:
    response = client.get("/api/v1/metadata/cuisines", params={"city": "Delhi"})
    assert response.status_code == 200
    cuisines = response.json()["cuisines"]
    assert "mughlai" in cuisines
