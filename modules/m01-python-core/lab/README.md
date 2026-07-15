# Lab 1 — The Product Foundation

**Duration:** ~80 min · **Day:** 1 · **Module:** 1 (Python Core)

> **Concepts used:** dicts, functions, defaults, exceptions → `codealong/module-1.ipynb`.
> This lab applies Module 1's `BankAccount` concepts to the course's `Product` domain — same patterns, different thing (the deliberate concept-vs-lab seam). A product is a **dict**; the catalog is a **list** of them. (Module 3 turns these into a class.)

## Goal
Build the in-memory core of the catalog with Module 1's tools — **dicts, functions, exceptions**: a `make_product` factory and an `add` / `find` / `search` / `list` set of functions over a list, failing gracefully on bad input and logging each add. Every later lab extends this.

## You start with
- An empty `catalog/` package (just `__init__.py`)
- `pyproject.toml` in place — `pip install -e ".[dev]"`

## You'll end with
- `catalog/models.py` — `make_product`, `add_product`, `find_product`, `search_by_name`, `list_products`
- `catalog/cli.py` — `list` and `add` subcommands (`search` / `save` / `load` arrive in Lab 2)
- `python -m catalog.cli list` printing 5 seeded products

## Starter files
`starter/` holds the two files you build. Copy them into your `catalog/` package and fill the `# TODO`s — the signatures and docstrings are the contract.

```bash
cp ../labs/lab-01-product-foundation/starter/*.py catalog/   # run from my-catalog/
```

| File | You write |
|---|---|
| `starter/models.py` | the 5 function bodies (a product dict + list operations) |
| `starter/cli.py` | the `cmd_list` / `cmd_add` bodies |

## Steps

1. **`make_product(...)`** — return a dict with `id, name, category, price, in_stock, tags`. Default `in_stock=True`; default `tags` to a **new** list via the `None` sentinel — never `tags=[]` (one list shared across every product: the Module-1 trap).

   ```python
   def make_product(id, name, category, price, in_stock=True, tags=None):
       if tags is None:
           tags = []
       return {"id": id, "name": name, "category": category,
               "price": price, "in_stock": in_stock, "tags": tags}
   ```

2. **`add_product(catalog, product)`** — the catalog is a list. `raise ValueError` if `price < 0`, or if a product with the same `id` is already present (loop to check). Otherwise append, `logger.info(...)`, return the product.

3. **`find_product(catalog, id)`** — loop the list; return the match; `raise LookupError(f"no product id={id}")` if none.

   **Read the traceback** when it fires — Python tracebacks read bottom-up: the last line is the exception type + message (the *what*); the lines above are *where*.

4. **`search_by_name` / `list_products`** — a `for` loop that keeps case-insensitive name matches; and a **copy** of the list (so callers can't mutate yours).

5. **`cli.py`** — `seed_catalog()` is given (5 products). Fill `cmd_list` (print each product as a row, then an `<n> products` footer) and `cmd_add`. Run `list`, then add a negative-price product to trigger your first error.

## Expected output

```
$ python -m catalog.cli list
INFO: added product id=1 name='USB-C Cable'
...
    1  USB-C Cable                  Electronics    ₹  499.00  in stock
    2  Mechanical Keyboard          Electronics    ₹ 5499.00  in stock
    3  Steel Water Bottle           Home           ₹  899.00  in stock
    4  Yoga Mat                     Fitness        ₹ 1299.00  OOS
    5  Bluetooth Speaker            Electronics    ₹ 2499.00  in stock

5 products
```

## Make it pass

```bash
pytest tests/test_lab01.py -v
```

It **skips** until `catalog/models.py` exists, then goes red → green. Target: `TestProductDict` + `TestCatalogFunctions` green. (`test_tags_are_not_shared_between_products` is the mutable-default trap — it stays red if you write `tags=[]`.)

## Common pitfalls
- `tags=[]` as a default → one list shared across all products. Use the `None` sentinel.
- Returning the catalog list itself from `list_products` — callers can then mutate your data. Return a copy.
- `logger.info(...)` prints nothing without `logging.basicConfig(...)` (the CLI sets it up).

## Stretch (optional)
- Add `remove_product(catalog, id)` that raises `LookupError` if the id is missing.
- Add `summary(catalog)` returning `{"count": int, "total_value": float}`.
