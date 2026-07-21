---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 3 · Test It — pytest, Mocking, Coverage & CI"
footer: "Acuity Training · Day 3 of 4"
---

<!-- _class: title -->

# Module 8
## Mocking
**3 sections · ~40 min** — run it for real → mock the edge → verify + simulate failure
1 Test the server with TestClient · 2 Mock the network client · 3 Verify + side_effect
---
# When do you actually mock?

You mock at the **boundary** between your code and something you can't (or shouldn't) run in a unit test — the network, a paid API, a clock, an email send. Your own cheap, in-memory logic? Run it for real.

```text
cheap + in-process (a ProductCatalog, a temp file)  →  run it for real     — mocking proves nothing
uncontrollable edge (the network, an LLM)            →  fake it             — the real thing can't run here
```

This module teaches that judgment as a **contrast**: §1 runs the server for real; §2–§3 mock the one call that leaves the machine.
---
<!-- _class: section -->

# Section 1 · Test the server for real — `TestClient`
## The catalog is cheap and in-process. Don't mock it — run it.
## FastAPI's `TestClient` drives your real app with no network.
---
# 1.1 · `TestClient` runs your app in-process

No uvicorn, no sockets — `TestClient` calls your real routes against a real `ProductCatalog`.

```python
from fastapi.testclient import TestClient
from catalog.server import app

client = TestClient(app)

def test_list_returns_seed():
    r = client.get("/products")
    assert r.status_code == 200
    assert len(r.json()) == 5        # the 5 seeded products
```

No `@patch` anywhere — the app and its catalog are **real**. Hold that against §2.
---
# 1.2 · A round-trip, then the error mappings

```python
def test_create_then_get_roundtrip():
    body = {"id": 900, "name": "Test", "category": "QA", "price": 12.0}
    assert client.post("/products", json=body).status_code == 201
    assert client.get("/products/900").json()["name"] == "Test"

def test_missing_is_404():
    assert client.get("/products/999").status_code == 404
```

A duplicate id (POST id 1, already seeded) returns **409** — the same `CatalogError`→status mapping your routes already do.
---
# 1.3 · Isolate the tests — reseed the global

`server.py` holds `catalog` as a **module global**, so a `POST` in one test leaks into the next. An **autouse** fixture reseeds before each test.

```python
import pytest
from catalog import server
from catalog.models import ProductCatalog
from catalog.storage import seed_products

@pytest.fixture(autouse=True)
def reset_catalog():
    server.catalog = ProductCatalog(list(seed_products()))
    yield
```

That's M7's fixtures idea again — here it buys **test isolation**, not just tidy setup.

<div class="code-along">▶ Code-along now → notebook §1 — the mock vocabulary you'll aim at requests.get; TestClient shown for the lab</div>
---
<!-- _class: section -->

# Section 2 · Mock the network client
## `get_products` calls `requests.get` — the one thing a unit test can't run.
## Replace it with a fake you control: `patch` + `MagicMock`.
---
# 2.1 · The thing under test

`catalog/client.py` — no retry, no Session, no APIError. Just one call that leaves the machine.

```python
import requests
from catalog.models import Product

def get_products(base_url="http://localhost:8000") -> list[Product]:
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
```

Calling this for real needs a running server. A unit test must not depend on that — so we fake `requests.get`.
---
# 2.2 · `patch` swaps the real call for a fake

```python
from unittest.mock import patch, MagicMock
from catalog.client import get_products
from catalog.models import Product

def test_returns_typed_products():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = [
            {"id": 1, "name": "Cable", "category": "Electronics",
             "price": 499.0, "in_stock": True, "tags": []}]
        mock_get.return_value.raise_for_status.return_value = None
        result = get_products()
    assert isinstance(result[0], Product)     # dicts came back as Products
```

`return_value` is the fake response; `.json()` returns whatever you decide.
---
# 2.3 · Patch where the name is *looked up*

```python
patch("catalog.client.requests.get")   # ✓ where get_products looks it up
```

`client.py` did `import requests`, so `patch("requests.get")` *also* works here (same module object). But the habit that survives — when a file does `from requests import get` — is to patch **the name where the code uses it**: `catalog.client.requests.get`.

Add `spec=requests.Response` to a fake response and a typo'd attribute (`.jsonn()`) fails loudly instead of returning a silent `MagicMock`.

<div class="code-along">▶ Code-along now → notebook §2 — patch a call, set return_value, assert the typed result</div>
---
<!-- _class: section -->

# Section 3 · Verify the call + simulate failure
## A mock records *how* it was called — and can be made to fail on demand.
---
# 3.1 · Assert the right call was made

Beyond "what came back", check the call itself — the URL, the timeout.

```python
def test_hits_right_url():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status.return_value = None
        get_products("http://x")
    mock_get.assert_called_once_with("http://x/products", timeout=5)
```

`assert_called_once_with` fails if the URL was wrong, the timeout was dropped, or it was called twice.
---
# 3.2 · `side_effect` — make the fake fail

`return_value` gives a fixed result; `side_effect` **raises** (or yields a sequence). Use it to drive your error path.

```python
import requests, pytest

def test_network_error_propagates():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("down")
        with pytest.raises(requests.ConnectionError):
            get_products()
```

You can't make the real network drop on cue — the mock can.
---
# 3.3 · The test that actually earns its keep

"The network raised" just re-raises. The *valuable* failure test: the server returns a **bad row**, and your client refuses to hand it back.

```python
from pydantic import ValidationError

def test_rejects_malformed_response():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value.json.return_value = [
            {"id": 1, "name": "X", "category": "c", "price": -5,   # price < 0
             "in_stock": True, "tags": []}]
        mock_get.return_value.raise_for_status.return_value = None
        with pytest.raises(ValidationError):
            get_products()
```

`Product.model_validate` guards the boundary — garbage from the server never leaks out as a `Product`. M4's Pydantic, earning its keep in a test.

<div class="code-along">▶ Code-along now → notebook §3 — assert_called_once_with, then side_effect, then malformed→ValidationError</div>
---
<!-- _class: lab -->

# 🧪 Lab 8 — TestClient vs. Mocking

**~50 min** · open `modules/m08-mocking/lab/README.md`

You'll write:
- `tests/test_server.py` — drive the real app with `TestClient` (no mocks): count 5, round-trip, 404, 409
- `tests/test_client.py` — mock `catalog.client.requests.get`: typed return, right URL, `side_effect` error, malformed→`ValidationError`

**The judgment:** run the cheap server for real; fake the uncontrollable network.

Run `uv run pytest tests/test_server.py tests/test_client.py -q` → **9 passed**.
