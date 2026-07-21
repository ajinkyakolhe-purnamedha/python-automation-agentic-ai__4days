# Lab 7 — Unit Tests for the Catalog

**~70 min · Day 3 · Module 7 (Unit Testing)**

> **Concepts used:** `assert` + pytest discovery, `pytest.raises`, `@pytest.mark.parametrize`, `@pytest.fixture` / `conftest.py`, and the built-in `tmp_path` fixture → `../codealong-m07-pytest-basics.ipynb`.
> **No mocks in this lab.** Everything here is pure logic and real objects — models, the catalog, a real temp file. You only reach for a mock at an external edge, and the first one of those (the network) is M08's job, not this one.

## Goal
Write the catalog's first real test suite: pin the Pydantic **models**' promises, the **`ProductCatalog`** class's behavior (happy paths *and* error paths), and **storage**'s save→load round-trip on a real temp file. Done when
`uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q` → **22 passed**.

## You start with
Your Day-2 folder (`my-catalog/`) — `catalog/models.py` with the Pydantic `Product` / `ProductCatalog` / `CatalogError`, and `catalog/storage.py` with `save_json` / `load_json`. Nothing new to install; this lab is pure logic on code you already have.

## Get the starter tests
```bash
# run from my-catalog/
cp -r ../../modules/m07-pytest-basics/lab/starter/tests .
```

| File | What |
|---|---|
| `tests/conftest.py` | **provided** fixtures (`sample_product`, `seeded_catalog`) — use, don't edit |
| `tests/test_models.py` | stubs to fill — model validation + the `Field`-rule table |
| `tests/test_catalog.py` | stubs to fill — add/get/delete/queries + `pytest.raises` |
| `tests/test_storage.py` | stubs to fill — the `tmp_path` save→load round-trip |

Each stub fails with a `# TODO` + `pytest.fail(...)` until you implement it — that's the plan, not a bug: red until you fill it, green once you do.

## What to implement
Mapped straight onto the three code-along sections:

- **§1 asserts → `test_catalog.py` happy paths.** A brand-new catalog starts empty; `add` + `get` returns what you put in; `search_by_name` / `filter_by_price` / `group_by_category` return the rows you expect. One `assert` per behavior — precise failures beat one test asserting five things.
- **§2 `pytest.raises` + `@parametrize` → `test_catalog.py` error paths and `test_models.py`'s rule table.** Duplicate-id `add` and missing-id `get`/`delete`/`update` all raise `CatalogError` — assert it with `pytest.raises(CatalogError, match="...")`, and use the **narrowest** exception, not `Exception`. Then collapse the model's bad-field cases (`name=""`, `price=-1`, `id=0`) into one `test_rejects_invalid` via `@pytest.mark.parametrize` instead of three near-identical tests.
- **§3 fixtures + `tmp_path` → `test_storage.py`.** `conftest.py`'s `seeded_catalog` fixture is already wired into `test_catalog.py` — ask for it by naming it as a test parameter and you get a fresh 3-product catalog every time. `test_storage.py` is new: `save_json` a catalog to `tmp_path / "catalog.json"`, `load_json` it back, and assert the round-trip is equal. This is a *real* file on disk, not a mock — see Watch out.

## Steps
1. Copy the starter `tests/` into `my-catalog/` (command above) — `tests/__init__.py` is included, keep it.
2. Fill `test_models.py`, replacing each `pytest.fail(...)` with real asserts. Run `uv run pytest tests/test_models.py -q`; watch reds go green.
3. Do the same for `test_catalog.py` — ask for the `seeded_catalog` fixture by naming it as a test parameter (fresh each test).
4. Do the same for `test_storage.py` — use `tmp_path` (built into pytest, no import needed) for a real file, and `save_json`/`load_json` from `catalog.storage`.
5. Run the whole suite: `uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q` → **22 passed**.

## Watch out
- Use the **narrowest** exception in `pytest.raises` (`CatalogError`, not `Exception`) — a bare `Exception` would also swallow real bugs in your code.
- One behavior per test — a precise failure name beats one test asserting five things.
- In `test_storage.py`, use `tmp_path`, never mock the filesystem. The temp file is cheap and the point is to verify *real* serialization — mocking `write_text`/`read_text` would assert nothing about whether your JSON actually round-trips. (Mocks are the right tool for M08's network edge, not this one.)

## Stretch (optional)
- Add a fourth parametrize row to `test_rejects_invalid` for `category=""` — same rule, one more field.
- Write a test for `ProductCatalog.update()` that changes two fields in one `ProductUpdate` and asserts both landed.
- Add a `test_storage.py` case that round-trips an **empty** catalog (`ProductCatalog()`) — does `save_json`/`load_json` handle zero products cleanly?

## Make it pass
```bash
uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q
```
```
......................
22 passed in 0.02s
```
