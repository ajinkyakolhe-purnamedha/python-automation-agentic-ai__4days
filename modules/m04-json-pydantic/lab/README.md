# Lab 4 — Pydantic Models for the Catalog

**Duration:** ~60 min · **Day:** 2 · **Module:** 4 (JSON & Pydantic)

> **Concepts used:** `BaseModel`, `Field` constraints, `model_validate`/`model_dump`, typed FastAPI → `../codealong-m04-json-pydantic.ipynb`.
> Applies Module 4's `BankAccount` concepts to `Product`. The migration: Lab 3's `@dataclass Product` becomes a Pydantic `BaseModel` — same fields, now **validated**.

## Goal
Turn `Product` into a Pydantic model so bad data is rejected **at the boundary**, then make the FastAPI server typed — a bad `POST` returns an automatic **422** with field-level errors, and `/docs` is generated from the model.

## You start with
- Your Lab 3 working folder (`@dataclass Product` + `ProductCatalog` class + `server.py`).

## You'll end with
- `catalog/models.py` — `Product(BaseModel)` with `Field` constraints; `ProductCatalog` (unchanged class, now holding Pydantic Products)
- `catalog/storage.py` — `save_json`/`load_json` updated to use `model_dump()` / `model_validate()`
- `catalog/server.py` — routes typed with `Product` + `response_model`; bad `POST` → 422; `GET /health` carried over from Lab 3 untouched

## Starter files
```bash
cp ../../modules/m04-json-pydantic/lab/starter/*.py catalog/   # run from capstone-project/my-catalog/
```

| File | You write |
|---|---|
| `starter/models.py` | the `Product` fields + `Field` constraints. **`ProductCatalog` is given** — it's your Lab 3 class, unchanged. |
| `starter/storage.py` | the two bodies: `save_json` (`model_dump`) / `load_json` (`model_validate`) |
| `starter/server.py` | the typed routes: `product: Product` bodies + `response_model` |

## Steps

1. **`@dataclass` → `BaseModel`.** Subclass `BaseModel` and list the same six fields Lab 3 had — but each one now carries its **rule**, not just its type. `Field(...)` is where a rule lives (module-4 §2.1; the code-along has the syntax):

   | Field | Type | Rule |
   |---|---|---|
   | `id` | `int` | at least 1 |
   | `name` | `str` | at least 1 character — no empty names |
   | `category` | `str` | at least 1 character |
   | `price` | `float` | at least 0 — **not** "greater than 0"; a free item is legal, a negative one isn't |
   | `in_stock` | `bool` | defaults `True` |
   | `tags` | `list[str]` | defaults to an empty list |

   That last row is the Lab 3 trap again: a bare `= []` is shared across every instance. `Field` takes the same escape hatch the dataclass did, for the same reason.

2. **The catalog doesn't change — so it's given.** `ProductCatalog` in the starter is your Lab 3 class, carried over untouched: it holds Pydantic Products now and needed no edits to do it. **That's today's lesson, so read it rather than retype it.** Two things worth noticing: `add` lost its manual negative-price check (the **model** rejects a bad price before `add` ever runs), while the duplicate-id rule stays — a *catalog* rule, not a *field* rule.

3. **`storage.py` — one word each.** Same module, same signatures as Lab 3; both functions keep their shape. `save_json` called `p.to_dict()` on each product — a Pydantic model doesn't have that, so find the method that dumps a model to a plain dict (§3.2). `load_json` rebuilt each row with `Product(**row)`, which trusted the file completely — swap it for the *validating* way in (§3.1). That second one is the real upgrade: a hand-edited `catalog.json` with `price: -5` now fails on load, instead of poisoning the catalog silently.

4. **Type the server.** Body parameter `product: Product` makes FastAPI validate the JSON — a bad body returns **422** automatically (delete the old manual 400). Add `response_model=Product` (and `list[Product]`) so output is typed and documented. Keep `CatalogError` → 404 (missing) / 409 (duplicate).

5. **Run it & break it.**
   ```bash
   uv run uvicorn catalog.server:app --reload
   curl -X POST localhost:8000/products \
        -H 'Content-Type: application/json' \
        -d '{"id":51,"name":"","category":"x","price":-1}'      # 422 with field errors
   ```
   Then open `/docs` — every field, type, and constraint is there.

## Expected output

```
$ curl -s -X POST localhost:8000/products \
       -H 'Content-Type: application/json' \
       -d '{"id":51,"name":"","category":"x","price":-1}'
{"detail":[                                                    # HTTP 422 — trimmed: each
  {"type":"string_too_short",   "loc":["body","name"],         # entry also carries "input"
   "msg":"String should have at least 1 character"},           # and "ctx" (e.g. {"ge":0.0})
  {"type":"greater_than_equal", "loc":["body","price"],
   "msg":"Input should be greater than or equal to 0"}
]}
```

**Two errors, one per broken field** — you never wrote that check. `loc` says *where*, `msg` says *what*, `type` says *why* (module-4 §2.2). Lab 6 drops this exact list straight into the import report.

> Keep the `-H 'Content-Type: application/json'`. Without it, curl sends form data and you still get a 422 — but for the boring reason ("Input should be a valid dictionary"), because FastAPI never parsed the body. Same status code, none of the lesson.

## Make it pass

```bash
uv run pytest tests/test_lab04.py -v
```

Skips until `Product` is a Pydantic model, then red → green. Target: `TestModel` + `TestCatalog` + `TestServer` green.

> Lab 1–3 graders now **skip** — `Product` is no longer a dict or a dataclass. `test_lab04.py` is the live spec.

## Common pitfalls
- Pydantic v2 uses `model_dump()` / `model_validate()` — not v1's `.dict()` / `.parse_obj()`.
- Leaving the manual `price < 0` check in `catalog.add` — redundant now (the model rejects it first), and it raises the wrong error type.
- `price: float = Field(gt=0)` forbids free (`0.0`) items — use `ge=0`.
- Returning `model_dump()` from a route that has `response_model=Product` — just return the `Product`; FastAPI serialises it.

## Stretch (optional)
- Add a `ProductUpdate` model (all fields optional, `ConfigDict(extra="forbid")`) and a `PATCH /products/{id}` that merges via `model_copy(update=patch.model_dump(exclude_unset=True))`.
