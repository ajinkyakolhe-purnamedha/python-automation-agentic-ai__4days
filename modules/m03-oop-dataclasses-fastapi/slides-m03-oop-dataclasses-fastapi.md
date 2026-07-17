---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 1 · Build It — Clean Python to a Local API"
footer: "Acuity Training · Day 1 of 4"
---

<!-- _class: title -->

# Module 3
## OOP, Dataclasses & FastAPI
**4 sections · ~50 min** — each builds on the last; we code each one live
1 The class by hand · 2 @dataclass · 3 Inheritance · 4 FastAPI
---
# What we're really building today

Not four OOP features — **one application**. You already have the pieces from M1–M2; today they become an app with a real **front door**.

```
 browser / curl  ──▶  server.py   ──▶  Product +          ──▶  .json
 (any caller)         (FastAPI)        ProductCatalog          .csv
                      ↑ today (§4)     ↑ your M1–M2 core        ↑ M2
```

Right now the core is loose functions in files. **§1–3 make it a solid core; §4 adds the API front door** — the same catalog, reachable by more and more callers.
---
# From a dict to a class

Module 2 left an account as a `dict` + loose `insert/update/fetch` functions — and a **mixed-value dict that was hard to type** (§2.6). The fix: a **class** — fields *and* behavior in one typed object.

```python
acct = {"id": 1, "owner": "Ada", "balance": 1500.0}   # M2: a bare dict
ada  = BankAccount(1, "Ada", 1500.0)                   # M3: an object with methods
```

Today: build the class by hand → shortcut it with `@dataclass` → specialize with inheritance → expose it over HTTP. This class is the **core** every caller talks to — a script now, HTTP in §4, an agent on Day 4.
---
<!-- _class: section -->

# Section 1 · OOP — the class by hand
## why → class/__init__/self → attributes → methods
**Why now:** the app's core must protect its own data — a bare `dict` can't.
---
# 1.1 · Why a class

A `dict` holds data but no **behavior** and no **guardrails** — nothing stops `balance = -50` or a typo'd key. A **class** bundles the data *and* the operations that protect it.

```python
acct = {"owner": "Ada", "balance": 1500.0}   # data only — deposit/withdraw live elsewhere
```
---
# 1.2 · `class` + `__init__` + `self`

A **class** is a blueprint; an **object** is one thing built from it. `__init__` runs once when you build an object and sets up its data. `self` is *that* object.

```python
class BankAccount:
    def __init__(self, id, owner, balance):
        self.id = id; self.owner = owner; self.balance = balance

ada = BankAccount(1, "Ada", 1500.0)   # __init__ runs, returns the object
```
---
# 1.3 · Attributes — the data on an object

Attributes are the per-object data set in `__init__`. Read/write them with a **dot** — clearer than a dict's string key, and a typo is an *error*, not a silent `None`.

```python
ada.balance          # 1500.0   (vs d["balance"])
ada.owner = "Ada K." # set with the dot too
```
---
# 1.4 · Methods — behavior, with guardrails

A **method** is a function inside the class; its first parameter is `self`, the object. M2's loose functions become methods — and a method can `raise` to enforce a rule, so the data can't go invalid.

```python
class BankAccount:
    ...
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")   # the rule lives with the data
        self.balance -= amount
```

<div class="code-along">▶ Code-along now → notebook Section 1 — build BankAccount: __init__, attributes, a method with a guardrail</div>
---
<!-- _class: section -->

# Section 2 · @dataclass — the clean record
## boilerplate → @dataclass → the data-structure step → defaults → methods
**Why now:** the core's shape is right — kill the boilerplate so the record stays honest.
---
# 2.1 · That's a lot of boilerplate

A real account has six fields. Writing `__init__` (plus a readable print, plus `==`) **by hand** for every field is tedious and easy to get wrong.

```python
def __init__(self, id, owner, account_type, balance, is_active, tags):
    self.id = id; self.owner = owner; ...   # ...repeat for every field
```
---
# 2.2 · `@dataclass` — the boilerplate, for free

Put `@dataclass` on top and just **list the typed fields**. You get `__init__`, a readable `__repr__` (how it prints), and `__eq__` (`==` by value) — written for you.

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float

print(BankAccount(1, "Ada", 1500.0))   # BankAccount(id=1, owner='Ada', balance=1500.0)
```

> The `@` is a **decorator** — it hands your class to a framework (here, `dataclass`). In this course you **use** decorators; you never write your own.
---
# 2.3 · The next data structure

The progression: **variable** (M1) → **list & dict** (M2) → **dataclass** (M3) — a typed, fixed-shape record. Exactly the fix for M2's "mixed-value dict you couldn't type cleanly."

```python
@dataclass
class BankAccount:
    id: int
    owner: str
    balance: float        # each field named AND typed — no more dict[str, object]
```
---
# 2.4 · Defaults & the tags field

Give a field a default after the typed ones. For a **mutable** default (a list), use `field(default_factory=list)` — never `tags: list = []` (one list shared across every account: the M1 trap).

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float
    is_active: bool = True
    tags: list[str] = field(default_factory=list)
```
---
# 2.5 · Behavior still lives on it

A dataclass is still a class — your methods sit right alongside the fields. Clean data **and** behavior, together.

```python
@dataclass
class BankAccount:
    id: int; owner: str; balance: float = 0.0
    def withdraw(self, amount):
        if amount > self.balance: raise ValueError("insufficient funds")
        self.balance -= amount
```

<div class="code-along">▶ Code-along now → notebook Section 2 — migrate BankAccount to @dataclass: fields, defaults, keep the methods</div>
---
<!-- _class: section -->

# Section 3 · Inheritance
## is-a → inherit → override + super() → Pydantic
**Why now:** specialize the core without rewriting it — the same `is-a` that powers Pydantic (Day 2).
---
# 3.1 · Why inherit — *is-a*

A `SavingsAccount` **is a** `BankAccount` that also earns interest. Inheritance lets a new class reuse everything the parent has and add or change just the difference.

```python
@dataclass
class SavingsAccount(BankAccount):
    rate: float = 0.04        # plus everything BankAccount already has
```
---
# 3.2 · A subclass inherits everything

`SavingsAccount(BankAccount)` gets the parent's fields **and** methods for free — `withdraw`, `balance`, all of it — without rewriting them.

```python
s = SavingsAccount(1, "Ada", 1500.0)
s.withdraw(100)        # BankAccount's method, inherited as-is
```
---
# 3.3 · Override + `super()`

Redefine a method to **specialize** it; call `super().<method>()` to reuse the parent's logic and add to it.

```python
class SavingsAccount(BankAccount):
    def withdraw(self, amount):
        super().withdraw(amount)   # reuse the parent's guardrail
        self.balance -= 1          # then apply a savings withdrawal fee
```
---
# 3.4 · You'll see this again — Pydantic

Day 2's models are classes that **inherit** from Pydantic's `BaseModel`:

```python
class Product(BaseModel):   # is-a BaseModel → gets validation for free
    id: int
    name: str
```

Same `is-a` mechanism you just learned — `@dataclass` becomes `BaseModel`, plus runtime validation.

<div class="code-along">▶ Code-along now → notebook Section 3 — SavingsAccount(BankAccount): inherit, override withdraw with super()</div>
---
<!-- _class: section -->

# Section 4 · FastAPI — the app's front door
## what it is → why an API → why FastAPI → build → run → where it sits → AI apps
---
# 4.1 · What FastAPI *is*

**FastAPI is a web framework**: it turns your Python functions into **HTTP endpoints** other programs can call over the network. You write a function; FastAPI makes it reachable at a URL.

```
 your Python function   ──FastAPI──▶   GET http://localhost:8000/products
```

It's the **front door** to your Python app: the core stays pure Python; FastAPI lets the outside world in.
---
# 4.2 · Why an API? Callers aren't always Python

Your catalog core is the **engine**. But a browser, a mobile app, another team's service, or a script in another language can't `import catalog` — they speak **HTTP**. The API is the shared doorway.

```
 browser ┐
 mobile  ├─▶ HTTP ─▶ server.py ─▶ ProductCatalog ─▶ files
 service ┘           (one door)     (one core)       (data)
```

**One core, many callers.** Change the core freely; the doorway stays the same.
---
# 4.3 · Why *FastAPI*

It turns the **type hints** you've written since M1 into real machinery — for free:

- **Validation** — a route typed `product_id: int` rejects `/products/abc` with a clean `422`, *before* your code runs
- **Docs** — an interactive `/docs` page, generated from your signatures
- **Pydantic-powered** — the Day-2 models become the request/response contract
- **The Python standard for APIs — and for AI/ML services** (model endpoints, RAG, agent backends)

The hints stop being decoration and start doing work.
---
# 4.4 · A route is a function with `@app.get` on top

FastAPI turns a function into a web endpoint: put `@app.get("/path")` above it, and it runs when a request hits that path.

```python
app = FastAPI()

@app.get("/accounts")
def list_accounts():
    return ACCOUNTS
```

> That `@` is a decorator again — same idea as `@dataclass`: you hand `list_accounts` to FastAPI and it becomes a route. You'll meet this shape twice more — `@pytest.fixture` on Day 3, `@agent.tool` on Day 4.
---
# 4.5 · Build the server — GET & POST

One function per route. Return your objects and FastAPI serialises them to JSON; take a **path parameter** to fetch one.

```python
@app.get("/accounts/{id}")
def get_account(id: int):
    return fetch(STORE, id)

@app.post("/accounts")
def create(acct: dict):
    insert(STORE, acct); return acct
```
---
# 4.6 · Run it — `uvicorn` + `/docs`

Start the server, then hit it from a browser or curl. FastAPI generates **interactive docs** for free.

```bash
uv sync                                # once — installs FastAPI
uv run uvicorn catalog.server:app --reload
curl localhost:8000/accounts/1
# then open http://localhost:8000/docs
```

**This is the end-of-Day-1 artifact:** a running API serving a catalog you built.

<div class="code-along">▶ Code-along now → notebook Section 4 — a FastAPI app over the accounts: GET, POST, run it</div>
---
# 4.7 · The shape of a real Python app

Step back: the three files you wrote **are** a layered application — each module one job, each layer talking only to the next.

```
 HTTP ─▶ server.py    · API layer    — routes, HTTP status, JSON   (FastAPI)
            │
            ▼
         models.py    · domain core  — Product, ProductCatalog, the rules
            │
            ▼
         storage.py   · persistence  — save / load JSON & CSV
```

**This layering is the lesson** — swap FastAPI for a CLI, or JSON for a database, and the core never changes.
---
# 4.8 · The same shape builds AI apps

A modern AI app is **a FastAPI backend** with an LLM wired in. Your catalog server is exactly the backend an AI feature calls:

```
 user ─▶ FastAPI backend ─▶ LLM ─▶ picks a "tool"
                 ▲                     │
                 └────  your catalog ◀─┘   (the tool runs, returns data)
```

The **tool-calling** pattern *is* the pattern you just learned: an agent **tool** is a typed Python function a framework exposes to the LLM — exactly like `@app.get` exposes one over HTTP. The **Pydantic types** become the tool's schema (Day 2 → Day 4).

> `@app.get` exposes your function to the **web**; `@agent.tool` exposes it to an **LLM**. Same move.
---
# 4.9 · Where this goes — the decorator you keep meeting

You've now *used* two framework decorators — `@dataclass` and `@app.get` — without writing either. That same "hand your function to a framework" move returns twice more:

| Day | Decorator | The framework then… |
|---|---|---|
| 1 (today) | `@dataclass` · `@app.get` | builds a record · serves a route |
| 3 | `@pytest.fixture` · `@parametrize` | injects test setup · fans a test over data |
| 4 | `@agent.tool` | exposes your function to an **LLM** |

Every one is the same idea you met building this app today.
---
<!-- _class: lab -->

# 🧪 Lab 3 — Local API Server

**80 min** · open `modules/m03-oop-dataclasses-fastapi/lab/README.md` · scaffolds in `starter/`

You'll build (on `Product`, not `BankAccount`):
- `catalog/models.py` — `Product` as a class → `@dataclass` (typed fields, `field(default_factory=list)`)
- `catalog/server.py` — FastAPI app: `GET /products`, `GET /products/{id}`, `POST /products`
- a running server on `localhost:8000` with `/docs`

End of Day 1 → your repo serves a real catalog API.
