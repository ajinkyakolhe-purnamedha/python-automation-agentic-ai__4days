# Lab 11 — Build the `CatalogAgent`

**~40 min · Day 4 · Module 11** — wrap your `ProductCatalog` methods as LLM-callable tools using Pydantic AI.

## Prereqs

```bash
uv add pydantic-ai
```

Set **one** API key (pick whichever you have):

```bash
# Gemini (free — recommended)
# Get your key at: https://aistudio.google.com/apikey
export GOOGLE_API_KEY=AIza…

# OR OpenAI (paid)
# Get your key at: https://platform.openai.com
export OPENAI_API_KEY=sk-…
```

## Goal

An LLM that **calls your `ProductCatalog` methods as tools**: it reads the user's question, calls the right tool, reads the result, and answers in plain language.

By the end, this works:

```python
from catalog.agent import catalog_agent
from catalog.models import ProductCatalog
from catalog.storage import seed_products

result = catalog_agent.run_sync(
    "What's our most expensive product?",
    deps=ProductCatalog(seed_products()),
    model="google:gemini-2.5-flash",   # or "openai:gpt-4o-mini"
)
print(result.output)
```

## You start with → you'll end with

| Start | End |
|---|---|
| `starter/catalog/agent.py` — agent + plumbing **given**, tool bodies are `# TODO` | Four working tools: `list_products`, `search_products`, `count_by_category`, `update_price` |
| Lab 10 done (`CatalogQuery` + `parse_nl_query`) | A fully functional catalog agent |

```bash
cp ../labs/lab-11-catalog-agent/starter/catalog/agent.py catalog/   # from my-catalog/
```

## Steps

1. **Read the plumbing** — `catalog_agent = Agent(...)` is given. `@catalog_agent.tool` registers each function. `RunContext[ProductCatalog]` gives you `ctx.deps` — the injected catalog.

2. **Fill the four `@catalog_agent.tool` functions.** Each one follows the same pattern:
   - Access the catalog via `ctx.deps` (that's your injected `ProductCatalog`)
   - Call the right `ProductCatalog` method (open `models.py` to see them)
   - Return **JSON-friendly** values — tools can't return Pydantic objects; convert them first

   The four tools:
   - `list_products` — no extra params, returns all products
   - `search_products(term)` — search by name substring
   - `count_by_category` — no extra params, returns `{category: count}`
   - `update_price(product_id, new_price)` — update a product's price

3. **Demo it** (no server needed — just run):
   ```python
   from catalog.agent import catalog_agent
   from catalog.models import ProductCatalog
   from catalog.storage import seed_products
   result = catalog_agent.run_sync(
       "What's our most expensive product?",
       deps=ProductCatalog(seed_products()),
       model="google:gemini-2.5-flash",   # or "openai:gpt-4o-mini"
   )
   print(result.output)
   ```

## Expected output

```
The most expensive product is the Mechanical Keyboard, at ₹5,499.
```

The model called `list_products` once, read the data, then answered.

## Pitfalls

- **Returning Pydantic objects from a tool** — tool return values must be JSON-serializable. Use `.model_dump()` on your Products.
- **Forgetting `ctx: RunContext[ProductCatalog]`** as the first parameter — without it, the tool can't access `ctx.deps`.
- **Missing the docstring** — the LLM picks tools by reading descriptions. No docstring = the LLM won't know what the tool does.
- **Re-creating the catalog every call** — pass it once via `deps=`.

## Stretch

- **Swap the model:** if you used Gemini, try `model="openai:gpt-4o-mini"` (set `OPENAI_API_KEY`), or vice versa. One line changes — the tools stay identical.
- **Add a `delete_product` tool** + a confirmation step: the LLM proposes, your code asks y/n, executes only on yes.
