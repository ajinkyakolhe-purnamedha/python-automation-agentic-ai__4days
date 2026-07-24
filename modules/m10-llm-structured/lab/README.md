# Lab 10 — Classify a Product, then NL Query → Catalog Filter

**~80 min · Day 4 · Module 10** — first feel an open-source model (Part A), then make a closed LLM speak your schema (Part B).

**Part A (open-source, ~20 min):** a standalone local classifier — no key, no server.
**Part B (your first LLM app, ~60 min):** one LLM call → validated `CatalogQuery` → pure-Python filter over the `ProductCatalog`. Concepts → `codealong/module-10.ipynb`. No agent loop, no tools — that's Lab 11.

## Part A — classify a Product (open-source, no key)

Feel a local model before touching an API. A `transformers` zero-shot pipeline guesses a product's category from its name + description.

```bash
pip install transformers torch        # one-off, ~700 MB, CPU is fine
cp ../labs/lab-10-nl-query-filter/starter/classify_products.py .   # from my-catalog/
```

1. Fill `build_classifier()` — return a `pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")`.
2. Fill `guess_category()` — call the pipeline with `candidate_labels=CATEGORIES`, return the top label (`result["labels"][0]`).
3. Run `python classify_products.py` → expect a per-row `OK/MISS` table and `N/4 correct`.

**Why this matters:** no prompt, no JSON, no validation — the *task is the model*. Part B is the opposite: a general model you must constrain with a schema. Same goal (a label / a query), two philosophies.

> First run downloads the model (a minute or two). It's cached after that. If your laptop can't spare the space, read the solution and move to Part B — Part A is not a Part B prerequisite.

## Part B — NL query → CatalogQuery

## Prereqs — OpenAI API

```bash
pip install openai
export OPENAI_API_KEY=sk-…       # your key
```
The code uses the OpenAI SDK (`chat.completions.create` + JSON mode).

## Goal

Turn *"electronics under 5000 in stock"* into a **Pydantic-validated `CatalogQuery`** with one LLM call, then run it as a pure-Python filter over the `ProductCatalog`. Validate everything the model returns — the schema is the contract.

## You start with → you'll end with

| Start | End |
|---|---|
| `project/checkpoints/day-4-start/` (or your Lab 9) | Part A: `classify_products.py` runs; Part B: `catalog/agent.py` with `CatalogQuery`, `parse_nl_query`, `apply_query` |
| `starter/classify_products.py` (Part A) + `starter/catalog/agent.py` — schema + `NL_QUERY_SYSTEM` given; **two bodies TODO** (Part B) | a classifier table + a REPL where a question returns the right rows |

```bash
cp ../labs/lab-10-nl-query-filter/starter/catalog/agent.py catalog/   # from my-catalog/
```

## Steps

1. **Sharpen the schema.** The four `CatalogQuery` fields are given — tighten each `Field(description=…)` (the LLM reads it). Say what valid values and `null` mean. Don't rename or retype fields.
2. **`parse_nl_query` — force JSON, then validate.** One call with `response_format={"type":"json_object"}`, then `CatalogQuery.model_validate_json(raw)`. Never trust raw JSON.
3. **`apply_query` — pure Python, no LLM.** Start from `catalog.list_all()`, narrow by each field that is *set* (skip nulls), `return [p.model_dump() for p in items]`. Guard `max_price is not None` — `0` is a valid bound.
4. **Drive it from a REPL** (no server needed — just import `ProductCatalog`).
5. **Prove the schema protects you.** Ask nonsense (*"products that taste like pizza"*) → expect an empty/null `CatalogQuery` or a clean `ValidationError`. Silently lying is the only wrong answer.

## Expected output

```python
>>> q = parse_nl_query("show me electronics under 5000 that are in stock")
>>> print(q)
CatalogQuery(category='Electronics', max_price=5000.0, in_stock_only=True, name_contains=None)
>>> from catalog.models import ProductCatalog
>>> from catalog.storage import seed_products
>>> catalog = ProductCatalog(seed_products())
>>> for row in apply_query(q, catalog): print(row["id"], row["name"], row["price"])
1   USB-C Cable          499.0
3   Bluetooth Speaker   2499.0
```

## Pitfalls

- Skipping `response_format={"type":"json_object"}` → the model returns prose → `model_validate_json` explodes.
- Vague `description=` → vague queries. State the valid values **and** the null case.
- `if query.max_price:` drops a valid `max_price=0` — use `is not None`.
- Trusting the model's JSON without `model_validate_json`. **Always** parse through Pydantic — that's the contract.

## Stretch — fine-tuning tie-in

Hand-write ~10–15 `(NL query → CatalogQuery JSON)` pairs as chat-format JSONL, hold out 3–4, and score `parse_nl_query` against them (`correct/total`) — a golden-eval in miniature (M12). That JSONL is the exact shape OpenAI fine-tuning ingests, so it doubles as your base-vs-tuned training file.
