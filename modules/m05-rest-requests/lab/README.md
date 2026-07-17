# Lab 5 — Build the `APIClient`

**Duration:** ~60 min · **Day:** 2 · **Module:** 5 (REST APIs with `requests`)

> **Concepts used:** `requests.Session`, the `_request` funnel, the retry loop, typed returns → `../codealong-m05-rest-requests.ipynb`.
> Applies the module's `AccountClient` concepts to `Product` — same patterns, different domain.

## Goal
Build a typed `APIClient`: one `_request` funnel that wraps `requests`, a retry loop inside it for resilience, and methods that return Pydantic `Product` objects — **not raw dicts**. This client becomes the **toolbelt the agent uses on Day 4**.

## You start with
- Lab 4 end-state — Pydantic-typed `Product` + FastAPI server.
- `starter/client.py` — `APIError`, `__init__`, `_extract_detail`, and `health`/`get_product`/`delete_product` **already written** as worked examples; you fill three `# TODO` bodies.

## You'll end with
- `catalog/client.py` — `APIClient` + `APIError`, typed `list_products() -> list[Product]` and `create_product(...) -> Product`, with one retry loop in the funnel covering every call

## Starter files
```bash
cp ../../modules/m05-rest-requests/lab/starter/*.py catalog/   # run from capstone-project/my-catalog/
```

| File | You write |
|---|---|
| `starter/client.py` | bodies of `_request`, `list_products`, `create_product`. The `FakeSession`/`FakeResponse` helpers at the bottom are **given** — they let you run with no server. |

## Steps

1. **`_request` — the funnel, with the retry loop.** Every method below funnels through here, so what you write once, they all inherit. Four jobs:

   - **Timeout** — default `timeout` to `self.timeout`, but don't stomp one the caller passed. (`dict` has a method for precisely this.)
   - **URL** — join `self.base_url` and `path`.
   - **Send, up to `RETRY_TIMES` times** — through **`self._session`**, never `requests.get`: the session carries the headers, and the tests hand you a fake one. Stop looping the moment you get a response. On a `TRANSIENT_ERRORS` fault, give up only on the last attempt; otherwise `time.sleep(RETRY_DELAY)` and go again.
   - **Check** — a non-2xx becomes `APIError(status, detail)`; the given `_extract_detail` gets you the detail.

   The design question worth pausing on: **where does that last job go, relative to the loop?** A 4xx must never be retried (§1.2), and it's the *placement* that guarantees it — not a comment.

   The given `get_product` is the template every typed method repeats:
   ```python
   def get_product(self, product_id: int) -> Product:
       data = self._request("GET", f"/products/{product_id}").json()   # the funnel
       return Product.model_validate(data)                             # dict → model
   ```

2. **`list_products` — looped.** The same two moves as `get_product`, except `/products` answers with a **list** of dicts — so every one needs validating, not just the one. (A comprehension.)

3. **`create_product` — POSTing.** `requests` wants the body as `json=<a dict>`, and what you hold is a `Product` — convert it (module-4 §3.2). The server echoes the created product back, so finish exactly like `get_product`: validate that response into a `Product`.

4. **Drive it — no server needed.** Inject the given `FakeSession`. Start a REPL with `uv run python` (so the venv's deps are on the path), then:
   ```python
   from catalog.client import APIClient, FakeSession, FakeResponse, SAMPLE_PRODUCTS
   c = APIClient(session=FakeSession([FakeResponse(200, SAMPLE_PRODUCTS)]))
   print(c.list_products())   # → list[Product], straight from the fake
   ```

## Expected output

No server needed — the given `FakeSession` answers every call. Three things prove the client works:

```python
>>> c = APIClient(session=FakeSession([FakeResponse(200, SAMPLE_PRODUCTS)]))
>>> c.list_products()
[Product(id=1, name='USB-C Cable', category='Electronics', price=499.0, in_stock=True, tags=['cable', 'usb-c']),
 Product(id=2, name='Mechanical Keyboard', category='Electronics', price=5499.0, in_stock=True, tags=['mech'])]
```
**`Product` objects, not dicts** — that's the typed return earning its keep.

```python
>>> c = APIClient(session=FakeSession([FakeResponse(409, {"detail": "Product id 1 already exists"})]))
>>> c.get_product(1)
APIError: 409: Product id 1 already exists       # .status_code == 409
```
**A non-2xx became a clean `APIError`** — no `requests` exception leaked out of the client.

```python
>>> s = FakeSession([requests.ConnectionError("blip"), requests.ConnectionError("blip"),
...                  FakeResponse(200, SAMPLE_PRODUCTS)])
>>> APIClient(session=s).list_products(); s.calls
2 products after 3 attempts
```
**The retry loop rode out two dropped connections** — and `s.calls == 3` proves it actually re-sent.

## Make it pass

```bash
uv run pytest tests/test_lab05.py -v
```

Skips until `client.py` exists, then red → green. Target: `TestAPIClient` green (typed returns, `APIError` on non-2xx, the retry loop recovering from a transient failure — an injected fake session stands in for the server).

## Common pitfalls
- Calling `requests.get(...)` instead of `self._session.request(...)` skips the injected session + the retry. **Always** go through `_request`.
- Returning the raw dict from `.json()` instead of `model_validate`-ing it — the typed return is the whole point.
- A bare `except Exception` in the loop retries a 4xx too — catch `TRANSIENT_ERRORS` only.
- Forgetting the `break` after a successful `request(...)` — you'd re-send every call `RETRY_TIMES` times.
- Forgetting `timeout` — a hung server hangs your script forever.

## Stretch (optional)
- Add `auth_token: Optional[str] = None` to `__init__` and inject `Authorization: Bearer …` on every request.
- Log each call in `_request` (`logger.info("%s %s", method, path)`) and watch a `list_products()` trace itself.
- Uncomment `update_product` at the bottom of `client.py`. **Needs Lab 4's stretch first** — it depends on the `ProductUpdate` model and the `PATCH /products/{id}` route from there. Skip it if you skipped that one.
