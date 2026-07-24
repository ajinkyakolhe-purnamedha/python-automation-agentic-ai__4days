# Python Testing Masterclass — 10 Explorable Notebooks

Ten runnable Jupyter notebooks that teach production-grade Python testing. Every notebook uses the
**`%%writefile` → `!pytest`** pattern: a markdown cell explains the concept, a code cell writes real
`.py` files to disk, and a shell cell runs the tool and shows you the output — exactly how you'd test
a real project.

## Curriculum

| # | Notebook | You learn |
|---|----------|-----------|
| 01 | Pytest Core & Assertions | discovery, naming, plain-`assert` introspection, `-k` |
| 02 | Fixtures & State | `@pytest.fixture`, `yield` teardown, per-test isolation |
| 03 | Parametrization | `@pytest.mark.parametrize`, edge-case matrices, `ids=` |
| 04 | Mocking & Isolation | `mocker.patch`, faking HTTP, no real network |
| 05 | Determinism & Time | `time_machine.travel` to freeze the clock |
| 06 | Errors & Logs | `pytest.raises`, `caplog`, `capsys` |
| 07 | Asynchronous Testing | `pytest-asyncio`, `asyncio_mode=auto`, `asyncio.gather` |
| 08 | Integration & Snapshots | FastAPI `TestClient`, `syrupy` snapshots |
| 09 | E2E Testing (Playwright) | headless Chromium, the `page` fixture, `expect()` |
| 10 | Test Quality & CI | coverage vs. mutation testing (`mutmut`), killing survivors |

## Setup

```bash
python3.12 -m venv .venv          # Python 3.12 recommended (3.14 is too new for some tools)
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/python -m ipykernel install --user --name testing-masterclass \
    --display-name "Testing Masterclass (3.12)"
```

Then open the notebooks in JupyterLab (`.venv/bin/jupyter lab`) and select the
**"Testing Masterclass (3.12)"** kernel. Run the cells top to bottom.

> **Note:** The first cell of every notebook prepends the kernel's `bin/` to `PATH` so the `!pytest` /
> `!mutmut` / `!playwright` shell cells resolve to *this* environment's tools rather than any other
> Python on your machine.

## Files

- `01`–`10` `*.ipynb` — the lessons (pre-executed, with outputs saved).
- `requirements.txt` — pinned toolchain.
- `nbNN_*.py`, `test_nbNN.py`, `nb09_page.html`, `nb10/`, `__snapshots__/` — demo artifacts the
  notebooks generate when run. Safe to delete; they're recreated by the `%%writefile` cells.
