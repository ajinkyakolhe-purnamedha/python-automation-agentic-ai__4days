---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 1 · Build It — Clean Python to a Local API"
footer: "Acuity Training · Day 1 of 4"
---

<!-- _class: title -->

# Day 1
## Python Fundamentals
## **+ build the Catalog Foundation**

6 hours · 3 modules · 3 labs · one repo for the week
---
# What we build today

By 6 PM, a **local FastAPI server** running on your laptop, serving a `Product` catalog you wrote from scratch.

- Module 1 → Python core → Lab 1: `Product` foundation
- Module 2 → Data structures, files, modules → Lab 2: Persistent catalog
- Module 3 → OOP, dataclasses, FastAPI → Lab 3: Local API server

**Same repo carries through Day 2, 3, 4.** No throwaway demos.
---
# The week, in one picture

```
Day 1   Product class + FastAPI server
Day 2   + Pydantic + APIClient + CSV bulk-import
Day 3   + pytest suite + mocks + CI green
Day 4   + LLM-powered CatalogAgent + agent tests
```

Every day extends yesterday's project (your `my-catalog/`).
A catch-up baseline (`day-N-start/`) is provided each morning.
---
<!-- _class: title -->

# Module 1
## Python Core
**6 sections · ~40 min** — each builds on the last; we code each one live
1 Variables · 2 Control flow · 3 Functions · 4 Exceptions · 5 Zen of Python · 6 Revision
---
# Our story for today: bank accounts

Every example today is one **account**. In Python an account is just a `dict` — named fields, no class yet (classes come in Module 3).

```python
acct = {"id": 1, "owner": "Ada", "account_type": "savings",
        "balance": 1500.0, "is_active": True,
        "tags": ["primary", "online"]}
```

Same six fields all day. M2 stores many of these in files; M3 turns them into a class.
---
<!-- _class: section -->

# Section 1 · Variables
## variables & operations → types → hints → list / dict → the account
---
# 1.1 · Variables & operations

A variable is a name pointing at a value; you don't declare a type, Python infers it. Then you **operate** on those values.

```python
owner = "Ada"; balance = 1500.0; rate = 0.04
balance = balance + balance * rate    # arithmetic on numbers
label = "owner: " + owner             # + joins strings
wealthy = balance > 5000              # comparison → a bool
```
---
# 1.2 · Types — one per kind

`type(x)` reveals the kind Python inferred for a value. The account's fields cover Python's core types.

```python
print(type("Ada"))     # <class 'str'>
print(type(1))         # <class 'int'>
print(type(1500.0))    # <class 'float'>
print(type(True))      # <class 'bool'>
print(type(None))      # <class 'NoneType'>
```
---
# 1.3 · Type hints — just a hint

A variable can hold **any** type, and you can rebind it to another at runtime. A **type hint** (`name: type`) documents intent — it is **not enforced**.

**🔮 Predict:** after `balance: float = 1500.0`, does `balance = "frozen"` raise?

```python
balance = 1500.0      # float now...
balance = "frozen"    # ...str later — Python allows it

balance: float = 1500.0   # a hint; it still won't stop balance = "frozen"
```
---
# 1.4 · Advanced variables — list & dict

When one value isn't enough: a **list** holds many in order; a **dict** holds named fields you look up by key.

```python
tags: list[str] = ["primary", "online"]            # ordered, indexable
acct: dict = {"owner": "Ada", "balance": 1500.0}   # look up by key
```
---
# 1.5 · Using list & dict

Read a **list** by index, a **dict** by key — and each carries handy methods.

```python
tags[0]; len(tags)            # "primary" ; 2
acct["owner"]; acct.get("x")  # "Ada" ; None (safe — no KeyError)
acct.keys(); acct.values()    # the field names ; the values
acct.items()                  # (key, value) pairs — great for loops
```
---
# 1.6 · An account = every type, in one dict

Put it together: one bank account is just a `dict` whose fields span all the types we met. **This is our domain object for the whole course.**

```python
acct = {"id": 1, "owner": "Ada", "account_type": "savings",
        "balance": 1500.0, "is_active": True, "tags": ["primary", "online"]}
```

<div class="code-along">▶ Code-along now → notebook Section 1 — variables & ops → types → hints → list/dict → the account</div>
---
<!-- _class: section -->

# Section 2 · Control flow
## truthiness · if / elif / else · for · while
---
# 2.1 · Truthiness — empty things are False

You can test a value straight in `if`. "Empty" / "zero" values are **falsy**: `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False`. Everything else is truthy.

```python
if not acct["tags"]:        # empty list is falsy
    print("no tags yet")
```
---
# 2.2 · Branching — if / elif / else

`if/elif/else` picks exactly one branch. **Indentation** (not braces) marks the block.

```python
if not a["is_active"]:   label = "inactive"
elif a["balance"] < 100: label = "low balance"
else:                    label = "healthy"
```
---
# 2.3 · Loops — for (and while)

`for` walks any sequence — a list, a dict's `.items()`, a counter via `enumerate`, or a numeric `range`. `while` repeats until a condition flips.

```python
for a in accounts: ...                # over a list
for key, value in acct.items(): ...   # over a dict's pairs
for i, a in enumerate(accounts): ...  # i is the counter: 0, 1, 2…
for n in range(3): ...                # 0, 1, 2
while sam["balance"] < 100: ...       # repeat until it clears 100
```

<div class="code-along">▶ Code-along now → notebook Section 2 — branch accounts by status, top up a balance with <code>while</code></div>
---
<!-- _class: section -->

# Section 3 · Functions
## arguments & defaults · return · type hints · *args / **kwargs
---
# 3.1 · Functions — arguments, defaults, return

`def` names reusable logic. **Arguments** feed it; parameters can carry **default values**; `return` hands a result back.

```python
def total_balance(accounts, only_active=True):   # only_active defaults to True
    return sum(a["balance"] for a in accounts if a["is_active"])
```
---
# 3.2 · Type hints on functions

Annotate the parameters and the return type. As with variables, hints **document** the signature — Python does **not** enforce them; a wrong type still runs.

```python
def total_balance(accounts: list[dict], only_active: bool = True) -> float:
    ...
total_balance("oops")   # a type checker complains; Python runs it anyway
```
---
# 3.3 · Flexible args — *args / **kwargs

`*args` collects extra **positional** args into a tuple; `**kwargs` collects extra **keyword** args into a dict — handy for "any number of fields."

```python
def open_account(**fields):      # fields is a dict
    return {"is_active": True, **fields}
open_account(id=2, owner="Lin", balance=800.0)
```

<div class="code-along">▶ Code-along now → notebook Section 3 — <code>total_balance()</code> with hints, then a <code>**kwargs</code> factory</div>
---
<!-- _class: section -->

# Section 4 · Exceptions
## raise · try / except / else / finally
---
# 4.1 · raise — business logic as a readable error

`raise` an error instead of returning a bad value (or a silent `None`). A good error is **business logic made readable** — the type + message say exactly which rule broke.

```python
def find_account(accounts, acct_id):
    for a in accounts:
        if a["id"] == acct_id: return a
    raise LookupError(f"no account with id={acct_id}")
```
---
# 4.2 · try / except / else / finally

`try` the risky code, `except` the failure, `else` runs only on success, `finally` always runs (cleanup).

**🔮 Predict:** with **no** `try`, what does `find_account(accounts, 99)` do to the program?

```python
try:    acct = find_account(accounts, 99)
except LookupError as err: print("not found:", err)
else:   print("found:", acct["owner"])
finally:print("lookup done")
```

<div class="code-along">▶ Code-along now → notebook Section 4 — raise on overdraft & missing id, handle both</div>
---
<!-- _class: section -->

# Section 5 · The Zen of Python
## clean code: easy to read, easy to maintain
---
# 5.1 · Zen of Python — write for the reader

`import this` prints Python's creed. It's really about **clean, maintainable code** — code is read far more often than it's written.

> "If you write code as cleverly as possible, you are *not* clever enough to debug it."

Favour **clear over clever**: explicit > implicit, simple > complex, flat > nested.
---
# 5.2 · Clean code in practice

Say what you mean, the obvious way — the reader (often future-you) should grasp each line at a glance.

```python
if len(tags) == 0: ...   # clever / noisy   →   if not tags: ...   # clear
```

**Flat > nested:** return early (a guard clause) instead of wrapping the body in `if`.
---
# 5.3 · Names & explicit types

The cheapest readability wins: **honest names** and **explicit type hints**. A good name removes the need for a comment.

```python
def calc(x): ...                              # what is x? what comes back?
def total_active_balance(accounts: list[dict]) -> float: ...   # name + hints tell the story
```

<div class="code-along">▶ Code-along now → notebook Section 5 — rename for clarity, add explicit hints, flatten the flow</div>
---
<!-- _class: section -->

# Section 6 · Revision
## the four moves, together
---
# 6.1 · The four moves, one picture

| Move | Tool |
|---|---|
| store one thing with named fields | `dict` |
| choose / repeat | `if / elif / else`, `for`, `while` |
| reuse logic, hand back a result | `def … return` |
| fail clearly, recover | `raise`, `try / except` |

Plus the Zen: clear names, explicit type hints, readable flow.

<div class="code-along">▶ Code-along now → notebook Section 6 — one little bank exercising all four moves</div>
---
<!-- _class: lab -->

# 🧪 Lab 1 — The `Product` Foundation

**80 min** · open `modules/m01-python-core/lab/README.md` · scaffolds in `starter/`

You'll build (now on `Product`, not `BankAccount`):
- `catalog/models.py` — product dict factory + catalog list functions
- `catalog/cli.py` — `list`, `add` subcommands

End state: `python -m catalog.cli list` prints 5 seeded products.
