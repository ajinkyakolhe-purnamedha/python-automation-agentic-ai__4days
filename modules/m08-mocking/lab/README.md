# Lab 8 — TestClient vs. Mocking

**~50 min · Day 3 · Module 8 (Mocking)**

> **Concepts used:** FastAPI's `TestClient` (in-process, no network), `unittest.mock.patch` / `MagicMock`, `return_value`, `assert_called_once_with`, `side_effect` → `../codealong-m08-mocking.ipynb`.

## Goal
Learn the central judgment of mocking, taught as a contrast: test the Day-1
**server** for real with `TestClient` — it's cheap and in-process, so faking
it would prove nothing — then **mock** the new network **client**, because
its dependency (the network) is the one thing a unit test genuinely can't
run. Done when
`uv run pytest tests/test_server.py tests/test_client.py -q` → **9 passed**.

## You start with
Lab 7 green (`test_models.py` / `test_catalog.py` / `test_storage.py` — 22 passed).

## Add the new code
The lab introduces one new function — `get_products`. It is **not** the
Day-2 `APIClient`: no retry, no `Session`, no `APIError`. Just the single
call that actually leaves the machine.

You already have a `catalog/client.py` (it holds your Day-2 `APIClient`).
**Add `get_products` to it — don't overwrite the file** (`import_csv.py`
still imports `APIClient`). Copy the function out of the starter and paste
it below your existing class:

```python
# append to your existing catalog/client.py — `import requests` is already there
def get_products(base_url: str = "http://localhost:8000") -> list[Product]:
    """Fetch every product from the catalog API. Returns typed Products."""
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
```

> Starting fresh from `checkpoints/day-3-start/`? Its `client.py` already
> has both `APIClient` and `get_products` — skip this step.

## Get the starter tests
```bash
cp ../../modules/m08-mocking/lab/starter/tests/test_server.py tests/
cp ../../modules/m08-mocking/lab/starter/tests/test_client.py tests/
```

| File | What |
|---|---|
| `catalog/client.py` | `get_products` **added** to your existing file (above) — the only new production code |
| `tests/test_server.py` | stubs to fill — drive the real app with `TestClient`; `reset_catalog` fixture is **provided** |
| `tests/test_client.py` | stubs to fill — mock `catalog.client.requests.get`; `_ok_response` helper is **provided** |

Each stub fails with a `# TODO` + `pytest.fail(...)` until you implement it — that's the plan, not a bug: red until you fill it, green once you do.

## What to implement

- **§1 `test_server.py` — no mocks.** `TestClient(server.app)` runs the real
  FastAPI app with a real `ProductCatalog`, in-process — no uvicorn, no
  sockets. Assert: `/health` reports the seed count (5); `/products` lists
  5; a `POST` then `GET` round-trips the created product; a missing id is
  404; re-posting an id that's already seeded (id 1) is 409.
- **§2–§3 `test_client.py` — mock the network.** `get_products` calls
  `requests.get`, which is the one call a unit test must not actually make.
  Patch `catalog.client.requests.get`, then: a faked 200 comes back as
  `list[Product]`; the call was made with the right URL and
  `timeout=5` (`mock_get.assert_called_once_with("http://x/products", timeout=5)`);
  a `side_effect = requests.ConnectionError(...)` propagates unhandled;
  and a **malformed** row from the (faked) server — e.g. `price: -5` — raises
  `ValidationError`, because `get_products` validates every row through
  `Product.model_validate` before it ever reaches the caller.

## The judgment (call it out)
You run the cheap, in-process server **for real** in §1 — mocking a
`ProductCatalog` you already fully unit-tested in Lab 7 would just assert
against your own fake. But you **must fake** the network in §2–§3 — you
can't (and shouldn't) spin up a live server for a unit test. **Mock the
uncontrollable edge, run the cheap thing for real.** This is the exact
judgment Day 4 reuses to mock the LLM (`CatalogAgent(llm_client=...)`).

## Steps
1. Add `get_products` to your `catalog/client.py` (above) — the only new production code this lab adds. Don't overwrite the file.
2. Copy both starter test files into `tests/` (command above).
3. Fill `test_server.py`. Drive `client` (the module-level `TestClient`, already built for you) exactly like you'd drive `requests` against a live server — `client.get(...)`, `client.post(..., json={...})` — then assert on `.status_code` / `.json()`. Run `uv run pytest tests/test_server.py -q`; watch reds go green.
4. Fill `test_client.py`. Inside `with patch("catalog.client.requests.get") as mock_get:`, set `mock_get.return_value` (or `.side_effect`) *before* calling `get_products()`. Run `uv run pytest tests/test_client.py -q`.
5. Run both files together: `uv run pytest tests/test_server.py tests/test_client.py -q` → **9 passed**.

## Watch out
- **Patch where it's looked up, not where it's defined.** `client.py` does
  `import requests`, so patch `catalog.client.requests.get` — not
  `requests.get` directly. (Both happen to work here because `client.py`
  imports the module, not the name — but the target you patch is
  `catalog.client.requests.get`; that's the habit that survives when it
  doesn't.)
- **`reset_catalog` isolates the server tests.** `server.py` keeps `catalog`
  as a module global seeded with 5 products, so a `POST` in one test would
  otherwise leak into the next. The provided autouse fixture reseeds before
  every test — don't remove it, and don't add your own second reseed.
- **`spec=requests.Response`** on the fake in `_ok_response` means a
  typo'd attribute (`.jsonn()`) fails loudly instead of silently returning
  a `MagicMock`.
- **Set the mock up before you call the function.** `mock_get.return_value = ...`
  (or `.side_effect = ...`) has to happen *inside* the `with patch(...)`
  block, before `get_products()` runs.

## Make it pass
```bash
uv run pytest tests/test_server.py tests/test_client.py -q
```
```
.........
9 passed in 0.10s
```
