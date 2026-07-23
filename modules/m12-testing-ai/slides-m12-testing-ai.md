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
# 12.3 · Tool tests — deterministic Python

```python
class TestTools:
    def test_search_is_case_insensitive(self):
        agent = _make_agent()
        out = agent.registry.get("search_products").fn(term="KEYBOARD")
        assert out[0]["id"] == 2
```

The tools are **not magic** — they're the functions you tested all Day 3. Same Arrange → Act → Assert. No LLM involved.
---
# 12.4 · Schema tests — Pydantic validation

```python
def test_rejects_negative_price(self):
    with pytest.raises(ValidationError):
        CatalogQuery(max_price=-5.0)

def test_apply_query_filters(self):
    api = _fake_api(SAMPLE_PRODUCTS)
    q = CatalogQuery(category="Electronics", max_price=1000.0)
    assert {p["id"] for p in apply_query(q, api)} == {1}
```

Pure Pydantic + pure Python — the constraints from M10. The LLM is not in the loop.
---
# 12.5 · Loop tests — mock the LLM (Day-3 déjà vu)

```python
def test_single_tool_call_then_answer(self):
    agent = _make_agent()
    agent.llm.chat.completions.create.side_effect = [
        _llm_response(_llm_message(tool_calls=[_tool_call("c1", "count_by_category")])),
        _llm_response(_llm_message(content="We have 3 Electronics.")),
    ]
    r = agent.ask("how many electronics?")
    assert [c.tool for c in r.tool_calls] == ["count_by_category"]
```

`side_effect=[...]` scripts the LLM's replies — **the same mock pattern as Day 3's `requests` retry test.** No network, no key, deterministic.
---
# 12.6 · Loop tests — runaway protection

```python
def test_max_steps_hit_raises(self):
    agent = _make_agent()
    agent.llm.chat.completions.create.return_value = _llm_response(
        _llm_message(tool_calls=[_tool_call("c1", "count_by_category")]))
    with pytest.raises(AgentError, match="did not converge"):
        agent.ask("loop forever")
```

The `max_steps` net you wrote in Lab 11 now has a test. A future refactor that drops the cap → CI goes red.
---
# 12.7 · Golden evals — a file of cases

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
# 12.8 · Parametrize over the golden file

```python
@pytest.mark.eval
class TestGoldenQueries:
    @pytest.mark.parametrize("case", _golden_cases(),
                             ids=[c["id"] for c in _golden_cases()])
    def test_case(self, case):
        agent = _make_agent()
        agent.llm.chat.completions.create.side_effect = _scripted(case)
        result = agent.ask(case["prompt"])
        assert [c.tool for c in result.tool_calls] == case["expected_tool_calls"]
        for needle in case["expected_answer_contains"]:
            assert needle in result.answer
```

`@pytest.mark.eval` (a Day-3 custom marker) lets you run *just* these: `pytest -m eval`.

<div class="code-along">▶ Code-along now → notebook: module-12 golden-evals section — mock the LLM with side_effect, assert the tool sequence, then parametrize the golden file</div>
---
# 12.9 · Same CI, one green check

```yaml
# .github/workflows/tests.yml — already in place from Day 3
- run: pytest --cov --html=report.html
```

**No new workflow.** Agent tests live under `tests/` alongside model + client tests, so the **same Day-3 CI matrix** runs them all.

```text
✓ test (3.10)   ✓ test (3.11)   ✓ test (3.12)   53 tests incl. agent
```

One green check covers the whole stack — Python, API, and AI.
---
# 12.10 · Production-ready AI app shape

An AI app is still an app. The LLM is one component inside a normal system boundary:

```text
UI / CLI
  ↓
application service
  ↓
agent / structured LLM call
  ↓
tools = APIClient methods
  ↓
database / external systems
```

The production question is not "is the model smart?" It is:
**can we control, observe, test, and recover from what the model does?**
---
# 12.11 · Reliability boundaries

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
# 12.12 · Observe every AI step

If production breaks, you need a trace:

```python
logger.info("agent_step", extra={
    "request_id": request_id,
    "model": self.model,
    "step": step,
    "tool": call.function.name,
    "arguments": call.function.arguments,
    "latency_ms": latency_ms,
})
```

Log: prompt id, model, tool calls, arguments, observations, final answer, latency, token cost.

No trace = no debugging. No debugging = no reliable AI app.
---
# 12.13 · Human-in-the-loop for writes

Not all tools carry the same risk:

| Tool type | Example | Policy |
|---|---|---|
| Read | `list_products` | call directly |
| Search | `search_products` | call directly |
| Update | `update_price` | ask for confirmation |
| Delete | `delete_product` | require confirmation + audit |

Pattern:

```text
LLM proposes action → app shows diff → user confirms → tool executes
```

The model can recommend. Your application decides.
---
# 12.14 · Eval ladder for AI apps

Start cheap and deterministic; add live checks only where they earn their keep:

```text
unit tests
  ↓
schema tests
  ↓
mocked loop tests
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
<!-- _class: lab -->

# 🧪 Lab 12 — Test the Agent ⭐

**80 min** · open `labs/lab-12-test-the-agent.md`

You'll write:
1. Tool tests (deterministic Python)
2. Schema tests (Pydantic validation)
3. Loop tests with a mocked LLM (`side_effect`)
4. Golden evals from `tests/evals/golden_queries.json` (`@pytest.mark.eval`)

End state: `pytest -q` green, **no `OPENAI_API_KEY` needed**, ~53 tests. Your repo matches `project/solution/`.
---
<!-- _class: title -->

# End of Day 4 ✅

**Your `my-catalog/` project:**

- Python catalog + dataclasses + type hints (Day 1)
- FastAPI + Pydantic + `APIClient` + bulk-import (Days 1–2)
- pytest + mocks + parametrize + HTML reports + CI (Day 3)
- LLM-powered `CatalogAgent` with **its own test suite** (Day 4)

**One project. Four days. Tested. Agentic. Done.**
---
<!-- _class: title -->

# Where to next

- Swap OpenAI for Anthropic / Azure / a local model — the injection seam means **one file changes**
- Climb the M10 ladder for real: few-shot → RAG when the catalog outgrows the context window
- Add memory: persist `messages` per `session_id`
- Fine-tune `parse_nl_query` once volume justifies it — you already have the eval
- Take the patterns home: every one works on your real production code
