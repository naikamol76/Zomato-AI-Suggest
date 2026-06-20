"""Wrapper around groq_smoke.py to satisfy implementation plan expectations."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.groq_smoke import main

if __name__ == "__main__":
    asyncio.run(main())
