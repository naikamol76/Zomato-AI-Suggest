# Data Schema: Zomato Restaurant Dataset

Source: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) on Hugging Face (~51.7k rows, Bangalore-focused listings).

Ingest implementation: `backend/app/data/ingest.py`  
Processed output: `data/processed/restaurants.parquet`

---

## Raw → processed column mapping

| Raw column (HF / CSV) | Processed column | Transformation |
|----------------------|------------------|----------------|
| `url` | — | Used only for stable `restaurant_id` hash |
| `name` | `name` | Strip whitespace; required |
| `address` | `city` | City inferred via keyword match (e.g. Bengaluru → Bangalore, New Delhi → Delhi) |
| `location` | `locality` | Neighbourhood; fallback empty → null |
| `listed_in(city)` | — | Locality hint (often neighbourhood name, not metro city) |
| `rate` | `rating` | Parse `4.1/5`; drop `NEW`, `-`, invalid |
| `votes` | `votes` | Integer; default 0 |
| `cuisines` | `cuisines` | Lowercase string; comma-separated preserved |
| `approx_cost(for two people)` | `approx_cost_for_two` | Numeric INR; commas stripped |
| — | `budget_band` | `low` / `medium` / `high` from cost tertiles (or 500/1000 ₹ fallback) |
| `name` + `address` + `url` | `restaurant_id` | SHA-256 hash (16 hex chars) |

---

## Processed schema

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `restaurant_id` | string | yes | Primary key |
| `name` | string | yes | |
| `city` | string | yes | Canonical names: Bangalore, Delhi, … |
| `locality` | string | null | |
| `cuisines` | string | yes | Substring match in Phase 2 filter |
| `rating` | float | yes | 0–5 |
| `votes` | int | yes | ≥ 0 |
| `approx_cost_for_two` | float | null | INR for two people |
| `budget_band` | string | yes | `low`, `medium`, `high` |

---

## Cleaning rules

1. Drop rows without `name`, `city`, or parseable `rating` (see edge case DATA-03).  
2. Deduplicate on `restaurant_id` (keep first).  
3. Ratings outside 0–5 after parse are dropped.  
4. City defaults to **Bangalore** when no known city keyword is found in address (most source rows are Bangalore listings).

---

## Budget bands

| Band | Rule (default when few cost values) |
|------|-------------------------------------|
| `low` | ≤ ₹500 for two |
| `medium` | ₹501 – ₹1000 |
| `high` | > ₹1000 |

When ≥10 rows have valid cost, **33rd / 66th percentiles** of `approx_cost_for_two` define band thresholds instead.

---

## Expected volumes (after ingest)

| Metric | Typical range |
|--------|----------------|
| Raw rows | ~51,700 |
| Processed rows | ~40,000 – 52,000 (depends on rating parse drops) |
| Primary city | Bangalore (majority) |
| Other cities | Present when address contains Delhi, Mumbai, etc. |

---

## Commands

```bash
# From repository root
python -m scripts.ingest
```

```bash
# Or via Make
make ingest
```

---

## Related

- [edgecase.md](./edgecase.md) — DATA-* edge cases  
- [eval/phase-1/eval.md](./eval/phase-1/eval.md) — Phase 1 verification  
