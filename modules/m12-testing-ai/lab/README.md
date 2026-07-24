# Lab 12 — Test the Agent ⭐

**~80 min · Day 4 · Module 12 · the spine module**

## Goal
Write the agent's test suite — **four classes**, none needing an OpenAI key. AI systems look non-deterministic from the outside, but the discipline is the same one you built on Day 3: tools are plain functions, LLM JSON is a Pydantic schema, the loop is mocked, behaviour is locked by golden cases. Done when `unset OPENAI_API_KEY && uv run pytest -q` → **all passed**.

## Start with
Your Lab 11 folder (`my-catalog/` with a working `catalog_agent`), or `project/checkpoints/day-4-start/` + the `agent.py` you built in Lab 11.

## Get the starter tests
```bash
cp -r ../labs/lab-12-test-the-agent/starter/tests/test_agent.py tests/   # run from my-catalog/
cp -r ../labs/lab-12-test-the-agent/starter/tests/evals tests/
```
| File | What |
|---|---|
| `tests/test_agent.py` | helpers `_fake_catalog` / `_force_tool_call` / `_scripted_calls` are **provided** (plumbing). Four classes are **stubs to fill** |
| `tests/evals/golden_queries.json` | **3 starter cases** — add more as you ship |

Each stub fails with a `pytest.fail(...)` until you implement it. The LLM is mocked via Pydantic AI's `FunctionModel` and `TestModel`; you script its responses per test.

## What to implement
- **TestTools** — force a tool call with `FunctionModel`, then inspect the tool return in `capture_run_messages()`. Assert deterministic results (`count_by_category` → `{"Electronics": 3, "Fitness": 1}`, case-insensitive search, `update_price` mutates).
- **TestCatalogQuerySchema** — `pytest.raises(ValidationError)` on bad LLM JSON (`CatalogQuery(max_price=-5.0)`); `apply_query(q, catalog)` filters by category/price and `in_stock_only`.
- **TestAgentLoop** — use `FunctionModel` with `_scripted_calls` to script tool-call sequences; use `capture_run_messages()` to verify tool **order**. Include a `TestModel` smoke test that confirms all tools are callable.
- **TestGoldenQueries** (`@pytest.mark.eval`) — parametrize over the JSON; assert tool calls match and every `expected_answer_contains` substring appears in `result.output`.

## Steps

1. Copy the starter `test_agent.py` and `evals/` into your `my-catalog/tests/` (commands above).

2. **Fill `TestTools`.** Force a tool call via `FunctionModel`, then find the result in messages:
   ```python
   catalog = _fake_catalog(SAMPLE_PRODUCTS)
   with catalog_agent.override(model=FunctionModel(
       _force_tool_call("count_by_category")
   )):
       with capture_run_messages() as msgs:
           catalog_agent.run_sync("count", deps=catalog)
   tool_return = [p for msg in msgs for p in msg.parts
                  if p.part_kind == "tool-return"][0]
   assert tool_return.content == {"Electronics": 3, "Fitness": 1}
   ```

3. **Fill `TestCatalogQuerySchema`.** The schema guards what the LLM returns:
   ```python
   with pytest.raises(ValidationError):
       CatalogQuery(max_price=-5.0)
   ```
   Then `apply_query(CatalogQuery(category="Electronics", max_price=1000.0), _fake_catalog(SAMPLE_PRODUCTS))` → `{1}`.

4. **Fill `TestAgentLoop`.** Script the model, then assert what *your* code did:
   ```python
   catalog = _fake_catalog(SAMPLE_PRODUCTS)
   with catalog_agent.override(model=FunctionModel(
       _scripted_calls([("count_by_category", {})], "We have 3 Electronics.")
   )):
       with capture_run_messages() as msgs:
           result = catalog_agent.run_sync("how many?", deps=catalog)
   tool_calls = [p.tool_name for msg in msgs for p in msg.parts
                 if p.part_kind == "tool-call"]
   assert tool_calls == ["count_by_category"]
   ```

5. **Fill `TestGoldenQueries`.** Parametrize over `_golden_cases()`; for each case, build a `_scripted_calls` from `expected_tool_calls`, set the final answer to join `expected_answer_contains`, and assert tool order + substrings.

6. **Register the `eval` marker** in `pyproject.toml` (so `--strict-markers` accepts it):
   ```toml
   markers = [
       "integration: tests that hit a live FastAPI server (slow)",
       "eval: golden-prompt evaluation cases (Day 4)",
   ]
   ```

7. **Run it — without an API key:**
   ```bash
   unset OPENAI_API_KEY && uv run pytest -q
   uv run pytest -q -m eval                  # just the golden cases
   uv run pytest -q -m "not integration"     # CI-fast subset
   ```

Add a golden case **every time a real bug ships** — that's how the JSON earns its keep.

## Expected output

```
$ unset OPENAI_API_KEY && uv run pytest -q
....................                                                      [100%]
20 passed in 1.2s

$ uv run pytest -q -m eval
...                                                                      [100%]
3 passed in 0.3s
```

## Common pitfalls
- Asserting the LLM's **exact** wording. LLMs paraphrase — assert on **substrings, tool calls, and schemas**, never prose.
- Forgetting `pydantic_ai.models.ALLOW_MODEL_REQUESTS = False` — without it, a missing `override` silently hits the real API.
- Not using `capture_run_messages()` — without it, you can't inspect which tools were called.
- Writing 20 golden cases on day one. Start with 3-6 high-signal ones; grow on real bugs.
- Testing "the LLM is smart" — you can't. Test that **your code reacts correctly** to a class of LLM behaviours.

## Stretch (optional)
- Opt-in real-LLM check: a separate `@pytest.mark.live_llm` test, skipped in CI, run manually to confirm the mocked golden cases reflect reality.
- Record real model responses once with `pytest-recording` / `vcrpy`, then replay them deterministically.
- A cost-ceiling test asserting one agent loop stays under N tool calls (runaway-cost regression guard).

---

**End of Day 4 — and the workshop.** Your `my-catalog/` is now a tested, agentic project: Python core + `ProductCatalog` (Day 1) → Pydantic models + CSV import (Day 2) → `pytest` suite with mocks + CI (Day 3) → LLM `CatalogAgent` with tools, loop, and tests (Day 4). **One project. Four days. Tested. Agentic. Done.**
