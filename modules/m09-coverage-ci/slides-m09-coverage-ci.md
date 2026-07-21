---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 3 · Test It — pytest, Mocking, Coverage & CI"
footer: "Acuity Training · Day 3 of 4"
---

<!-- _class: title -->

# Module 9
## Coverage, CI & the Quality Gate
**3 sections · ~40 min** — measure → automate → enforce
1 Coverage · 2 CI with GitHub Actions · 3 Make it a gate
---
# You have tests. Two questions left.

M7–M8 gave you a green suite. But:

- **How much** of your code does it actually exercise? *(you don't know)*
- Does it run **without you remembering** to? *(it doesn't)*

M9 answers both — **coverage** (measure) and **CI** (automate) — and turns the suite into a **gate** nothing red can pass.
---
<!-- _class: section -->

# Section 1 · Coverage
## Green tests ≠ tested code.
## Coverage shows what your suite **never touches.**
---
# 1.1 · Green ≠ tested

A suite can pass with whole functions **never called**. "All green" tells you the tests you *wrote* pass — not that the code is *covered*.

```text
20 tests, all green ✓   …but withdraw() and delete() were never run by any of them
```

You can't see that gap by reading pass/fail — you **measure** it.
---
# 1.2 · `pytest-cov` — the %, and the missing lines

`pytest --cov` reports how much of each file ran; `term-missing` names the **exact lines** no test reached.

```bash
pytest --cov=catalog --cov-report=term-missing
# catalog/server.py    79%   Missing: 46-49, 54-57   ← those routes never ran
# catalog/storage.py   55%   Missing: 39-59          ← the CSV helpers, untested
```
---
# 1.3 · Coverage is a floor, not a target

100% means every line **ran** — not that it's **correct** (a line can run and still be wrong). Use it to find the **untested branch that matters**, not to chase a number.

```python
def delete(self, product_id):
    if product_id not in self._items:            # is THIS branch tested? coverage tells you
        raise CatalogError(f"Product id {product_id} not found")
    return self._items.pop(product_id)
```

Aim for the risky paths covered — not 100% for its own sake.
---
<!-- _class: section -->

# Section 2 · CI with GitHub Actions
## A suite you forget to run protects nothing.
## CI runs it on **every push.**
---
# 2.1 · Tests only help if they run

A green suite on *your* laptop helps no one when a teammate pushes a breaking change and never runs it. **CI** runs the suite automatically on every push and pull request — nobody has to remember.
---
# 2.2 · The workflow file

A YAML file in `.github/workflows/` tells GitHub: on a push, set up Python, install, run pytest.

```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5     # this project is uv-based
      - uses: actions/setup-python@v5
      - run: uv sync                     # installs the [dependency-groups] dev tools
      - run: uv run pytest
```
---
# 2.3 · The matrix + the green check

A **matrix** runs the suite across several Python versions at once — catch a 3.10-only break before users do. The result is a ✓ or ✗ **on the pull request itself.**

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```
---
<!-- _class: section -->

# Section 3 · Make it a gate
## Turn "tests exist" into "**red can't merge.**"
## Artifacts, a threshold, a gate.
---
# 3.1 · Reports — artifacts you can open

CI's console scrolls away. Produce **files**: an HTML report (browsable) + JUnit XML (other tools read it), uploaded as build **artifacts**.

```yaml
- run: pytest --cov --html=report.html --junitxml=results.xml
- uses: actions/upload-artifact@v4
  with: { path: report.html }
```
---
# 3.2 · Fail under a threshold

Make coverage a **rule**, not a vibe. `--cov-fail-under` fails the build if coverage drops below the line — so a new untested feature can't sneak in.

```bash
pytest --cov=catalog --cov-fail-under=80     # exit 1 if below 80%
```
---
# 3.3 · The payoff — a quality gate

Require the check to pass before merge, and **red can't reach `main`.** Your suite stopped being "tests that exist" and became a **gate**.

```text
push → CI runs pytest + coverage → ✓ merge allowed   /   ✗ blocked
```

End of Day 3: models, catalog, storage, server + client — **tested, measured, and gated.**

<div class="code-along">▶ Code-along now — run <code>pytest --cov</code> locally, read the workflow file, set a threshold</div>
---
<!-- _class: lab -->

# 🧪 Lab 9 — Reports + GitHub Actions

**~45 min** · open `modules/m09-coverage-ci/lab/README.md`

You'll add (to your repo):
- coverage + HTML report config in `pyproject.toml`
- `.github/workflows/tests.yml` — install, run `pytest` with coverage, upload the report
- push to GitHub → watch the check go **green**

End of Day 3 — your catalog is **tested, measured, and gated.**
