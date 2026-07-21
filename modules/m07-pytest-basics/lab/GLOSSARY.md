# Module 7 — Glossary

Key terms for **testing fundamentals & pytest basics**. General concepts — not tied to any one example. Read once before the lab.

## Why we test

| Term | Plain English |
|---|---|
| **Test** | A saved, automated check that re-runs in seconds — so you change code without fear. |
| **Test suite** | The full collection of tests run together. |
| **Regression** | When a change silently breaks something that used to work. |
| **Regression test** | A saved check that catches a regression before you ship it. |
| **Manual testing** | Running the code and eyeballing the output by hand — works once, doesn't scale. |
| **Automated testing** | The machine runs the checks and asserts the result every time. |

## Kinds of test

| Term | Tests… | Speed / scope |
|---|---|---|
| **Unit test** | One piece in isolation, no I/O. | Fast — most of your tests. |
| **Integration test** | Real parts wired together (server, DB). | Slower, more realistic. |
| **API test** | A client against an API (mocked or live). | Medium. |
| **End-to-end (e2e)** | The whole system, like a real user. | Slowest — few of them. |

### The test pyramid
A picture of where effort goes: **many** fast unit tests at the base, **some** integration tests, **few** slow e2e tests at the top. Push tests down the pyramid when you can.

## Anatomy of a test

| Term | Meaning |
|---|---|
| **Assertion** | A statement that must be true — the test fails if it isn't (`assert x == y`). |
| **Arrange → Act → Assert** | The three beats of every test: set up inputs, run the one thing under test, check the result. |
| **One behavior per test** | Each test checks a single thing — so when it fails, the *name* tells you what broke. |
| **Test case** | One specific scenario with its expected result. |
| **SUT** (System Under Test) | The thing you're actually testing. |

## pytest mechanics

| Term | Meaning |
|---|---|
| **pytest** | A Python test framework — a test is just a function with a plain `assert`. |
| **Test discovery** | pytest auto-finds files named `test_*.py` and functions named `test_*` — no registration. |
| **`assert`** | pytest reads a plain `assert` and shows **both sides** on failure (no `assertEqual` ceremony). |
| **Pass / fail** | `.` = pass, `F` = fail; a failure prints the exact line and both values. |
| **`pytest.raises`** | A context manager that passes **only if** the expected exception is raised — used to test error paths. |

## Fixtures & state

| Term | Meaning |
|---|---|
| **Fixture** | Reusable setup that builds **fresh** state for a test; a test gets it by naming it as a parameter. |
| **`conftest.py`** | A file where shared fixtures live — pytest finds them automatically, no import needed. |
| **Setup / teardown** | Preparing state before a test and cleaning up after. |
| **Test isolation** | Each test runs on a clean slate — no leftover state contaminating the next test. |
| **Shared state** | State reused across tests — a common source of flaky, order-dependent failures. |

## Paths & outcomes

| Term | Meaning |
|---|---|
| **Happy path** | The success case — valid input, everything works. |
| **Error path** | The case where your code should reject bad input or raise an exception. |
| **Edge case** | An unusual but valid input at the boundary (zero, empty, negative, max). |
| **Flaky test** | A test that sometimes passes and sometimes fails without code changes — usually a state or timing leak. |

## One-line summary

> A **test** is a saved `assert` that re-runs forever. Write mostly **unit** tests (Arrange → Act → Assert), give each one a clean slate with a **fixture**, and pin both the **happy path** and the **error path** with `pytest.raises`.
