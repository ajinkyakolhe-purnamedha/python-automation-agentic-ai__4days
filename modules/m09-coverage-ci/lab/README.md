# Lab 9 — Coverage + CI

**~45 min · Day 3 · Module 9 (Coverage & CI)** · concepts → `../codealong-m09-coverage-ci.ipynb`

## Goal
Make your Lab 7–8 suite **visible** and **automatic**: measure coverage (and read the
*Missing* column), then write a GitHub Actions workflow that runs the tests across
Python 3.10 / 3.11 / 3.12. Done when `uv run pytest --cov --cov-report=term-missing -q`
prints a coverage table and your `tests.yml` has no `# TODO` left.

## You start with
Lab 8 green — `tests/test_models.py`, `test_catalog.py`, `test_storage.py`,
`test_server.py`, `test_client.py` all passing.

## Get the starter files
```bash
# run from my-catalog/
cp -r ../../modules/m09-coverage-ci/lab/starter/.github .
cat ../../modules/m09-coverage-ci/lab/starter/pyproject-additions.toml   # blocks to paste
```
| File | What |
|---|---|
| `pyproject-additions.toml` | the `[tool.coverage.run]` + marker config to fill and paste into your `pyproject.toml` |
| `.github/workflows/tests.yml` | CI workflow skeleton — fill every `# TODO` |

## What to implement
- **`pyproject.toml`** — point coverage at `source = ["catalog"]`, `branch = true`, and register the `integration` marker (paste the two blocks from `pyproject-additions.toml` and fill their TODOs).
- **`tests.yml`** — the triggers (`push` · `pull_request` · `workflow_dispatch`); the `python-version` matrix (`"3.10"`, `"3.11"`, `"3.12"`); install (`pip install -e ".[dev]"`); the pytest+coverage command; and the artifact upload.

## Steps
1. Paste the `pyproject-additions.toml` blocks into your `pyproject.toml` and fill their TODOs; copy `.github/` into `my-catalog/`.
2. Measure coverage locally and read the *Missing* column:
   ```bash
   uv run pytest --cov --cov-report=term-missing --html=report.html --self-contained-html
   open report.html        # xdg-open on Linux · start on Windows
   ```
3. Fill every `# TODO` in `.github/workflows/tests.yml`.

## Read the Missing column
Your Day-3 suite is green, but green ≠ fully covered. Over the catalog you'll see roughly:

```
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
catalog/models.py       74      0     12      0   100%
catalog/server.py       38      8      0      0    79%   46-49, 54-57
catalog/storage.py      43     18      6      0    55%   39-47, 51-59
----------------------------------------------------------------
TOTAL                  155     26     18      0    83%
```

That 83% is the lesson, not a failure: the *Missing* column points at real gaps — the
server's `PATCH`/`DELETE` routes (lines 46–57) and `storage.py`'s CSV helpers (39–59) that
your Lab 7–8 tests never exercised. Coverage found the untested paths that "all green"
hid. (Your exact numbers depend on which tests you wrote.)

## Watch out
- `fail-fast: false` — otherwise one failing Python version cancels the others, and you lose the signal.
- Upload the report with `if: always()` — the failing run is exactly when you need the report.
- `--strict-markers` turns a typo'd marker into an error, not a silent skip — register `integration` so it's known.

## Make it pass
```bash
uv run pytest --cov --cov-report=term-missing -q
```
```
...
TOTAL   155   26   18   0   83%
32 passed
```

## Stretch
- Push to your own GitHub for a green badge on the pull request.
- Add `--cov-fail-under=80` to gate CI — a new untested feature that drops coverage below 80% now fails the build.
- Write the tests that cover the *Missing* lines (the `PATCH`/`DELETE` routes) and watch the number climb.

---

**End of Day 3.** Your catalog is now **tested** (M7), with the network edge **mocked**
(M8), and the whole suite **measured and automated** (M9).
