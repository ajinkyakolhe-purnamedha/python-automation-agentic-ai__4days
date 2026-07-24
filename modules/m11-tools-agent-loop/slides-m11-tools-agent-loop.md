---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 4 · Add AI to the Catalog, then Test the AI"
footer: "Acuity Training · Day 4 of 4"
---

<!-- _class: title -->

# Module 11
## Building LLM Applications
**~40 min · then 80 min lab** — the two directions of the code↔LLM seam: the LLM *processes* your code's output, then *drives* it
---
# Module 11 — two directions of one seam

1. **Code → LLM** — your Python produces raw data; the LLM **synthesizes** the answer (delete the parsing code)
2. **LLM → code** — *tool calling*: the LLM decides which of your functions to run

Direction 1 is the agent loop's **`observe` step**, taught on its own first. Then we close the loop.
---
<!-- _class: title -->

# Section 1
## The LLM processes your code's output
code → LLM · synthesis instead of parsing
---
# 1.1 · Stop writing output-processing code

Your Python pulls raw data from several places — a few API calls, some rows, a couple of files. The old way: write merge + parse + format + branch code to turn it into an answer.

**The new way:** hand the raw output to the LLM and ask for the answer.

```python
raw = [t.__dict__ for t in tickets]          # output returned by your code
answer = llm.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"What should on-call look at first?\n{raw}"}]
).choices[0].message.content
```

The LLM **is** the processing layer — no parsing code.
---
# 1.2 · The code you stop writing

**Without the LLM** — you write the merge/parse/format yourself:

```python
products = catalog.list_all()
by_cat = {}
for p in products:
    by_cat.setdefault(p.category, []).append(p)
most_exp = max(products, key=lambda p: p.price)
answer = f"Most expensive: {most_exp.name} (₹{most_exp.price}).\n"
answer += "\n".join(f"{cat}: {len(ps)} items" for cat, ps in by_cat.items())
```

**With the LLM** — hand it the data and ask:

```python
products = [p.model_dump() for p in catalog.list_all()]
answer = llm.chat.completions.create(model="gpt-4o-mini", messages=[
    {"role": "user",
     "content": f"Most expensive product? Summarize by category.\n{products}"}
]).choices[0].message.content
```

7 lines of logic → 1 question. The gap widens with every new question you need to answer.
---
# 1.3 · Free-text is for humans, structure is for code

A prose answer is great for a person. When the *next line of code* needs the result, ask the LLM to fill a shape — and validate it, exactly like M10 §3.

```python
class TicketDigest(BaseModel):
    open_count: int
    top_priority: str
    headline: str

digest = TicketDigest.model_validate_json(raw_json)   # untrusted output → typed
```

Same boundary discipline as Day 2 — now on the LLM's synthesis of *your* data.
---
# 1.4 · Two sources, one answer

The real power: synthesis across *multiple* data sources in one call.

```python
products = catalog.list_all()
groups   = catalog.group_by_category()
counts   = {cat: len(ps) for cat, ps in groups.items()}

answer = llm.chat.completions.create(model="gpt-4o-mini", messages=[
    {"role": "system", "content": "You are a catalog analyst."},
    {"role": "user",   "content": f"Compare inventory:\n{counts}\n\nProducts:\n{products}"}
]).choices[0].message.content
# → "Electronics leads with 3 products. Fitness has 1, currently out of stock."
```

No merge logic, no string templates. The LLM handles the reasoning — your code supplies the data. This is what the agent's **observe** step does, every iteration.
---
# 1.5 · This is the agent's `observe` step

```text
§1        code output → LLM → answer                           (one shot)
agent     [ LLM picks a tool → run it → feed result back ] → answer   (a loop)
```

§1 is half of an agent: the LLM digesting a result. §2 adds the other half — the LLM choosing *which* of your functions to run. Same synthesis, now inside a loop.

<div class="code-along">▶ Code-along now → notebook: module-11 §1 — synthesize raw tickets free-text, then as a validated TicketDigest</div>
---
<!-- _class: title -->

# Section 2
## Tools and the agent loop
LLM → code · plan → act → observe
---
# 2.1 · The big idea

> In GenAI, a **"tool"** is just a Python function the LLM is allowed to call.

No magic. You hand the LLM:
- A list of function **signatures** (as JSON schemas)
- The user's question

The LLM returns: *"Call `search_products` with `{"term": "keyboard"}`."*
Your code: looks it up, calls it, sends the result back, lets the LLM decide what's next.
---
# 2.2 · What the LLM actually sees

When you pass `tools=` to the API, each tool arrives as a **JSON schema**:

```json
{
  "type": "function",
  "function": {
    "name": "search_products",
    "description": "Find products whose name contains the term.",
    "parameters": {
      "type": "object",
      "properties": {
        "term": { "type": "string", "description": "Search substring" }
      },
      "required": ["term"]
    }
  }
}
```

You write this dict **by hand** in the raw approach. Get the schema wrong → the LLM calls your tool wrong. §3 will eliminate it.
---
# 2.3 · Under the hood — the raw loop

```python
def ask(prompt, tools, llm):
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}]
    for step in range(1, max_steps + 1):
        resp = llm.chat.completions.create(
            model="gpt-4o-mini", messages=messages,
            tools=[t.openai_schema() for t in tools])
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content                    # final answer
        messages.append(msg)                      # assistant msg with tool_calls
        for call in msg.tool_calls:
            result = run_tool(call)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    raise RuntimeError("did not converge")
```

About 15 lines. That's the entire agent loop.
---
# 2.4 · 🔮 What happens if you forget `tool_call_id`?

The LLM asked you to call `search_products`. You ran it, got results, appended a `tool` message… but forgot to set `tool_call_id`.

What do you think happens on the next API call?

---
# 2.5 · The `tool_call_id` chain

**The #1 lab-breakage point** when building this by hand. When the LLM asks for a tool, you must append **two things**:

1. The assistant message carrying `.tool_calls`
2. One `tool` message per call, **with `tool_call_id` matching the call's id**

```python
messages.append(msg)                           # 1. assistant
messages.append({"role": "tool",
                 "tool_call_id": call.id,      # must match
                 "content": json.dumps(result)})  # 2. per call
```

Miss the id → the next API call 400s. This is why frameworks exist.
---
# 2.6 · The loop, visually

- **User prompt** → enters the loop
- **LLM(messages, tools)** → decides next action
- **tool_calls?** → yes: run tools, append observation, loop (up to `max_steps`) / no: return final answer

**Plan** (LLM picks a tool) → **Act** (your code runs it) → **Observe** (feed the result back) → repeat until done.

<div class="code-along">▶ Code-along now → notebook: module-11 §2 cells 1–3 — build the raw loop, watch tool_call_id chaining</div>
---
# 2.7 · When the loop goes wrong

Three failure modes you'll hit — and one fix each:

| Symptom | Root cause | Fix |
|---|---|---|
| Tool **never called** | description is vague — the LLM can't tell when to use it | rewrite the docstring: say *what* it does and *when* to call it |
| **Infinite loop** | system prompt doesn't say when to stop | add a `max_steps` cap + tell the model "answer when you have enough data" |
| **Wrong tool** called | two tools have overlapping parameter names or descriptions | rename to be distinct: `search_by_name` vs `filter_by_category` |

The LLM reads tool descriptions like a developer reads docs — if your docs are ambiguous, so are the calls. §3's framework doesn't fix bad descriptions; it fixes the *plumbing* around them.
---
<!-- _class: title -->

# Section 3
## Pydantic AI — the framework does the loop
`@agent.tool` · `RunContext` · `run_sync`
---
# 3.1 · `@agent.tool` is the third decorator moment

| Day | Decorator | Framework does |
|---|---|---|
| 1 | `@app.get("/products")` | serves it as an HTTP route |
| 3 | `@pytest.fixture` | injects it as test setup |
| 4 | `@agent.tool` | exposes it as a tool the LLM can call |

Same pattern every time: **hand your function to a framework** with `@`. The framework stamps metadata and does the plumbing.
---
# 3.2 · Define the agent + tools

```python
from pydantic_ai import Agent, RunContext

catalog_agent = Agent(
    deps_type=ProductCatalog,
    instructions=SYSTEM_PROMPT,
)

@catalog_agent.tool
def search_products(ctx: RunContext[ProductCatalog], term: str) -> list[dict]:
    """Find products whose name contains the given substring."""
    return [p.model_dump() for p in ctx.deps.search_by_name(term)]
```

Schema auto-derived from type hints (`term: str`) + docstring. No hand-written JSON dict.
---
# 3.3 · Schema: hand-written vs auto-derived

The same `search_products` tool — two ways to declare it:

| By hand (§2) | `@agent.tool` (§3) |
|---|---|
| 12-line JSON dict | 3-line function signature |
| `"description"` as a string literal | the docstring |
| `"type": "string"` | `term: str` |
| easy to typo, hard to refactor | stays in sync with the code |

```python
@catalog_agent.tool
def search_products(ctx: RunContext[ProductCatalog], term: str) -> list[dict]:
    """Find products whose name contains the given substring."""
```

Type hints + docstring → Pydantic AI derives the JSON schema. You never touch the dict.
---
# 3.4 · `RunContext` — the injection seam returns

```python
@catalog_agent.tool
def list_products(ctx: RunContext[ProductCatalog]) -> list[dict]:
    """Return every product in the catalog."""
    return [p.model_dump() for p in ctx.deps.list_all()]
```

`ctx.deps` is your injected `ProductCatalog` — the **same** dependency-injection pattern from Day 3.

| Day 3 | Day 4 |
|---|---|
| `APIClient(session=mock_session)` | `agent.run_sync(prompt, deps=catalog)` |
| inject a fake `requests.Session` | inject a test `ProductCatalog` |
| test the client without the network | test the agent without the LLM |
---
# 3.5 · Run the agent — and swap the brain

```python
result = catalog_agent.run_sync(
    "What's our most expensive product?",
    deps=ProductCatalog(seed_products()),
    model="openai:gpt-4o-mini",            # ← change this string, everything else stays
)
print(result.output)
# → "The most expensive product is the Mechanical Keyboard, at ₹5,499."
```

No loop, no `tool_call_id` chaining, no `max_steps`. **Your code is the tools.** And the model is a parameter, not an architecture decision — swap to `"anthropic:claude-haiku-4-5"` or `"ollama:llama3.2"` and nothing else changes. This is M10's "vendors are swappable" made real.
---
# 3.6 · When Pydantic AI goes wrong

The framework hides the loop — so when it breaks, the errors come from *inside* the framework. Three you'll hit:

| Error | Root cause | What to do |
|---|---|---|
| `ModelRetry` on every call | tool raises an unhandled exception | add a try/except in the tool body, return an error *string* |
| `UnexpectedModelBehavior` | model returns malformed tool call JSON | check the model string — smaller models hallucinate schemas more |
| Agent "answers" without calling tools | system prompt doesn't tell it to use tools | add "Always use tools to look up data — never guess" to `instructions` |

The raw loop from §2 makes these obvious — the framework just wraps them in its own exception hierarchy. **Understanding §2 is how you debug §3.**
---
# 3.7 · By hand vs. framework — why we showed both

| By hand (§2) | Pydantic AI (§3) |
|---|---|
| Hand-written JSON schema dicts | Schema auto-derived from type hints |
| Manual `ask()` loop + `tool_call_id` chaining | `agent.run_sync(...)` — hidden |
| `max_steps` → `raise RuntimeError` | built-in turn limit |
| ~80 lines | ~30 lines |

When a real agent breaks — a `tool_call_id` 400, a runaway loop — whoever hand-rolled it debugs in minutes. The framework **saves typing**, not understanding.

<div class="code-along">▶ Code-along now → notebook: module-11 §3 — the same agent in Pydantic AI, then swap the model string</div>
---
<!-- _class: lab -->

# 🧪 Lab 11 — Synthesize, then build the `CatalogAgent`

**80 min** · open `modules/m11-tools-agent-loop/lab/README.md`

**Part A (~20 min):** the LLM processes your `ProductCatalog` output — raw products in → a plain-English answer, then a validated `CatalogSummary`.

**Part B (the core):** build the `CatalogAgent` with Pydantic AI — `Agent(...)`, four `@agent.tool` functions, `agent.run_sync()`. The `RunContext[ProductCatalog]` injection is the Day-3 seam — no server needed.

**Stretch:** swap the model parameter from `model="openai:gpt-4o-mini"` to `model="anthropic:claude-haiku-4-5"` in `run_sync` — one line, same tools.
