"""CLI entrypoint: python -m scripts.ingest (from repository root)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow imports from backend package when run from repo root
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.data.ingest import run_ingest  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    output = ROOT / "data" / "processed" / "restaurants.parquet"
    path = run_ingest(output)
    print(f"Ingest complete: {path} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
