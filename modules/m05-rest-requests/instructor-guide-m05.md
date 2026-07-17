# Instructor Guide — Module 5: REST API Client

*Day 2 · 50 min concept + 70 min lab · 20 slides · Written 2026-07-17*

> **How to use this.** Part 1 is the only part you *must* read — it's the frame. Parts 2–3 are the delivery. Part 4 is a bank to raid live: everything is tagged so you can scan it.
>
> `❓` a question they'll ask · `🔥` a war story · `⚡` deeper, only if the room is strong · `▶` a demo you can run
>
> **Nothing in Part 4 is on a slide.** It's there so you can answer without stalling, not so you can cover it. Covering all of it would blow the module by 30 minutes.

---

## Part 1 — Before you walk in

### The spine

**The five-line client that lies to you.**

Open by writing the naive client live. It works. Then show that it lies — and every section today kills one lie:

| Section | The lie it kills |
|---|---|
| **§1** The HTTP request | *"it can't tell you it failed"* — `.json()` on a 404 hands you an error body wearing data's clothes |
| **§2** requests | *"it hangs, and it forgets who you are"* — no `timeout` = forever; a bare `get()` forgets your headers |
| **§3** The APIClient | *"it trusts whatever shape comes back"* — a dict off the wire is not a `BankAccount` |

This is on the slides now (slide 2, the three section headers, the closing slide). **Say the frame out loud at each section boundary** — that's what stops it feeling like a feature list. Every slide should answer *"which lie does this kill?"* If you can't answer that for a slide, skip it; you've found a cut.

Underneath the lies there's one idea, if you want to name it for a senior room: **a client is a trust boundary.** Every line of the `APIClient` is one sentence — *"I used to trust X. I don't anymore."*

### The one thing they must leave with

> **A 404 doesn't raise.** The request succeeded; the answer was just "no". If you don't check, an error body flows into your program as if it were data.

Everything else in M5 is technique. This is the idea that changes how they write code on Monday. If you have 60 seconds left and one thing to repeat, repeat this.

### The shape of the 50 minutes

| Block | Slides | Minutes |
|---|---|---|
| Cold open (slides 1–2) | 2 | **4** |
| §1 The HTTP request | 3–7 | **15** |
| §2 requests | 8–13 | **15** |
| §3 The APIClient | 14–18 | **14** |
| Lab handoff + close (19–20) | 2 | **2** |

Then 70 min of Lab 5. The whole block is 120 min — **there is no slack.** If you're running long, use the cut list below rather than compressing §3, which is where the payoff lands.

### Cut list, in order

1. **2.2 "Python has async"** (−3 min) — the *rule of thumb* line is the value; the `httpx` snippet is optional. Cut the snippet, keep the sentence.
2. **The 401/403 row of the status map** (−1 min) — a nice aside, not load-bearing.
3. **1.1 Verbs** (−3 min) — compress to "GET/PUT/DELETE safe to re-send, POST isn't — hold that thought." §3.3 re-teaches it anyway.
4. **3.3 "POST isn't idempotent"** (−4 min) — *only* if desperate. It's the honesty slide and strong rooms love it, but §3.2 stands without it.

### Never cut

- **1.3 A 404 doesn't raise** — the one thing.
- **3.1's `if not resp.ok`** — it's 1.3 paying off. Cutting it makes 1.3 pointless.
- **3.4 Typed returns** — it's the M4 payoff *and* the Day-4 setup.

### Read the room

- **Strong/senior room** → pull `⚡` items, especially backoff+jitter and the trust-boundary framing. They'll push on retry policy; let them.
- **Struggling room** → drop every `⚡`, spend the time on 1.3 and 3.1, and lean on the demos. The lab only needs `_request` + `list_products` + `create_product` + `count_by_category`.
- **Quiet room** → the cold open is a question, not a statement. Actually wait after *"Ship it?"*.

---

## Part 2 — The cold open (4 min, scripted)

This is the highest-leverage 4 minutes in the module. It sets the frame, and it makes §1.3 land before you've reached §1.

**Setup:** their Lab-4 server running — `uv run uvicorn catalog.server:app --reload`.

> ⚠️ **Domain seam.** The slides say `/accounts` (`BankAccount`); your live server is `/products`. That's the deliberate concept-vs-lab split used all week. Don't apologise for it — say *"same shape, your catalog"* and move on. If it confuses anyone, that's a 10-second answer, not a detour.

### Beat 1 — write it live, and let it work

```python
import requests
products = requests.get("http://localhost:8000/products").json()
```
```
got 5 products, first = 'USB-C Cable'
```

**Say:** *"Five lines. It drives the server you built yesterday. Done? Ship it?"*

**Then actually pause.** Someone will hedge. Whatever they say, you're about to agree with them.

### Beat 2 — break it in one line

```python
data = requests.get("http://localhost:8000/products/99").json()   # no such product
```
```
{'detail': 'Product id 99 not found'}
```

**Say:** *"That's a 404. Notice what didn't happen — nothing raised. And look what `.json()` handed me: a dict. My code wanted a product. It got an error body wearing data's clothes."*

### Beat 3 — the payoff (this is the money shot)

```python
[Product.model_validate(p) for p in data]     # data is a dict, not a list!
```
```
ValidationError: 1 validation error for Product
  Input should be a valid dictionary or instance of Product
  [type=model_type, input_value='detail', input_type=str]
```

**Say:** *"Read that carefully. `input_value='detail'`. It looped over the dict's **keys** and tried to validate the string `'detail'` as a Product. The server told me 'not found' — politely, in JSON — and my program turned that into a crash about the wrong thing, in the wrong place. Nothing here mentions 404."*

**Land it:** *"That's today. This client lies to you three ways, and each section kills one."* → slide 2.

> *(All three outputs above are from a real run against `solution/` on 2026-07-17 — they're what you'll actually see.)*

**If you have no server / no time:** do it in the notebook instead — §1 cell `1.4` shows the same 404-doesn't-raise beat offline. You lose the drama; you keep the point.

---

## Part 3 — Slide by slide

### Slide 1 · Title
Nothing to say. Move.

### Slide 2 · The five-line client
**Beat:** the map of the whole module.
**Do:** if you ran the cold open, this slide *is* the recap — 20 seconds, point at the three lies, go. Don't re-explain.
**Don't:** read the table aloud. They just watched it happen.

---

### Slide 3 · §1 header — The HTTP request
**Beat:** *"The lie: it can't tell you it failed."*
**Say:** *"To check whether the server said no, you have to know what 'no' sounds like. That's this section — it's vocabulary. §3 is where we enforce it, and you can't enforce what you can't name."*

### Slide 4 · 1.1 Verbs — which are safe to retry
**Beat:** sets up the *only* question that matters for retry: does sending it twice do harm?
**Open with the question, not the taxonomy:** *"If I send this twice, what breaks?"* Then let them classify DELETE and POST themselves.
**Aha:** idempotent isn't jargon for its own sake — it's the yes/no that decides whether retry is legal.
❓ *"So we can't retry POST?"* → **Gift.** *"Slide 3.3 is literally your question. Hold it."* (The deck anticipating a student is worth real credibility.)

### Slide 5 · 1.2 The status-code map
**Beat:** vocabulary — and a callback, not new material.
**Do this, don't lecture:** put the table up and ask *"which of these has your server already sent you?"* They wrote 201, 204, 404, 409 in Labs 3–4. **422 is the one to dwell on** — that's M4's automatic Pydantic error; they saw that exact JSON yesterday.
**Say:** *"You wrote most of this table. You just didn't know it was a table."*
🔥 the 401/403 mnemonic: *"401 = who are you? 403 = I know exactly who you are, and no."*
⚡ Why 422 and not 400 → Part 4.

### Slide 6 · 1.3 A 404 doesn't raise ⭐
**Beat:** THE slide. The one thing.
**Open:** *"Here's the one that costs people an afternoon."*
**Aha (say it exactly):** *"An **exception** means the round trip failed — nobody answered. A **status code** means it worked and you didn't like the answer. `requests` only raises for the first one."*
**Then:** `raise_for_status()` exists precisely because you must *choose* to care.
**Point forward:** *"§3.1 makes that choice once, in one place, forever."*
❓ *"Why not just use `raise_for_status()` everywhere?"* → the best question in the module. Part 4 has the answer. **Don't rush it.**
▶ Code-along: notebook §1.

### Slide 7 · 1.4 Why retry hinges on the code
**Beat:** turns the map into a policy.
**Say:** *"4xx is a refusal — send it again, get refused again, forever. 5xx is a stumble — it might work in a second. So: retry 5xx and network errors, never 4xx. One line. That's the whole policy."*
**Point forward:** *"§3.2 doesn't just follow that rule — it's shaped so it can't break it."*
❓ *"What about 429?"* → strong student. Part 4.

---

### Slide 8 · §2 header — requests
**Beat:** *"The lie: it hangs, and it forgets who you are."*
**Say the unifier, or this section IS a feature list:** *"Four things here look unrelated — await, Session, `json=`, auth. They're one idea: **configure the boundary once**. One connection, one timeout, one header, set up front — instead of remembering them at every call site."*
This is the section that most needs the frame. Don't skip that sentence.

### Slide 9 · 2.1 Where's the `await`?
**Beat:** pre-empts a distraction before it derails you.
**Do:** ask *"anything missing from this line?"* Someone says `await`. *"Right. And it's not a bug."*
**Aha:** blocking is the *simple* choice, and simple is correct for scripts, tests, and imports. There's no UI thread to starve.

### Slide 10 · 2.2 Python has async
**Beat:** closes the door so nobody's still thinking about it.
**Value is one sentence:** *"scripts and tests → sync. Servers under load → async."*
**Day-1 callback worth making:** their FastAPI routes were `def`, not `async def`, and worked fine — FastAPI ran them in a threadpool. They already chose the simple spelling without knowing it.
**First cut if you're long.**

### Slide 11 · 2.3 A Session, with a timeout
**Beat:** kills *"it forgets who you are"* AND *"it hangs"*.
**Say:** *"`timeout` is not optional. The default is `None`. `None` means **forever**."*
🔥 The 3am bulk import → Part 4. Best war story in the module; costs 30 seconds.
▶ The hang demo → Part 4. **If you run one extra demo all module, run this one** — the silence does the teaching.
⚡ What a Session actually reuses → Part 4.
▶ Code-along: notebook §2.

### Slide 12 · 2.4 `json=` — sending a body
**Beat:** kills a lie they'll hit in the lab within 20 minutes (`create_product`).
**Aha:** `json=` is two jobs — body *and* `Content-Type`. `data=` form-encodes, and FastAPI won't read it.
**The callback is the whole slide:** Lab 4 made them keep `-H 'Content-Type: application/json'` on that curl, or they got *"a 422 for the boring reason"*. **`json=` is that header, in Python.** They've already been bitten by this — from the other side.

### Slide 13 · 2.5 Auth — a token in a header
**Beat:** configure the boundary once, secrets included.
**Aha:** it's not about auth mechanics — it's about *where the secret lives*. URL → server logs and browser history. Source → git, forever.
**Keep it tight.** This slide invites a 10-minute secrets tangent. Don't take it.
⚡ basic vs bearer → Part 4 (not on the slide; the outline promises it, the deck doesn't deliver it — see Part 6).

---

### Slide 14 · §3 header — The APIClient
**Beat:** *"The lie: it trusts whatever shape comes back."*
**Say:** *"Everything until now was rules and tools. Now we spend them — and every lie dies in the same five lines."*

### Slide 15 · 3.1 One `_request` funnel
**Beat:** the payoff of §1.3.
**Do:** *"Five methods each remembering url-join, timeout, and an error check. How many places is that to forget the timeout?"* → five.
**The line that matters:** *"`if not resp.ok` — that's slide 1.3, paid off. A 404 won't raise itself, so the funnel raises for it. Write it once and no caller ever imports `requests` again."*
❓ *"Why `APIError` instead of `raise_for_status()`?"* → Part 4.

### Slide 16 · 3.2 The retry loop
**Beat:** §1.4's rule made structural.
**The insight to sell:** *"Don't read this as 'the retry loop'. Read what the `except` catches: **only** network faults. A 4xx can't reach it — physically. It becomes an `APIError` after the loop. The rule isn't a comment here. It's the shape."*
**Ask:** *"What happens if I move the `ok` check inside the try?"* → you'd retry 422s forever. That's the lab's real design question.
⚡ Exponential backoff + jitter → Part 4.
❓ *"Why 3 and 0.2?"* → Part 4.

### Slide 17 · 3.3 But POST isn't idempotent…
**Beat:** honesty. Pays off 1.1.
**Why it earns its slide:** most courses would hide this. *"We're retrying every verb, POST included. That's a real risk, and here's exactly why we get away with it: our ids are client-supplied, so a double POST hits the duplicate rule → 409 → recorded in the report. Not a silent second product."*
**Land:** *"The catalog's own rule is what makes this safe. Without it you'd scope the loop to idempotent verbs. Know which world you're in."*
🔥 The double-charge → Part 4.

### Slide 18 · 3.4 Typed returns
**Beat:** kills the last lie, and it's the M4 payoff.
**Aha:** *"Return the raw dict and a server that drops a field blows up three functions later, mysteriously — exactly like the cold open. Validate here and it fails **now**, with a field name."*
**Bookend the module:** this is the cold open, fixed. Say that.
❓ *"The server already validated. Why again?"* → **the deepest question in M5.** Part 4.
▶ Code-along: notebook §3.

### Slide 19 · Lab 5
Four TODOs: `_request`, `list_products`, `create_product`, `count_by_category`. The `FakeSession` is given — **no server needed**.
**Say:** *"`count_by_category` is Lab 3's `group_by_category`, except the catalog is on another machine now and your counting code doesn't notice. On Day 4 the agent calls that method to answer 'how many electronics do we have?' You're writing an agent tool right now."*

### Slide 20 · Closing
**Beat:** the payoff. *"Five lines → a client you'd trust at 3am."* Every lie dead. Then the forward pointer: Day 3 mocks that `session=` seam; Day 4 turns these methods into tools.

---

## Part 4 — The extras bank

### ❓ Questions they will ask

**❓ "Why not just use `raise_for_status()`?"** *(the best question in the module)*
Three reasons, in order of weight:
1. **It ties every caller to `requests`.** `raise_for_status()` throws `requests.HTTPError`. Now anyone who wants to catch it must `import requests` — including your tests, and Day 4's agent. `APIError` is *yours*; the dependency stops at the client's edge.
2. **It throws away the detail.** Their server sends `{"detail": "Product id 99 not found"}`. `raise_for_status()` gives you a generic message; `_extract_detail` keeps the server's own words. Lab 6's import report is built from exactly that string.
3. **You'd still repeat it five times.** The funnel is the point.
*Escape hatch:* *"Short version — it raises someone else's exception type. Slide 3.1 raises ours."*

**❓ "The server already validated with Pydantic. Why validate again in the client?"** *(the deepest one)*
Different trust boundary. **M4 = don't trust the caller. M5 = don't trust the callee.** The server validated its *input*; you're validating that the server kept its *contract*. It's a different program — possibly a different version, possibly another team's, possibly a proxy that mangled something. And the cold open is the proof: the thing that came back wasn't a product at all, and the server was behaving perfectly.
*Escape hatch:* *"Hold that — it's exactly what Day 3 tests."*

**❓ "Why 3 retries? Why 0.2 seconds?"**
Honest answer: **they're a budget, not a truth.** 3 × 0.2s = 0.6s of added worst-case latency, which is cheap. Pick numbers by asking "how long may this call take before someone notices?" Real systems use exponential backoff + jitter (`⚡` below) and cap *total elapsed time*, not attempts.

**❓ "Shouldn't we retry 429 (rate limited)?"** *(strong student)*
Yes — in real life. 429 is the one 4xx that *is* retryable, because the server is telling you *"not now"*, not *"never"*. And it usually tells you when: the `Retry-After` header. We don't handle it here because their catalog never sends one. **Say "good catch"** — this is a genuine hole in the simple rule, and admitting it is better than defending it.

**❓ "Why isn't this async?"** → slides 2.1/2.2 answer it. If asked early: *"Two slides away."*

**❓ "Why does the loop retry POST if POST isn't idempotent?"** → slide 3.3. *"Your question is literally the next slide."*

**❓ "Why not `httpx` / `aiohttp`?"**
`httpx` is a fine choice — near-identical API, plus async and HTTP/2. `requests` is the lingua franca: every StackOverflow answer, every legacy script, every LLM's default. Learn `requests`, and `httpx` costs you an afternoon. Also: **everything today transfers** — Session, timeout, `json=`, status codes are HTTP, not a library.

**❓ "What if the server returns 200 with garbage?"** → slide 3.4. `model_validate` is the only thing standing between garbage and your program.

---

### 🔥 War stories

**🔥 The 3am bulk import** *(for 2.3 — the best one, 30 seconds)*
`requests`' default timeout is `None`. Not 30 seconds. Not 60. **`None` means wait forever.** Someone kicks off a CSV import of 10,000 rows before going home. Row 4,000 hits a server that accepts the connection and then says nothing — no error, no reset, just silence. The script is *still sitting there* at 3am. It didn't crash. It didn't finish. It didn't log. Nothing to alert on, because nothing failed. That's why `timeout` isn't optional.

**🔥 The retry storm** *(for 3.2)*
A service gets slow. Every client retries. Now it has 3× the traffic — *because* it was struggling. It falls over properly. The clients retry harder. This is why real backoff is exponential **and jittered**: without jitter, every client retries at the same instant and you've built a synchronised hammer.

**🔥 The double charge** *(for 3.3)*
A payment API times out. Did the charge go through? Nobody knows — the reply got lost, not the request. Retry and you might charge twice; don't and you might charge zero. This exact problem is why idempotency keys exist: the client generates a unique key per *intent*, the server remembers it, and a repeat is a no-op that returns the original result. Their catalog gets the same protection for free from client-supplied ids — which is what slide 3.3 is really saying.

**🔥 The 404 that became data** *(the cold open — your own demo)*
Worth naming explicitly: the bug didn't crash where the mistake was. The mistake was at the HTTP boundary; the crash was in a Pydantic validator, complaining about a string called `'detail'`. **Distance between cause and symptom is the whole cost of not validating at the boundary.**

---

### ⚡ Deeper mechanics (strong rooms only)

**⚡ What a `Session` actually reuses**
Not "the headers" — that's the visible part. It keeps a **connection pool**: the TCP handshake *and* the TLS handshake (the expensive one — multiple round trips) are paid once and reused. Over HTTPS with 100 sequential calls, a Session is often several times faster than 100 bare `requests.get`s, and the difference is nearly all handshake.

**⚡ `timeout` is two numbers**
`timeout=5` means *5s for connect and 5s for read, separately* — worst case is ~10s. You can split them: `timeout=(3, 30)` — 3s to establish, 30s to wait for the body. Useful when the server is fast to greet and slow to think. And note: it's **not** a total-elapsed budget. Nothing in `requests` gives you that.

**⚡ Exponential backoff + jitter**
Their loop sleeps a flat 0.2s. Production: `sleep(base * 2**attempt + random.uniform(0, jitter))` → 0.2, 0.4, 0.8… The doubling gives the server room to recover; the jitter de-synchronises the herd. `urllib3`'s `Retry` adapter does this for you and mounts onto a Session — worth naming if someone asks "surely this is a solved problem?"

**⚡ `Retry-After`**
On 429 and sometimes 503, the server tells you when to come back — seconds, or an HTTP date. Honoring it is strictly better than guessing. Ignoring it is how you get banned.

**⚡ Why 422 and not 400?**
400 = *"I can't even parse this."* 422 = *"I parsed it fine; it's just wrong."* Their JSON was syntactically perfect and semantically invalid (`price: -1`), which is exactly 422's meaning — Unprocessable Content. FastAPI returns it automatically for a Pydantic body failure. It's a fine distinction most APIs get wrong; theirs gets it right for free.

**⚡ `verify=False`**
It will appear in the first StackOverflow answer they find for a TLS error, and it disables certificate verification — i.e. turns off the part that makes HTTPS mean anything. If someone suggests it: *"That's not fixing the error, that's agreeing to be MITM'd."*

---

### ▶ Demos

**▶ The cold open** — Part 2. Verified output there.

**▶ The hang** *(for 2.3 — 60 seconds, huge payoff)*
A server that accepts and never replies:
```bash
nc -l 8011          # in a second terminal
```
```python
requests.get("http://localhost:8011")            # no timeout
```
**Then just stand there.** Let it get uncomfortable — 10 seconds of nothing is the entire lesson. *"It's not broken. It's doing exactly what I asked: wait. Forever."* Ctrl-C, then:
```python
requests.get("http://localhost:8011", timeout=2)
# raised ReadTimeout after 2.0s
```
*(Verified 2026-07-17: no timeout → still waiting after 4s, no exception. `timeout=2` → `ReadTimeout` in 2.0s.)*

**▶ The double POST** *(for 3.3 — 30 seconds)*
Send the identical create twice against their server:
```python
p = {"id": 77, "name": "Demo Widget", "category": "Electronics", "price": 100.0}
requests.post(U, json=p)   # 201 {'name': 'Demo Widget', ..., 'id': 77}
requests.post(U, json=p)   # 409 {'detail': 'Product id 77 already exists'}
```
*"That 409 is what makes retrying POST survivable here — the server refuses to duplicate. Take away client-supplied ids and this same demo quietly creates **two** products."*
*(Verified 2026-07-17 against `solution/`.)*

---

## Part 5 — Callback ledger

**Backward** — every one of these is "you already did this", which is worth more than any new fact:

| Slide | Calls back to |
|---|---|
| 1.2 status map | **their own `server.py`** — 201, 204, 404, 409 they wrote in Labs 3–4 |
| 1.2 · 422 | **M4** — the automatic Pydantic error, whose JSON they saw in Lab 4's expected output |
| 2.2 async | **Day 1** — their routes were `def`, not `async def`, and worked (threadpool) |
| 2.4 `json=` | **Lab 4's curl** — `-H 'Content-Type: application/json'`, the "422 for the boring reason" |
| 3.1 funnel | **M1** — functions exist so you write it once |
| 3.4 `model_validate` | **M4 §3.1** — dict → model, validated |
| Lab · `count_by_category` | **Lab 3's `group_by_category`** — same counting code, remote catalog |

**Forward** — say these; they're why the module isn't a detour:

- **M6 (next):** the `APIError` you raise becomes a row in the import report. 409 = "fix the conflict", ValidationError = "fix the row".
- **Day 3 / M8:** that `session=` parameter is the **mock seam**. Tests hand it a fake and never touch the network. *Same pattern, different seam,* as Day 4's `llm_client`.
- **Day 4 / M11:** `list_products`, `count_by_category`, `search_products` **become the agent's tools**, unchanged. The LLM calls the methods they wrote today.

---

## Part 6 — Known seams & live decisions

Things you may get asked, or may want to decide before you walk in. **None of these are bugs in the material** — they're open questions logged in `private_teaching_content_prep/HANDOFF.md`.

- **`BankAccount` vs `Product`.** Slides and notebook teach on `BankAccount`; the lab is `Product`. Deliberate — concept-vs-lab seam, used all week. One sentence if anyone notices.
- **The JS bridges are an unresolved bet.** Slides 2.1 and 2.3 lean on `await`/`fetch` and `axios.create`. That was added on the basis that the room is React/TS, but the outline says the audience is broad/senior (SWE, QA, DevOps, AI/ML, leads) — logged as **D-audience**, still open. **If the room is mixed, those analogies land for only part of it.** The ideas stand alone: *"`requests` blocks"* and *"a Session configures once and reuses"* need no JS. Read the room and drop the nouns if they're not landing. (This guide deliberately adds no new JS bridges.)
- **Query params and basic-vs-bearer are not taught.** The outline promises both for M5; the deck delivers neither. `params=` can't be taught honestly until a route accepts one — `GET /products` currently takes no arguments, so a student passing `?category=Electronics` would get all 5 back and think they broke it. If someone asks about query params: *"Real APIs filter server-side with `?category=…`; ours doesn't yet — you'd add it to the route."* That's an honest answer and a genuinely good stretch task.
- **⚠️ Don't screen-share `capstone-project/solution/` during M5.** `solution/client.py` still wears an `@retry` decorator with a `decorators.py` beside it — the pre-refactor state, which directly contradicts M5's "retry is a plain loop; you never write decorators". A fix is logged; until then, the starter and the graders are the safe things to show.

---

## Appendix — the module in one breath

> *You built a server yesterday. Today you write the program that drives it. The naive version is one line and it works — and it lies to you three ways: it can't tell you it failed, it hangs forever and forgets who you are, and it trusts whatever shape comes back. §1 teaches you to name the failure. §2 configures the boundary once. §3 spends both in a single funnel, and every lie dies in the same five lines. What's left is a client you'd trust at 3am — which, on Day 4, is the agent's toolbelt.*
