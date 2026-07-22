# M7 Sandbox — a real pytest playground 🧪

A small, **already-runnable** pytest project on the **BankAccount** domain you met in M3.
Its only job is to let you *experiment with real `pytest`* — the thing the code-along notebook
can only simulate.

> This is **not** the code-along and **not** the graded lab.
> - **Code-along** → `../codealong-m07-pytest-basics.ipynb` (guided, run alongside the slides)
> - **Lab** (graded) → `../lab/README.md` (on the `Product` catalog)
> - **This sandbox** → play freely; nothing here is checked.

## Run it

```bash
pytest -v            # from this folder — watch every test go green
```

(No install needed — it's plain stdlib + pytest.)

## What's here

| File | What it holds |
|------|---------------|
| `bank.py` | the code under test — `BankAccount`, `BankCatalog`, `BankError` |
| `conftest.py` | shared fixtures (`account`, `catalog`) — auto-discovered by pytest |
| `test_account.py` | §2 ideas — `assert`, a fixture, first `pytest.raises` |
| `test_catalog.py` | §3 ideas — Arrange-Act-Assert, happy paths, error paths |

## Things to try

1. **Break a test.** Change an expected value (`== 150.0` → `== 151.0`), rerun, and read pytest's
   introspected diff — *this* is why pytest beats a bare `assert`.
2. **Add your own test.** Look for the `# TODO:` prompts in the test files.
3. **Prove fixture isolation.** In one test, mutate `catalog`; in another, assert it's untouched.
   Each test gets its own fresh fixture — order never matters.
4. **Select a subset.** `pytest -k raises -v` runs only the error-path tests.
5. **Add a `tmp_path` test.** Write something to `tmp_path / "x.txt"`, read it back, assert equal.
