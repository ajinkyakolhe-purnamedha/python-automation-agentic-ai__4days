---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 4 · Add AI to the Catalog, then Test the AI"
footer: "Acuity Training · Day 4 of 4"
---

<!-- _class: title -->

# Module 11
## Building AI Agents with Pydantic AI
**~40 min · then 40 min lab** — from "hello world" to a tool-calling agent
---
# What is an AI Agent?

An LLM that can **take actions** — not just answer questions.

| Chatbot | Agent |
|---|---|
| You ask → it answers from training data | You ask → it **calls your code** → reads the result → answers |
| One turn: question → answer | A **loop**: plan → act → observe → repeat |

The "agent" is just a **while loop** around an LLM call. The LLM decides what to do; your Python code does it.

M10 showed the LLM as a stateless string-to-string machine. Now you give it **tools** — functions it can call — and it becomes an agent.
---
# The Agent Loop — plan → act → observe

```text
User: "What's our most expensive product?"

  ┌─────────────────────────────────────────┐
  │  PLAN    LLM reads the question + tools │
  │          → decides: call list_products() │
  │                                         │
  │  ACT     Your code runs list_products() │
  │          → returns product data          │
  │                                         │
  │  OBSERVE LLM reads the result           │
  │          → "Mechanical Keyboard, ₹5,499" │
  └─────────────────────────────────────────┘
```

The LLM **names** a function + arguments. Your code runs it. The result goes back. Repeat until the LLM has enough data to answer.
---
# What is a "tool"?

> A **tool** is just a Python function the LLM is allowed to call.

```python
def search_products(term: str) -> list[dict]:
    """Find products whose name contains the term."""
    return [p for p in products if term.lower() in p["name"].lower()]
```

The LLM never runs your code. It reads three things:
- The **function name** → `search_products`
- The **docstring** → "Find products whose name contains the term"
- The **parameter types** → `term: str`

…and decides when to call it, like you'd read API docs. Your code executes it and sends the result back.
---
<!-- _class: title -->

# Section 1
## Hello World with Pydantic AI
`pip install pydantic-ai` · your first agent in 4 lines
---
# 1.1 · What is Pydantic AI?

A Python framework for building AI agents — by the team that built Pydantic.

**The pitch:** it does for AI agents what FastAPI did for web APIs.

| You write | The framework handles |
|---|---|
| Tool functions with type hints | JSON schema generation for the LLM |
| `@agent.tool` decorator | Tool registration + the agent loop |
| `agent.run_sync(prompt)` | Message passing, retries, convergence |

You focus on **your tools** — the LLM integration plumbing is handled.

```bash
uv add pydantic-ai               # installs all providers (OpenAI, Gemini, etc.)
```

### API key — pick one

| Provider | Free? | Get key | Env var |
|---|---|---|---|
| **Gemini** ✅ | yes (free tier) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `export GOOGLE_API_KEY=…` |
| **OpenAI** | paid | [platform.openai.com](https://platform.openai.com) | `export OPENAI_API_KEY=…` |

```bash
# Gemini (free — recommended for the workshop)
export GOOGLE_API_KEY=AIza…

# OR OpenAI (paid)
export OPENAI_API_KEY=sk-…
```
---
# 1.2 · Hello world — an agent in 4 lines

```python
from pydantic_ai import Agent

agent = Agent(
    'google:gemini-2.5-flash',                  # or 'openai:gpt-4o-mini'
    instructions='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
# → "The first known use was in a 1974 C programming textbook."
```

`Agent(model, instructions)` + `run_sync(prompt)`. That's the whole API.

The model is a **string** — swap `'google:gemini-2.5-flash'` to `'openai:gpt-4o-mini'` and nothing else changes.
---
# 1.3 · TestModel — no API key needed

```python
from pydantic_ai import Agent

agent = Agent('test', instructions='Be concise.')

result = agent.run_sync('Hello!')
print(result.output)
# → "success (no tool calls)"
```

`'test'` is a **fake LLM** built into Pydantic AI — same idea as Day 3's mock `Session`.

It runs every tool with default args and returns a canned response. Perfect for testing your agent's wiring without burning API credits.

<div class="code-along">▶ Code-along now → notebook: module-11 §1 — hello world agent + TestModel</div>
---
<!-- _class: title -->

# Section 2
## Your First Tool
`@agent.tool` · schema from type hints · `RunContext`
---
# 2.1 · `@agent.tool` — the third decorator moment

| Day | Decorator | Framework does |
|---|---|---|
| 1 | `@app.get("/products")` | serves it as an HTTP route |
| 3 | `@pytest.fixture` | injects it as test setup |
| 4 | `@agent.tool` | exposes it as a tool the LLM can call |

Same idea every time: **`@` hands your function to a framework**. The framework stamps metadata and does the plumbing.
---
# 2.2 · A simple tool — `@agent.tool_plain`

```python
from pydantic_ai import Agent

agent = Agent('test', instructions='Use tools to answer questions.')

@agent.tool_plain
def get_temperature(city: str) -> str:
    """Get the current temperature for a city."""
    return f"The temperature in {city} is 28°C"

result = agent.run_sync('What is the weather in Mumbai?')
```

`@agent.tool_plain` — for tools that don't need shared state.

- `city: str` → Pydantic AI auto-generates the JSON schema
- The docstring → becomes the tool description the LLM reads
- No hand-written JSON dict — **type hints + docstring = schema**
---
# 2.3 · Schema: by hand vs. auto-derived

The LLM needs a JSON schema to know how to call your tool:

| By hand (raw OpenAI API) | `@agent.tool` (Pydantic AI) |
|---|---|
| 12-line JSON dict | 1-line function signature |
| `"description"` as a string literal | the docstring |
| `"type": "string"` | `city: str` |
| typo-prone, hard to refactor | stays in sync with the code |

You never touch the JSON dict. The framework reads your Python and builds it.
---
# 2.4 · `RunContext` — tools that need shared data

When tools need access to shared state, use `RunContext`:

```python
from pydantic_ai import Agent, RunContext

agent = Agent('test', deps_type=list)

@agent.tool
def count_items(ctx: RunContext[list]) -> int:
    """Count how many items are in the list."""
    return len(ctx.deps)

result = agent.run_sync('How many items?', deps=['a', 'b', 'c'])
```

`ctx.deps` is your injected dependency — **the same DI pattern from Day 3:**

| Day 3 | Day 4 |
|---|---|
| `APIClient(session=mock_session)` | `agent.run_sync(prompt, deps=catalog)` |
| inject a fake `Session` for tests | inject a test `ProductCatalog` |

<div class="code-along">▶ Code-along now → notebook: module-11 §2 — tool_plain + RunContext</div>
---
<!-- _class: title -->

# Section 3
## Building the Catalog Agent
multiple tools · `RunContext[ProductCatalog]` · `run_sync`
---
# 3.1 · Define the agent + tools

```python
from pydantic_ai import Agent, RunContext
from catalog.models import ProductCatalog

catalog_agent = Agent(
    deps_type=ProductCatalog,
    instructions="You are a catalog assistant. Use tools to answer questions.",
)

@catalog_agent.tool
def list_products(ctx: RunContext[ProductCatalog]) -> list[dict]:
    """Return every product in the catalog."""
    return [p.model_dump() for p in ctx.deps.list_all()]

@catalog_agent.tool
def search_products(ctx: RunContext[ProductCatalog], term: str) -> list[dict]:
    """Find products whose name contains the given substring."""
    return [p.model_dump() for p in ctx.deps.search_by_name(term)]
```

Each tool: access the catalog via `ctx.deps`, call a method, return JSON-friendly data.
---
# 3.2 · Run it — and swap the brain

```python
result = catalog_agent.run_sync(
    "What's our most expensive product?",
    deps=ProductCatalog(seed_products()),
    model="google:gemini-2.5-flash",        # or "openai:gpt-4o-mini"
)
print(result.output)
# → "The most expensive product is the Mechanical Keyboard, at ₹5,499."
```

No loop code, no JSON schema dicts, no message chaining. **Your code is the tools.**

And the model is a **parameter** — swap the string, everything else stays:

```python
# Gemini (free)                              # OpenAI (paid)
model="google:gemini-2.5-flash"              model="openai:gpt-4o-mini"
```

This is M10's "vendors are swappable" made real.
---
# 3.3 · Common pitfalls

| Symptom | Root cause | Fix |
|---|---|---|
| Tool **never called** | docstring is vague | rewrite: say *what* it does and *when* to call it |
| Agent "answers" without calling tools | instructions don't say to use tools | add "Always use tools — never guess" |
| Tool returns error | returning Pydantic objects | use `.model_dump()` — tools return JSON-serializable values |
| Missing `ctx` parameter | forgot `RunContext` as first arg | add `ctx: RunContext[YourType]` |

The LLM reads tool descriptions like a developer reads docs. Bad docs → bad calls.

<div class="code-along">▶ Code-along now → notebook: module-11 §3 — catalog agent with TestModel + optional live run</div>
---
<!-- _class: lab -->

# 🧪 Lab 11 — Build the `CatalogAgent`

**~40 min** · open `modules/m11-tools-agent-loop/lab/README.md`

Build the `CatalogAgent` with Pydantic AI — `Agent(...)`, four `@agent.tool` functions, `agent.run_sync()`.

The `RunContext[ProductCatalog]` injection is the Day-3 seam — no server needed.

Four tools to fill: `list_products`, `search_products`, `count_by_category`, `update_price`.

**Stretch:** swap `model="google:gemini-2.5-flash"` to `model="openai:gpt-4o-mini"` — one line changes, tools stay identical.
