"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_restaurants.parquet"


def _build_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "restaurant_id": "aaa111",
                "name": "North Spice Kitchen",
                "city": "Bangalore",
                "locality": "Indiranagar",
                "cuisines": "north indian, chinese",
                "rating": 4.5,
                "votes": 1200,
                "approx_cost_for_two": 800.0,
                "budget_band": "medium",
            },
            {
                "restaurant_id": "bbb222",
                "name": "Budget Bites",
                "city": "Bangalore",
                "locality": "BTM",
                "cuisines": "north indian",
                "rating": 4.0,
                "votes": 400,
                "approx_cost_for_two": 350.0,
                "budget_band": "low",
            },
            {
                "restaurant_id": "ddd444",
                "name": "Old Town Diner",
                "city": "Bangalore",
                "locality": "Koramangala",
                "cuisines": "north indian",
                "rating": 3.9,
                "votes": 200,
                "approx_cost_for_two": 700.0,
                "budget_band": "medium",
            },
            {
                "restaurant_id": "eee555",
                "name": "Premium Palace",
                "city": "Bangalore",
                "locality": "UB City",
                "cuisines": "north indian, mughlai",
                "rating": 4.8,
                "votes": 2500,
                "approx_cost_for_two": 950.0,
                "budget_band": "medium",
            },
            {
                "restaurant_id": "fff666",
                "name": "Wok Express",
                "city": "Bangalore",
                "locality": "HSR",
                "cuisines": "chinese",
                "rating": 4.6,
                "votes": 800,
                "approx_cost_for_two": 600.0,
                "budget_band": "medium",
            },
            {
                "restaurant_id": "ccc333",
                "name": "Delhi Darbar Express",
                "city": "Delhi",
                "locality": "Connaught Place",
                "cuisines": "mughlai, north indian",
                "rating": 4.2,
                "votes": 900,
                "approx_cost_for_two": 1200.0,
                "budget_band": "high",
            },
            {
                "restaurant_id": "ggg777",
                "name": "Capital Chinese",
                "city": "Delhi",
                "locality": "Karol Bagh",
                "cuisines": "chinese, thai",
                "rating": 4.6,
                "votes": 1100,
                "approx_cost_for_two": 1100.0,
                "budget_band": "high",
            },
        ]
    )


@pytest.fixture(scope="session", autouse=True)
def sample_parquet_file() -> Path:
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _build_sample_dataframe().to_parquet(FIXTURE_PATH, index=False)
    return FIXTURE_PATH


@pytest.fixture
def loaded_repository(sample_parquet_file: Path):
    from app.data.repository import RestaurantRepository

    repo = RestaurantRepository(data_path=sample_parquet_file)
    repo.load()
    return repo


@pytest.fixture
def filter_service(loaded_repository):
    from app.services.filter import CandidateFilterService

    return CandidateFilterService(loaded_repository)


@pytest.fixture
def client(sample_parquet_file: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATA_PATH", str(sample_parquet_file.resolve()))

    from app.config import get_settings

    get_settings.cache_clear()

    from app.deps import get_repository_singleton

    get_repository_singleton.cache_clear()

    from app.main import create_app

    from fastapi.testclient import TestClient

    with TestClient(create_app()) as test_client:
        yield test_client
