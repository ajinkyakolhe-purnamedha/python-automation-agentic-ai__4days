---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 3 · Test It — pytest, Mocking, Coverage & CI"
footer: "Acuity Training · Day 3 of 4"
---

<!-- _class: title -->

# Module 7
## Unit Testing
**3 sections · ~40 min** — assert → raises + parametrize → fixtures + tmp_path
1 Test functions + assert · 2 pytest.raises + @parametrize · 3 Fixtures + tmp_path
---
# Real logic, real objects — no mocks here

Everything in M7 tests **pure logic with real objects**: real `Product`s, a real `ProductCatalog`, a real temp file. Nothing here talks to the network or a server.

```text
M7 today:  real Product · real ProductCatalog · real temp file    — no fakes needed
M8 later:  a network call you can't run in a unit test           — that's where mocks earn their keep
```

**No mocks here — mocks are M08's edge.** You only reach for a mock at a boundary you can't run for real; today, everything is cheap enough to run for real.
---
<!-- _class: section -->

# Section 1 · Test functions + `assert`
## A test is just a function named `test_*` that makes an `assert`.
## pytest discovers it, runs it, and on failure shows **both sides**.
---
# 1.1 · The smallest possible test

No special API, no base class — a function named `test_*`, a plain `assert`.

```python
def test_math():
    assert 1 + 1 == 2
```

```bash
$ pytest -q
.                                                                       [100%]
1 passed in 0.00s
```
---
# 1.2 · Break it — read the introspected diff

Change the assert to something false and rerun. pytest doesn't just say "failed" — it shows **both sides** of the comparison it rewrote for you.

```python
def test_math():
    assert 1 + 1 == 3
```

```text
    def test_math():
>       assert 1 + 1 == 3
E       assert 2 == 3
```

**This** is why pytest over `unittest` — no `assertEqual(a, b)` ceremony, just `assert`, and pytest tells you exactly what didn't match.
---
# 1.3 · A real object: `Product`

```python
from catalog.models import Product

p = Product(id=1, name="Cable", category="Electronics", price=499.0)
assert p.price == 499.0
assert p.tags == []          # the model's default
```

Same idea as `1 + 1 == 2` — you're just asserting on a richer object.
---
# 1.4 · A query: seed a `ProductCatalog`

```python
from catalog.models import ProductCatalog

cat = ProductCatalog([
    Product(id=1, name="Cable", category="Electronics", price=499.0),
    Product(id=2, name="Mat", category="Fitness", price=1299.0),
])
assert len(cat.list_all()) == 2
```

Arrange the catalog, then assert on what it returns — no server, no mock, just the object.
---
# 1.5 · Discovery and selection

pytest finds files named `test_*.py` and functions named `test_*` — **no registration**. Select a subset with `-k`, see names with `-v`.

```bash
pytest -q                     # run everything, dots only
pytest -k search               # run only tests whose name contains "search"
pytest -v                      # print each test's name + PASSED/FAILED
```

<div class="code-along">▶ Code-along now → notebook §1 — write test_math, break it, then assert on a real Product and a seeded ProductCatalog</div>
---
<!-- _class: section -->

# Section 2 · `pytest.raises` + `@parametrize`
## Good code fails loudly; tests must assert the **failure**, not just the happy path.
## Many cases, one body → `@pytest.mark.parametrize`.
---
# 2.1 · Assert that it raises

`with pytest.raises(Exc, match="..."):` passes **only if** that exception fires inside the block.

```python
import pytest
from catalog.models import CatalogError, Product

def test_add_rejects_duplicate_id(seeded_catalog):
    dup = Product(id=10, name="dup", category="x", price=1.0)
    with pytest.raises(CatalogError, match="already exists"):
        seeded_catalog.add(dup)
```
---
# 2.2 · Use the narrowest exception

`pytest.raises(Exception)` would also pass if your code raised the **wrong** thing — a real bug in your code now looks like a green test.

```python
# ✗ too broad — a TypeError from a real bug would also satisfy this
with pytest.raises(Exception):
    seeded_catalog.add(dup)

# ✓ narrow — only CatalogError satisfies it; anything else still fails the test
with pytest.raises(CatalogError, match="already exists"):
    seeded_catalog.add(dup)
```
---
# 2.3 · A second error path: missing id

```python
def test_get_missing_raises(seeded_catalog):
    with pytest.raises(CatalogError, match="not found"):
        seeded_catalog.get(999)
```

Same shape as 2.1 — a different rule, a different message to match.
---
# 2.4 · Model rules raise `ValidationError`

Pydantic's own `Field` constraints are testable the same way — they just raise a different exception.

```python
from pydantic import ValidationError
from catalog.models import Product

def test_empty_name_rejected():
    with pytest.raises(ValidationError):
        Product(id=1, name="", category="c", price=1.0)
```
---
# 2.5 · Collapse near-identical tests with `@parametrize`

Three tests that only differ by one bad field → **one** test body, a table of cases. A *used* decorator — you never write one, only apply it.

```python
@pytest.mark.parametrize("field,value,msg", [
    ("name",  "", "at least 1 character"),
    ("price", -1, "greater than or equal to 0"),
    ("id",     0, "greater than or equal to 1"),
])
def test_rejects_invalid(field, value, msg):
    base = dict(id=1, name="X", category="c", price=10.0)
    base[field] = value
    with pytest.raises(ValidationError) as exc:
        Product(**base)
    assert msg in str(exc.value)
```

```bash
$ pytest -v
test_rejects_invalid[name--at least 1 character] PASSED
test_rejects_invalid[price--1-greater than or equal to 0] PASSED
test_rejects_invalid[id-0-greater than or equal to 1] PASSED
```

<div class="code-along">▶ Code-along now → notebook §2 — pytest.raises on CatalogError and ValidationError, then one parametrized test replacing three</div>
---
<!-- _class: section -->

# Section 3 · Fixtures + `tmp_path`
## Repeated setup becomes a `@pytest.fixture` — each test gets its **own fresh copy**.
## `tmp_path` is pytest's built-in for real file I/O.
---
# 3.1 · From repeated setup to a fixture

Building the same `ProductCatalog([...])` in every test is copy-paste waiting to drift. A fixture builds it **once per test**, fresh.

```python
import pytest
from catalog.models import Product, ProductCatalog

@pytest.fixture
def seeded_catalog():
    return ProductCatalog([
        Product(id=10, name="Cable", category="Electronics", price=499.0),
        Product(id=11, name="Speaker", category="Electronics", price=2499.0),
    ])
```

A test **asks** for it by naming it as a parameter — no import, no manual call.
---
# 3.2 · Fresh per test — isolation, proven

```python
def test_mutate_one(seeded_catalog):
    seeded_catalog.delete(10)
    assert len(seeded_catalog) == 1

def test_other_is_unaffected(seeded_catalog):
    assert len(seeded_catalog) == 2   # the delete above never happened here
```

Each test got its **own** `seeded_catalog` — pytest reran the fixture function for each one. That's why order never matters.

Shared fixtures move to `conftest.py` — every test file in that folder can ask for them, **no import needed**.
---
# 3.3 · `tmp_path` — a real temp directory, built in

pytest ships fixtures too. `tmp_path` hands your test a fresh, real directory that's cleaned up automatically — the *right* tool for file I/O.

```python
from catalog.storage import save_json, load_json
from catalog.models import Product, ProductCatalog

def test_json_roundtrip(tmp_path):
    cat = ProductCatalog([Product(id=1, name="Cable", category="Electronics", price=499.0)])
    path = tmp_path / "catalog.json"
    save_json(cat, path)
    loaded = load_json(path)
    assert loaded.list_all() == cat.list_all()
```
---
# 3.4 · Why not mock the filesystem

The temp file is **cheap** — creating and reading it costs microseconds. Mocking `Path.write_text`/`read_text` would only prove your code *called* those functions, not that your JSON actually **round-trips**. Run the real thing when the real thing is cheap; that's the whole judgment M8 builds on next.

```text
mock write_text  →  proves: "we called write_text"      — tells you nothing about the JSON
tmp_path (real)  →  proves: "save then load gives back the same catalog" — the actual promise
```

<div class="code-along">▶ Code-along now → notebook §3 — a seeded_catalog fixture, move it to conftest.py, then the tmp_path save→load round-trip</div>
---
<!-- _class: lab -->

# 🧪 Lab 7 — Unit Tests for the Catalog

**~70 min** · open `modules/m07-pytest-basics/lab/README.md`

You'll write (testing your `Product` catalog — no mocks):
- `tests/test_catalog.py` — happy paths + `pytest.raises(CatalogError)`
- `tests/test_models.py` — the `Field`-rule table via `@pytest.mark.parametrize`
- `tests/test_storage.py` — a `tmp_path` save→load round-trip

Run `uv run pytest tests/test_models.py tests/test_catalog.py tests/test_storage.py -q` → **22 passed**.
