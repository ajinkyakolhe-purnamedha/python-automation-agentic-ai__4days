# Day 3 Combined Lab — Test the Catalog (one self-contained package)

**~60 min · Day 3 recap · pytest + mocking + coverage/CI in one folder**

Everything you saw across Modules 7–9, in one runnable package. Nothing from
Days 1–2 is required: the working **catalog** (models, storage, FastAPI server,
a tiny `get_products` client) ships inside this folder, already tested. You
**run it, read it, and tweak it** — the suite is green the moment you copy it.

## Start here
```bash
cp -r modules/day3-combined-lab ~/day3-lab   # or work in place
cd ~/day3-lab
uv sync                                       # FastAPI, pytest, pytest-cov, ...
uv run pytest -q                              # 13 passed
```

## What's inside
| Path | What |
|---|---|
| `catalog/` | the working code under test (provided — don't edit) |
| `tests/test_catalog.py` | Topic 1 — pytest basics (asserts, `pytest.raises`, `@parametrize`, `tmp_path`) |
| `tests/test_client.py` | Topic 2 — mocking (`TestClient` for real + mock the network) |
| `tests/conftest.py` | provided fixtures (`sample_product`, `seeded_catalog`) |
| `pyproject.toml` | deps + coverage config + the `integration` marker |
| `.github/workflows/tests.yml` | Topic 3 — CI across Python 3.10 / 3.11 / 3.12 |

---

## Topic 1 · pytest basics — `tests/test_catalog.py`

**Run it**
```bash
uv run pytest tests/test_catalog.py -v
```
**Read it** — a test is just a function named `test_*` that makes an `assert`;
pytest discovers it and, on failure, shows *both sides*. You have the three
moves: `pytest.raises` for error paths, `@pytest.mark.parametrize` to fan one
body over many cases, and `tmp_path` for real file I/O (never mock the
filesystem — the round-trip *is* the point).

**Try it**
- Change `== {"Cable"}` to `== {"Speaker"}` and rerun — read pytest's
  introspected diff, then change it back.
- Add a 4th `@parametrize` row: `("category", "")`. It passes — same rule
  (`min_length=1`), one more field.

## Topic 2 · mocking — `tests/test_client.py`

**Run it**
```bash
uv run pytest tests/test_client.py -v
```
**Read it** — the judgment of the whole day: the FastAPI app is cheap and
in-process, so `TestClient` runs it **for real** (§A). But `get_products` calls
`requests.get` — the one thing a unit test can't do — so you **mock** it (§B):
fake the response, assert the exact call (`assert_called_once_with(...,
timeout=5)`), and use `side_effect` to force a failure. **Mock the
uncontrollable edge; run the cheap thing for real.** *(Day 4 reuses this exact
pattern to mock the LLM.)*

**Try it**
- In `_ok_response`, delete `spec=requests.Response` from the `MagicMock(...)`.
  A mock without a spec says *yes to everything* — a typo'd attribute would
  pass silently. Restore it and the fake fails loudly. That's why it's there.

## Topic 3 · coverage & CI

**Run it**
```bash
uv run pytest --cov --cov-report=term-missing -q
```
**Read it** — green tests ≠ tested code. Coverage measures the whole
`catalog/` package, not just what these 13 tests exercise, and the number says
so:
```
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
catalog/__init__.py         1      0      0      0   100%
catalog/cli.py             60     60      6      0     0%   11-105
catalog/client.py          56     32      4      0    40%   ...
catalog/decorators.py      26     15      4      0    37%   ...
catalog/import_csv.py      52     52      4      0     0%   17-101
catalog/models.py          74     20     12      2    70%   ...
catalog/server.py          38     14      0      0    63%   37-41, 46-49, 54-57, 62
catalog/storage.py         43     20      6      1    49%   25-26, 39-47, 51-59
-------------------------------------------------------------------
TOTAL                     350    213     36      3    37%
```
That 37% is not one gap, it's several, and the **Missing** column names each
one: `cli.py` and `import_csv.py` sit at 0% because this trimmed suite never
even imports them; `client.py`'s `APIClient` class is untouched (only the
module-level `get_products` function is tested); and even inside the modules
we *do* test, `server.py`'s `PATCH`/`DELETE` routes and `storage.py`'s CSV
helpers are skipped. Coverage found every one of those gaps that "all green"
hid — it's a **floor, not a target**, and the Missing column is your next test
to write. Then open `.github/workflows/tests.yml`: CI runs this same command
on every push across Python 3.10 / 3.11 / 3.12, so a red test can't hide.

**Try it**
- Open `.github/workflows/tests.yml` and find the `matrix` — three Python
  versions, `fail-fast: false` so one version's failure doesn't cancel the rest.

---

## Done when
```bash
uv run pytest -q
```
```
.............
13 passed in 0.18s
```
And coverage prints a table like:
```
TOTAL                     350    213     36      3    37%
```
That 37% is the lesson, not a failure — the *Missing* column is your next
test to write.
