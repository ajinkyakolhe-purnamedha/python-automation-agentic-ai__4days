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
rm -rf catalog data              # keep tests/ — your lab graders live there
cp -r ../checkpoints/day-2-start/. .
uv sync                          # every baseline is Lab-3+ , so FastAPI is needed
uv run pytest tests/test_lab03.py -q     # 15 passed — you're caught up
```
`day-2-start/` = the finished **Lab 3**: `@dataclass Product` + `ProductCatalog` + the FastAPI server. Drop it in and you rejoin at the start of Day 2 with a green Lab 3; Labs 1–2 retire (they skip), Labs 4–6 wait.

> Later baselines (`day-3-start/`, `day-4-start/`) land as those days are authored.
