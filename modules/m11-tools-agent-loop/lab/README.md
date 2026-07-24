# Lab 11 — Synthesize, then build the `CatalogAgent`

**~80 min · Day 4 · Module 11** — both directions of the code↔LLM seam: first let the LLM **process** your catalog data (Part A), then let it **drive** your code as tools (Part B).

**Part A (~20 min):** raw products in → a plain-English answer, then a validated `CatalogSummary`. Standalone — no agent, no loop.
**Part B (the core):** wrap your `ProductCatalog` methods as LLM-callable **tools** using Pydantic AI. `RunContext[ProductCatalog]` is the injection seam; Lab 12 swaps in a test catalog.

## Part A — the LLM processes your catalog (code → LLM)

Before the agent *calls* your code, see the LLM *digest* its output. Your `ProductCatalog` returns raw product data; instead of writing aggregation/formatting code, hand it to the LLM.

```bash
cp ../labs/lab-11-catalog-agent/starter/summarize_catalog.py .   # from my-catalog/
```

1. Fill `summarize_free_text()` — embed `json.dumps(products)` in a user message, return `response.choices[0].message.content`. No code parses the products.
2. Fill `summarize_structured()` — same call with `response_format={"type":"json_object"}`, then `CatalogSummary.model_validate_json(raw)`. Validate the LLM's output, exactly like M10 §3.
3. Run `uv run python summarize_catalog.py` → a prose summary, then a typed `CatalogSummary`. No server needed — the script uses `ProductCatalog` directly.

**Why this matters:** this *is* the agent's `observe` step — the LLM turning a tool result into an answer. Part B wraps it in a loop where the LLM also picks *which* tool to run.

## Part B — build the `CatalogAgent` with Pydantic AI (LLM → code)

### Prereqs

```bash
uv add pydantic-ai
export OPENAI_API_KEY=sk-…       # your key
```

### Goal

An LLM that **calls your `ProductCatalog` methods as tools**: it proposes a call, your code runs it, feeds the result back, and the LLM calls again or answers. By the end, `catalog_agent.run_sync("what's our most expensive product?", deps=ProductCatalog(seed_products()), model="openai:gpt-4o-mini")` makes the model call `list_products`, reason over the data, and answer in plain language.

### You start with → you'll end with

| Start | End |
|---|---|
| Lab 10 done (`CatalogQuery` + `parse_nl_query`) | Part A: `summarize_catalog.py` runs; Part B: `catalog_agent` with 4 tools |
| `starter/catalog/agent.py` — agent + plumbing **given**, tool bodies are `# TODO` | Tools: `list_products`, `search_products`, `count_by_category`, `update_price` |

```bash
cp ../labs/lab-11-catalog-agent/starter/catalog/agent.py catalog/   # from my-catalog/
```

### Steps

1. **Read the plumbing** — `catalog_agent = Agent(...)` is given. `@catalog_agent.tool` registers each function. `RunContext[ProductCatalog]` gives you `ctx.deps` — the injected catalog.

2. **Fill the four `@catalog_agent.tool` functions.** Each calls `ctx.deps` (your `ProductCatalog`) and returns **JSON-friendly** values (`model_dump()` every `Product`):
   ```python
   @catalog_agent.tool
   def search_products(ctx: RunContext[ProductCatalog], term: str) -> list[dict]:
       """Find products whose name contains the given substring (case-insensitive)."""
       return [p.model_dump() for p in ctx.deps.search_by_name(term)]
   ```
   Same for `list_products` (no extra params), `count_by_category` (no extra params), `update_price(ctx, product_id, new_price)`.

3. **Demo it** (no server needed — just run):
   ```python
   from catalog.agent import catalog_agent
   from catalog.models import ProductCatalog
   from catalog.storage import seed_products
   result = catalog_agent.run_sync(
       "what's our most expensive product?",
       deps=ProductCatalog(seed_products()),
       model="openai:gpt-4o-mini",
   )
   print(result.output)
   ```

### Expected output

```
The most expensive product is the Mechanical Keyboard, at ₹5,499.
```

The model called `list_products` once, read the data, then answered.

### Pitfalls

- Returning a Pydantic `Product` from a tool — tool return values must be JSON-serializable. `model_dump()` your Products!
- Forgetting `ctx: RunContext[ProductCatalog]` as the first parameter — without it, the tool can't access `ctx.deps`.
- Missing the docstring on a tool function — the LLM picks tools by reading descriptions. No docstring = the LLM won't know what the tool does.
- Re-creating the catalog every call — pass it once via `deps=`.

### Stretch

- **Swap the model:** change `model="openai:gpt-4o-mini"` to `model="anthropic:claude-haiku-4-5"` in the `run_sync` call (install `uv add pydantic-ai[anthropic]`, set `ANTHROPIC_API_KEY`). One line changes — the tools stay identical.
- Add a `delete_product` tool + a **confirmation step**: the LLM proposes, your code asks y/n, executes only on yes.
