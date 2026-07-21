# Module 8 — Glossary

Key terms for **mocking & data-driven testing**. General concepts — not tied to any one example. Read once before the lab.

## Why we need test doubles

| Term | Plain English |
|---|---|
| **Unit test** | Tests one piece of code in isolation — fast, repeatable, no external setup. |
| **Dependency** | Something your code needs to do its job (a database, a server, an API, the clock). |
| **Collaborator** | A dependency the code-under-test actually talks to during a test. |
| **SUT** (System Under Test) | The thing you're actually testing — not its dependencies. |
| **Isolation** | The test depends on nothing external — no network, no DB, no files. Same result every run. |

## Test doubles

A **test double** is any stand-in for a real dependency (like a stunt double for an actor). The umbrella term. The members differ by the **question each answers** (Gerard Meszaros / Martin Fowler taxonomy):

| Double | What it does | The question it answers |
|---|---|---|
| **Dummy** | Passed but never used — just fills a required slot. | (none — it's a placeholder) |
| **Stub** | Returns **canned** (hardcoded) answers. No logic. | "What does my code do *given* this input?" |
| **Spy** | A stub that also **records** how it was called. | "How was the dependency called?" |
| **Mock** | Pre-programmed with **expectations**; you assert against it. | "Did my code call the dependency *correctly*?" |
| **Fake** | A **real but lightweight** working implementation (e.g. in-memory DB). | "Can I swap in something that works, just simpler?" |

> In everyday speech everyone says "mock" for all of these. The line that matters: **stub** = feed input in; **mock/spy** = check the call afterward.

## Core mocking words

| Term | Meaning |
|---|---|
| **Mocking** | Replacing a real dependency with a controllable double during a test. |
| **Canned response** | A pre-baked value the double returns regardless of input. A stub *is* canned answers. |
| **Patch** | Temporarily replacing a real object/function with a double, then restoring it after the test. |
| **Seam** | A point in the code where you can swap real-for-fake **without editing the code**. |
| **Dependency injection (DI)** | Passing a dependency *in* from outside, instead of creating it inside. DI is what makes a seam. |
| **Stubbing a return** | Setting what a fake call hands back. |
| **Recording / verification** | A mock remembers calls so you can later assert how it was used. |
| **Assertion on calls** | Checking the dependency was called the right number of times, with the right arguments. |

## Happy & unhappy paths

| Term | Meaning |
|---|---|
| **Happy path** | The success case — valid input, everything works. |
| **Unhappy path** | The failure case — errors, timeouts, dropped connections, bad data. |
| **Forced failure** | Using a double to *trigger* an error you can't reproduce on demand (network blip, server crash). |
| **Edge case** | An unusual but valid input at the boundary (zero, empty, max, negative). |

## Data-driven testing

| Term | Meaning |
|---|---|
| **Parametrized test** | One test body run against a **table** of input/expected pairs — each row reported separately. |
| **Data-driven testing** | Driving the same logic with many cases from a table instead of copy-pasting tests. |
| **Test case** | One row of inputs + the expected result. |
| **Fixture** | Reusable setup/teardown a test framework hands to a test. |
| **Marker / tag** | A label on a test used to select or skip groups (e.g. "slow", "integration"). |

## Levels of testing

| Term | Meaning |
|---|---|
| **Unit test** | One unit, all dependencies doubled — fast, isolated. |
| **Integration test** | Exercises real components together (real server, real DB) — slower, more realistic. |
| **Test suite** | The full collection of tests run together. |
| **Regression test** | A test that locks in fixed behavior so it can't silently break again. |

## One-line summary

> A **test double** stands in for a real dependency. Ask it for an answer → **stub**. Ask whether your code *called* it right → **mock**. Want real-but-light behavior → **fake**. You can swap any of them in only because of a **seam** (dependency injection).
