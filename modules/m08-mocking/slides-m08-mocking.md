---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 3 · Test It — pytest, Mocking, Coverage & CI"
footer: "Acuity Training · Day 3 of 4"
---

<!-- _class: title -->

# Module 8
## Mocking & Parametrize — Testing the APIClient
**5 sections · ~60 min** — doubles → mock → parametrize → unhappy path → workflow
1 Test doubles · 2 Mock the session · 3 Parametrize · 4 Unhappy path · 5 Import workflow
---
# M7 tested code with no dependencies. The client has one: a server.

The catalog was easy — pure logic, no I/O. But the `APIClient` **talks to a server**, and a unit test can't depend on a live server being up, seeded, and fast.

The fix is the seam you already built: the client takes its `session` by **injection** (M5). In a test, hand it a **fake** one.
---
<!-- _class: section -->

# Section 1 · Test doubles
## Don't test against the real server — swap it for a **stand-in you control.**
## The client's injected `session` is the seam that lets you.
---
# 1.1 · Why not hit the real server

A real server in a unit test is **slow** (network), **flaky** (down, or the data shifted), and **stateful** (your POST test leaves junk for the next run). Unit tests must be **fast and isolated** — same result every time, no setup.

```text
real server:  needs uvicorn up + seeded + reachable + reset between runs
test double:  answers instantly, the same way, every time
```
---
# 1.2 · A test double — a stand-in you control

You don't need the real session — only its *behavior*: a `.request()` that returns a response. Swap in a **double** through the injection seam from M5.

```python
client = AccountClient(session=FakeSession(...))   # no network — you decide the answers
```
---
# 1.3 · Stub vs mock vs fake

| Double | What it does | You use it to… |
|---|---|---|
| **stub** | returns canned answers | feed the code an input |
| **mock** | records how it was called | **assert** the code called it right |
| **fake** | a real-but-lightweight impl | stand in for a heavy dependency |

Same idea — swap the real thing — a different question each one answers.
---
<!-- _class: section -->

# Section 2 · Mock the session
## Give the client a canned response → test its logic with no network.
## `unittest.mock` builds the double for you **and records the call.**
---
# 2.1 · A hand-written fake session

The simplest double: a small object with the `.request()` the client calls, returning a canned response. Inject it; the client never knows it isn't real.

```python
class FakeSession:
    def __init__(self, status, payload): self.status, self.payload = status, payload
    def request(self, method, url, **kw):
        return FakeResponse(self.status, self.payload)

AccountClient(session=FakeSession(200, [{"id": 1, "owner": "Ada", "balance": 1500.0}])).list_accounts()
```
---
# 2.2 · `unittest.mock` — the double, built for you

`Mock()` fakes any object; set `.return_value` for what a call returns. No class to write — and it **remembers every call.**

```python
from unittest.mock import Mock
session = Mock()
session.request.return_value = Mock(ok=True, status_code=200,
    json=lambda: [{"id": 1, "owner": "Ada", "balance": 1500.0}])
AccountClient(session=session).list_accounts()
```
---
# 2.3 · A mock lets you assert *how* it was called

Beyond the return value, the mock recorded the call — so you can assert the client sent the **right request** (the GET to the right path), not just that it returned something.

```python
session.request.assert_called_with("GET", "http://server/accounts", timeout=5)
```

That's the **mock** question: not just "what came back" but "did my code call it correctly".
---
<!-- _class: section -->

# Section 3 · Parametrize
## One test body, a **table** of cases — data-driven testing.
## Run the client against every status code without copy-pasting the test.
---
# 3.1 · `@pytest.mark.parametrize` — one test, many cases

Instead of five near-identical tests, write **one** and feed it a table of inputs. pytest runs it once per row and reports each separately.

```python
@pytest.mark.parametrize("amount, expected", [(50, 150.0), (0, 100.0)])
def test_deposit(amount, expected):
    acct = BankAccount(1, "Ada", 100.0); acct.deposit(amount)
    assert acct.balance == expected
```
---
# 3.2 · Parametrize the status codes

The real payoff: drive the mocked client across every response code in **one** test — a 2xx returns a model, a 4xx raises `APIError`.

```python
@pytest.mark.parametrize("status", [400, 404, 409])
def test_4xx_raises_apierror(status):
    client = AccountClient(session=FakeSession(status, {"detail": "no"}))
    with pytest.raises(APIError):
        client.list_accounts()
```
---
# 3.3 · The one that *does* hit a server

Keep a few **integration** tests that drive a live server — but **mark** them, so the fast unit run skips them.

```python
@pytest.mark.integration
def test_against_live_server():
    client = AccountClient(base_url="http://localhost:8000")   # a real session
    assert isinstance(client.list_accounts(), list)
```

`pytest -m "not integration"` runs the fast suite; CI runs both.

<div class="code-along">▶ Code-along now — mock the client, assert the call, parametrize the status codes</div>
---
<!-- _class: section -->

# Section 4 · Testing the unhappy path
## Mocks let you trigger failures you **can't** reproduce live — a dropped
## connection, a timeout — and prove the client recovers (or doesn't).
---
# 4.1 · Force a transient failure — prove `@retry` recovers

You can't make a real server blip on cue; a mock can — **fail twice, then succeed.** Assert the client **retried**: the call happened 3 times.

```python
def test_retry_recovers():
    session = Mock()
    session.request.side_effect = [ConnectionError(), ConnectionError(),
                                   Mock(ok=True, json=lambda: ACCOUNTS)]
    AccountClient(session=session).list_accounts()
    assert session.request.call_count == 3      # 2 fails + 1 success
```
---
# 4.2 · A 4xx is *never* retried — the policy, proven

A 404 raises `APIError`, not a network error — so `@retry`'s exception tuple never catches it. The mock proves it: called exactly **once**.

```python
def test_4xx_not_retried():
    session = Mock()
    session.request.return_value = Mock(ok=False, status_code=404, text="x")
    with pytest.raises(APIError):
        AccountClient(session=session).list_accounts()
    assert session.request.call_count == 1      # no retry on a 4xx
```
---
<!-- _class: section -->

# Section 5 · Testing the import workflow
## Mock the client, feed the importer a tricky CSV, and assert the **report** —
## the three buckets M6 promised. That report is the day's real deliverable.
---
# 5.1 · Mock the client, run the importer

The importer takes the client by **injection** too — so a test passes a fake that creates accounts but raises `APIError` on a duplicate id. Feed it rows with a bad one and a dup.

```python
client = FakeClient(dup_ids={1})        # a fake that 409s on id 1
report = import_accounts(rows, client)  # rows: one good, one dup, one invalid
```
---
# 5.2 · Assert the report — the three buckets stay apart

The report *is* the contract: a bad row lands in `validation_errors`, a duplicate in `api_errors`, the rest in `created`. Pinning this shape is what Day 3 exists for.

```python
assert report["summary"]["created"] == 1
assert report["summary"]["validation_errors"] == 1
assert report["summary"]["api_errors"] == 1
```

<div class="code-along">▶ Code-along now — test `@retry` recovery + the import report's three buckets</div>
---
<!-- _class: lab -->

# 🧪 Lab 8 — Test the `APIClient` (mocked + integration)

**~60 min** · open `labs/lab-08-test-apiclient.md`

You'll write (testing your `Product` `APIClient` + importer):
- `tests/test_client.py` — mock the session; typed returns + `APIError`; `parametrize` `200/400/404/500`; **`@retry` recovery + no-retry-on-4xx**
- `tests/test_import.py` — mock the client, run `import_csv`, assert the **report's 3 buckets**
- a `TestIntegration` class marked `@pytest.mark.integration` (live server)

**The same mocking pattern returns on Day 4 to mock the LLM.**
