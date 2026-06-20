"""Load Hugging Face Zomato data, clean, and write processed Parquet."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

HF_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"

# Raw column names in the HF / CSV schema
COL_URL = "url"
COL_NAME = "name"
COL_ADDRESS = "address"
COL_RATE = "rate"
COL_VOTES = "votes"
COL_LOCATION = "location"
COL_CUISINES = "cuisines"
COL_COST = "approx_cost(for two people)"
COL_LISTED_CITY = "listed_in(city)"

CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "mumbai": "Mumbai",
    "kolkata": "Kolkata",
    "chennai": "Chennai",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
}

BUDGET_LOW_MAX = 500
BUDGET_MEDIUM_MAX = 1000


def resolve_output_path(data_path: str | Path) -> Path:
    path = Path(data_path)
    if path.is_absolute():
        return path
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists() or cwd_candidate.parent.exists():
        return cwd_candidate
    backend_parent = (Path(__file__).resolve().parents[3] / path).resolve()
    return backend_parent


def parse_rating(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NEW", "-", "NAN"}:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    rating = float(match.group(1))
    if rating > 5:
        rating = rating / 10 if rating <= 50 else None
    if rating is None or rating < 0 or rating > 5:
        return None
    return round(rating, 2)


def parse_cost(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    digits = re.sub(r"[^\d.]", "", text.replace(",", ""))
    if not digits:
        return None
    cost = float(digits)
    return cost if cost > 0 else None


def extract_city(address: object, listed_in_city: object, location: object) -> str:
    """Infer city from address; default Bangalore for this dataset's majority."""
    parts: list[str] = []
    for val in (address, listed_in_city, location):
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            parts.append(str(val).lower())

    blob = " ".join(parts)
    for key, canonical in CITY_ALIASES.items():
        if key in blob:
            return canonical

    return "Bangalore"


def assign_budget_band(cost: float | None, low_max: float, medium_max: float) -> str:
    if cost is None:
        return "medium"
    if cost <= low_max:
        return "low"
    if cost <= medium_max:
        return "medium"
    return "high"


def make_restaurant_id(name: str, address: str, url: str) -> str:
    key = f"{name}|{address}|{url}".strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_raw_dataframe() -> pd.DataFrame:
    from datasets import load_dataset

    logger.info("Downloading dataset %s from Hugging Face…", HF_DATASET_ID)
    dataset = load_dataset(HF_DATASET_ID, split="train")
    return dataset.to_pandas()


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    raw_count = len(df)
    logger.info("Raw rows: %s", raw_count)

    working = df.copy()

    working["_rating"] = working[COL_RATE].map(parse_rating) if COL_RATE in working else None
    working["_cost"] = working[COL_COST].map(parse_cost) if COL_COST in working else None

    working["city"] = working.apply(
        lambda row: extract_city(
            row.get(COL_ADDRESS),
            row.get(COL_LISTED_CITY),
            row.get(COL_LOCATION),
        ),
        axis=1,
    )

    working["locality"] = working.get(COL_LOCATION, working.get(COL_LISTED_CITY))
    working["locality"] = working["locality"].fillna("").astype(str).str.strip()
    working.loc[working["locality"] == "", "locality"] = None

    working["name"] = working[COL_NAME].astype(str).str.strip()
    working["cuisines"] = (
        working[COL_CUISINES].fillna("").astype(str).str.strip().str.lower()
        if COL_CUISINES in working
        else ""
    )

    working["votes"] = (
        pd.to_numeric(working[COL_VOTES], errors="coerce").fillna(0).astype(int)
        if COL_VOTES in working
        else 0
    )

    address_series = (
        working[COL_ADDRESS].fillna("").astype(str)
        if COL_ADDRESS in working
        else pd.Series([""] * len(working))
    )
    url_series = (
        working[COL_URL].fillna("").astype(str) if COL_URL in working else pd.Series([""] * len(working))
    )

    working["restaurant_id"] = [
        make_restaurant_id(n, a, u) for n, a, u in zip(working["name"], address_series, url_series, strict=True)
    ]

    # Drop rows missing required fields
    working = working[working["name"].astype(bool)]
    working = working[working["city"].astype(bool)]
    working = working[working["_rating"].notna()]

    costs = working["_cost"]
    if len(costs.dropna()) >= 10:
        low_max = float(costs.quantile(0.33))
        medium_max = float(costs.quantile(0.66))
    else:
        low_max, medium_max = BUDGET_LOW_MAX, BUDGET_MEDIUM_MAX

    working["approx_cost_for_two"] = working["_cost"]
    working["rating"] = working["_rating"].astype(float)
    working["budget_band"] = working["approx_cost_for_two"].map(
        lambda c: assign_budget_band(c, low_max, medium_max)
    )

    processed = working[
        [
            "restaurant_id",
            "name",
            "city",
            "locality",
            "cuisines",
            "rating",
            "votes",
            "approx_cost_for_two",
            "budget_band",
        ]
    ].copy()

    processed = processed.drop_duplicates(subset=["restaurant_id"], keep="first")
    processed = processed.reset_index(drop=True)

    logger.info(
        "Processed rows: %s (dropped %s, %.1f%%)",
        len(processed),
        raw_count - len(processed),
        100 * (raw_count - len(processed)) / max(raw_count, 1),
    )
    return processed


def run_ingest(output_path: str | Path | None = None) -> Path:
    """Run full ingest pipeline and return path to written Parquet file."""
    settings_path = output_path or Path("../data/processed/restaurants.parquet")
    out = resolve_output_path(settings_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    raw = load_raw_dataframe()
    processed = transform_dataframe(raw)

    tmp = out.with_suffix(".parquet.tmp")
    processed.to_parquet(tmp, index=False)
    tmp.replace(out)

    logger.info("Wrote %s rows to %s", len(processed), out)
    return out
