---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 2 · Automate It — Validation & a Typed Client"
footer: "Acuity Training · Day 2 of 4"
---

<!-- _class: title -->

# Module 5
## REST API Client — automate & validate
**3 sections · ~50 min** — each builds on the last; we code each one live
1 The HTTP request · 2 requests · 3 The APIClient
---
# The five-line client

M4 gave us validated models and a typed server. Here's the Python that drives it:

```python
accounts = requests.get("http://localhost:8000/accounts").json()
```

**It works.** Ship it? — It also **lies to you**, three ways. Each section today kills one:

```text
§1  it can't tell you it FAILED   .json() on a 404 hands you an
                                  error body wearing data's clothes
§2  it hangs · it forgets you     no timeout = forever; a bare get()
                                  forgets your headers on every call
§3  it trusts the SHAPE           a dict off the wire is not a BankAccount
```

By the end it's an `APIClient` you'd trust at 3am — and on **Day 4, these methods become the agent's tools.**
---
<!-- _class: section -->

# Section 1 · The HTTP request
## verbs → the status-code map → the 404 that doesn't raise → the retry rule
**The lie we kill:** *"it can't tell you it failed."* Learn to name what the server actually said — §3 enforces it, and you can't enforce what you can't name.
---
# 1.1 · Verbs — which are safe to retry

A retry **re-sends the identical request** — so the only question is: *does sending it twice do harm?* **Idempotent** = same end state no matter how many sends.

```text
DELETE /accounts/5   ×2  → still just "deleted"     (idempotent → safe to retry)
POST   /accounts {…} ×2  → TWO accounts created     (not idempotent → retry double-creates)
```

`GET`/`PUT`/`DELETE` are idempotent; `POST` isn't. Hold that thought — **§3.3 has to answer for it.**
---
# 1.2 · The status-code map

Three families: **2xx** you're fine · **4xx** *you* broke it · **5xx** *they* broke it. Then the ones you'll actually meet:

```text
200  OK              GET /accounts — it worked
201  Created         your @app.post(..., status_code=201)
204  No Content      your @app.delete(...) — nothing to send back
401  Unauthorized    "who are you?"
403  Forbidden       "I know who you are — no."
404  Not Found       your CatalogError → 404
409  Conflict        your duplicate-id rule → 409
422  Unprocessable   FastAPI's automatic Pydantic error — M4's payoff
500  / 503           the server stumbled — a retry might win
```

**You wrote most of this table.** 201, 204, 404, 409 and 422 all come out of the server *you* built — this is a callback, not new vocabulary.
---
# 1.3 · A 404 doesn't raise

The request **succeeded** — the server heard you and said *no*. `requests` has nothing to complain about, so it stays quiet.

```python
r = session.get(f"{url}/accounts/99")   # no such account
# ...nothing raised. The round trip worked.
r.status_code            # 404
r.ok                     # False
r.json()                 # {'detail': 'Account 99 not found'}

r.raise_for_status()     # NOW it raises — requests.HTTPError
```

An **exception** means the round trip itself failed (`ConnectionError`, `Timeout`) — §1.4's retry case. A **status code** means it worked and you didn't like the answer. So you must *choose* to care: check `.ok`, or call `raise_for_status()`.

<div class="code-along">▶ Code-along now → notebook Section 1 — read a status code; watch a 404 not raise</div>
---
# 1.4 · Why retry hinges on the code

A **4xx** means the server *understood you and refused* — your request is wrong, so sending it again gets the **same** refusal. A **5xx** (or dropped connection) is the server *stumbling* — the same request might work a moment later.

```text
POST {bad json} → 422 → retry → 422 → 422 …   (never recovers — don't retry)
GET  /accounts  → 503 → retry → 200           (server recovered — retry won)
```

So: **retry 5xx + network errors, never 4xx.** That one line is the whole policy — **§3.2 makes the code obey it.**
---
<!-- _class: section -->

# Section 2 · requests
## where's the await? → Session + timeout → json= a body → auth
**The lie we kill:** *"it hangs, and it forgets who you are."* Configure the boundary **once** — one connection, one timeout, one header.
---
# 2.1 · Wait — where's the `await`?

You're about to see `resp = session.get(url)` with **no `await`**. That's not a typo. `requests` is **blocking**: the line stops, waits for the server, then hands you the answer.

```python
# JS — the network is always async
const r = await fetch(url);  const data = await r.json();

# Python + requests — the line just waits
r = session.get(url);        data = r.json()
```

**Why that's right here:** there's no UI thread to starve — this is a script, not a browser. Blocking is the *simple* choice, and simple is correct for scripts, tests, and imports.
---
# 2.2 · Python *has* async — it's a choice, not an absence

Async HTTP exists (`httpx`, `aiohttp`) and you'd reach for it when one process must hold **thousands** of connections at once. That's a server's problem, not ours.

```python
async def main():                       # the async flavour, for reference
    async with httpx.AsyncClient() as c:
        r = await c.get(url)            # there's your await
```

> **The Day-1 callback:** your FastAPI routes were `def`, not `async def` — and they worked. FastAPI runs a plain `def` route in a **threadpool** so blocking code can't stall the server. Both spellings are allowed; you picked the simple one without knowing it.

**Rule of thumb:** scripts & tests → sync `requests`. Servers under load → async.
---
# 2.3 · A Session, with a timeout

Each bare `requests.get(...)` opens a **new** TCP connection and forgets your headers. A `Session` keeps one alive and carries them across every call — it is **`axios.create({ baseURL, headers })`**: configure once, reuse everywhere. And **`timeout` is not optional** — omit it and a server that never replies blocks your thread *forever*.

```python
s = requests.Session()       # one connection, reused; headers remembered
s.get(url)                   # ⚠️ no timeout → hangs forever if the server stalls
s.get(url, timeout=5)        # ✓ raises after 5s instead of hanging
```

<div class="code-along">▶ Code-along now → notebook Section 2 — a Session with timeout, a JSON body, and auth</div>
---
# 2.4 · `json=` — sending a body

`json=` does **two** jobs: it serialises the body *and* sets `Content-Type: application/json`. `data=` form-encodes instead — and FastAPI won't parse that as JSON.

```python
s.post(url, json={"owner": "Ada", "balance": 1500})   # ✓ body + Content-Type, both handled
s.post(url, data={"owner": "Ada", "balance": 1500})   # ✗ form-encoded → FastAPI can't read it → 422
```

> **You've met this already — from the other side.** Lab 4 told you to keep `-H 'Content-Type: application/json'` on that curl, or you'd get "a 422, but for the boring reason". **`json=` *is* that header**, in Python.

Lab 5's `create_product` is exactly this move: `json=payload.model_dump()`.
---
# 2.5 · Auth — a token in a header, from the environment

Auth is just a header you set **once** on the session; every later call carries it. The trap is *where* the secret lives — a token in the URL lands in server logs and browser history (leaked forever); a token in source lands in git.

```python
# ❌ token in the URL → logged everywhere it travels
s.get(f"{url}?api_key={TOKEN}")
# ✓ token in a header, value from an env var → never logged, never committed
s.headers["Authorization"] = f"Bearer {os.environ['TOKEN']}"
```
---
<!-- _class: section -->

# Section 3 · The APIClient
## _request funnel → the retry loop → typed/validated returns
**The lie we kill:** *"it trusts whatever shape comes back."* One funnel — and every lie above dies in the same five lines.
---
# 3.1 · One `_request` funnel

Five CRUD methods each repeating url-join + timeout + error-check = five places to get wrong (and one route quietly missing a timeout). Funnel it: write that **once**, and every public method becomes a one-liner that *can't* forget the timeout.

```python
def _request(self, method, path, **kw):
    resp = self._session.request(method, self.base_url + path, timeout=5, **kw)
    if not resp.ok:
        raise APIError(resp.status_code, resp.text)   # non-2xx → a clean error
    return resp

def delete_account(self, id):  self._request("DELETE", f"/accounts/{id}")   # one line
```

**That `if not resp.ok` is §1.3 paying off** — a 404 won't raise itself, so the funnel raises for it. One check, and no caller ever imports `requests`.
---
# 3.2 · The retry loop — §1.4's rule, in code

Because *every* call funnels through `_request`, the retry goes in **one place** and every method inherits it. Look at what the `except` catches: **only** network errors. A 4xx never reaches it — it becomes an `APIError`, raised *after* the loop. §1.4's "retry 5xx + network, never 4xx" isn't a convention here; it's the shape of the code.

```python
for attempt in range(1, 4):
    try:
        resp = self._session.request(method, url, **kw)
        break                                   # got an answer — done looping
    except (ConnectionError, Timeout):          # ONLY transient faults
        if attempt == 3: raise                  # out of tries — give up
        time.sleep(0.2)                         # else wait, go again

if not resp.ok:
    raise APIError(resp.status_code, ...)       # a 422 lands HERE — never retried
```
---
# 3.3 · But §1.1 said `POST` isn't idempotent…

Right — and this loop retries **every** verb, `create_product` included. A timeout can mean **the server did the work and the reply got lost**; retrying then sends it twice. We accept that here for one specific reason:

```text
our ids are client-supplied → a double POST hits the
duplicate-id rule → 409, recorded in the report (M6)
…not a silent second product
```

The catalog's own rule is what makes retry-everything safe here. **Without it you'd scope the loop to idempotent verbs** — real clients do exactly that, or send an idempotency key. Know which world you're in.
---
# 3.4 · Typed returns — validate at the boundary

Return the raw dict and a server that drops `balance` blows up *three functions later*, mysteriously. Parse into the **M4 model** right here instead — a bad response fails **now**, with a field-level error, and callers get real `BankAccount` objects (types, autocomplete).

```python
def list_accounts(self) -> list[BankAccount]:
    data = self._request("GET", "/accounts").json()       # list of dicts off the wire
    return [BankAccount.model_validate(r) for r in data]  # validated → fails here if malformed
```

This is what **"validating API responses"** means in practice.

<div class="code-along">▶ Code-along now → notebook Section 3 — build AccountClient: _request, the retry loop, Pydantic returns</div>
---
<!-- _class: lab -->

# 🧪 Lab 5 — Build the `APIClient`

**70 min** · open `modules/m05-rest-requests/lab/README.md`

You'll build (on `Product`, not `BankAccount`):
- `catalog/client.py` — `APIClient` + `APIError`, one `_request` funnel
- the retry loop in the funnel — transient faults only, never a 4xx
- full typed CRUD: `list` / `get` / `create` / `delete` → `list[Product]` / `Product` (validated)
- `count_by_category()` — Lab 3's `group_by_category`, now over the wire (and Day 4's first agent tool)

End state: `APIClient().list_products()` returns `list[Product]`.
---
> **Five lines → a client you'd trust at 3am.** Every lie is dead: it *reports* failure (`APIError`), it *can't* hang (`timeout`), it *survives* a blip (the retry loop), and it hands back real `BankAccount` objects instead of a dict that might be an error. On **Day 4 these same methods become the agent's tools.**
>
> **Where the *testing* comes:** Day 3 / M8 wraps this client in a pytest suite — mocking `requests` so tests don't need a live server, and parametrizing across status codes. M5 builds & validates; Day 3 tests systematically.
