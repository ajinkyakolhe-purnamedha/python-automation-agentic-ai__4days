# Day 3 (Testing) Redesign — Design Spec

**Date:** 2026-07-21
**Modules:** M07, M08, M09 (Day 3)
**Status:** Approved design — ready for implementation plan

## 1. Goal

Redesign Day 3 so it teaches **three testing pillars — unit testing, mocking, and
coverage — and depends only on Modules 01–04** (Python core → files → OOP/dataclass →
Pydantic + FastAPI). Day 3 no longer requires **M05** (the `requests`-based `APIClient`
with its retry loop) or **M06** (CSV bulk import).

The design is driven by teaching, not architecture: each module teaches Python/pytest
**features**, demonstrated on the Product Catalog spine. We do not build engineering
*patterns* (e.g. retry) for their own sake.

## 2. Locked decisions

1. **Keep Pydantic** (M04). It is the Day-2 payoff and earns its place: the model's
   `Field` constraints are the natural subject for unit tests and `@parametrize`.
2. **Drop the M05 `APIClient`** (typed client + `@retry` + session + `APIError` mapping)
   from the Day-3 dependency chain. Its only genuinely mock-worthy dependency was the
   network; its complexity (retry, status mapping) is not a testing *feature*.
3. **Mocking is taught on the network** — the one call that leaves the machine. A new,
   ~4-line-of-logic `catalog/client.py` (NOT the M05 client) provides the single seam.
4. **Module → pillar mapping:** M07 = Unit testing · M08 = Mocking · M09 = Coverage. M08
   also uses FastAPI's `TestClient` to test the Day-1 server *for real* (in-process, no
   network) — the deliberate contrast that teaches *when* to mock vs. run the real thing,
   and the only thing that exercises `server.py`.
5. **Each module = 2–3 sections.** Each section: *teach one feature → code-along that
   feature → fold it into the catalog in the lab.*
6. **Storage is a fixtures lesson, not a mock lesson.** `storage.save_json/load_json`
   touch only the local filesystem, so they are tested with pytest's built-in `tmp_path`
   (a real save→load round-trip), NOT by mocking file I/O (which would be an anti-pattern).

## 3. Foundation Day 3 stands on (end of M04)

Students arrive at Day 3 with (all already implemented in `capstone-project/solution`):

- `catalog/models.py` — Pydantic `ProductBase` / `ProductCreate` / `Product` /
  `ProductUpdate` (with `Field` constraints + the `_split_csv_tags` validator),
  `CatalogError`, and the `ProductCatalog` class
  (`add` / `delete` / `update` / `get` / `list_all` / `__len__` /
  `search_by_name` / `filter_by_price` / `group_by_category`).
- `catalog/storage.py` — `save_json` / `load_json` (+ `save_csv` / `load_csv` /
  `seed_products`).
- `catalog/server.py` — FastAPI `app` + a module-level `catalog`; routes
  `GET/POST/PATCH/DELETE /products`, `GET /health`.

No `requests`, no `APIClient`, no CSV-import workflow is required.

## 4. New code introduced in Day 3

A single small module, added at the start of M08, is the entire new surface area:

```python
# catalog/client.py  — the Day-3 network seam. Deliberately tiny: NO retry,
# NO Session class, NO APIError mapping. Just one call that leaves the machine.
import requests

from .models import Product

DEFAULT_BASE_URL = "http://localhost:8000"


def get_products(base_url: str = DEFAULT_BASE_URL) -> list[Product]:
    """Fetch every product from the catalog API. Returns typed Products."""
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
```

Why this shape:
- **One honest external edge** — the network — so mocking is *legitimate*, not contrived.
- **Returns `list[Product]`**, reusing M04's Pydantic model → keeps the spine coherent and
  lets a mock test assert `isinstance(result[0], Product)`.
- **Teaches the full mock vocabulary** on one function (see M08 below).
- A second function (`get_product(product_id)`) MAY be added if an extra parametrize /
  second-layer-mock example is wanted; not required for the core lesson.

**Placement (important — avoids a Day-4 collision).** The solution's existing
`catalog/client.py` already holds the M05 `APIClient`, and Day-4's `agent.py` + Day-2's
`import_csv.py` import it — so it **must not be overwritten**. Therefore:
- **Solution:** `get_products` is **added alongside** the existing `APIClient` in
  `catalog/client.py` (both coexist; APIClient stays for Day 2/4).
- **Day-3 module starter (`m08.../lab/starter/`) and a student on the M01–M04 track:**
  `client.py` contains **only** `get_products` — that student never built the `APIClient`.
- Grader `test_lab08.py` imports `from catalog.client import get_products` via
  `pytest.importorskip`, so it passes in both the student copy and the solution.

---

## 5. Module designs — full section articulation

Each section below is written to be authored directly into a slide segment + a code-along
cell group + a lab step. Format per section: **Concept & why → Code-along beats (the live
demo, in order) → Lab fold (what the student writes).**

### M07 — Unit Testing *(write real tests for real logic)*

Frame: everything in M07 tests **pure logic with real objects — no mocks.** "No mocks here"
is itself a lesson: you only reach for mocks at an external edge (M08).

#### M07 §1 — Test functions + `assert`
- **Concept & why.** A test is just a function named `test_*` that makes an `assert`.
  pytest discovers it, runs it, and on failure shows *both sides* of the comparison
  (rich assert rewriting) — no `assertEqual`, no boilerplate. Run with `pytest -q`; select
  with `-k`; see names with `-v`.
- **Code-along beats.**
  1. `def test_math(): assert 1 + 1 == 2` → `pytest -q` shows `1 passed`.
  2. Break it to `== 3`, rerun, read the introspected diff (`assert 2 == 3`). *This* is why
     pytest over `unittest`.
  3. Real object: `p = Product(id=1, name="Cable", category="Electronics", price=499.0)`
     then `assert p.price == 499.0` and `assert p.tags == []` (default).
  4. A query: seed a `ProductCatalog([...])`, `assert len(cat.list_all()) == 2`.
  5. Discovery/naming rules (`test_*.py`, `test_*`), and `pytest -k search` to run one.
- **Lab fold.** Pin the catalog's happy paths in `test_catalog.py`: construct → `add` →
  `get` returns it; a `search_by_name` / `filter_by_price` result is what you expect.

#### M07 §2 — `pytest.raises` + `@pytest.mark.parametrize`
- **Concept & why.** Good code fails loudly; tests must assert the failure, not just the
  happy path. `with pytest.raises(Exc, match="..."):`. When many cases share one body,
  don't copy-paste — `@pytest.mark.parametrize` turns one test into a table of cases
  (a *used* decorator, consistent with the course's "you use `@`, never write it" rule).
- **Code-along beats.**
  1. `with pytest.raises(CatalogError, match="already exists"): cat.add(dup)`.
  2. Use the **narrowest** exception — show that `Exception` would also swallow real bugs.
  3. Missing id: `with pytest.raises(CatalogError, match="not found"): cat.get(999)`.
  4. Model rule: `with pytest.raises(ValidationError): Product(id=1, name="", category="c", price=1.0)`.
  5. Collapse three near-identical model tests into one parametrized body:
     `@pytest.mark.parametrize("field,value,msg", [("name","","at least 1 character"),
     ("price",-1,"greater than or equal to 0"),("id",0,"greater than or equal to 1")])`;
     show the three generated test ids under `-v`.
- **Lab fold.** `test_catalog.py`: duplicate-id and missing-id raise `CatalogError`.
  `test_models.py`: the `Field`-constraint table (`test_rejects_invalid`) via parametrize.

#### M07 §3 — Fixtures (`@pytest.fixture`, `conftest.py`) + `tmp_path`
- **Concept & why.** Repeated setup becomes a `@pytest.fixture`; a test *asks* for it by
  naming it as a parameter, and pytest hands each test its **own fresh copy** (isolation).
  Shared fixtures live in `conftest.py` (auto-discovered, no import). pytest ships built-in
  fixtures too — `tmp_path` gives a real temporary directory, which is the *correct* way to
  test file I/O.
- **Code-along beats.**
  1. Refactor a repeated `ProductCatalog([...])` into a `seeded_catalog` fixture; two tests
     request it; mutate in one and show the other is unaffected (fresh per test).
  2. Move `sample_product` / `seeded_catalog` into `conftest.py`; note tests use them with
     no import.
  3. `tmp_path` round-trip: `save_json(cat, tmp_path/"c.json")` then
     `loaded = load_json(tmp_path/"c.json")`; `assert loaded.list_all() == cat.list_all()`.
  4. Explain why **not** mock here: the temp file is cheap and the point is to verify real
     serialization — mocking `write_text` would assert nothing. (Sets up M08's contrast.)
- **Lab fold.** Adopt the provided `conftest.py` fixtures across `test_catalog.py`; add
  `test_storage.py` with the `tmp_path` save→load round-trip.

### M08 — Mocking *(when to run the real thing, when to fake it)*

Frame: M07 tested logic you can run for real. Day 1 also gave you a FastAPI **server**, and
M08 adds a tiny network **client**. This module teaches the central *judgment* of mocking
through their contrast: the server + catalog are cheap and in-process, so you test them
**for real** (`TestClient`, §1); the client's dependency is the **network**, which you can't
run in a unit test, so you **mock** it (§2–3).

#### M08 §1 — Test the server for real: `TestClient`
- **Concept & why.** FastAPI's `TestClient` runs your `app` in-process — real routes, real
  `ProductCatalog`, no network, no uvicorn. Because the catalog is cheap and deterministic,
  you do **not** mock it; the real thing gives a truer test. This is the "don't mock what's
  cheap to run" half of the judgment — and it's what finally exercises `server.py` (so M09's
  coverage sees it).
- **Code-along beats.**
  1. `from fastapi.testclient import TestClient` · `from catalog.server import app` ·
     `client = TestClient(app)`.
  2. `r = client.get("/products"); assert r.status_code == 200; assert len(r.json()) == 5`
     (the five seeded products from `storage.seed_products`).
  3. Round-trip: `client.post("/products", json={...})` → 201; then
     `client.get("/products/{id}")` returns the same product.
  4. Error mapping: `client.get("/products/999").status_code == 404`; a duplicate POST → 409.
  5. Note there is **no `@patch` anywhere** — app + catalog are real. Hold this against §2.
- **Test isolation (must-handle).** `server.py` holds `catalog` as a **module global**
  seeded with 5 products, so a `POST` in one test leaks into the next — an order-dependent
  `len == 5` can see 6. Add a fixture that **reseeds** the global before each test (e.g.
  `monkeypatch.setattr(server, "catalog", ProductCatalog(list(seed_products())))`, or an
  autouse reset fixture). This is also a nice callback to M07's fixtures lesson.
- **Lab fold.** `test_server.py` — a reset fixture, then health, list (seed count = 5),
  create→get round-trip, 404 on missing, 409 on duplicate.

#### M08 §2 — Mock the network client: `patch` / `MagicMock`, `return_value`
- **Concept & why.** `client.get_products()` calls `requests.get` — the **network**. A unit
  test must not depend on a live server, so replace the call with a fake you control. This is
  the "must mock — the dependency is external" half of the judgment, in direct contrast to
  §1. `unittest.mock.patch("catalog.client.requests.get")` swaps it; `.return_value` is a
  fake response whose `.json()` returns product dicts.
- **Code-along beats.**
  1. Motivate: `get_products()` with no server → `ConnectionError`; the *client* must be
     testable in isolation (the *server* was §1's job).
  2. `with patch("catalog.client.requests.get") as mock_get:`
     `mock_get.return_value.json.return_value = [ {one product dict} ]`;
     `mock_get.return_value.raise_for_status.return_value = None`; call `get_products()`;
     `assert isinstance(result[0], Product)`.
  3. **Patch target, taught honestly.** Patch `catalog.client.requests.get` — the robust
     habit is "patch the name where the code looks it up." Note `requests.get` *also* works
     here because `client.py` did `import requests` (same module object); the distinction
     only bites with `from requests import get`. Teach the robust form and explain why both
     work here — don't over-claim.
  4. What a `MagicMock` is (auto-attributes, callable, records calls); `spec=requests.Response`
     on the fake so a typo'd attribute fails loudly.
- **Lab fold.** `test_client.py::test_get_products_returns_typed_products` — a faked 200 →
  `list[Product]`, no server.

#### M08 §3 — Verify the call + simulate failure: `assert_called_once_with`, `side_effect`
- **Concept & why.** A mock records *how* it was called and can be made to fail on demand.
  Two moves: (a) assert the right call was made; (b) drive the error path. The *meaningful*
  failure test is **not** "the network raised" (with no handling that just re-raises — a
  tautology) but **"the server returned a bad row"** → `Product.model_validate` rejects it,
  so `get_products` raises `ValidationError`. That is real boundary-validation behavior and
  reinforces M04. The `ConnectionError` case stays only to demonstrate the `side_effect`
  mechanic.
- **Code-along beats.**
  1. `mock_get.assert_called_once_with("http://x/products", timeout=5)`; inspect
     `mock_get.call_args` (`.args`, `.kwargs`) to show the URL was built from `base_url`.
  2. `side_effect` mechanic: `mock_get.side_effect = requests.ConnectionError("down")` →
     `with pytest.raises(requests.ConnectionError): get_products()`. Contrast `side_effect`
     (raise / sequence) with `return_value` (one fixed value).
  3. The **valuable** error test: `mock_get.return_value.json.return_value = [ {bad row,
     e.g. price: -5} ]` → `with pytest.raises(ValidationError): get_products()`. Garbage from
     the server never leaks out as a `Product` — the client validates at the boundary.
- **Lab fold.** `test_client.py` — `test_hits_right_url`, `test_propagates_network_error`
  (`side_effect`), `test_rejects_malformed_response` (`ValidationError`).

> **Honest caveat, stated in §2's narrative:** you mock the *client* because its dependency
> is the network; you did **not** mock the *server* (§1) because its dependency (the catalog)
> is cheap and real. That contrast — fake the uncontrollable edge, run the cheap thing for
> real — is exactly the judgment Day 4 reuses when it mocks the LLM
> (`CatalogAgent(llm_client=...)`).

### M09 — Coverage *(make the tests visible & automatic)*

Domain-agnostic; substantively the current M09, kept to two sections.

#### M09 §1 — Coverage (`pytest-cov`, term-missing, HTML)
- **Concept & why.** A green suite doesn't tell you *what it didn't test*. Coverage measures
  which lines (and branches) ran. `pytest --cov=catalog --cov-report=term-missing`; the
  *Missing* column names the unreached lines; `branch = true` catches half-taken `if`s.
- **Code-along beats.**
  1. Run coverage on the M07+M08 suite; read the summary table and the *Missing* column.
  2. Point at a real uncovered line (e.g. an error branch in `ProductCatalog`); write the
     one test that reaches it; rerun and watch the % rise.
  3. Generate `--html` (`--self-contained-html`) and open the report.
- **Lab fold.** Configure `[tool.coverage.run] source = ["catalog"]`, `branch = true`;
  reach the target coverage on `catalog`.

#### M09 §2 — CI (GitHub Actions, version matrix)
- **Concept & why.** Tests are only trustworthy if they run automatically, everywhere. A
  GitHub Actions workflow runs the suite on push/PR across Python versions.
- **Code-along beats.**
  1. Walk a minimal `.github/workflows/tests.yml`: triggers
     (`push` · `pull_request` · `workflow_dispatch`), the `python-version` matrix, install
     (`pip install -e ".[dev]"`), the pytest+coverage command, upload the HTML report.
  2. Explain `fail-fast: false` (don't cancel other versions) and `if: always()` on the
     upload (you need the report most when the run failed).
- **Lab fold.** Fill every `# TODO` in `tests.yml`. Stretch: push for a green badge; add
  `--cov-fail-under=80` to gate CI.

---

## 6. Artifacts per module (repo convention)

Each module keeps its parallel set:
- `slides-<module>.md` (Marp) + rendered `.html`
- `codealong-<module>.ipynb` — live-coding the section beats above
- `lab/README.md` — the handout (contract: *start with X → end with Y → run this command*)
- `lab/starter/*` — stub files with `# TODO`s

Capstone graders `capstone-project/*/tests/test_lab07.py` / `test_lab08.py` /
`test_lab09.py` remain the students' scoreboard (skip-until-built via
`pytest.importorskip`). Each lab README ends on the grader command whose green output is shown.

## 7. Downstream / consistency impact

- **Source-of-truth chain** (`outline_v4.2-24hrs.md` → slides → lab README → starter/solution)
  must be updated together for Day 3. The outline's M08 description ("APIClient mocking /
  retry") changes to "mocking a network call"; `@parametrize` is listed under M07.
- **`capstone-project/solution/`** — `get_products` is **added alongside** the existing
  `APIClient` in `catalog/client.py` (the `APIClient` stays — Day-2 `import_csv.py` and Day-4
  `agent.py` import it; overwriting it would break Day 4). Solution `tests/` **gains**
  `test_server.py` (TestClient) and `get_products` tests; the existing `APIClient`/agent tests
  are left intact. The M05 client is simply no longer part of the *Day-3* chain — it is not
  removed.
- **Day 4** inherits an already-tested core and gains the *authentic* mock target (the LLM).
  M08's mock mechanic transfers directly to `CatalogAgent(llm_client=...)`.
- **Day-1 catalog code is untouched** — no Notifier, no injected collaborator added to
  `ProductCatalog`. The only new file is `catalog/client.py`.
- **`requests` stays a declared dependency.** Even though the M05 client is dropped,
  `catalog/client.py` imports `requests`, so the Day-3 `pyproject.toml` and the
  `day-3-start` checkpoint must list `requests`. FastAPI's `TestClient` additionally needs
  `httpx` (used by `starlette`'s test client) in the dev dependencies.
- **Folder rename.** `modules/m08-parametrize-mock` → `modules/m08-mocking` (parametrize
  moved to M07 §2; M08 is now `TestClient` + mocking). Rename the slide/codealong filenames
  and update the outline reference to match.

## 8. Non-goals / out of scope

- No retry / resilience engine, no typed multi-method HTTP client, no `APIError` taxonomy.
- No CSV-import (M06) dependency in any Day-3 lab.
- No mocking of the filesystem or of the catalog's own internal objects (anti-pattern here).
- No change to Days 1–2 module content beyond what the source-of-truth chain requires for
  consistency (e.g. an outline line).
- Day-4 rewrite itself is out of scope (tracked separately in `day4_change_plan.md`).

## 9. Success criteria

- M07/M08/M09 labs run green depending only on M01–M04 artifacts plus the ~4-line
  `catalog/client.py`.
- M07 uses no mocks; M08 §1 tests the server for real via `TestClient` while §2–3 mock the
  network client; M09 reports coverage (server now exercised, so `--cov-fail-under=80` is
  reachable) and defines a CI workflow.
- Each module has 2–3 sections, each articulated as concept → code-along beats → lab fold.
- The three lab READMEs each end on a grader command with shown expected output.
