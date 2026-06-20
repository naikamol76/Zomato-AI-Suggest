from pathlib import Path

import pytest

from app.data.repository import RestaurantDataNotLoadedError, RestaurantRepository


def test_repository_load_and_query(sample_parquet_file: Path) -> None:
    repo = RestaurantRepository(data_path=sample_parquet_file)
    repo.load()

    assert repo.row_count == 7
    cities = repo.list_cities()
    assert "Bangalore" in cities
    assert "Delhi" in cities

    bangalore = repo.filter_by_city("Bangalore")
    assert len(bangalore) == 5
    assert all(r.city == "Bangalore" for r in bangalore)


def test_list_cuisines_scoped_by_city(sample_parquet_file: Path) -> None:
    repo = RestaurantRepository(data_path=sample_parquet_file)
    repo.load()

    delhi_cuisines = repo.list_cuisines(city="Delhi")
    assert "mughlai" in delhi_cuisines


def test_not_loaded_raises() -> None:
    repo = RestaurantRepository(data_path="missing.parquet")
    with pytest.raises(RestaurantDataNotLoadedError):
        repo.list_cities()


def test_missing_parquet_file_raises(sample_parquet_file: Path) -> None:
    repo = RestaurantRepository(data_path=sample_parquet_file.parent / "does_not_exist.parquet")
    with pytest.raises(FileNotFoundError, match="Restaurant data not found"):
        repo.load()
