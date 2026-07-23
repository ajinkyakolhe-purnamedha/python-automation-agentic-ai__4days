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
# 1.2 · Free-text is for humans, structure is for code

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
# 1.3 · This is the agent's `observe` step

```text
§1        code output → LLM → answer                           (one shot)
agent     [ LLM picks a tool → run it → feed result back ] → answer   (a loop)
```

§1 is half of an agent: the LLM digesting a result. §2 adds the other half — the LLM choosing *which* of your functions to run. Same synthesis, now inside a loop.

<div class="code-along">▶ Code-along now → notebook: module-11 §1 — synthesize raw tickets free-text, then as a validated TicketDigest</div>
---
<!-- _class: title -->

# Section 2a
## The agent calls your code
LLM → code · plan → act → observe (build it by hand)
---
# 2a.1 · The big idea

> In GenAI, a **"tool"** is just a Python function the LLM is allowed to call.

No magic. No framework required. You hand the LLM:
- A list of function **signatures** (as JSON schemas)
- The user's question

The LLM returns: *"Call `search_products` with `{"term": "keyboard"}`."*
Your code: looks it up, calls it, sends the result back, lets the LLM decide what's next.
---
# 2a.2 · A tool is the M5 decorator, reimagined

```python
@registry.tool(
    name="search_products",
    description="Find products whose name contains the given substring.",
    parameters={"type": "object",
                "properties": {"term": {"type": "string"}},
                "required": ["term"]})
def search_products(term: str) -> list[dict]:
    return [p.model_dump() for p in self.api.list_products()
            if term.lower() in p.name.lower()]
```

The decorator stamps metadata on the function and registers it — **the Day-1 `@dataclass` / `@app.get` pattern returns**, now describing tools to an LLM.
---
# 2a.3 · Tool schema — what the LLM sees

```json
{ "type": "function",
  "function": {
    "name": "search_products",
    "description": "Find products whose name contains the given substring.",
    "parameters": {
      "type": "object",
      "properties": {"term": {"type": "string"}},
      "required": ["term"] } } }
```

The few words of `description=` are the **most important text in your codebase** for an agent — the LLM picks tools by reading them. Write them like API docs.
---
# 2a.4 · The agent loop

```text
┌────────────────────────────────────┐
│   user prompt                       │
│   ┌──────────────────────────┐      │
│   │  LLM(messages, tools)    │      │
│   └────────────┬─────────────┘      │
│        tool_calls?                  │
│       /         \                   │
│   yes /           \ no              │
│      ▼             ▼                │
│  run tools     return answer        │
│      │                              │
│  append obs ─── loop (max_steps) ┐  │
└──────────────────────────────────┘  │
```

Plan (LLM) → act (your code runs the tool) → observe (feed the result back) → repeat.
---
# 2a.5 · Chaining the tool result back (`tool_call_id`)

**The #1 lab-breakage point.** When the LLM asks for a tool, you append **two kinds** of message before the next call:

```python
messages.append(msg)                       # 1. the assistant msg carrying .tool_calls
for call in msg.tool_calls:                 # 2. one tool msg PER call
    messages.append({"role": "tool",
                     "tool_call_id": call.id,        # must match the call's id
                     "content": json.dumps(result)})
```

Each `tool` message **must** carry the matching `tool_call_id`. Miss it, or skip the assistant message, and the next API call 400s.
---
# 2a.6 · The agent loop, in code

```python
def ask(self, user_prompt: str) -> AgentResult:
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt}]
    for step in range(1, self.max_steps + 1):
        resp = self.llm.chat.completions.create(
            model=self.model, messages=messages,
            tools=self.registry.openai_schemas())
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return AgentResult(answer=msg.content, steps=step)
        messages.append(msg)
        for call in msg.tool_calls:
            result = self._invoke_tool(call.function.name, call.function.arguments)
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    raise AgentError("did not converge")
```

About 30 lines. That's the whole "agent".
---
# 2a.7 · Always cap `max_steps`

```python
def ask(self, prompt):
    for step in range(1, self.max_steps + 1):   # default 5
        ...
    raise AgentError(f"did not converge in {self.max_steps} steps")
```

Without a cap, a confused model loops forever, burning tokens. With a cap, you **fail loudly**. M12's tests will *assert* this raises — that's how you prove the safety net holds.

<div class="code-along">▶ Code-along now → notebook: module-11 §2a — register a tool, run ask() through one plan→act→observe step, watch the tool messages chain</div>
---
<!-- _class: title -->

# Section 2b
## The same agent, with a framework
you don't hand-roll the loop forever
---
# 2b.1 · The framework removes the typing, not the understanding

The loop you just wrote — `tool_call_id` chaining, `max_steps`, `_invoke_tool` — is exactly what a framework does for you. Rebuild the SAME agent in **Pydantic AI**:

```python
agent = Agent("openai:gpt-4o-mini", deps_type=list)

@agent.tool
def search_tickets(ctx: RunContext[list], term: str) -> list[dict]:
    """Find tickets whose subject contains term."""
    return [t.__dict__ for t in ctx.deps if term.lower() in t.subject.lower()]
```

Schema from type hints + docstring; the loop is gone. `RunContext.deps` is the Day-3 injection seam again. *(OpenAI Agents SDK is the other common choice — same idea, OpenAI-native.)*
---
# 2b.2 · Why we built it by hand first

| By hand (Lab 11) | Framework |
|---|---|
| `ToolRegistry` + `@registry.tool(parameters={...})` | `@agent.tool` — schema auto-derived |
| `ask()` loop, `tool_call_id` chaining | `agent.run_sync(...)` — hidden |
| `max_steps` → `AgentError` | built-in turn limit |
| ~80 lines | ~15 lines |

When a real agent breaks — a `tool_call_id` 400, a runaway loop — whoever hand-rolled it debugs in minutes. **Memory & context** are the same story: more Python around the LLM (a session DB, a RAG retriever), not more magic.

<div class="code-along">▶ Code-along now → notebook: module-11 §2b — the same agent in Pydantic AI</div>
---
<!-- _class: lab -->

# 🧪 Lab 11 — Synthesize, then build the `CatalogAgent`

**80 min** · open `labs/lab-11-catalog-agent/README.md`

**Part A (~20 min):** the LLM processes your `APIClient` output — raw products in → a plain-English answer, then a validated `CatalogSummary`.

**Part B (the core):** build the hand-rolled `CatalogAgent` — `@registry.tool` ×4, `ask()` loop with `tool_call_id` chaining, `max_steps` + `AgentError`.

**Stretch:** rebuild Part B's agent in Pydantic AI — watch the loop vanish.
