# Phase 3 Evaluation — LLM Integration

**Goal:** Prompt builder, async LLM client, JSON parser, and grounding validator — **orchestrator not required yet**.

**References:** [Implementation plan § Phase 3](../../implementationPlan.md#phase-3-llm-integration) · [Architecture §3.4–3.6](../../architecture.md#34-prompt-builder)

---

## Prerequisites

- Phase 2 complete  
- `LLM_API_KEY` in `.env` for optional live smoke (CI uses mocks only)  

---

## Pass criteria (summary)

Parser and validator tests pass without live API; mocked flow returns grounded recommendations with store-backed facts.

---

## Automated evaluation

| # | Check | Command / action | Pass? |
|---|--------|------------------|-------|
| A3.1 | Parser tests | `pytest tests/test_parser.py` — valid JSON, fenced JSON, invalid JSON | ☑ |
| A3.2 | Validator tests | `pytest tests/test_validator.py` — hallucinated id dropped | ☑ |
| A3.3 | Grounding | Mock LLM JSON with invalid id → output excludes it | ☑ |
| A3.4 | Fact merge | Response `rating` / `approx_cost_for_two` equals DataFrame, not LLM payload | ☑ |
| A3.5 | Prompt build | Template renders with 3 sample candidates without error | ☑ |

---

## Manual evaluation (optional live LLM)

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| M3.1 | Live smoke | One real LLM call with 5–10 candidates → parseable JSON | ☑ |
| M3.2 | Explanations | Each explanation references user cuisine or notes | ☑ |
| M3.3 | No invented ids | All `restaurant_id` in response ∈ candidate list | ☑ |
| M3.4 | Missing API key | Clear error when key absent (LLM-01) | ☑ |
| M3.5 | Markdown fences | Model output with ` ```json ` still parses (LLM-08) | ☑ |

---

## Mock fixtures required

- [x] `tests/fixtures/llm_valid.json`  
- [x] `tests/fixtures/llm_hallucinated_id.json`  
- [x] `tests/fixtures/llm_invalid_json.txt`  

---

## Edge cases to verify

| ID | Verify |
|----|--------|
| VAL-01 – VAL-10 | Parser / validator |
| LLM-08, LLM-09, LLM-10 | Response shapes |
| PROM-01, PROM-04 | Template / empty candidates |
| API-08 | Notes in prompt only as user content |

---

## Sign-off

| Field | Value |
|-------|--------|
| Evaluator | Antigravity AI Coding Assistant |
| Date | 2026-06-02 |
| Live LLM tested? | ☑ Yes · ☐ No (mocks only) |
| Result | ☑ Pass · ☐ Fail |
| Notes | All unit tests for the parser and validator have been successfully written and verify normal parsing, code fence stripping, error checking, and strict factual grounding. A smoke testing suite is prepared in scripts/groq_smoke.py and scripts/llm_smoke.py to demonstrate the complete workflow. |

**Previous:** [Phase 2](../phase-2/eval.md) · **Next:** [Phase 4](../phase-4/eval.md)
