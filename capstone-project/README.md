# The project

One Python project, built across 4 days. Three folders, three jobs — all the **same project at different points in time**:

| Folder | What it is | What you do with it |
|---|---|---|
| `start-here/` | The Day-1 baseline: empty `catalog/` package + the `tests/` scoreboard | **Copy it once, build here all week** |
| `checkpoints/` | The project frozen at the start of Days 2 / 3 / 4 | **Fell behind? Reset from here** to rejoin |
| `solution/` | The finished reference answer (Day-4 end state) | **Peek when stuck — don't edit** |

All you need installed is **`uv`** (`brew install uv` · `winget install astral-sh.uv` · or the standalone installer). No manual venv, no activation.

## Start (Day 1)
```bash
cp -r start-here my-catalog && cd my-catalog     # run from capstone-project/
```
**Labs 1–2 are pure stdlib — nothing to install.** Run the code with `python`, the graders with `uvx` (fetches pytest once, no venv):
```bash
python -m catalog.cli list                  # your code
uvx pytest tests/test_lab01.py -v           # that lab's grader
```
**Lab 3 adds FastAPI** — the first real dependency. From here on, sync once and use `uv run`:
```bash
uv sync                                     # creates .venv + installs deps (incl. dev)
uv run uvicorn catalog.server:app --reload
uv run pytest -q                            # all remaining specs SKIP — the scoreboard
```
Per lab: copy the lab's `starter/` files into `catalog/`, fill the `# TODO`s, run that lab's check.

## Fell behind?
```bash
cd my-catalog
rm -rf catalog data .github          # keep tests/ — your lab graders live there
cp -r ../checkpoints/day-N-start/. .
uv sync                              # (Day 3+ baselines; Day-2 baseline is stdlib-only)
```
