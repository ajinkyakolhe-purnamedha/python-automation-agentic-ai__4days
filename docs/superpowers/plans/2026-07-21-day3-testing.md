# Day 3 (Testing) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author Day 3 (Modules M07 Unit Testing, M08 Mocking, M09 Coverage) so it depends only on Modules 01–04 plus one ~4-line `get_products` network function, teaching unit testing, mocking, and coverage on the Product Catalog spine.

**Architecture:** Day 3 adds no production logic to the catalog except a tiny `get_products` network client (the single mock seam). Each module ships the repo's parallel artifact set — Marp slides, a code-along notebook, a lab README, and lab/starter test stubs — plus a *filled reference* test suite used as the acceptance target against `capstone-project/solution`. The student's own passing test suite is the scoreboard; there are no new `test_labNN.py` graders.

**Tech Stack:** Python ≥3.10, `pytest`, `pytest-cov`, `pytest-html`, `pytest-mock`, `unittest.mock`, FastAPI `TestClient` (needs `httpx`), `requests`, Pydantic v2, Marp, uv.

**Source spec:** `docs/superpowers/specs/2026-07-21-day3-testing-redesign-design.md` (§5 holds the per-section concept → code-along beats → lab-fold content that slides/notebooks/READMEs are authored from — do not duplicate that prose here; cite it).

## Global Constraints

- **Dependency floor:** Day-3 artifacts import only from `catalog.models`, `catalog.storage`, `catalog.server`, and the new `catalog.client.get_products`. No `APIClient`, no `@retry`, no CSV import.
- **Do NOT overwrite** `capstone-project/solution/catalog/client.py` — `agent.py` (Day 4) and `import_csv.py` (Day 2) import `APIClient`. `get_products` is **added alongside** it.
- **Decorators are used, never written** (`@pytest.fixture`, `@pytest.mark.parametrize`). No custom decorators in student-facing code.
- **All validation is Pydantic.** `get_products` returns `list[Product]` via `Product.model_validate`.
- **Never commit** `__pycache__/` or `*.pyc`.
- **`capstone-project/solution/` is `.gitignore`d (per CLAUDE.md — solution is intentionally uncommitted).** *Execution amendment (2026-07-21):* solution changes (`get_products`, `test_server.py`, `test_get_products.py`, `test_storage.py`) are **on-disk reference only** — used to compute acceptance numbers and as the answer key — and are **NOT committed**. The tracked/shipped copies live in the module starters (`modules/m0N-.../lab/starter/**`). Committed deliverables are `modules/**`, `docs/**`, the outline, `.gitignore`, and `capstone-project/checkpoints/day-3-start/**`. Solution-reference files are created/verified by the controller, not via reviewed subagent tasks.
- **Each lab README ends** on a runnable command whose expected output is shown; for Day 3 that command is the module's `pytest` run showing `N passed`.
- **Slides** are Marp (`marp: true`, `theme: acuity` frontmatter); render `.md` → `.html` with the Marp CLI.
- **Run commands** are uv-based: `uv run pytest ...` from a working copy (`capstone-project/solution` or a student `my-catalog`).
- **Patch target rule (M08):** patch `catalog.client.requests.get` (patch-where-looked-up), taught honestly.
- **Test isolation (M08 server tests):** reseed the module-global `server.catalog` before each test.

---

## Phase 0 — Foundation (the one new production function + solution safety net)

### Task 0.1: Add `get_products` to the solution client (alongside `APIClient`)

**Files:**
- Modify: `capstone-project/solution/catalog/client.py` (append a module-level function; do not touch `APIClient`)
- Test: `capstone-project/solution/tests/test_get_products.py` (create)

**Interfaces:**
- Produces: `catalog.client.get_products(base_url: str = "http://localhost:8000") -> list[Product]` — GETs `{base_url}/products`, calls `raise_for_status()`, returns `[Product.model_validate(row) for row in response.json()]`.

- [ ] **Step 1: Write the failing test**

Create `capstone-project/solution/tests/test_get_products.py`:

```python
"""Unit tests for the tiny Day-3 network client `catalog.client.get_products`."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from catalog.client import get_products
from catalog.models import Product

ONE_PRODUCT = [{"id": 1, "name": "Cable", "category": "Electronics",
                "price": 499.0, "in_stock": True, "tags": ["usb"]}]


def _ok_response(payload):
    resp = MagicMock(spec=requests.Response)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_returns_typed_products():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value = _ok_response(ONE_PRODUCT)
        result = get_products()
    assert isinstance(result[0], Product)
    assert result[0].id == 1


def test_hits_the_right_url():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value = _ok_response([])
        get_products("http://x")
    mock_get.assert_called_once_with("http://x/products", timeout=5)


def test_propagates_network_error():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("down")
        with pytest.raises(requests.ConnectionError):
            get_products()


def test_rejects_malformed_response():
    bad = [{"id": 1, "name": "X", "category": "c", "price": -5, "in_stock": True, "tags": []}]
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value = _ok_response(bad)
        with pytest.raises(ValidationError):
            get_products()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd capstone-project/solution && uv run pytest tests/test_get_products.py -q`
Expected: FAIL — `ImportError: cannot import name 'get_products' from 'catalog.client'`.

- [ ] **Step 3: Write minimal implementation**

Append to `capstone-project/solution/catalog/client.py` (below `APIClient`; the file already `import requests` and imports `Product`):

```python
# ---- Day-3 tiny network client (mock seam for M08). NOT the APIClient. ----

def get_products(base_url: str = DEFAULT_BASE_URL) -> list[Product]:
    """Fetch every product from the catalog API. Returns typed Products.

    Deliberately minimal — no retry, no Session, no APIError. One call that
    leaves the machine, so M08 has an honest thing to mock.
    """
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd capstone-project/solution && uv run pytest tests/test_get_products.py -q`
Expected: PASS — 4 passed.

- [ ] **Step 5: Confirm nothing else broke**

Run: `cd capstone-project/solution && uv run pytest -q -m "not integration and not eval"`
Expected: existing `APIClient`/agent/catalog tests still pass (no regressions).

- [ ] **Step 6: Commit**

```bash
git add capstone-project/solution/catalog/client.py capstone-project/solution/tests/test_get_products.py
git commit -m "feat(solution): add tiny get_products client alongside APIClient for Day-3 mocking"
```

### Task 0.2: Add `TestClient` server tests + reseed fixture to the solution

**Files:**
- Create: `capstone-project/solution/tests/test_server.py`

**Interfaces:**
- Consumes: `catalog.server.app`, `catalog.server.catalog` (module global), `catalog.storage.seed_products`, `catalog.models.ProductCatalog`.

- [ ] **Step 1: Write the failing test**

Create `capstone-project/solution/tests/test_server.py`:

```python
"""M08 §1 reference — test the FastAPI server for real, in-process (no mocks).

The app holds `catalog` as a module global seeded with 5 products, so a POST in
one test leaks into the next. The autouse fixture reseeds it before each test.
"""

import pytest
from fastapi.testclient import TestClient

from catalog import server
from catalog.models import ProductCatalog
from catalog.storage import seed_products

client = TestClient(server.app)


@pytest.fixture(autouse=True)
def reset_catalog():
    server.catalog = ProductCatalog(list(seed_products()))
    yield


def test_health_reports_seed_count():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "count": 5}


def test_list_returns_seed():
    r = client.get("/products")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_create_then_get_roundtrip():
    body = {"id": 900, "name": "Test", "category": "QA", "price": 12.0}
    assert client.post("/products", json=body).status_code == 201
    got = client.get("/products/900")
    assert got.status_code == 200
    assert got.json()["name"] == "Test"


def test_missing_returns_404():
    assert client.get("/products/999").status_code == 404


def test_duplicate_returns_409():
    body = {"id": 1, "name": "Dup", "category": "x", "price": 1.0}  # id 1 is seeded
    assert client.post("/products", json=body).status_code == 409
```

- [ ] **Step 2: Run test to verify it passes** (the app already exists, so these pass immediately — they are the reference the lab reproduces)

Run: `cd capstone-project/solution && uv run pytest tests/test_server.py -q`
Expected: PASS — 5 passed. If `httpx` is missing, `uv sync` first (it is already in the solution dev deps).

- [ ] **Step 3: Commit**

```bash
git add capstone-project/solution/tests/test_server.py
git commit -m "test(solution): add TestClient server tests + reseed fixture (M08 §1 reference)"
```

---

## Phase 1 — M07 Unit Testing

Content source: spec §5 → "M07 — Unit Testing", sections §1–§3.

### Task 1.1: M07 lab starter — add the `tmp_path` storage stub

**Files:**
- Verify (no change expected): `modules/m07-pytest-basics/lab/starter/tests/test_models.py`, `test_catalog.py`, `conftest.py` (already catalog/Pydantic-based stubs)
- Create: `modules/m07-pytest-basics/lab/starter/tests/test_storage.py`

- [ ] **Step 1: Confirm the existing starter stubs are catalog-based**

Run: `sed -n '1,20p' modules/m07-pytest-basics/lab/starter/tests/test_models.py`
Expected: imports `from catalog.models import Product, ProductCreate, ProductUpdate`; bodies are `pytest.fail("TODO...")`. If so, leave unchanged.

- [ ] **Step 2: Write the storage stub (student fills the two asserts)**

Create `modules/m07-pytest-basics/lab/starter/tests/test_storage.py`:

```python
"""Lab 7 · Part C — storage round-trips on a REAL temp file (pytest's tmp_path).

`tmp_path` is a built-in fixture: a fresh temp directory per test. This is the
right tool for file I/O — you verify real serialization, you do NOT mock the
filesystem (that's an anti-pattern; mocks are for M08's network edge).

Fill each `# TODO`, replace `pytest.fail(...)`, run `pytest tests/test_storage.py -q`.
"""

import pytest

from catalog.models import Product, ProductCatalog
from catalog.storage import save_json, load_json


def test_json_roundtrip(tmp_path):
    """save_json then load_json returns an equal catalog."""
    cat = ProductCatalog([
        Product(id=1, name="Cable", category="Electronics", price=499.0),
        Product(id=2, name="Mat", category="Fitness", price=1299.0, in_stock=False),
    ])
    path = tmp_path / "catalog.json"
    # TODO: save_json(cat, path); loaded = load_json(path)
    #       assert loaded.list_all() == cat.list_all()
    pytest.fail("TODO: implement test_json_roundtrip")


def test_load_missing_file_returns_empty(tmp_path):
    """load_json on a non-existent path returns an empty catalog, not a crash."""
    # TODO: loaded = load_json(tmp_path / "nope.json"); assert len(loaded) == 0
    pytest.fail("TODO: implement test_load_missing_file_returns_empty")
```

- [ ] **Step 3: Write the FILLED reference (acceptance target) and verify against the solution**

Create a scratch file `capstone-project/solution/tests/test_storage.py` with the two `# TODO`s implemented:

```python
import pytest
from catalog.models import Product, ProductCatalog
from catalog.storage import save_json, load_json


def test_json_roundtrip(tmp_path):
    cat = ProductCatalog([
        Product(id=1, name="Cable", category="Electronics", price=499.0),
        Product(id=2, name="Mat", category="Fitness", price=1299.0, in_stock=False),
    ])
    path = tmp_path / "catalog.json"
    save_json(cat, path)
    loaded = load_json(path)
    assert loaded.list_all() == cat.list_all()


def test_load_missing_file_returns_empty(tmp_path):
    loaded = load_json(tmp_path / "nope.json")
    assert len(loaded) == 0
```

Run: `cd capstone-project/solution && uv run pytest tests/test_storage.py -q`
Expected: PASS — 2 passed. (This proves the stub's TODOs are solvable against the real `storage.py`.)

- [ ] **Step 4: Commit**

```bash
git add modules/m07-pytest-basics/lab/starter/tests/test_storage.py capstone-project/solution/tests/test_storage.py
git commit -m "feat(m07): add tmp_path storage round-trip test (stub + reference)"
```

### Task 1.2: M07 lab README

**Files:**
- Modify: `modules/m07-pytest-basics/lab/README.md`

- [ ] **Step 1: Rewrite the README to the Day-3 contract**

Author `modules/m07-pytest-basics/lab/README.md` following the repo's lab-README contract (*start with X → end with Y → run this command*) and spec §5 M07:
- **Title/meta:** `# Lab 7 — Unit Tests for the Catalog` · Day 3 · concepts → `../codealong-m07-pytest-basics.ipynb`.
- **You start with:** your Day-2 folder (`catalog/` with Pydantic models + storage). **No mocks in this lab.**
- **Get the starter tests:** `cp -r ../../modules/m07-pytest-basics/lab/starter/tests .` (into `my-catalog/`).
- **What to implement**, mapped to the three sections: (§1) happy-path asserts in `test_catalog.py`; (§2) `pytest.raises` + the parametrized `Field`-rule table in `test_models.py`/`test_catalog.py`; (§3) fixtures from `conftest.py` + the `tmp_path` round-trip in `test_storage.py`.
- **Watch out:** narrowest exception in `pytest.raises`; one behavior per test; use `tmp_path`, never mock the filesystem.
- **Ends on** (the shown command + output):

  ```
  uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q
  ...
  N passed
  ```

- [ ] **Step 2: Verify the final command's count is real**

Run the filled reference suite to determine N:
`cd capstone-project/solution && uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q`
Then set the README's shown `N passed` to that exact number.
Expected: a concrete integer (e.g. `18 passed`) — no placeholder.

- [ ] **Step 3: Commit**

```bash
git add modules/m07-pytest-basics/lab/README.md
git commit -m "docs(m07): rewrite lab README for Day-3 unit-testing contract"
```

### Task 1.3: M07 slides

**Files:**
- Create/Modify: `modules/m07-pytest-basics/slides-m07-pytest-basics.md`
- Render: `modules/m07-pytest-basics/slides-m07-pytest-basics.html`

- [ ] **Step 1: Author the deck**

Write `slides-m07-pytest-basics.md` with Marp frontmatter (`marp: true`, `theme: acuity`). Structure: one slide segment per spec §5 M07 section (§1 assert · §2 raises+parametrize · §3 fixtures/tmp_path), using the **exact code-along beats** listed there as the on-slide code. Every code block must be runnable Python against the catalog. Include the "no mocks here — mocks are M08's edge" framing on the opening slide.

- [ ] **Step 2: Render and verify**

Run: `marp modules/m07-pytest-basics/slides-m07-pytest-basics.md -o modules/m07-pytest-basics/slides-m07-pytest-basics.html`
Expected: exits 0, `.html` produced, no Marp warnings about frontmatter.

- [ ] **Step 3: Commit**

```bash
git add modules/m07-pytest-basics/slides-m07-pytest-basics.md modules/m07-pytest-basics/slides-m07-pytest-basics.html
git commit -m "docs(m07): author unit-testing slides"
```

### Task 1.4: M07 code-along notebook

**Files:**
- Create: `modules/m07-pytest-basics/codealong-m07-pytest-basics.ipynb`

- [ ] **Step 1: Author the notebook**

Build the notebook cell-by-cell from spec §5 M07 beats (§1→§3). Each section: a markdown cell (the concept) then code cells reproducing the beats. Because pytest runs from the CLI, use `ipytest` or `!uv run pytest` cells, OR write plain assert cells that execute inline (recommended for a code-along: define a `Product`/`ProductCatalog`, assert inline; show `pytest.raises` via a small `try/except`-style demonstration then the real `pytest.raises` snippet as markdown). End with a cell running the lab suite: `!cd <my-catalog> && uv run pytest -q`.

- [ ] **Step 2: Execute top-to-bottom to verify it's clean**

Run: `cd modules/m07-pytest-basics && uv run --with jupyter jupyter nbconvert --to notebook --execute --inplace codealong-m07-pytest-basics.ipynb`
Expected: exits 0, no cell raises an uncaught exception.

- [ ] **Step 3: Strip outputs and commit**

Run: `uv run --with jupyter jupyter nbconvert --clear-output --inplace modules/m07-pytest-basics/codealong-m07-pytest-basics.ipynb`
```bash
git add modules/m07-pytest-basics/codealong-m07-pytest-basics.ipynb
git commit -m "docs(m07): author unit-testing code-along notebook"
```

---

## Phase 2 — M08 Mocking

Content source: spec §5 → "M08 — Mocking", sections §1–§3. Folder rename happens first.

### Task 2.1: Rename the module folder `m08-parametrize-mock` → `m08-mocking`

**Files:**
- Rename: `modules/m08-parametrize-mock/` → `modules/m08-mocking/` and its `slides-…`, `codealong-…` basenames.

- [ ] **Step 1: Rename with git**

```bash
git mv modules/m08-parametrize-mock modules/m08-mocking
git mv modules/m08-mocking/slides-m08-parametrize-mock.md modules/m08-mocking/slides-m08-mocking.md
# rename the codealong dir/file if present:
git mv modules/m08-mocking/codealong-m08-parametrize-mock modules/m08-mocking/codealong-m08-mocking 2>/dev/null || true
```

- [ ] **Step 2: Verify no path references the old name**

Run: `grep -rn "m08-parametrize-mock" modules docs private_* 2>/dev/null || echo "clean"`
Expected: `clean` (fix any stragglers, e.g. the outline — handled in Task 4.2).

- [ ] **Step 3: Commit**

```bash
git add -A modules/m08-mocking
git commit -m "refactor(m08): rename m08-parametrize-mock -> m08-mocking (parametrize moved to M07)"
```

### Task 2.2: M08 lab starter — `client.py` + test stubs

**Files:**
- Create: `modules/m08-mocking/lab/starter/catalog/client.py` (get_products only)
- Replace: `modules/m08-mocking/lab/starter/tests/test_client.py` (old APIClient-mock version → get_products mock stubs)
- Create: `modules/m08-mocking/lab/starter/tests/test_server.py` (TestClient stubs)

- [ ] **Step 1: Write the starter `client.py` (the one the student copies in)**

Create `modules/m08-mocking/lab/starter/catalog/client.py`:

```python
"""Day-3 tiny network client — the one thing M08 mocks.

NOT the M05 APIClient: no retry, no Session, no APIError. One call that leaves
the machine (`requests.get`), returning typed Products.

Copy into your `catalog/` package. Then write tests that mock `requests.get`.
"""

import requests

from .models import Product

DEFAULT_BASE_URL = "http://localhost:8000"


def get_products(base_url: str = DEFAULT_BASE_URL) -> list[Product]:
    """Fetch every product from the catalog API. Returns typed Products."""
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
```

- [ ] **Step 2: Write the `test_client.py` stub (student fills)**

Create `modules/m08-mocking/lab/starter/tests/test_client.py`:

```python
"""Lab 8 · Part B — mock the network. `get_products` calls requests.get; a unit
test must not hit a real server, so patch `catalog.client.requests.get`.

PROVIDED: `_ok_response`. Fill every `# TODO`; run `pytest tests/test_client.py -q`.
Concepts: codealong/module-8 §"Mock the network".
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from catalog.client import get_products
from catalog.models import Product

ONE_PRODUCT = [{"id": 1, "name": "Cable", "category": "Electronics",
                "price": 499.0, "in_stock": True, "tags": ["usb"]}]


def _ok_response(payload):  # PROVIDED — a fake requests.Response
    resp = MagicMock(spec=requests.Response)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_get_products_returns_typed_products():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response(ONE_PRODUCT)
        #       result = get_products(); assert isinstance(result[0], Product)
        pytest.fail("TODO: implement test_get_products_returns_typed_products")


def test_hits_right_url():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response([]); get_products("http://x")
        #       mock_get.assert_called_once_with("http://x/products", timeout=5)
        pytest.fail("TODO: implement test_hits_right_url")


def test_propagates_network_error():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.side_effect = requests.ConnectionError("down")
        #       with pytest.raises(requests.ConnectionError): get_products()
        pytest.fail("TODO: implement test_propagates_network_error")


def test_rejects_malformed_response():
    bad = [{"id": 1, "name": "X", "category": "c", "price": -5, "in_stock": True, "tags": []}]
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response(bad)
        #       with pytest.raises(ValidationError): get_products()
        pytest.fail("TODO: implement test_rejects_malformed_response")
```

- [ ] **Step 3: Write the `test_server.py` stub (student fills)**

Create `modules/m08-mocking/lab/starter/tests/test_server.py` — same structure as the solution reference in Task 0.2 but with the assert lines replaced by `# TODO` + `pytest.fail(...)`, and the `reset_catalog` autouse fixture PROVIDED intact (it teaches fixtures, not the lesson under test).

- [ ] **Step 4: Verify stubs import and fail (not error) against the solution**

Copy stubs into the solution scratch and run:
`cd capstone-project/solution && uv run pytest tests/test_client.py -q` should already pass (that's the reference from Task 0.1's `test_get_products.py` — reuse it as the answer key).
Expected: the stub bodies `pytest.fail` cleanly (collectible, no ImportError).

- [ ] **Step 5: Commit**

```bash
git add modules/m08-mocking/lab/starter
git commit -m "feat(m08): starter get_products client + mock/TestClient test stubs"
```

### Task 2.3: M08 lab README

**Files:**
- Modify: `modules/m08-mocking/lab/README.md`

- [ ] **Step 1: Rewrite the README**

Author to the lab contract + spec §5 M08:
- **Title:** `# Lab 8 — TestClient vs. Mocking`. Day 3.
- **You start with:** Lab 7 green. **Add** `catalog/client.py` (copy from starter) — the only new code.
- **What to implement:** (§1) `test_server.py` — drive the real app with `TestClient` (health, list=5, create→get, 404, 409), no mocks; (§2–§3) `test_client.py` — patch `catalog.client.requests.get`: typed return, right URL (`assert_called_once_with`), `side_effect` network error, malformed→`ValidationError`.
- **Watch out:** patch where it's looked up (`catalog.client.requests.get`); reseed the server catalog between tests; `spec=` on mocks catches typos.
- **Ends on:**

  ```
  uv run pytest tests/test_server.py tests/test_client.py -q
  ...
  N passed
  ```

- [ ] **Step 2: Set N from the reference**

Run: `cd capstone-project/solution && uv run pytest tests/test_server.py tests/test_get_products.py -q`
Set the README's `N passed` (server 5 + client 4 = 9) to the observed number.

- [ ] **Step 3: Commit**

```bash
git add modules/m08-mocking/lab/README.md
git commit -m "docs(m08): rewrite lab README for TestClient + mocking contract"
```

### Task 2.4: M08 slides

**Files:**
- Create/Modify: `modules/m08-mocking/slides-m08-mocking.md` + render `.html`

- [ ] **Step 1: Author the deck** from spec §5 M08 §1–§3 (TestClient real → mock the client → verify+side_effect+malformed). Lead with the *when-to-mock judgment* (run the cheap server for real; fake the network). Marp frontmatter as in Task 1.3.
- [ ] **Step 2: Render**: `marp modules/m08-mocking/slides-m08-mocking.md -o modules/m08-mocking/slides-m08-mocking.html` → exits 0.
- [ ] **Step 3: Commit**

```bash
git add modules/m08-mocking/slides-m08-mocking.md modules/m08-mocking/slides-m08-mocking.html
git commit -m "docs(m08): author mocking slides"
```

### Task 2.5: M08 code-along notebook

**Files:**
- Create: `modules/m08-mocking/codealong-m08-mocking.ipynb`

- [ ] **Step 1: Author** from spec §5 M08 beats: a `TestClient` demo section (real app), then `patch`/`MagicMock`/`return_value`, `assert_called_once_with`, `side_effect`, malformed→`ValidationError`. Use inline `unittest.mock.patch` context managers in cells so each executes standalone.
- [ ] **Step 2: Execute**: `cd modules/m08-mocking && uv run --with jupyter jupyter nbconvert --to notebook --execute --inplace codealong-m08-mocking.ipynb` → exits 0.
- [ ] **Step 3: Clear outputs + commit**

```bash
uv run --with jupyter jupyter nbconvert --clear-output --inplace modules/m08-mocking/codealong-m08-mocking.ipynb
git add modules/m08-mocking/codealong-m08-mocking.ipynb
git commit -m "docs(m08): author mocking code-along notebook"
```

---

## Phase 3 — M09 Coverage + CI

Content source: spec §5 → "M09 — Coverage", §1–§2. Starter files already exist (`pyproject-additions.toml`, `.github/workflows/tests.yml`) — verify, then author teaching artifacts.

### Task 3.1: Verify + finalize M09 lab starter

**Files:**
- Verify/Modify: `modules/m09-coverage-ci/lab/starter/pyproject-additions.toml`
- Verify/Modify: `modules/m09-coverage-ci/lab/starter/.github/workflows/tests.yml`

- [ ] **Step 1: Confirm the coverage config targets `catalog`**

Run: `cat modules/m09-coverage-ci/lab/starter/pyproject-additions.toml`
Expected: a `[tool.coverage.run]` block with `source = ["catalog"]` + `branch = true` (as `# TODO` for the student to complete). If missing, add it as the fill-in target.

- [ ] **Step 2: Confirm the CI skeleton has the matrix + upload TODOs**

Run: `cat modules/m09-coverage-ci/lab/starter/.github/workflows/tests.yml`
Expected: triggers, `python-version` matrix, install, pytest+coverage, artifact upload — each a `# TODO`. Ensure it references `pip install -e ".[dev]"` and `pytest --cov --cov-report=... --html=...`.

- [ ] **Step 3: Commit any fixes**

```bash
git add modules/m09-coverage-ci/lab/starter
git commit -m "chore(m09): finalize coverage + CI starter TODOs"
```

### Task 3.2: M09 lab README + slides + code-along

**Files:**
- Modify: `modules/m09-coverage-ci/lab/README.md`
- Create/Modify: `modules/m09-coverage-ci/slides-m09-coverage-ci.md` + `.html`
- Create: `modules/m09-coverage-ci/codealong-m09-coverage-ci.ipynb`

- [ ] **Step 1: README** to the lab contract + spec §5 M09: coverage run, read *Missing*, fill `pyproject` coverage config, fill `tests.yml`. **Ends on:**

  ```
  uv run pytest --cov --cov-report=term-missing -q
  ...
  TOTAL   ...   NN%
  ```
  Determine the real `NN%` by running against the solution suite (Step 2).

- [ ] **Step 2: Slides** from spec §5 M09 §1–§2; render `.html` (exits 0). **Code-along** from the beats; execute clean (`nbconvert --execute`), clear outputs.

- [ ] **Step 3: Compute the real coverage number**

Run: `cd capstone-project/solution && uv run pytest --cov --cov-report=term-missing -q -m "not integration and not eval"`
Put the observed `TOTAL … NN%` into the README (no placeholder). Confirm `--cov-fail-under=80` (stretch) is reachable now that `test_server.py` exercises `server.py`; if below 80, note the true reachable number in the stretch instead.

- [ ] **Step 4: Commit**

```bash
git add modules/m09-coverage-ci/lab/README.md modules/m09-coverage-ci/slides-m09-coverage-ci.md modules/m09-coverage-ci/slides-m09-coverage-ci.html modules/m09-coverage-ci/codealong-m09-coverage-ci.ipynb
git commit -m "docs(m09): author coverage + CI README, slides, code-along"
```

---

## Phase 4 — Integration & housekeeping

### Task 4.1: Ignore `__pycache__` so `.pyc` never lands in git

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Ensure the ignore rules exist**

Run: `grep -qE '^\s*__pycache__/' .gitignore && grep -qE '^\s*\*\.pyc' .gitignore && echo present || echo missing`
If `missing`, append:
```
__pycache__/
*.pyc
```

- [ ] **Step 2: Untrack any already-committed caches (none should exist on this branch)**

Run: `git ls-files '*.pyc' '**/__pycache__/**' | head` → expected empty. If non-empty: `git rm -r --cached <paths>`.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore __pycache__/ and *.pyc"
```

### Task 4.2: Update the outline for the Day-3 changes

**Files:**
- Modify: `private_goal_details/outline_v4.2-24hrs.md` (Day-3 rows)

- [ ] **Step 1: Locate the Day-3 lines**

Run: `grep -nE "M0[789]|Lab 7|Lab 8|Lab 9|parametrize|APIClient|retry" private_goal_details/outline_v4.2-24hrs.md`

- [ ] **Step 2: Edit** so: M07 = unit testing incl. `@parametrize`; M08 = "mocking a network call + `TestClient`" (remove APIClient/retry framing); M09 unchanged; rename any `m08-parametrize-mock` reference to `m08-mocking`.

- [ ] **Step 3: Commit**

```bash
git add private_goal_details/outline_v4.2-24hrs.md
git commit -m "docs(outline): align Day-3 with testing redesign (parametrize->M07, M08=mocking)"
```

### Task 4.3: Create the `day-3-start` checkpoint

**Files:**
- Create: `capstone-project/checkpoints/day-3-start/` (a Day-2-complete working copy + Day-3 lab starter tests copied in)

- [ ] **Step 1: Seed from the Day-2 end-state**

The checkpoint is a runnable copy where Days 1–2 are done and Day-3 tests are ready to fill. Build it from `capstone-project/solution` catalog code minus Day-4 files, or from a completed Day-2 copy. Concretely: copy `solution/catalog` (excluding `agent.py`, `decorators.py`, `import_csv.py` if keeping Day-3 scope tight — OR keep all; decide with the maintainer) + `solution/pyproject.toml` + the Day-1–2 `test_lab0N.py` graders, then add the M07/M08 starter `tests/` stubs.

- [ ] **Step 2: Verify it runs and Day-3 stubs are present-but-failing**

Run: `cd capstone-project/checkpoints/day-3-start && uv sync && uv run pytest -q`
Expected: Day-1–2 graders pass/skip as designed; the copied Day-3 stub tests `fail` on their TODOs (not error).

- [ ] **Step 3: Add a `.gitignore` for `.venv`/caches, then commit** (do not commit `.venv`, `uv.lock` is fine)

```bash
git add capstone-project/checkpoints/day-3-start
git commit -m "feat(capstone): add day-3-start checkpoint"
```

### Task 4.4: Full Day-3 acceptance run

- [ ] **Step 1: Solution suite green**

Run: `cd capstone-project/solution && uv run pytest -q -m "not integration and not eval"`
Expected: all pass, including the new `test_get_products.py`, `test_server.py`, `test_storage.py`.

- [ ] **Step 2: Every deck renders**

Run: `for m in m07-pytest-basics m08-mocking m09-coverage-ci; do marp modules/$m/slides-$m.md -o modules/$m/slides-$m.html || echo "FAIL $m"; done`
Expected: no `FAIL` lines.

- [ ] **Step 3: Every code-along executes clean**

Run each module's `nbconvert --execute` (as in Tasks 1.4/2.5/3.2) → all exit 0.

- [ ] **Step 4: No `m08-parametrize-mock` / `APIClient`-in-Day-3 stragglers**

Run: `grep -rn "m08-parametrize-mock" modules docs private_* 2>/dev/null || echo clean`
Expected: `clean`.

---

## Self-Review (completed by plan author)

**Spec coverage:** Locked decisions 1–6 → Tasks 0.1 (get_products/Pydantic), 1.1/1.3/1.4 (M07 sections), 2.2–2.5 (M08 sections), 3.1–3.2 (M09), 2.1 (folder rename), 1.1 (storage=fixtures). §4 client placement → 0.1 + 2.2. §5 all eight sections → the slides/codealong/README tasks per module. §6 artifacts → every module has slides+codealong+README+starter tasks. §7 downstream → 0.1 (add-not-replace), 4.2 (outline), 4.1 (gitignore), 4.3 (checkpoint). §8 non-goals respected (no retry, no CSV, no fs mocking). §9 success criteria → 4.4 acceptance run.

**Placeholder scan:** All test/impl code is complete and runnable. Slide/notebook/README tasks cite spec §5 for prose (DRY) but pin exact files, required code blocks, and a concrete verify command; the two numeric done-signals (`N passed`, `NN%`) are computed from the solution in their own steps, not left as placeholders.

**Type consistency:** `get_products(base_url="http://localhost:8000") -> list[Product]` identical across Tasks 0.1, 2.2, and every test. `reset_catalog` autouse fixture identical in 0.2 and 2.2. Patch target `catalog.client.requests.get` consistent throughout.
