---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 2 · Automate It — Validation & a Typed Client"
footer: "Acuity Training · Day 2 of 4"
---

<!-- _class: title -->

# Module 6
## Data-Driven Automation
**3 sections · ~50 min** — concept first, then build it in Python
1 The pattern · 2 Validating the source · 3 Drive the API + report
---
# The capstone: a file becomes API actions

M2 gave us **files**, M4 gave us **validation**, M5 gave us the **client**. M6 wires them into **one workflow** — a data file in, API calls out, a report to show for it.

```text
products.csv  →  validate each row  →  POST via APIClient  →  import_report.json
```

This *is* what "automate API workflows" means on the job.
---
<!-- _class: section -->

# Section 1 · The pattern
## **Data-driven** = the data lives *outside* the code; the logic stays *fixed*.
## Write the workflow once — run it over 1 row or 10,000. That's the whole idea.
---
# 1.1 · What "data-driven" means

The **logic is fixed**; the **data lives outside** it — a file, a spreadsheet, a table. You don't edit code to add a record; you add a row.

```text
code (fixed):   for each record →  validate  →  send  →  record the result
data (varies):  products.csv  →  10 rows today, 10,000 tomorrow — same code
```
---
# 1.2 · Why it's the automation workhorse

- **Scale** — one row or ten thousand, the code is identical.
- **Separation** — ops hands you a CSV; no developer needed to "add the data".
- **One place to maintain** — the workflow is written once.

QA engineers know this as **data-driven testing**: one test, many input rows.
---
# 1.3 · The shape — source → process → report

Every data-driven job is the same three parts:

```text
SOURCE          PROCESS (per record)        SINK
a CSV / JSON  →  validate → act (API)   →   a report of what happened
```

The **report is the deliverable** — the input file is just the input.

<div class="code-along">▶ Code-along now → notebook Section 1 — the shape, in code: one loop over records</div>
---
<!-- _class: section -->

# Section 2 · Validating the source
## A CSV is **all strings**; JSON has types but no **shape or limits**.
## One model handles both — bad records raise, good ones come back typed.
---
# 2.1 · Read the CSV — every cell is a string

`csv.DictReader` gives one dict per row, keyed by the header — but every value is **text**, even numbers and booleans.

```python
for row in csv.DictReader(open("products.csv")):
    row    # {'id': '1', 'price': '499.0', 'in_stock': 'true'} — all str
```
---
# 2.2 · Validate = coerce + check, in one step

Hand the string-dict straight to your Pydantic model. It **coerces** `"499.0"`→float, `"true"`→bool, **and** enforces the constraints — a bad row raises `ValidationError`.

```python
Product.model_validate({"id":"1","name":"Cable","category":"Elec","price":"499.0"})  # typed ✓
Product.model_validate({"id":"1","name":"Cable","category":"Elec","price":"-5"})     # ValidationError
```

---
# 2.3 · Same model, whatever the source

Swap the CSV for a JSON file and **nothing changes** — `model_validate` is still the one gate. Only the *reason* a record fails shifts:

```python
Product.model_validate(csv_row)              # dict of strings  → coerced + checked
Product.model_validate(json.loads(raw))      # real types       → still checked
```

| Source | Gives you | Still can't promise |
|---|---|---|
| **CSV** | text, always | any type at all — `"abc"` as a price |
| **JSON** | real types (`499.0` *is* a float) | the right **shape or limits** |

```json
{"id": 1, "name": "", "price": -5}    // valid JSON, invalid product
```

**That's the payoff:** the model is the contract, so the source is an implementation detail. One gate, many sources.

<div class="code-along">▶ Code-along now → notebook Section 2 — DictReader → model_validate each row; then the same model on JSON</div>
---
<!-- _class: section -->

# Section 3 · Drive the API + report
## One bad row must **not** kill the batch.
## Keep the two failure kinds apart, and hand back a report of exactly what happened.
---
# 3.1 · A row fails in two different ways

Keep them apart — they need different fixes, and collapsing them lies to the operator.

| Failure | Where | Fix |
|---|---|---|
| **bad data** | never reaches the API (`ValidationError`) | fix the row |
| **server says no** | well-formed, rejected (409 duplicate) | fix the conflict |
---
# 3.2 · The loop — validate, send, bucket

`try` each step; on failure, drop the row into the right bucket and `continue`. One bad row never stops the batch.

```python
for n, row in enumerate(rows):
    try:    product = Product.model_validate(row)
    except ValidationError as e: bad_data.append({"row": n, "errors": e.errors()}); continue
    try:    client.create_product(product); created.append(product.id)
    except APIError as e:        rejected.append({"row": n, "status": e.status_code})
```
---
# 3.3 · The report is the product

The CSV/JSON was the input; this is what you hand back — and what Day 3 tests.

```python
report = {"created": created, "validation_errors": bad_data, "api_errors": rejected}
json.dump(report, open("import_report.json", "w"), indent=2)
```

<div class="code-along">▶ Code-along now → notebook Section 3 — the bulk-import loop + write import_report.json</div>
---
<!-- _class: lab -->

# 🧪 Lab 6 — Bulk-Import Workflow

**~60 min** · open `modules/m06-data-driven-csv/lab/README.md`

You'll build (on `Product`):
- `data/products.csv` with some deliberately bad rows
- `catalog/import_csv.py` — read → validate → `POST` via `APIClient` → `import_report.json`
- the report: `{created, validation_errors, api_errors}`

End of Day 2 → your repo matches `checkpoints/day-3-start/`.
