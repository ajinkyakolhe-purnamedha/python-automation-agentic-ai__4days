---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 2 · Automate It — Validation & a Typed Client"
footer: "Acuity Training · Day 2 of 4"
---

<!-- _class: title -->

# Day 2
## JSON & API Automation
## **against your Day-1 API**

6 hours · 3 modules · 3 labs · same repo as yesterday
---
# Where we left off

Day 1 ended with a **FastAPI server** serving an `@dataclass` catalog. But a dataclass trusts you — `price=-50` sails through silently.

Today:
- **M4** — validate every payload with **Pydantic** (clean 422s)
- **M5** — drive the server from Python with an **APIClient**
- **M6** — bulk-import a CSV → API, with a report

Same project, typed end to end.
---
<!-- _class: title -->

# Module 4
## JSON & Pydantic
**5 sections · ~55 min** — each builds on the last; we code each one live
1 dataclass → Pydantic · 2 Validation rules · 3 validate / dump · 4 Pydantic in FastAPI · 5 The model is data
---
<!-- _class: section -->

# Section 1 · From @dataclass to Pydantic
## the problem → BaseModel → validated on construction
---
# 1.1 · Your annotations don't run — in TS *or* in Python

You already have the right instinct: a TS `interface` is **erased** — it guards nothing at runtime. Python's hints are exactly the same. Decoration. `@dataclass` stores whatever you hand it.

```ts
interface Account { balance: number }   // erased at compile time — checks nothing
```
```python
BankAccount(id=1, owner="", balance=-50)   # accepted silently — the hint checked nothing
```

**Pydantic is where that stops being true.** M3 promised your hints would start doing work — this is the module where they actually do.
---
# 1.2 · Pydantic — same fields, one base class

Subclass `BaseModel` and list the **same typed fields**. That's the only structural change.

```python
from pydantic import BaseModel
class BankAccount(BaseModel):
    id: int
    owner: str
    balance: float
```
---
# 1.3 · Validated on construction

A `BaseModel` checks types **when you build it** — good data becomes an object; bad data raises `ValidationError` immediately, at the boundary.

```python
BankAccount(id=1, owner="Ada", balance=1500.0)    # ok
BankAccount(id="x", owner="Ada", balance=1500.0)  # ValidationError: id is not an int
```

<div class="code-along">▶ Code-along now → notebook Section 1 — dataclass vs BaseModel; watch bad data raise</div>
---
<!-- _class: section -->

# Section 2 · Validation rules
## Field constraints → reading a ValidationError
---
# 2.1 · `Field` — rules beyond the type

A type says "a float"; `Field` says "a float **≥ 0**". Constraints live on the field and run on construction.

```python
from pydantic import Field
class BankAccount(BaseModel):
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0)        # ge = "greater than or equal to"
```

> Used **zod**? `Field(min_length=1)` *is* `z.string().min(1)`. Same idea, same place — the rule rides on the field.
---
# 2.2 · Reading a ValidationError

The error is **structured** — for every bad field it tells you *where*, *what*, and *why*.

```python
try:
    BankAccount(id=1, owner="", balance=-5)
except ValidationError as e:
    e.errors()   # [{'loc': ('owner',), 'msg': '...', 'type': 'string_too_short'}, ...]
```

<div class="code-along">▶ Code-along now → notebook Section 2 — add Field constraints; read e.errors()</div>
---
<!-- _class: section -->

# Section 3 · model_validate / model_dump
## dict → model → dict, with coercion
---
# 3.1 · `model_validate` — a dict becomes a model

An HTTP body or a file row arrives as a plain `dict`. `model_validate` turns it into a validated object (or raises).

```python
BankAccount.model_validate({"id": 2, "owner": "Lin", "balance": 800.0})   # dict → model
```

> Got a JSON **string** rather than a dict? `model_validate_json(raw)` — same gate, one step earlier, no `json.loads` first. Remember it: on **Day 4 the LLM answers with text**, and that's the line that turns text into a checked object.
---
# 3.2 · `model_dump` — a model becomes a dict

The other direction — back to a plain dict, ready for JSON / the wire.

```python
acct.model_dump()   # {'id': 2, 'owner': 'Lin', 'balance': 800.0}
```

These two are on **every line** of Modules 5–6.
---
# 3.3 · Coercion — where your zod instinct is wrong

**zod is strict** — `z.number().parse("800")` *throws*. **Pydantic is lax** — it converts: `"800.0"`→float, `"true"`→bool, `"2"`→int. Same intent, **opposite default**. This is the one place your JS instinct will mislead you.

```python
# zod:  z.number().parse("800")  →  ZodError
BankAccount.model_validate({"id": "2", "owner": "Lin", "balance": "800.0"})  # → 800.0 ✓
```

This is **why a CSV of strings feeds the API with no manual parsing** (M6's through-line) — and why `ConfigDict(strict=True)` exists for when you want zod's behaviour back.

<div class="code-along">▶ Code-along now → notebook Section 3 — validate a dict, dump it back, coerce a string row</div>
---
<!-- _class: section -->

# Section 4 · Pydantic in FastAPI
## typed body → 422 → response_model → docs
---
# 4.1 · A typed body validates itself

Type the route parameter as your model. FastAPI validates the incoming JSON — bad data returns an automatic **422** with field errors, *before* your code runs.

```python
@app.post("/accounts")
def create(account: BankAccount):   # FastAPI validates the body into a BankAccount
    ...
```
---
# 4.2 · `response_model` — typed output

Declare what a route returns; FastAPI serialises the model to JSON and documents the shape.

```python
@app.get("/accounts/{id}", response_model=BankAccount)
def get_account(id: int):
    ...
```
---
# 4.3 · /docs, from the schema

The model **is** the schema. FastAPI's `/docs` now shows every field, type, and constraint — and lets you try the API in the browser. No extra work.

<div class="code-along">▶ Code-along now → notebook Section 4 — a Pydantic-typed route; a bad body returns 422</div>
---
<!-- _class: section -->

# Section 5 · The model is data
## model_json_schema → description=  → optional fields
**Why now:** §4 showed the schema *rendered* as docs. Now take it as **data** — that's the handle Day 4 hands to an LLM.
---
# 5.1 · `model_json_schema()` — the schema, as a dict

§4.3 claimed *the model **is** the schema*. Here it is — not a docs page, a **plain Python dict**. Look closely: the `Field` rules you wrote in §2.1 became **JSON Schema keywords**, for free.

```python
Product.model_json_schema()
# {'type': 'object', 'title': 'Product',
#  'properties': {'id':    {'type': 'integer', 'minimum': 1},      # ← Field(ge=1)
#                 'name':  {'type': 'string', 'minLength': 1},     # ← Field(min_length=1)
#                 'price': {'type': 'number', 'minimum': 0}, ...}, # ← Field(ge=0)
#  'required': ['id', 'name', 'category', 'price']}
```

`/docs` is **rendered from this**. And on **Day 4 you hand this exact dict to an LLM** so it knows how to call your function. One model, three consumers.
---
# 5.2 · `description=` — documentation that *is* prompt text

Same `Field()` from §2.1, doing a different job. The description rides into the schema (§5.1) — and on Day 4 **the LLM reads it** to decide what to pass.

```python
class CatalogQuery(BaseModel):
    max_price: float | None = Field(
        default=None, ge=0,
        description="Upper price bound in INR, or null for no bound.",
    )
# → schema: {'description': 'Upper price bound in INR, or null for no bound.',
#            'anyOf': [{'type': 'number', 'minimum': 0}, {'type': 'null'}]}
```

**This is the punchline of Day 2 → Day 4:** a docstring the machine obeys. Write it badly and the LLM calls your tool badly.
---
# 5.3 · Optional fields — `| None`

`in_stock: bool = True` was a **default**. This is different: the field may legitimately be **nothing at all**. `str | None` and `Optional[str]` are the same thing — `| None` is the modern spelling.

```python
CatalogQuery.model_validate({})                        # all None — fine
CatalogQuery.model_validate({"max_price": 2000})       # → 2000.0
CatalogQuery.model_validate({"max_price": -5})         # ValidationError — ge=0 still applies
```

Optional means *"may be absent"*, **not** *"unchecked"*. Day 4's `CatalogQuery` is entirely optional fields — ask for "cheap electronics" and you named no product, so `name_contains` is `None`.

<div class="code-along">▶ Code-along now → notebook Section 5 — dump the schema; add a description; validate an all-optional model</div>
---
<!-- _class: lab -->

# 🧪 Lab 4 — Pydantic Models for the Catalog

**60 min** · open `modules/m04-json-pydantic/lab/README.md`

You'll do (on `Product`, not `BankAccount`):
- migrate `Product` from `@dataclass` → Pydantic `BaseModel` (with `Field` constraints)
- wire `response_model=Product` into the Day-1 server routes
- a bad POST → **422** with structured field errors
