import pytest

from app.models.preferences import UserPreferences
from app.models.restaurant import BudgetBand
from app.services.filter import CandidateFilterService


def _prefs(
    city: str = "Bangalore",
    budget: BudgetBand = BudgetBand.MEDIUM,
    cuisine: str = "North Indian",
    min_rating: float = 4.0,
) -> UserPreferences:
    return UserPreferences(
        city=city,
        budget=budget,
        cuisine=cuisine,
        min_rating=min_rating,
    )


def test_golden_filter_bangalore_medium_north_indian(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(_prefs(), max_candidates=20)
    assert 1 <= len(results) <= 20
    names = {r.name for r in results}
    assert "North Spice Kitchen" in names
    assert "Premium Palace" in names
    assert "Budget Bites" not in names  # low budget
    assert "Old Town Diner" not in names  # rating 3.9
    assert "Wok Express" not in names  # chinese only


def test_invalid_city_returns_empty(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(
        _prefs(city="Zanzibar"),
        max_candidates=20,
    )
    assert results == []


def test_case_insensitive_city(filter_service: CandidateFilterService) -> None:
    lower = filter_service.apply(_prefs(city="bangalore"), max_candidates=20)
    title = filter_service.apply(_prefs(city="Bangalore"), max_candidates=20)
    assert {r.restaurant_id for r in lower} == {r.restaurant_id for r in title}


def test_cuisine_substring_indian(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(
        _prefs(cuisine="Indian", min_rating=0.0),
        max_candidates=20,
    )
    assert len(results) >= 2
    assert all("indian" in r.cuisines.casefold() for r in results)


def test_strict_min_rating(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(_prefs(min_rating=4.0), max_candidates=20)
    assert all(r.rating >= 4.0 for r in results)
    assert not any(r.name == "Old Town Diner" for r in results)


def test_budget_mismatch_excluded(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(
        _prefs(budget=BudgetBand.LOW, min_rating=0.0),
        max_candidates=20,
    )
    assert all(r.budget_band == BudgetBand.LOW for r in results)
    assert any(r.name == "Budget Bites" for r in results)


def test_max_candidates_cap(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(
        _prefs(cuisine="indian", min_rating=0.0),
        max_candidates=2,
    )
    assert len(results) == 2


def test_sort_by_rating_then_votes(filter_service: CandidateFilterService) -> None:
    results = filter_service.apply(_prefs(), max_candidates=20)
    ratings = [r.rating for r in results]
    assert ratings == sorted(ratings, reverse=True)
    if len(results) >= 2 and results[0].rating == results[1].rating:
        assert results[0].votes >= results[1].votes


def test_cuisine_special_characters_literal_match(filter_service: CandidateFilterService) -> None:
    """FILT-09: substring match must not treat ( as regex."""
    results = filter_service.apply(
        _prefs(cuisine="(south)", min_rating=0.0),
        max_candidates=20,
    )
    assert results == []


def test_zero_max_candidates(filter_service: CandidateFilterService) -> None:
    assert filter_service.apply(_prefs(), max_candidates=0) == []


def test_user_preferences_validation() -> None:
    with pytest.raises(ValueError):
        UserPreferences(
            city="  ",
            budget=BudgetBand.MEDIUM,
            cuisine="Italian",
        )


def test_filter_case_insensitive_name_deduplication(loaded_repository) -> None:
    """Test that duplicate names with different casing are deduplicated in filter.py."""
    df = loaded_repository.get_dataframe().copy()
    import pandas as pd
    
    duplicate_row = pd.DataFrame([{
        "restaurant_id": "ccc888",
        "name": "north spice kitchen",  # Same name, lower case
        "city": "Bangalore",
        "locality": "Indiranagar",
        "cuisines": "north indian",
        "rating": 4.6,
        "votes": 100,
        "approx_cost_for_two": 600.0,
        "budget_band": "medium"
    }])
    df = pd.concat([df, duplicate_row], ignore_index=True)
    
    from app.data.repository import RestaurantRepository
    from unittest.mock import MagicMock
    
    mock_repo = MagicMock(spec=RestaurantRepository)
    mock_repo.get_dataframe.return_value = df
    mock_repo.dataframe_to_restaurants.side_effect = loaded_repository.dataframe_to_restaurants
    
    service = CandidateFilterService(mock_repo)
    results = service.apply(_prefs(), max_candidates=20)
    
    names = [r.name.lower() for r in results]
    assert names.count("north spice kitchen") == 1
