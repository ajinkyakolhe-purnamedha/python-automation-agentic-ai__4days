# Lab 3 — Local API Server

**Duration:** ~80 min · **Day:** 1 · **Module:** 3 (OOP, Dataclasses & FastAPI)

> **Concepts used:** `@dataclass`, classes & methods, FastAPI routes → `codealong/module-3.ipynb`.
> Applies Module 3's `BankAccount` concepts to `Product`. The big refactor: Lab 1/2's product-**dicts** and loose **functions** become a typed **`@dataclass`** and a **`ProductCatalog` class** whose methods are those functions. (You *use* decorators throughout this course but never write your own — a decorator just hands your function to a framework.)

## Goal
Refactor the catalog into real objects, then expose it over HTTP. `Product` becomes a `@dataclass`; the loose `make_product`/`insert`/`fetch`/`search` functions become **methods** on a `ProductCatalog` class. Then stand up a **FastAPI** server — the end-of-Day-1 artifact.

## You start with
- Your Lab 2 working folder (including `catalog/storage.py`). **This lab adds `models.py`** — the `ProductCatalog` class owns the data and the queries; `storage.py` stays a separate module and keeps handling JSON/CSV persistence (now serialising `Product` objects).

## You'll end with
- `catalog/models.py` — `@dataclass Product`, `class ProductCatalog` (`add`/`get`/`delete`/`search_by_name`/`filter_by_price`/`list_all`/`__len__`)
- `catalog/storage.py` — carried over from Lab 2; `save_json(catalog, path)` / `load_json(path)` (and the CSV pair) now read/write `Product` objects via `to_dict()` / `Product(**row)`
- `catalog/server.py` — a FastAPI `app`: `GET /health`, `GET /products`, `GET /products/{id}`, `POST /products`, `DELETE /products/{id}`
- A server running at `http://localhost:8000` with `/docs`

## Starter files
```bash
cp ../labs/lab-03-local-api-server/starter/*.py catalog/   # run from my-catalog/
```

| File | You write |
|---|---|
| `starter/models.py` | the `Product` fields + the `ProductCatalog` method bodies |
| `starter/server.py` | the five route bodies; map `CatalogError` → 404 / 409 / 400 |

## Steps

1. **`Product` → `@dataclass`.** List the typed fields; `in_stock: bool = True`; `tags: list[str] = field(default_factory=list)`. You now get `__init__`, `__repr__`, and `==` for free, and `p.price` replaces `p["price"]`.

2. **The loose functions → methods.** Your Lab 1/2 logic moves *inside* `ProductCatalog`, operating on `self._items` (the `{id: Product}` store):
   - `add` — `raise CatalogError` on negative price or duplicate id, then store + log.
   - `get` / `delete` — `raise CatalogError` if missing.
   - `search_by_name` / `filter_by_price` — comprehensions over `self._items.values()`.
   - persistence stays in `storage.py` (a separate module, not a class method): `save_json(catalog, path)` writes `[p.to_dict() for p in catalog.list_all()]`; `load_json(path)` rebuilds a catalog with `Product(**row)`.

3. **FastAPI server.** Each `@app.get/post/delete` registers a route. Return `asdict(product)` (or a list of them) and FastAPI makes JSON. Map errors: `get` missing → 404, `add` duplicate → 409, `Product(**payload)` `TypeError` (bad body) → 400.

4. **Run it.**
   ```bash
   uvicorn catalog.server:app --reload
   curl http://localhost:8000/health          # {"status":"ok","count":5}
   curl http://localhost:8000/products/2
   curl -X POST http://localhost:8000/products \
        -H 'Content-Type: application/json' \
        -d '{"id":99,"name":"Test","category":"Misc","price":42.0}'
   ```
   Then open **http://localhost:8000/docs** — generated from your routes for free.

## Expected output

```
$ curl http://localhost:8000/health
{"status":"ok","count":5}

$ curl -o /dev/null -w '%{http_code}\n' http://localhost:8000/products/999
404
$ curl -o /dev/null -w '%{http_code}\n' -X POST .../products -d '{"id":99,...}'   # twice
201
409
```

## Make it pass

```bash
pytest tests/test_lab03.py -v
```

`TestServer` uses FastAPI's `TestClient` (in-process — no uvicorn needed). Target: `TestProduct` + `TestProductCatalog` + `TestServer` green.

> Lab 1 and Lab 2's graders now **skip** — you refactored their dict-functions into this class, so those specs retire and `test_lab03.py` takes over. That's the migration, made visible.

## Common pitfalls
- `tags: list = []` on a dataclass field shares one list across instances — use `field(default_factory=list)`.
- Returning a raw `Product` from a route works in modern FastAPI, but `asdict(p)` is explicit and matches the spec.
- Not catching `CatalogError` in a route → a duplicate POST returns 500 instead of 409.
- Forgetting `--reload` and wondering why edits don't take effect.

## Stretch (optional)
- **Inheritance:** add `class DigitalProduct(Product)` with a `download_url` field and a method the base lacks; confirm `isinstance(dp, Product)`.
- Add `PATCH /products/{id}` that updates price.

---

**End of Day 1.** Your working folder is the input for Day 2 — it matches `project/checkpoints/day-2-start/`.
