# Lab 12 — Test the Agent ⭐

**~80 min · Day 4 · Module 12 · the spine module**

## Goal
Write the agent's test suite — **four classes**, none needing an OpenAI key. AI systems look non-deterministic from the outside, but the discipline is the same one you built on Day 3: tools are plain functions, LLM JSON is a Pydantic schema, the loop is mocked, behaviour is locked by golden cases. Done when `unset OPENAI_API_KEY && pytest -q` → **~53 passed**.

## Start with
Your Lab 11 folder (`my-catalog/` with a working `CatalogAgent`), or `project/checkpoints/day-4-start/` + the `agent.py` you built in Lab 11.

## Get the starter tests
```bash
cp -r ../labs/lab-12-test-the-agent/starter/tests/test_agent.py tests/   # run from my-catalog/
cp -r ../labs/lab-12-test-the-agent/starter/tests/evals tests/
```
| File | What |
|---|---|
| `tests/test_agent.py` | mock helpers `_fake_api` / `_make_agent` / `_llm_message` / `_tool_call` / `_llm_response` are **provided** (plumbing). Four classes are **stubs to fill** |
| `tests/evals/golden_queries.json` | **3 starter cases** — add more as you ship |

Each stub fails with a `# TODO` message until you implement it. The LLM is a bare `MagicMock`; you script its responses per test.

## What to implement
- **TestTools** — each tool is a plain function: `agent.registry.get(name).fn(...)`. Assert deterministic results (`count_by_category` → `{"Electronics": 3, "Fitness": 1}`, case-insensitive search, `update_price` mutates, unknown name → `KeyError`).
- **TestCatalogQuerySchema** — `pytest.raises(ValidationError)` on bad LLM JSON (`CatalogQuery(max_price=-5.0)`); `apply_query(q, api)` filters by category/price and `in_stock_only`.
- **TestAgentLoop** — mock the LLM with `create.side_effect=[...]`; assert tool **order** + arguments + `steps`. Include the **`max_steps`→`AgentError("did not converge")`** runaway test and the **unknown-tool case** (records an `{"error": ...}` observation — it does **not** raise — so the agent can recover).
- **TestGoldenQueries** (`@pytest.mark.eval`) — parametrize over the JSON; assert tool calls match and every `expected_answer_contains` substring appears.

## Steps

1. Copy the starter `test_agent.py` and `evals/` into your `my-catalog/tests/` (commands above). Keep `tests/__init__.py`.

2. **Fill `TestTools`.** Reach a tool through the registry and assert on the value:
   ```python
   result = agent.registry.get("count_by_category").fn()
   assert result == {"Electronics": 3, "Fitness": 1}
   ```

3. **Fill `TestCatalogQuerySchema`.** The schema guards what the LLM returns:
   ```python
   with pytest.raises(ValidationError):
       CatalogQuery(max_price=-5.0)
   ```
   Then `apply_query(CatalogQuery(category="Electronics", max_price=1000.0), _fake_api(SAMPLE_PRODUCTS))` → `{1}`.

4. **Fill `TestAgentLoop`.** Script the LLM, then assert what *your* code did:
   ```python
   agent.llm.chat.completions.create.side_effect = [
       _llm_response(_llm_message(tool_calls=[_tool_call("c1", "count_by_category")])),
       _llm_response(_llm_message(content="We have 3 Electronics.")),
   ]
   r = agent.ask("how many electronics?")
   assert [c.tool for c in r.tool_calls] == ["count_by_category"]
   assert r.steps == 2
   ```
   Add the runaway test (`return_value` is always a tool call → `pytest.raises(AgentError, match="did not converge")`) and the unknown-tool test (`r.tool_calls[0].result["error"]` contains `"unknown tool"`; no raise).

5. **Fill `TestGoldenQueries`.** Parametrize over `_golden_cases()`; for each case, script one tool call per `expected_tool_calls` entry then a final answer joining the `expected_answer_contains` substrings; assert tool order + substrings.

6. **Register the `eval` marker** in `pyproject.toml` (so `--strict-markers` accepts it):
   ```toml
   markers = [
       "integration: tests that hit a live FastAPI server (slow)",
       "eval: golden-prompt evaluation cases (Day 4)",
   ]
   ```

7. **Run it — without an API key:**
   ```bash
   unset OPENAI_API_KEY && pytest -q
   pytest -q -m eval                  # just the golden cases
   pytest -q -m "not integration"     # CI-fast subset
   ```

Add a golden case **every time a real bug ships** — that's how the JSON earns its keep.

## Expected output

```
$ unset OPENAI_API_KEY && pytest -q
.....................................................                    [100%]
53 passed in 0.9s

$ pytest -q -m eval
...                                                                      [100%]
3 passed in 0.04s
```

## Common pitfalls
- Asserting the LLM's **exact** wording. LLMs paraphrase — assert on **substrings, tool calls, and schemas**, never prose.
- Forgetting `unset OPENAI_API_KEY` in CI — a "test" run that hits the real API bills you. The setup must never build a real client.
- `OpenAI()` at the top of `agent.py` grabs the key at import and kills keyless machines — construct it lazily inside `default_openai_client()`.
- Writing 20 golden cases on day one. Start with 3-6 high-signal ones; grow on real bugs.
- Testing "the LLM is smart" — you can't. Test that **your code reacts correctly** to a class of LLM behaviours.

## Stretch (optional)
- Opt-in real-LLM check: a separate `@pytest.mark.live_llm` test, skipped in CI, run manually to confirm the mocked golden cases reflect reality.
- Record real OpenAI responses once with `pytest-recording` / `vcrpy`, then replay them deterministically.
- A cost-ceiling test asserting one agent loop stays under N tool calls (runaway-cost regression guard).

---

**End of Day 4 — and the workshop.** Your `my-catalog/` is now a tested, agentic project: Python core (Day 1) → FastAPI + typed `APIClient` + CSV import (Days 1-2) → `pytest` suite with mocks + CI (Day 3) → LLM `CatalogAgent` with tools, loop, and tests (Day 4). **One project. Four days. Tested. Agentic. Done.**
