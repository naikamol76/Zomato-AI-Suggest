# Edge Cases & Expected Behavior

Catalog of **non-happy-path** scenarios for the restaurant recommendation service. Use with [`architecture.md`](./architecture.md) and [`implementationPlan.md`](./implementationPlan.md).

Each edge case has:

- **ID** — reference in tests and phase eval docs  
- **Area** — component layer  
- **Expected behavior** — what the system should do  
- **Phase** — earliest phase where it must be handled  
- **Severity** — `P0` (must fix for MVP) · `P1` (should fix) · `P2` (nice to have)

---

## How to use this document

1. When implementing a phase, review edge cases tagged for that phase and earlier.  
2. Add automated tests where marked **Automatable**.  
3. Record manual results in the phase [`eval/`](./eval/) checklist.  
4. End-to-end grounding cases are re-verified in **Phase 7**.

---

## 1. Data ingestion & Parquet

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| DATA-01 | HF download fails (network, 403) | Ingest exits non-zero; clear error; no partial corrupt Parquet | 1 | P0 | Mock |
| DATA-02 | Missing required columns in raw schema | Fail ingest with column mapping error; document in `dataSchema.md` | 1 | P0 | Yes |
| DATA-03 | Row missing `name`, `city`, or `rating` | Row dropped; count logged | 1 | P0 | Yes |
| DATA-04 | Duplicate restaurants (same name + city) | Dedupe or keep first; stable `restaurant_id` | 1 | P1 | Yes |
| DATA-05 | `rating` out of range (e.g. > 5, negative) | Clamp or drop; log count of fixes | 1 | P1 | Yes |
| DATA-06 | `approx_cost_for_two` non-numeric / empty | Treat as null; assign `budget_band` via fallback or drop | 1 | P1 | Yes |
| DATA-07 | Cost is 0 or extreme outlier | Still assign band or mark `unknown`; do not crash ingest | 1 | P2 | Yes |
| DATA-08 | Empty cuisine string | Allow; filter by cuisine may exclude | 1 | P2 | Yes |
| DATA-09 | City name inconsistent (`Bengaluru` vs `Bangalore`) | Normalize map in ingest OR document canonical names | 1 | P1 | Partial |
| DATA-10 | Re-run ingest over existing Parquet | Overwrite atomically (write temp → rename) | 1 | P1 | Manual |
| DATA-11 | Parquet file missing at API startup | Startup fails fast with actionable message | 1 | P0 | Yes |
| DATA-12 | Corrupt / truncated Parquet | Startup or load error; no silent empty catalog | 1 | P0 | Yes |
| DATA-13 | Very large file (>100MB) | Load within target (<5s) or log warning | 1 | P2 | Manual |

---

## 2. Restaurant repository & metadata

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| REPO-01 | `list_cities()` on empty DataFrame | Return `[]`; health may report degraded | 1 | P0 | Yes |
| REPO-02 | `list_cuisines(city)` for city with no rows | Return `[]` | 1 | P0 | Yes |
| REPO-03 | `list_cuisines()` without city param | Return global distinct cuisines (or document city-required) | 5 | P1 | Yes |
| REPO-04 | City string with leading/trailing spaces | Trim on query or at ingest | 2 | P1 | Yes |
| REPO-05 | Case mismatch in city (`bangalore`) | Case-insensitive match in filter; metadata lists canonical casing | 2 | P0 | Yes |
| REPO-06 | Concurrent reads during request | Read-only DataFrame safe for MVP single process | 4 | P2 | N/A |

---

## 3. User input & API validation

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| API-01 | Missing required field (`city`, `budget`, `cuisine`) | `422` with field-level errors | 5 | P0 | Yes |
| API-02 | Invalid `budget` enum (`cheap`, `MEDIUM`) | `422`; only `low`/`medium`/`high` accepted | 5 | P0 | Yes |
| API-03 | `min_rating` < 0 or > 5 | `422` | 5 | P0 | Yes |
| API-04 | `min_rating` omitted | Default (e.g. 0 or 3.0) — document in API | 5 | P1 | Yes |
| API-05 | Empty string `city` | `422` | 5 | P0 | Yes |
| API-06 | `additional_notes` very long (10k chars) | Truncate or `422` with max length | 5 | P0 | Yes |
| API-07 | `additional_notes` with control chars / null bytes | Strip or reject | 5 | P1 | Yes |
| API-08 | `additional_notes` prompt-injection attempt | Pass as user text only; system prompt forbids overriding rules | 3 | P1 | Manual |
| API-09 | Malformed JSON body | `422` / `400` | 5 | P0 | Yes |
| API-10 | Wrong `Content-Type` | `422` or `415` | 5 | P2 | Yes |
| API-11 | Extra unknown JSON fields | Ignore (Pydantic default) or reject — document choice | 5 | P2 | Yes |

---

## 4. Candidate filtering

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| FILT-01 | City not in dataset (`Zanzibar`) | Empty candidates; no LLM call; helpful `message` | 2 | P0 | Yes |
| FILT-02 | Valid city but cuisine not found | Empty candidates; suggest relaxing cuisine | 2 | P0 | Yes |
| FILT-03 | Cuisine partial match (`north` → `North Indian`) | Substring match works per architecture | 2 | P0 | Yes |
| FILT-04 | `min_rating` very high (4.9) in sparse city | Empty or few results; no crash | 2 | P0 | Yes |
| FILT-05 | Budget `low` but all matches are `medium` | Empty after budget filter | 2 | P0 | Yes |
| FILT-06 | Filters match > `MAX_CANDIDATES` (e.g. 500 rows) | Return top N by rating, then votes | 2 | P0 | Yes |
| FILT-07 | Filters match exactly 1 row | Single candidate to LLM; still valid | 2 | P0 | Yes |
| FILT-08 | Filters match 0 rows | Empty list; orchestrator skips LLM | 2 | P0 | Yes |
| FILT-09 | Cuisine with special regex chars (`(`, `+`) | Literal substring match, not regex crash | 2 | P1 | Yes |
| FILT-10 | Unicode in city/cuisine (e.g. café) | No encoding crash | 2 | P1 | Yes |
| FILT-11 | `min_rating` = 0 | All ratings included | 2 | P1 | Yes |

---

## 5. Prompt builder

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| PROM-01 | 0 candidates passed to builder | Orchestrator must not call builder/LLM | 4 | P0 | Yes |
| PROM-02 | 1 candidate | Prompt still valid; asks for up to `MAX_RECOMMENDATIONS` | 3 | P0 | Yes |
| PROM-03 | 20 candidates — prompt size | Under model context limit; log token estimate if possible | 3 | P1 | Manual |
| PROM-04 | Missing Jinja2 template file | Clear error at startup or build time | 3 | P0 | Yes |
| PROM-05 | `additional_notes` empty | Prompt omits or says "none" | 3 | P2 | Yes |
| PROM-06 | Candidate with null `locality` / `votes` | Serialize without breaking JSON | 3 | P1 | Yes |

---

## 6. LLM client & provider

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| LLM-01 | Missing `LLM_API_KEY` | Startup warning or fail; recommend 503 on call | 3 | P0 | Yes |
| LLM-02 | Invalid API key | `503` with generic message; log provider error | 3 | P0 | Mock |
| LLM-03 | Provider timeout (>60s) | `503`; optional retry per tenacity | 3 | P0 | Mock |
| LLM-04 | Rate limit 429 | Retry with backoff; then `503` | 3 | P0 | Mock |
| LLM-05 | Provider 5xx | Retry; then `503` | 3 | P0 | Mock |
| LLM-06 | Empty response body | Treat as parse failure | 3 | P0 | Mock |
| LLM-07 | Ollama / custom `LLM_BASE_URL` unreachable | `503`; clear config hint | 3 | P1 | Manual |
| LLM-08 | Model returns markdown-wrapped JSON | Parser strips fences | 3 | P0 | Yes |
| LLM-09 | Model returns prose only (no JSON) | Parse fail → fallback or `502` | 3 | P0 | Yes |
| LLM-10 | Model invents `restaurant_id` not in list | Validator drops; see VAL-* | 3 | P0 | Yes |

---

## 7. Parser & validator (grounding)

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| VAL-01 | Valid JSON, all ids in candidate set | Full enrich from DataFrame | 3 | P0 | Yes |
| VAL-02 | One hallucinated id among five | Drop invalid; return valid remainder | 3 | P0 | Yes |
| VAL-03 | All ids hallucinated | Fallback top-3 by rating OR `502` — document choice | 4 | P0 | Yes |
| VAL-04 | Duplicate ranks (two `rank: 1`) | Re-rank sequentially or keep first | 3 | P1 | Yes |
| VAL-05 | Missing `explanation` field | Default text or drop item — document | 3 | P1 | Yes |
| VAL-06 | LLM returns wrong `rating` in JSON | Ignore; use store values only | 3 | P0 | Yes |
| VAL-07 | LLM returns fewer than `MAX_RECOMMENDATIONS` | Return what is valid | 3 | P1 | Yes |
| VAL-08 | LLM returns more than `MAX_RECOMMENDATIONS` | Truncate to max after validation | 3 | P1 | Yes |
| VAL-09 | `restaurant_id` type mismatch (number vs string) | Coerce to string for lookup | 3 | P1 | Yes |
| VAL-10 | Partial JSON / truncated response | Parse fail → fallback path | 4 | P0 | Yes |

---

## 8. Orchestrator

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| ORCH-01 | Zero candidates after filter | No LLM; `recommendations: []`; `message` set | 4 | P0 | Yes |
| ORCH-02 | LLM success but validator returns 0 items | Fallback or error; log raw response | 4 | P0 | Yes |
| ORCH-03 | LLM throws mid-request | `503`; no partial unvalidated response | 4 | P0 | Yes |
| ORCH-04 | `meta.candidates_considered` matches filter count | Accurate for debugging | 4 | P1 | Yes |
| ORCH-05 | Double submit (two parallel requests) | Both complete independently; no shared mutable state | 5 | P1 | Manual |

---

## 9. REST API & CORS

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| HTTP-01 | `GET /health` before data loaded | `503` or `degraded` — document | 0 | P1 | Yes |
| HTTP-02 | Unknown route | `404` | 5 | P2 | Yes |
| HTTP-03 | `POST` to metadata endpoint | `405` | 5 | P2 | Yes |
| HTTP-04 | CORS preflight from React origin | `200` with allowed methods/headers | 5 | P0 | Manual |
| HTTP-05 | CORS from unknown origin | Blocked in production config | 5 | P1 | Manual |
| HTTP-06 | `GET /metadata/cuisines` without `city` | Global list or `422` — match implementation | 5 | P1 | Yes |

---

## 10. React frontend

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| UI-01 | Submit with empty required fields | Inline validation; no API call | 6 | P0 | Yes |
| UI-02 | API returns empty recommendations + message | Show empty state, not error | 6 | P0 | Yes |
| UI-03 | API `503` during LLM failure | Error banner; allow retry | 6 | P0 | Manual |
| UI-04 | Slow LLM (10s+) | Loading indicator; no double-submit | 6 | P0 | Manual |
| UI-05 | Double-click Submit | Debounce or disable button while loading | 6 | P1 | Manual |
| UI-06 | Wrong `VITE_API_BASE_URL` | Clear network error | 6 | P0 | Manual |
| UI-07 | Backend down on page load | Metadata dropdown fails gracefully | 6 | P1 | Manual |
| UI-08 | City changes — cuisine list | Refresh cuisines for selected city | 6 | P1 | Manual |
| UI-09 | Very long explanation text | Card layout wraps; no overflow break | 6 | P2 | Manual |
| UI-10 | `min_rating` entered as non-number | Client-side block | 6 | P1 | Yes |

---

## 11. Security & configuration

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| SEC-01 | `.env` committed to git | Prevented by `.gitignore` + review | 0 | P0 | Manual |
| SEC-02 | API key in client bundle | Never; only backend env | 6 | P0 | Manual |
| SEC-03 | Log full prompt with user notes in prod | Disabled or redacted | 7 | P1 | Manual |
| SEC-04 | Unauthenticated public API abuse | Accept for MVP; document rate-limit as future | 7 | P2 | N/A |

---

## 12. End-to-end grounding (critical)

| ID | Scenario | Expected behavior | Phase | Sev | Automatable |
|----|----------|-------------------|-------|-----|-------------|
| E2E-01 | Golden query: Bangalore, medium, North Indian, ≥4 | ≥1 result; all fields match Parquet | 7 | P0 | Manual |
| E2E-02 | Every displayed name exists in Parquet for that city | Manual spot-check | 7 | P0 | Manual |
| E2E-03 | Explanation mentions user criteria (cuisine/budget/notes) | Qualitative review | 7 | P1 | Manual |
| E2E-04 | Same request twice | Same restaurant set (LLM may vary text) | 7 | P2 | Manual |
| E2E-05 | Impossible filter combo | Empty UI + message; no fabricated venues | 7 | P0 | Manual |

---

## 13. Phase → edge case index

| Phase | Must verify IDs |
|-------|-----------------|
| 0 | SEC-01, HTTP-01 |
| 1 | DATA-01–13, REPO-01–02 |
| 2 | FILT-01–11, REPO-04–05 |
| 3 | PROM-*, LLM-*, VAL-01–10 |
| 4 | ORCH-01–04, VAL-03, VAL-10 |
| 5 | API-*, HTTP-*, ORCH-05 |
| 6 | UI-01–10, SEC-02 |
| 7 | All P0; E2E-01–05; SEC-03 |

---

## Related documents

- Phase evaluation: [`eval/README.md`](./eval/README.md)  
- [`architecture.md`](./architecture.md) — error handling §7.1  
- [`implementationPlan.md`](./implementationPlan.md) — build phases  
