---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 4 · Add AI to the Catalog, then Test the AI"
footer: "Acuity Training · Day 4 of 4"
---

<!-- _class: title -->

# Module 12 ⭐
## Testing & Validating AI Tools and Outputs
**~40 min · then 80 min lab** — the spine module: Day-3 patterns applied to AI
---
# Day 3 → Day 4: same patterns, new target

| Day 3 (deterministic code) | Day 4 (AI code) |
|---|---|
| `mock_session = Mock()` | `catalog_agent.override(model=TestModel())` |
| `@patch("requests.Session")` | `FunctionModel(_scripted_calls(...))` |
| `@pytest.mark.parametrize` | `@pytest.mark.parametrize` over golden evals |
| assert exact equality | assert **shape**, **tools called**, **substring** |

Same `pytest` muscle, same injection seams, same CI. The only difference: **the thing you're isolating is an LLM, not a network call.**
---
<!-- _class: title -->

# Section 1
## Why test AI differently?
the problem + the taxonomy
---
# 12.1 · Why AI needs a different testing strategy

```text
traditional:  same input → same output → assertEqual()
AI:           same input → distribution of outputs → ?
```

You can't `assertEqual` on prose. You **can** assert on:
- **Shape** — validates against the Pydantic schema
- **Behaviour** — which tools got called, in what order
- **Substrings** — the answer mentions the key fact
- **Bounds** — ≤ N tool calls, ≤ M steps

Stop testing prose. Start testing shape and behaviour.
---
# 12.2 · Four classes of tests for an AI system

```text
1. Tool tests     ─ each tool is plain Python
2. Schema tests   ─ LLM JSON validates against Pydantic
3. Loop tests     ─ mock the LLM, verify the orchestration
4. Golden evals   ─ a file of cases that lock behaviour
```

**All four run without an API key** — CI never pays OpenAI. Only an optional live eval does.
---
<!-- _class: title -->

# Section 2
## Writing the tests
`FunctionModel` · `TestModel` · `capture_run_messages` · golden evals
---
# 12.3 · `FunctionModel` — scripting the LLM's replies

`FunctionModel` replaces the real LLM with a **Python function you control** — same idea as `Mock(return_value=...)` from Day 3.

```python
from pydantic_ai.models.function import FunctionModel

def _force_tool_call(tool_name):
    """Return a function that makes the agent call one specific tool, then answer."""
    def model_fn(messages, info):
        # first call → ask for the tool; second call → final text answer
        ...
    return model_fn
```

You write the function; the agent loop runs exactly as if a real LLM responded. No network, no API key, deterministic.
---
# 12.4 · Tool tests — deterministic Python

```python
class TestTools:
    def test_count_by_category(self):
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

The tools are **not magic** — they're the functions you tested all Day 3. `FunctionModel` forces one specific tool call so you can inspect its return value.
---
# 12.5 · Schema tests — Pydantic validation

```python
def test_rejects_negative_price(self):
    with pytest.raises(ValidationError):
        CatalogQuery(max_price=-5.0)

def test_apply_query_filters(self):
    catalog = _fake_catalog(SAMPLE_PRODUCTS)
    q = CatalogQuery(category="Electronics", max_price=1000.0)
    assert {p["id"] for p in apply_query(q, catalog)} == {1}
```

Pure Pydantic + pure Python — the constraints from M10. The LLM is not in the loop.
---
# 12.6 · Loop tests — script the model (Day-3 déjà vu)

```python
def test_single_tool_call_then_answer(self):
    catalog = _fake_catalog(SAMPLE_PRODUCTS)
    with catalog_agent.override(model=FunctionModel(
        _scripted_calls([("count_by_category", {})],
                        "We have 3 Electronics.")
    )):
        with capture_run_messages() as msgs:
            result = catalog_agent.run_sync("how many?", deps=catalog)
    tool_calls = [p.tool_name for msg in msgs for p in msg.parts
                  if p.part_kind == "tool-call"]
    assert tool_calls == ["count_by_category"]
```

`FunctionModel` scripts the LLM's replies — **the same mock pattern as Day 3's `requests` retry test.** No network, no key, deterministic.
---
# 12.7 · 🔮 What does `TestModel` pass as arguments?

`TestModel()` calls every registered tool automatically — no scripting. But what arguments does it use?

Think about it: `search_products(term: str)`. What does `TestModel` pass for `term`?

---
# 12.8 · The quick way — `TestModel`

```python
def test_all_tools_callable(self):
    """TestModel calls every tool with default args — smoke test."""
    catalog = _fake_catalog(SAMPLE_PRODUCTS)
    with catalog_agent.override(model=TestModel()):
        result = catalog_agent.run_sync("test", deps=catalog)
    assert result.output
```

`TestModel` auto-calls each registered tool with **default-typed arguments**: `str → "a"`, `int → 0`, `bool → True`. Great for smoke tests — no scripting needed. Use `FunctionModel` when you need to control **which** tool gets called and with what args.
---
# 12.9 · Golden evals — a file of cases

```json
[
  { "id": "eval-01",
    "prompt": "How many products are in Electronics?",
    "expected_tool_calls": ["count_by_category"],
    "expected_answer_contains": ["Electronics"] },
  { "id": "eval-02",
    "prompt": "What's the most expensive product?",
    "expected_tool_calls": ["list_products"],
    "expected_answer_contains": ["Mechanical Keyboard"] }
]
```

Cases live **outside** the code (Day 2 / M6). Add a row every time a real bug ships — the file becomes your **regression suite for behaviour**. This is M10's held-out eval, made permanent.
---
# 12.10 · Parametrize over the golden file

```python
@pytest.mark.eval
class TestGoldenQueries:
    @pytest.mark.parametrize("case", _golden_cases(),
                             ids=[c["id"] for c in _golden_cases()])
    def test_case(self, case):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        tool_sequence = [(n, {}) for n in case["expected_tool_calls"]]
        answer = " ".join(case["expected_answer_contains"])
        with catalog_agent.override(model=FunctionModel(
            _scripted_calls(tool_sequence, answer)
        )):
            with capture_run_messages() as msgs:
                result = catalog_agent.run_sync(case["prompt"], deps=catalog)
        tool_calls = [p.tool_name for msg in msgs for p in msg.parts
                      if p.part_kind == "tool-call"]
        assert tool_calls == case["expected_tool_calls"]
        for needle in case["expected_answer_contains"]:
            assert needle in result.output
```

`@pytest.mark.eval` (a Day-3 custom marker) lets you run *just* these: `uv run pytest -m eval`.

<div class="code-along">▶ Code-along now → notebook: module-12 golden-evals section — FunctionModel to script the LLM, assert the tool sequence, then parametrize the golden file</div>
---
<!-- _class: title -->

# Section 3
## CI & production readiness
no API key in CI · reliability boundaries · the eval ladder
---
# 12.11 · Preventing accidental real API calls

```python
import pydantic_ai
pydantic_ai.models.ALLOW_MODEL_REQUESTS = False
```

Set this at the top of your test file. Any test that accidentally tries to hit a real model gets an immediate error instead of a surprise bill. Override with `catalog_agent.override(model=TestModel())` — the safeguard only blocks *unintended* real calls.
---
# 12.12 · Same CI, one green check

```yaml
# .github/workflows/tests.yml — already in place from Day 3
- run: uv run pytest --cov --html=report.html
```

**No new workflow.** Agent tests live under `tests/` alongside model + client tests, so the **same Day-3 CI matrix** runs them all.

```text
✓ test (3.10)   ✓ test (3.11)   ✓ test (3.12)   53 tests incl. agent
```

One green check covers the whole stack — Python, API, and AI.
---
# 12.13 · Production-ready AI app shape

An AI app is still an app. The LLM is one component inside a normal system boundary:

```text
UI / CLI
  ↓
application service
  ↓
agent / structured LLM call
  ↓
tools = ProductCatalog methods
  ↓
database / external systems
```

The production question is not "is the model smart?" It is:
**can we control, observe, test, and recover from what the model does?**
---
# 12.14 · Reliability boundaries

Separate what must be deterministic from what can be flexible:

| Deterministic | Flexible |
|---|---|
| tool functions | final wording |
| Pydantic schemas | explanation style |
| validation errors | reasoning path |
| max step limits | model phrasing |
| write confirmations | answer tone |

Design rule: **probabilistic model inside deterministic rails.**
---
# 12.15 · Eval ladder for AI apps

Start cheap and deterministic; add live checks only where they earn their keep:

```text
unit tests
  ↓
schema tests
  ↓
mocked loop tests (FunctionModel / TestModel)
  ↓
golden evals
  ↓
optional live LLM evals
  ↓
production monitoring
```

Every bug becomes either a test, a golden case, or a monitor.

That is how an AI demo becomes an AI application.
---
<!-- _class: title -->

# Section 4
## Observability — Logfire
tests catch bugs before deploy; tracing catches them after
---
# 12.16 · Logfire — two lines to trace every agent run

```python
import logfire
logfire.configure(send_to_logfire=False)   # local console, no token
logfire.instrument_pydantic_ai()           # auto-trace every run_sync()
```

Every agent run now prints a nested trace — which tools, in what order, how long, what failed:

```text
catalog_agent run
  chat function:model_fn:
  running tool: count_by_category        ← same data as capture_run_messages()
  chat function:model_fn:
```

Same information you assert on in tests — but for production, in real time. Add your own detail with `logfire.info("searching", term=term)` or `with logfire.span("catalog_search"):` inside tools.
---
# 12.17 · From console to dashboard

```python
logfire.configure()                        # drop send_to_logfire=False → sends to logfire.pydantic.dev
logfire.instrument_pydantic_ai()
```

Set `LOGFIRE_TOKEN` — traces flow to the Logfire dashboard. Filter by agent name, tool name, latency. Set alerts on error rates or runaway tool-call counts.

**The pattern:** tests catch bugs before deploy; Logfire catches them after. Same agent, same tools — the observability layer wraps around what you already built. Every bug becomes either a test, a golden case, or a monitor.

<div class="code-along">▶ Code-along now → notebook: module-12 Logfire cell — two lines, then watch the trace</div>
---
<!-- _class: lab -->

# 🧪 Lab 12 — Test the Agent ⭐

**80 min** · open `labs/lab-12-test-the-agent.md`

You'll write:
1. Tool tests (deterministic Python via `FunctionModel`)
2. Schema tests (Pydantic validation)
3. Loop tests with `FunctionModel` + `capture_run_messages`
4. Golden evals from `tests/evals/golden_queries.json` (`@pytest.mark.eval`)

End state: `uv run pytest -q` green, **no `OPENAI_API_KEY` needed**, ~20 tests. Your repo matches `project/solution/`.
---
<!-- _class: title -->

# End of Day 4 ✅

**Your `my-catalog/` project:**

- Python catalog + dataclasses + type hints (Day 1)
- Pydantic models + `ProductCatalog` + CSV import (Days 1–2)
- pytest + mocks + parametrize + HTML reports + CI (Day 3)
- LLM-powered `CatalogAgent` with **its own test suite** + Logfire observability (Day 4)

**One project. Four days. Tested. Agentic. Observable. Done.**
---
<!-- _class: title -->

# Where to next

- Swap OpenAI for Anthropic / Azure / a local model — change the model string, same tools
- Climb the M10 ladder for real: few-shot → RAG when the catalog outgrows the context window
- Add memory: persist `messages` per `session_id`
- Fine-tune `parse_nl_query` once volume justifies it — you already have the eval
- Connect Logfire to your dashboard — `logfire.configure()` + `LOGFIRE_TOKEN`, same two lines
- Take the patterns home: every one works on your real production code
