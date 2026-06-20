"""Unit tests for LlmResponseParser."""

from __future__ import annotations

from pathlib import Path
import pytest

from app.services.parser import LlmResponseParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_valid_json() -> None:
    parser = LlmResponseParser()
    valid_file = FIXTURES_DIR / "llm_valid.json"
    raw_text = valid_file.read_text(encoding="utf-8")

    payload = parser.parse(raw_text)
    assert payload.summary == "Here are the top restaurants matching your preferences."
    assert len(payload.recommendations) == 2
    assert payload.recommendations[0].restaurant_id == "aaa111"
    assert payload.recommendations[0].rank == 1
    assert payload.recommendations[0].explanation == "Great North Indian food with highly rated dishes."
    assert payload.recommendations[1].restaurant_id == "eee555"
    assert payload.recommendations[1].rank == 2
    assert payload.recommendations[1].explanation == "Premium Mughlai cuisine, perfect for a high rating experience."


def test_parse_fenced_json() -> None:
    parser = LlmResponseParser()
    raw_text = """
Some introductory text from LLM.
```json
{
  "summary": "Fenced JSON summary",
  "recommendations": [
    {
      "restaurant_id": "bbb222",
      "rank": 1,
      "explanation": "Yummy food."
    }
  ]
}
```
Some trailing remarks.
"""
    payload = parser.parse(raw_text)
    assert payload.summary == "Fenced JSON summary"
    assert len(payload.recommendations) == 1
    assert payload.recommendations[0].restaurant_id == "bbb222"
    assert payload.recommendations[0].rank == 1
    assert payload.recommendations[0].explanation == "Yummy food."


def test_parse_invalid_json() -> None:
    parser = LlmResponseParser()
    invalid_file = FIXTURES_DIR / "llm_invalid_json.txt"
    raw_text = invalid_file.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="Failed to parse LLM response as JSON"):
        parser.parse(raw_text)


def test_parse_empty_or_whitespace() -> None:
    parser = LlmResponseParser()
    with pytest.raises(ValueError, match="Empty response received"):
        parser.parse("")
    with pytest.raises(ValueError, match="Empty response received"):
        parser.parse("   \n  ")
