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
**3 sections · ~50 min** — the map, then one road driven all the way
1 The landscape · 2 Validating the source · 3 Drive the API + report
---
# The capstone: a file becomes API actions

M2 gave us **files**, M4 gave us **validation**, M5 gave us the **client**. M6 wires them into **one workflow** — a data file in, API calls out, a report to show for it.

```text
products.csv  →  validate each row  →  POST via APIClient  →  import_report.json
```

This *is* what "automate API workflows" means on the job.
---
<!-- _class: section -->

# Section 1 · The landscape
## the idea → four directions → chaining → reading a lot → config & secrets
**Why now:** the map before the road. You're about to build **one** of these all the way — it helps to know which one, and what the others would have cost you.
---
# 1.1 · Data-driven — and you'll meet it three times

The **logic is fixed**; the **data lives outside** it. You don't edit code to add a record — **ops adds a row, not a developer.**

```text
code (fixed):   for each record →  validate  →  act  →  record the result
data (varies):  products.csv    →  20 rows today, 10,000 next month — same code
```

That sentence isn't only today. It's a **spiral** you meet twice more this week:

| | the data | drives |
|---|---|---|
| **M6 · today** | `products.csv` | **API calls** |
| **M8 · Day 3** | a table of inputs | **tests** — `@pytest.mark.parametrize` |
| **M12 · Day 4** | `golden_queries.json` | **AI evals** |

Same sentence, three targets. QA already knows it as **data-driven testing**.
---
# 1.2 · Four directions, one loop

Every one of these is `source → process → sink`. **Only the ends change:**

```text
file → API       import / ingest         ← TODAY, and the lab
API → file/DB    export, reporting       ← needs pagination   (1.4)
API → API        sync, migration         ← needs chaining     (1.3)
config → code    declarative behaviour   ← env & secrets      (1.5)
```

We drive the **first one all the way** — read, validate, send, report. The other three are the *same loop* with a different source and sink. The next three slides are the map, so you know what you're **not** building today — and what it would take.

<div class="code-along">▶ Code-along now → notebook Section 1 — the shape, in code: one loop over records</div>
---
# 1.3 · Chaining — A's output is B's input

The second call needs something only the first can tell you — usually **the id the server assigned**.

```python
created = client.create_product(p)        # A — the server decides the id
client.update_price(created.id, 499)      # B — needs A's answer to exist
```

**The gotcha:** a chain fails *halfway*. A succeeded, B didn't — the world is now half-updated, and **no exception says so**. Real chains either record every step, or make B safe to re-run.

> Which is exactly why §3 hands back a **report** and not a boolean. Half-done is the normal case, not the exception.
---
# 1.4 · Reading a lot — pagination, rate limits, backoff

`GET /products` returns 5. What does it return when there are 10,000? **Not 10,000.** Real APIs hand back one *page* at a time:

```python
page = 1
while True:
    batch = client.list_products(page=page)   # ?page=1, ?page=2 …
    if not batch:                             # an empty page means done
        break
    yield from batch
    page += 1
```

And they push back when you go too fast: **429 Too Many Requests**, usually carrying a **`Retry-After`** header that says exactly when to return. Honour it — guessing gets you throttled or banned. That's M5's retry loop again, except **the server supplies the wait.**

**Your catalog doesn't paginate.** Real ones do — know the shape.
---
# 1.5 · Config & secrets — the data that isn't rows

Not everything that lives outside the code is a CSV. The **base URL**, the **API key**, the batch size — they change per environment, and they are **not code**.

```python
BASE  = os.environ.get("CATALOG_URL", "http://localhost:8000")   # a default is fine
TOKEN = os.environ["CATALOG_TOKEN"]      # ← no default: crash NOW if it's missing
```

**The trap is the second line.** A `.get()` default on a *secret* doesn't fail — it quietly runs your whole import unauthenticated, or against the wrong server, and tells you nothing. **Fail loudly at startup, not silently at row 4,000.**

Secrets live in the environment (or a `.env` you never commit) — never in source, never in the URL (M5 §2.5).
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
