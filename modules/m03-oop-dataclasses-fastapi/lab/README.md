# Lab 3 — Local API Server

**~80 min · Day 1 · Module 3 (OOP, Dataclasses & FastAPI)** · concepts → `../codealong-m03-oop-dataclasses-fastapi.ipynb`

The big refactor: Lab 1/2's product-**dicts** and loose **functions** become a typed **`@dataclass`** and a **`ProductCatalog` class**, then you expose it over HTTP. `@dataclass` and `@app.get` are decorators you **use** — the `@` hands your function to a framework; you never write your own.

## Goal
`Product` → `@dataclass`; the loose `make_product`/`insert`/`fetch`/`search` functions → **methods** on `ProductCatalog`; then a **FastAPI** server — the end-of-Day-1 artifact.

## You start with
Your Lab 2 working folder (incl. `catalog/storage.py`). This lab adds `models.py` (the class) and `server.py`; `storage.py` stays a separate module, now serialising `Product` objects.

## You'll end with
- `catalog/models.py` — `@dataclass Product`, `class ProductCatalog` (`add`/`get`/`delete`/`search_by_name`/`filter_by_price`/`list_all`/`__len__`)
- `catalog/storage.py` — carried over; JSON/CSV now round-trip `Product` via `to_dict()` / `Product(**row)`
- `catalog/server.py` — FastAPI `app`: `GET /health`, `GET/POST /products`, `GET/DELETE /products/{id}`
- A server at `http://localhost:8000` with `/docs`

## Starter files
```bash
cp ../../modules/m03-oop-dataclasses-fastapi/lab/starter/*.py catalog/   # run from capstone-project/my-catalog/
```
| File | You write |
|---|---|
| `starter/models.py` | the `Product` fields + `ProductCatalog` method bodies |
| `starter/server.py` | the five route bodies; map `CatalogError` → 404 / 409 / 400 |

## Steps

1. **`Product` → `@dataclass`.** Typed fields; `in_stock: bool = True`; `tags: list[str] = field(default_factory=list)`. You get `__init__`, `__repr__`, `==` for free, and `p.price` replaces `p["price"]`.
2. **Loose functions → methods** on `ProductCatalog`, over `self._items` (`{id: Product}`): `add` (`raise CatalogError` on negative price / duplicate id), `get`/`delete` (`raise CatalogError` if missing), `search_by_name`/`filter_by_price` (comprehensions). Persistence stays in `storage.py`: `save_json` writes `[p.to_dict() for p in catalog.list_all()]`; `load_json` rebuilds via `Product(**row)`.
3. **FastAPI server.** Each `@app.get/post/delete` registers a route; return `asdict(product)` and FastAPI makes JSON. Map errors: missing → 404, duplicate → 409, bad body (`TypeError`) → 400.
4. **Run it.** Lab 3 adds FastAPI — the first real dependency, so sync once, then use `uv run`:
   ```bash
   uv sync                                        # creates .venv + installs deps (once)
   uv run uvicorn catalog.server:app --reload
   curl http://localhost:8000/health          # {"status":"ok","count":5}
   curl -X POST http://localhost:8000/products \
        -H 'Content-Type: application/json' -d '{"id":99,"name":"Test","category":"Misc","price":42.0}'
   ```
   Then open **http://localhost:8000/docs** — generated from your routes for free.

## Expected output
```
$ curl -o /dev/null -w '%{http_code}\n' http://localhost:8000/products/999   # 404
$ curl -X POST .../products -d '{"id":99,...}'   # 201 first time, 409 on repeat
```

## Make it pass
```bash
uv run pytest tests/test_lab03.py -v
```
`TestServer` uses FastAPI's `TestClient` (in-process — no uvicorn needed). Target: `TestProduct` + `TestProductCatalog` + `TestServer` green.

> Lab 1 & 2 graders now **skip** — you refactored their dict-functions into this class, so those specs retire and `test_lab03.py` takes over. The migration, made visible.

## Common pitfalls
- `tags: list = []` on a dataclass field shares one list across instances — use `field(default_factory=list)`.
- Not catching `CatalogError` in a route → a duplicate POST returns 500 instead of 409.
- Forgetting `--reload` and wondering why edits don't take effect.

## Stretch (optional)
- **Inheritance:** `class DigitalProduct(Product)` with a `download_url` field + a method the base lacks; confirm `isinstance(dp, Product)`.
- `PATCH /products/{id}` that updates price.

---

**End of Day 1.** Your working folder is the input for Day 2 — it matches `capstone-project/checkpoints/day-2-start/`.
