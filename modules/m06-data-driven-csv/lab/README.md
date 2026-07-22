# Lab 6 — Bulk-Import Workflow

**Duration:** ~60 min · **Day:** 2 · **Module:** 6 (Data-Driven Automation)

> **Concepts used:** CSV → validate → API workflow and the structured import report → `../codealong-m06-data-driven-csv.ipynb` (the `APIClient` you built in Lab 5 brings its own retry loop — a network blip won't kill the batch).
> This lab applies the module's `BankAccount` import workflow to the course's `Product` domain — same patterns, different thing (the deliberate concept-vs-lab seam).

## Goal
Wire the pieces together. Read `data/products.csv`, validate each row with the
`Product` model, push valid rows through `APIClient.create_product()`, and
write a structured `import_report.json` that tells the operator **exactly
what failed and why**. This complete workflow becomes the
**system-under-test** for Day 3.

## You start with
- Lab 5 end-state — server + Pydantic models + working `APIClient`.

## You'll end with
- `data/products.csv` with intentionally bad rows mixed in
- `catalog/import_csv.py` runnable as `uv run python -m catalog.import_csv data/products.csv`
- An `import_report.json` with three sections: `created`, `validation_errors`, `api_errors`

## Starter files

`starter/` gives you the import scaffold and a ready-made CSV. Copy them in, then fill the three `# TODO`s in the loop (validate → create → record) and the health-check in `main()`. The report shape and CLI are decided; the loop logic is yours.

```bash
# run from capstone-project/my-catalog/
mkdir -p data                                                             # first lab to use data/ — it doesn't exist yet
cp ../../modules/m06-data-driven-csv/lab/starter/import_csv.py catalog/
cp ../../modules/m06-data-driven-csv/lab/starter/products.csv  data/      # the CSV lives under data/
```

| File | You write |
|---|---|
| `starter/import_csv.py` | the three loop bodies (validate / create / record) + the `health()` fail-fast in `main()` |
| `starter/products.csv` | **given** — 20 rows: ids 100–115 clean, ids 116–118 deliberately malformed (file lines 19–21), plus one well-formed row the server will refuse (find it) |

## Steps

1. **Read `data/products.csv` before you write anything.** It's given, and it's rigged — 20 rows, of which **4 fail**. Knowing what *should* fail is how you'll know your report is right. Three you can spot by eye:
   - empty name → validation error
   - `price = -50` → validation error
   - `price = not-a-number` → validation error (nothing to coerce)

   The fourth you **cannot find by reading the file**. It's a perfectly well-formed row — right types, sane values, nothing to complain about — that the *server* will refuse anyway. The only way to spot it in advance is to know what's already in the catalog (`curl localhost:8000/products`, or read the server's seed).

   That's not a gotcha; it's the whole point of §3.1. Bad data is a property of the **file** — you can find it with the file alone. A 409 is a property of the **world** — the same row is fine on an empty server and refused on this one. Two different failures, found two different ways, fixed by two different people. That's why they get two buckets.

2. **Write `catalog/import_csv.py`.** The loop over `csv.DictReader` is given (note `enumerate(..., start=2)`, so your row numbers match the file once the header is counted). Each row lands in exactly one of three buckets — each TODO is one `try` around one call:
   - **validate** — turn the row into a `Product`. If the model refuses it, the row must **not** reach the API: record `{"row", "input", "errors"}` in `validation_errors` — where `errors` is the structured list the exception carries (module-4 §2.2) — and move on.
   - **create** — send it through the client. A well-formed row the API *rejects* (duplicate id → 409) is a different failure: record `{"row", "input", "status", "detail"}` in `api_errors` and move on. The exception carries both of those last two.
   - **else** — success: record the created product in `created`, as a plain dict (the report is written out as JSON).

   Return a report dict: `source`, a `summary` (counts of rows_read / created / validation_errors / api_errors), then the three lists themselves. The report shape is already written in `starter/import_csv.py` — you fill the three loop TODOs.

   The three lists are **separate** on purpose. Validation failures and API failures need different fixes — never collapse them into a single "errors" bucket.

3. **The CLI is given — one TODO left in it.** `argparse` with `csv_path`, `--base-url`, `--report` is already wired up; don't rewrite it. What's missing is the **fail-fast**: ping the server once before importing anything and exit 2 if it doesn't answer. Otherwise a server that's down produces 19 identical errors instead of one clear one.

4. **Run it.** Two terminals — and that split matters for step 5:
   ```bash
   # terminal 1 — the server
   uv run uvicorn catalog.server:app --reload

   # terminal 2 — the importer
   uv run python -m catalog.import_csv data/products.csv
   cat import_report.json | head -30
   ```

5. **Read the report.** The `summary` should mirror what you saw in terminal 2. The `validation_errors[0].errors[0]` should pinpoint the offending field — that's Pydantic earning its keep.

   **Watch terminal 1 while it runs.** Every `INFO catalog.models: added product …` line shows up *there*, not in the importer — because `catalog.add` runs inside the **server** process. Two processes, two logs. That's not a quirk; it's the whole point of having an API in front of the catalog.

## Expected output

**Terminal 2 — the importer.** This is all of it: four warnings and the summary. The `INFO … added product` lines are *not* missing — they're in terminal 1 (see step 5).

```
$ uv run python -m catalog.import_csv data/products.csv
WARNING __main__: row 4 API error: 409: Product id 1 already exists
WARNING __main__: row 19 failed validation
WARNING __main__: row 20 failed validation
WARNING __main__: row 21 failed validation

20 rows  |  created 16  ·  validation errors 3  ·  API errors 1
report → import_report.json
```

Row 4 is the one you couldn't see in the file — `USB-C Cable`, sitting innocently between the USB-C Hub and the Laptop Stand. Nothing is wrong with it. The server just already has an id 1.

**Terminal 1 — the server**, meanwhile, logs one line per accepted row:

```
INFO catalog.models: added product id=100 name='Wireless Mouse'
...
INFO catalog.models: added product id=115 name='Trail Running Shoes'
```

```json
// import_report.json (excerpt)
{
  "summary": { "rows_read": 20, "created": 16,
                "validation_errors": 3, "api_errors": 1 },
  "validation_errors": [
    { "row": 19, "input": {"name": "", ...},
      "errors": [{"loc": ["name"],
                  "msg": "String should have at least 1 character"}] }
  ],
  "api_errors": [
    { "row": 4, "input": {"id": "1", "name": "USB-C Cable", ...},
      "status": 409, "detail": "Product id 1 already exists" }
  ]
}
```

Read those two entries side by side — it's the module in one screen. The validation error points at a **field** (`loc: ["name"]`): fix the spreadsheet. The API error points at a **status** (`409`): fix the conflict. Same report, two audiences.

## Make it pass

Your done-signal is the spec — the stdout/report above is the warm-up. It **skips** until `import_csv.py` exists, then goes red → green.

```bash
uv run pytest tests/test_lab06.py -v
```

Target: all of `TestImportCsv` green — the three buckets (`created` / `validation_errors` / `api_errors`) stay separated (a fake client stands in for the server).

## Common pitfalls
- `csv.DictReader` returns *every* value as a string. Pydantic v2 coerces `"true"` → `True` and `"1299"` → `1299` for you, but `"not-a-number"` won't coerce and will surface a clean error. **Don't pre-clean rows** — let Pydantic be the bouncer.
- Forgetting `start=2` on `enumerate` — your "row number" in the report becomes wrong by one because the header is row 1.
- Catching `Exception` instead of `ValidationError` / `APIError` will mask real bugs in your code.
- Writing the report inside the `with open` block — fine for small files, but if Pydantic raises and you forget `continue`, you might write a half-built report.

## Stretch (optional)
- Read CSV in chunks via `itertools.islice` if you ever need to import 100k rows.
- Print a per-category summary at the end (`created` grouped by category) using `Counter`.
- Add an `--update` flag: on duplicate id (409), retry with PATCH instead of giving up.

---

**End of Day 2.** Your working folder is now the input for Day 3 — your
checkpoint matches `capstone-project/checkpoints/day-3-start/`.
