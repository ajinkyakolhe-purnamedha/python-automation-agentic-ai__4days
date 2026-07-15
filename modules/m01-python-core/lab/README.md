# Lab 1 — The Product Foundation

**~50 min · Day 1 · Module 1 (Python Core)** · concepts → `../codealong-m01-python-core.ipynb`

A product is a **dict**; the catalog is a **list** of them. You already know dicts, lists, functions, and exceptions — this lab is about the *Python idioms* (the `None`-default trap, `raise`, list copies). Module 3 turns these into a class.

## Goal
A `make_product` factory + `add` / `find` / `search` / `list` functions over a list, failing loudly on bad input. Every later lab extends this.

## You start with
Empty `catalog/` package + `pyproject.toml`. **Pure stdlib — nothing to install.** You only need `uv` on your machine.

## You'll end with
- `catalog/models.py` — `make_product`, `add_product`, `find_product`, `search_by_name`, `list_products`
- `catalog/cli.py` — **given**; the `list` command runs once your functions work
- `uvx pytest tests/test_lab01.py -v` green

## Starter files
Copy both into `catalog/` and fill the `# TODO`s in `models.py` — signatures + docstrings are the contract. `cli.py` is given (boilerplate, not the lesson).

```bash
cp ../../modules/m01-python-core/lab/starter/*.py catalog/   # run from capstone-project/my-catalog/
```

## Steps (all in `models.py`)

1. **`make_product`** — return the 6-field dict. Default `in_stock=True`; default `tags` via the `None` sentinel, **never `tags=[]`** (one list shared across every product — the Python trap with no JS analog):
   ```python
   def make_product(id, name, category, price, in_stock=True, tags=None):
       if tags is None:
           tags = []
       return {"id": id, "name": name, "category": category,
               "price": price, "in_stock": in_stock, "tags": tags}
   ```
2. **`add_product(catalog, product)`** — `raise ValueError` on `price < 0` or a duplicate id (loop to check); else append, `logger.info(...)`, return it.
3. **`find_product(catalog, id)`** — return the match, or `raise LookupError(f"no product id={id}")`.
4. **`search_by_name` / `list_products`** — a case-insensitive-substring filter; and a **copy** of the list (callers must not mutate yours).

## Reward — run the given CLI
```
$ python -m catalog.cli list
  1  USB-C Cable            Electronics  ₹  499.00  in stock
  ...
  5  Bluetooth Speaker      Electronics  ₹ 2499.00  in stock

5 products
```

## Make it pass
```bash
uvx pytest tests/test_lab01.py -v     # uvx fetches pytest once — no venv, no install
```
Skips until `models.py` exists, then red → green. Target: `TestProductDict` + `TestCatalogFunctions`. (`test_tags_are_not_shared_between_products` stays red if you wrote `tags=[]`.)

## Common pitfalls
- `tags=[]` default → one shared list. Use the `None` sentinel.
- `list_products` returning the catalog itself → callers mutate your data. Return a copy.
- Reading a traceback: the *last* line is the exception type + message (the *what*); lines above are *where*.

## Stretch (optional)
- `remove_product(catalog, id)` — `LookupError` if missing.
- `summary(catalog)` → `{"count": int, "total_value": float}`.
