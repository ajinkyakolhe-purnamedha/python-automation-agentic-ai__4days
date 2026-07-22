---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 1 · Build It — Clean Python to a Local API"
footer: "Acuity Training · Day 1 of 4"
---

<!-- _class: title -->

# Module 2
## Lists, Dicts & Files
**5 sections · ~50 min** — each builds on the last; we code each one live
1 Lists & CSV · 2 Dicts & JSON · 3 Organizing via functions · 4 Logging · 5 Revision
---
# From one account to many

Module 1 left us with **one** account — a `dict`. A bank has many, and they must outlive the program.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0, ...}   # M1: one account, in memory
```

Today: **many** accounts in the two containers that matter — `list` and `dict` — saved to **files** (CSV, JSON). The third, most powerful structure — a **class** — is Module 3.
---
<!-- _class: section -->

# Section 1 · Lists & CSV
## elements → slice → loop → comprehensions → CSV → the type-loss gotcha → type hints
---
# 1.1 · List elements — index

A **list** holds many values in order. Build it with `[...]`; read any item by its **index** (0-based; negatives count from the end).

```python
owners = ["Ada", "Lin", "Sam"]
owners[0]    # "Ada"  (first)
owners[-1]   # "Sam"  (last)
```
---
# 1.2 · Slicing

A **slice** `[start:stop]` returns a sub-list — `stop` is excluded. Omit a side to run to the edge.

```python
owners[0:2]   # ['Ada', 'Lin']
owners[1:]    # ['Lin', 'Sam']
```
---
# 1.3 · Length & looping

`len()` counts the items; a `for` loop walks them in order.

```python
len(owners)            # 3
for name in owners:
    print(name)        # Ada / Lin / Sam
```
---
# 1.4 · List comprehension

Build a new list from an old one in one line — say *what*, not *how*. Add an `if` to filter.

```python
upper = [name.upper() for name in owners]          # transform → ['ADA','LIN','SAM']
with_a = [n for n in owners if n.startswith("A")]  # filter   → ['Ada']
```
---
# 1.5 · Comprehension patterns

Pluck a field, filter rows, transform each, or combine filter + transform — all one-liners over a list of product dicts.

```python
names    = [p["name"] for p in products]                    # pluck one field
cheap    = [p for p in products if p["price"] < 500]        # filter rows
labels   = [f'{p["name"]} — ₹{p["price"]}' for p in products]  # transform each
on_sale  = [p["name"] for p in products if p["in_stock"]]   # filter + transform
```
---
# 1.6 · A CSV row is a list

The most common real-world data is a **CSV**. Read it with `csv.reader` — **each row comes back as a list** of strings.

```python
import csv
for row in csv.reader(open("accounts.csv")):
    row    # ['1', 'Ada', '1500.0']  — a list; every value is a str
```
---
# 1.7 · Reading a CSV file — the ways

The **header** is just the first row. Split it off and loop the rest, or let `DictReader` pair each value with its column name.

```python
rows = list(csv.reader(open("accounts.csv")))
header, data = rows[0], rows[1:]        # header row vs the data rows
# or: csv.DictReader(...) -> each row a dict keyed by header (→ Section 2)
```
---
# 1.8 · Gotcha — CSV is the type-loss format

Write with `DictWriter`, read with `DictReader` — but numbers and bools come back as **text**, and a list field can't fit a flat cell at all. **Coerce on load.**

**🔮 Predict:** you saved `price` as `499.0`. Read it back from the CSV — a `float`, or a `str`?

```python
row = next(csv.DictReader(open("products.csv")))
row["price"]          # "499.0"   ← a string, not a float!
float(row["price"])   # 499.0     ← you must coerce it back yourself
row["in_stock"]       # "True"    ← a string too — "True" == True is False
# tags (a list) doesn't fit one cell → JSON is the format that keeps lists
```
---
# 1.9 · Now with type hints — best practice

We introduced lists plainly. **From here on, annotate them.** A hint on a collection (`list[str]`, `list[list[str]]`) and on a function signature lets editors and tools catch mistakes *before* you run — for free.

```python
owners: list[str] = ["Ada", "Lin", "Sam"]
rows: list[list[str]] = list(csv.reader(open("accounts.csv")))

def first_n(owners: list[str], n: int) -> list[str]:
    return owners[:n]
```

<div class="code-along">▶ Code-along now → notebook Section 1 — list ops → comprehension → CSV as lists → with type hints</div>
---
<!-- _class: section -->

# Section 2 · Dicts & JSON
## access → loop → functions → nested → grouping → JSON → the keys gotcha → type hints
---
# 2.1 · Dict element access

A **dict** stores named fields looked up by **key**, not position. `[key]` raises if missing; `.get(key)` returns `None` safely.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0}
acct["owner"]        # "Ada"
acct.get("phone")    # None — no KeyError
```
---
# 2.2 · Dict looping

Loop the keys, the values, or both together with `.items()`.

```python
for key in acct: ...               # keys
for value in acct.values(): ...    # values
for key, value in acct.items():    # both
    print(key, "=", value)
```
---
# 2.3 · Important dict functions

Add or overwrite by assignment or `update`; test membership with `in`; remove with `pop`.

```python
acct["balance"] = 1600.0           # update one field
acct.update({"tier": "gold"})      # add / merge fields
"owner" in acct                    # True
```
---
# 2.4 · Nested dicts

Values can themselves be lists or dicts — real records **nest**. Reach in by chaining keys.

```python
acct = {"owner": "Ada",
        "address": {"city": "Pune"},
        "tags": ["primary", "online"]}
acct["address"]["city"]   # "Pune"
```
---
# 2.5 · Worked example — group by category

A common real shape: bucket records under a key. Build a dict whose values are **lists**, appending as you loop — `setdefault` creates the empty list the first time.

```python
by_category = {}
for p in products:
    by_category.setdefault(p["category"], []).append(p)

by_category["Electronics"]   # [ {USB-C Cable…}, {Keyboard…} ]
list(by_category.keys())     # ['Electronics', 'Home', 'Fitness']
```
---
# 2.6 · Save & load with JSON

A dict maps exactly to **JSON**. `json.dump` writes it to disk; `json.load` reads it straight back **as a Python dict** — same shape, no parsing.

```python
import json
json.dump(acct, open("acct.json", "w"), indent=2)   # dict → file
back = json.load(open("acct.json"))                  # file → dict again
```
---
# 2.7 · Gotcha — JSON keys are always strings

JSON object keys can only be strings. Dump a store keyed by an **int** id, load it back, and the keys are now `"1", "2", "3"` — a lookup with the int `1` misses.

**🔮 Predict:** you dump `{1: acct}` keyed by the int `1`. After loading, does `store[1]` still find it?

```python
json.dump({1: acct}, open("store.json", "w"))
store = json.load(open("store.json"))
list(store.keys())    # ['1']        ← "1", a string — not 1
store[1]              # KeyError!    →  store["1"] works
```
---
# 2.8 · Now with type hints

Type a dict by its **key and value** types. Uniform values type precisely; our account **mixes** types, so the honest hint is `dict[str, object]` — and that vagueness is the signal that a fixed-field record wants a **class** (Module 3).

```python
balances: dict[str, float] = {"Ada": 1500.0, "Lin": 800.0}             # uniform → precise
acct: dict[str, object] = {"id": 1, "owner": "Ada", "balance": 1500.0} # mixed → vague → want a class
```

<div class="code-along">▶ Code-along now → notebook Section 2 — access & loop → nested → JSON round-trip → with type hints</div>
---
<!-- _class: section -->

# Section 3 · Organizing dict access via functions
## a store → insert/update → fetch → the seam → with type hints
---
# 3.1 · A dict as the store

Keep all accounts in one dict keyed by id — **instant (O(1))** lookup by account number.

```python
accounts = {}                       # {id: account}
accounts[1] = {"id": 1, "owner": "Ada", "balance": 1500.0}
accounts[1]                         # lookup by id, no scanning
```
---
# 3.2 · insert & update via functions

Wrap the writes in functions — one place owns "add" and "change", so every caller behaves the same.

```python
def insert(store, acct):           store[acct["id"]] = acct
def update(store, id, **changes):  store[id].update(changes)
```
---
# 3.3 · fetch via a function

A `fetch` function hides the lookup — and gives one place to validate, default, or raise on a missing id.

```python
def fetch(store, id):
    if id not in store:
        raise LookupError(f"no account id={id}")
    return store[id]
```
---
# 3.4 · The seam: JSON today, a database tomorrow

These functions hide **where** the data lives. Today they read/write a JSON file; later the same `insert`/`fetch` talk to a **database or data warehouse** — callers never change.

```python
# today:    store = json.load(open("accounts.json"))
# tomorrow: store = db.query("SELECT ...")   # same insert()/fetch() on top
```
---
# 3.5 · Now with type hints

Typed signatures make the storage layer **self-documenting**: the store is `dict[int, dict]`, an id is `int`, `fetch` returns a `dict`.

```python
def insert(store: dict[int, dict], acct: dict) -> None:
    store[acct["id"]] = acct

def fetch(store: dict[int, dict], id: int) -> dict:
    ...
```

<div class="code-along">▶ Code-along now → notebook Section 3 — store + insert/update/fetch, backed by JSON → with type hints</div>
---
<!-- _class: section -->

# Section 4 · Logging
## levels → applied to the storage
---
# 4.1 · Logging vs print

`print` is for throwaway scripts; real code uses **`logging`** — levels (`DEBUG < INFO < WARNING < ERROR`) dial detail up or down without deleting lines.

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bank")
log.info("started")     # shown · log.debug("...") hidden at INFO
```
---
# 4.2 · Logging the storage

Add one line to each storage op — now every `insert`/`update`/`fetch` and the JSON load leaves an **audit trail**.

```python
def fetch(store, id):
    log.info("fetch id=%s", id)     # %s args, not an f-string
    return store[id]
```

<div class="code-along">▶ Code-along now → notebook Section 4 — add logging to the Section-3 storage functions</div>
---
<!-- _class: section -->

# Section 5 · Revision
## the four moves of data · what survives a round-trip · one combined example
---
# 5.1 · The four moves of data

| Move | Tool |
|---|---|
| many things, in order | `list` · slice · comprehension |
| named fields, by key | `dict` · `.get` · `.items` |
| the flat, shareable file | **CSV** — strings only |
| the typed, nested file | **JSON** — keeps lists & numbers |

Plus: keep a **store** keyed by id, reach it through **functions**, and **log** every access.
---
# 5.2 · What survives a round-trip

The same product, saved two ways. JSON round-trips **identically**; CSV turns everything to strings and drops the list.

```python
p = {"id": 1, "price": 499.0, "tags": ["cable"]}   # int · float · list

save_json(p) → load_json()   # {"id": 1, "price": 499.0, "tags": ["cable"]}   ✓ identical
save_csv(p)  → load_csv()    # {"id": "1", "price": "499.0"}   ✗ all strings, tags gone
```
---
# 5.3 · One example, all four moves

A **list** of product **dicts** → filter with a **comprehension** → persist as **JSON** (full fidelity) and **CSV** (flat).

```python
products = [make_product(1, "USB-C Cable", "Electronics", 499.0), ...]  # list of dicts (M1)
cheap = [p for p in products if p["price"] < 1000]     # comprehension filter

store = make_store(products)          # {id: product} keyed store (Section 3)
save_json(store, "catalog.json")      # → JSON, keeps everything
save_csv(store,  "catalog.csv")       # → CSV, scalar fields only
load_json("catalog.json")             # round-trips identically
```

<div class="code-along">▶ Next → Lab 2 turns exactly this into `catalog/storage.py` — save & load, JSON & CSV.</div>
---
<!-- _class: lab -->

# 🧪 Lab 2 — Persistent Catalog

**80 min** · open `modules/m02-data-files/lab/README.md` · scaffolds in `starter/`

You'll build (on `Product`, not `BankAccount`):
- `catalog/storage.py` — save/load the catalog as JSON and CSV
- comprehension-powered `search_by_name`, `filter_by_price`
- `search` / `save` / `load` CLI subcommands

End state: your catalog **survives a process restart**.
