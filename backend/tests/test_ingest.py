import pandas as pd

from app.data.ingest import (
    assign_budget_band,
    extract_city,
    make_restaurant_id,
    parse_cost,
    parse_rating,
    transform_dataframe,
)


def test_parse_rating_variants() -> None:
    assert parse_rating("4.5/5") == 4.5
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_cost_variants() -> None:
    assert parse_cost("1,200") == 1200.0
    assert parse_cost("300") == 300.0
    assert parse_cost("") is None


def test_extract_city_from_address() -> None:
    assert extract_city("12 MG Road, Bengaluru, India", None, None) == "Bangalore"
    assert extract_city("Block A, New Delhi", None, None) == "Delhi"


def test_make_restaurant_id_stable() -> None:
    a = make_restaurant_id("Cafe", "Addr", "http://x")
    b = make_restaurant_id("Cafe", "Addr", "http://x")
    assert a == b


def test_transform_drops_invalid_rows() -> None:
    raw = pd.DataFrame(
        [
            {
                "name": "Valid Place",
                "address": "Street, Bangalore",
                "rate": "4.2/5",
                "votes": 10,
                "cuisines": "Italian",
                "approx_cost(for two people)": "500",
                "location": "HSR",
                "listed_in(city)": "HSR",
                "url": "http://example.com/1",
            },
            {
                "name": "No Rating",
                "address": "Street, Bangalore",
                "rate": "NEW",
                "votes": 0,
                "cuisines": "Cafe",
                "approx_cost(for two people)": "200",
                "location": "BTM",
                "listed_in(city)": "BTM",
                "url": "http://example.com/2",
            },
        ]
    )
    processed = transform_dataframe(raw)
    assert len(processed) == 1
    assert processed.iloc[0]["name"] == "Valid Place"
    assert processed.iloc[0]["budget_band"] in {"low", "medium", "high"}


def test_assign_budget_band_thresholds() -> None:
    assert assign_budget_band(300, 500, 1000) == "low"
    assert assign_budget_band(800, 500, 1000) == "medium"
    assert assign_budget_band(1500, 500, 1000) == "high"
