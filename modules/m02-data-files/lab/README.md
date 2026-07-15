# Lab 2 — Persistent Catalog

**Duration:** ~80 min · **Day:** 1 · **Module:** 2 (Lists, Dicts & Files)

> **Concepts used:** the `{id: …}` store, comprehensions, JSON/CSV, type hints → `codealong/module-2.ipynb`.
> Applies Module 2's `BankAccount` concepts to `Product` — same patterns, different thing. The catalog is now a **dict store** (`{id: product}`) reached through **functions**. (Module 3 wraps these into a class.)

## Goal
Make the catalog survive a restart and grow real queries — with Module 2's tools: a `{id: product}` **store**, **comprehension** queries, **JSON & CSV** persistence, and **type hints**. No classes yet.

## You start with
- Your Lab 1 working folder (`catalog/models.py`, `catalog/cli.py`).

## You'll end with
- `catalog/storage.py` — `make_store`, `insert`, `fetch`, `search_by_name`, `filter_by_price`, `save_json`, `load_json`, `save_csv`, `load_csv`
- A `catalog.json` / `catalog.csv` that round-trips across runs

## Starter files
You're **adding one file**. Copy `starter/storage.py` into your `catalog/` package and fill the `# TODO`s:

```bash
cp ../labs/lab-02-persistent-catalog/starter/storage.py catalog/   # run from my-catalog/
```

## Steps

1. **The store.** `make_store(products)` turns a list into `{p["id"]: p for p in products}` — instant lookup by id. `insert(store, product)` sets `store[id] = product`; `fetch(store, id)` returns it or `raise LookupError`.

2. **Queries are comprehensions** over `store.values()` — one line each:

   ```python
   def search_by_name(store: dict[int, dict], term: str) -> list[dict]:
       return [p for p in store.values() if term.lower() in p["name"].lower()]
   ```

   `filter_by_price(store, max_price)` is the same shape (`p["price"] <= max_price`).

3. **JSON** = your dicts, on disk. `save_json` writes `list(store.values())`; `load_json` reads it back and rebuilds the store with `make_store(...)`. **Missing file → return an empty store `{}`** (don't crash).

4. **CSV** = the type-loss format. `save_csv` writes the **scalar** fields only — a list doesn't fit a flat cell, so `tags` is dropped (`extrasaction="ignore"`); **JSON is the format that keeps lists**. `load_csv` reads each row back as **all strings**, so coerce: `int(id)`, `float(price)`, `in_stock == "True"` (`tags` defaults to `[]`). Reuse `make_product(...)`. (This string-coercion pain is exactly what Day-2 Pydantic removes.)

## Expected output

```bash
$ python -c "from catalog.storage import *; s=make_store([{'id':1,'name':'USB-C Cable','category':'Electronics','price':499.0,'in_stock':True,'tags':['cable']}]); save_json(s,'catalog.json'); print(load_json('catalog.json'))"
{1: {'id': 1, 'name': 'USB-C Cable', 'category': 'Electronics', 'price': 499.0, 'in_stock': True, 'tags': ['cable']}}
```

## Make it pass

```bash
pytest tests/test_lab02.py -v
```

Skips until `catalog/storage.py` exists, then red → green. Target: `TestStoreAndQueries` + `TestPersistence` green. `test_csv_coerces_types_back` catches a `load_csv` that leaves `price`/`id` as strings; `test_csv_drops_the_tags_list` confirms the list-field is (intentionally) not carried by CSV.

## Common pitfalls
- Writing CSV without `newline=""` → blank lines between rows on Windows.
- After CSV load, `price` is the **string** `"499.0"` until you `float(...)` it — `499.0 + 100` fails otherwise.
- Returning the store from `load_json` on a missing file instead of `{}`.

## Stretch (optional)
- Add `update(store, id, **changes)` and persist it.
- Add a `--format csv|json` flag to the CLI's `save` / `load`.
