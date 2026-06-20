"""In-memory restaurant store backed by processed Parquet."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd

from app.data.ingest import resolve_output_path
from app.models.restaurant import BudgetBand, Restaurant

logger = logging.getLogger(__name__)


class RestaurantDataNotLoadedError(RuntimeError):
    """Raised when the repository is used before load()."""


class RestaurantRepository:
    def __init__(self, data_path: str | Path) -> None:
        self._data_path = data_path
        self._df: pd.DataFrame | None = None
        self._load_duration_ms: float | None = None

    @property
    def is_loaded(self) -> bool:
        return self._df is not None

    @property
    def row_count(self) -> int:
        self._ensure_loaded()
        return len(self._df)  # type: ignore[arg-type]

    @property
    def load_duration_ms(self) -> float | None:
        return self._load_duration_ms

    def load(self) -> None:
        path = resolve_output_path(self._data_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Restaurant data not found at {path}. "
                "Run ingest first: python -m scripts.ingest (from repo root)."
            )

        start = time.perf_counter()
        df = pd.read_parquet(path)
        required = {
            "restaurant_id",
            "name",
            "city",
            "cuisines",
            "rating",
            "budget_band",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Parquet missing columns: {sorted(missing)}")

        self._df = df
        self._load_duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "Loaded %s restaurants from %s in %.0f ms",
            len(df),
            path,
            self._load_duration_ms,
        )

    def get_dataframe(self) -> pd.DataFrame:
        self._ensure_loaded()
        return self._df.copy()  # type: ignore[union-attr]

    def list_cities(self) -> list[str]:
        self._ensure_loaded()
        cities = self._df["city"].dropna().astype(str).str.strip()  # type: ignore[index]
        return sorted(cities.unique().tolist(), key=str.casefold)

    def list_cuisines(self, city: str | None = None) -> list[str]:
        self._ensure_loaded()
        df = self._df  # type: ignore[assignment]
        if city:
            df = df[df["city"].str.casefold() == city.strip().casefold()]

        tokens: set[str] = set()
        for value in df["cuisines"].dropna().astype(str):
            for part in value.split(","):
                token = part.strip()
                if token:
                    tokens.add(token)
        return sorted(tokens, key=str.casefold)

    def filter_by_city(self, city: str) -> list[Restaurant]:
        """Return all restaurants in a city (case-insensitive). Used in tests."""
        self._ensure_loaded()
        mask = self._df["city"].str.casefold() == city.strip().casefold()  # type: ignore[index]
        return self.dataframe_to_restaurants(self._df[mask])  # type: ignore[index]

    def dataframe_to_restaurants(self, df: pd.DataFrame) -> list[Restaurant]:
        return [self._row_to_model(row) for _, row in df.iterrows()]

    def _row_to_model(self, row: pd.Series) -> Restaurant:
        cost = row.get("approx_cost_for_two")
        if pd.isna(cost):
            cost_value = None
        else:
            cost_value = float(cost)

        locality = row.get("locality")
        if locality is None or (isinstance(locality, float) and pd.isna(locality)):
            locality_value = None
        else:
            locality_value = str(locality).strip() or None

        return Restaurant(
            restaurant_id=str(row["restaurant_id"]),
            name=str(row["name"]),
            city=str(row["city"]),
            locality=locality_value,
            cuisines=str(row.get("cuisines", "")),
            rating=float(row["rating"]),
            votes=int(row.get("votes", 0) or 0),
            approx_cost_for_two=cost_value,
            budget_band=BudgetBand(str(row["budget_band"]).lower()),
        )

    def _ensure_loaded(self) -> None:
        if self._df is None:
            raise RestaurantDataNotLoadedError("Call load() before using the repository.")
