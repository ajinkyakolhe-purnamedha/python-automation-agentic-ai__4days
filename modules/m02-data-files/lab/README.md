# Lab 2 — Persistent Catalog

**~80 min · Day 1 · Module 2 (Lists, Dicts & Files)** · concepts → `../codealong-m02-data-files.ipynb`

The catalog becomes a **dict store** (`{id: product}`) reached through **functions**, and it survives a restart. Module 3 wraps these into a class.

## Goal
A `{id: product}` store, **comprehension** queries, and **JSON + CSV** persistence — with type hints. No classes yet.

## You start with
Your Lab 1 working folder (`catalog/models.py`, `catalog/cli.py`).

## You'll end with
- `catalog/storage.py` — `make_store`, `insert`, `fetch`, `search_by_name`, `filter_by_price`, `save_json`, `load_json`, `save_csv`, `load_csv`
- A `catalog.json` / `catalog.csv` that round-trips across runs

## Starter files
Add one file — copy `starter/storage.py` into `catalog/` and fill the `# TODO`s:

```bash
cp ../../modules/m02-data-files/lab/starter/storage.py catalog/   # run from capstone-project/my-catalog/
```

## Steps

1. **The store.** `make_store(products)` → `{p["id"]: p for p in products}` (instant lookup). `insert(store, product)` sets `store[id]`; `fetch(store, id)` returns it or `raise LookupError`.
2. **Queries are comprehensions** over `store.values()` — one line each:
   ```python
   def search_by_name(store: dict[int, dict], term: str) -> list[dict]:
       return [p for p in store.values() if term.lower() in p["name"].lower()]
   ```
   `filter_by_price(store, max_price)` is the same shape (`p["price"] <= max_price`).
3. **JSON** = your dicts on disk. `save_json` writes `list(store.values())`; `load_json` reads it and rebuilds via `make_store(...)`. **Missing file → return an empty store `{}`**, don't crash.
4. **CSV** = the type-loss format. `save_csv` writes **scalar** fields only (`tags` is a list, dropped via `extrasaction="ignore"` — JSON is what keeps lists). `load_csv` reads every cell back as a **string**, so coerce: `int(id)`, `float(price)`, `in_stock == "True"`, `tags=[]`; reuse `make_product(...)`. *This string-coercion pain is exactly what Day-2 Pydantic removes.*

## Expected output
```bash
$ python -c "from catalog.storage import *; s=make_store([{'id':1,'name':'USB-C Cable','category':'Electronics','price':499.0,'in_stock':True,'tags':['cable']}]); save_json(s,'catalog.json'); print(load_json('catalog.json'))"
{1: {'id': 1, 'name': 'USB-C Cable', ..., 'tags': ['cable']}}
```

## Make it pass
```bash
uvx pytest tests/test_lab02.py -v     # still pure stdlib — no install needed
```
Target: `TestStoreAndQueries` + `TestPersistence` green. `test_csv_coerces_types_back` catches a `load_csv` that leaves `price`/`id` as strings; `test_csv_drops_the_tags_list` confirms CSV intentionally drops the list field.

## Common pitfalls
- CSV without `newline=""` → blank lines between rows on Windows.
- After CSV load, `price` is the string `"499.0"` until you `float(...)` it (`499.0 + 100` fails otherwise).
- `load_json` on a missing file returning something other than `{}`.

## Stretch (optional)
- `update(store, id, **changes)` and persist it.
- A `--format csv|json` flag on the CLI's `save` / `load`.
