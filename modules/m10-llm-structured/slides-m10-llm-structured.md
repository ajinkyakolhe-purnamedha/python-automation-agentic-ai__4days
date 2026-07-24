---
marp: true
theme: acuity
paginate: true
header: "Acuity · Day 4 · Add AI to the Catalog, then Test the AI"
footer: "Acuity Training · Day 4 of 4"
---

<!-- _class: title -->

# Day 4
## Add AI to the Catalog,
## **then test the AI**

6 hours · 3 modules · 3 labs · the day Day 3 was secretly setting up
---
# Three days of Python. Today, one new idea: the LLM.

You have a tested, CI-green catalog with a typed client. Today you bolt an **LLM agent** onto it — and lock it under the **same** testing discipline.

- **M10** — the *power* of LLMs: closed APIs, open models, and your first validated LLM app
- **M11** — tools = functions; the plan→act→observe loop
- **M12** ⭐ — test the AI: shape & behaviour, not prose

The agent's tools wrap the `ProductCatalog` you built Day 1. The catalog is injected like `Session` was Day 3.

Catch-up: `cp -r ../project/checkpoints/day-4-start/. .`
---
# Today's arc

| Module | ~40 min teach | 80 min lab |
|---|---|---|
| M10 | Power of LLMs: APIs · open models · first app | Lab 10: classify a Product + NL query → `CatalogQuery` |
| M11 | Tools as functions + agent loop | Lab 11: build `CatalogAgent` |
| M12 ⭐ | **Testing AI tools & outputs** | Lab 12: test the agent |

End-of-day: an agentic, **tested** Python system on your laptop — no new framework.
---
<!-- _class: title -->

# Module 10
## The Power of LLMs
**~40 min · then 80 min lab** — what LLMs can do (closed & open), then build your first validated LLM feature
---
# Module 10 — three sections

1. **Closed-source API power** — one hosted engine, many tasks (OpenAI; Gemini is the same shape)
2. **Open-source power** — models you run yourself, no API key (`transformers`)
3. **Your first LLM app** — prompt → structured output → **validate** → ready for M11

The first two show *what's possible*. The third is the part Lab 10 makes you build.
---
<!-- _class: title -->

# Section 1
## Closed-source API power
one API call, many tasks
---
# 1.1 · AI → ML → GenAI → Agentic

- **AI** — any system that "appears intelligent"
- **ML** — systems that learn patterns from data
- **GenAI** — ML that produces novel text / images / code
- **Agentic AI** — GenAI + tools + a loop + a goal

The **agent is the loop around the LLM**, not the LLM itself. The LLM is a stateless string-to-string machine; the state — **tools, memory, goals — lives in *your* code.** That's why Day 1–3 Python matters: you write the loop.
---
# 1.2 · The LLM is a task engine

Text in → text out, **aimed at a task.** Every useful call is one of a handful of tasks:

| Task | "Given text, produce…" |
|---|---|
| **classify** | a label (priority = high/low) |
| **extract** | structured fields (a `CatalogQuery`) |
| **summarize** | a shorter text |
| **generate** | new text (a reply draft) |
| **transform** | reshaped text (NL → JSON) |
| **reason** | a decision + which tool to call next |

Each is **spec'able**: define the input, output shape, constraints. M11's tools are just "reason → pick a task."
---
# 1.3 · One API call does all of them

Same method, different prompt — the task lives in the words, not the API.

```python
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": "Classify ticket priority: high/low."},
              {"role": "user", "content": ticket.subject}],
)
resp.choices[0].message.content   # -> "high"
```

One hosted model, billed per token, no weights to manage. **The prompt is the spec** — role, constraints, output shape (more in §3).

<div class="code-along">▶ Code-along now → notebook: module-10 §1 — classify + summarize a support ticket</div>
---
# 1.4 · Multimodal — not just text

The hosted frontier models take **more than text**:

- **Vision in** — an image + "what's broken in this photo?" → text
- **Audio in** — a recording → a transcript (or an answer)
- **Image out** — a prompt → a generated image

Same `create()` shape, different content parts. The task-engine idea is unchanged — only the modality of "text in" widens.
---
# 1.5 · Gemini — same shape, different vendor

Closed-source isn't one company. Google's **Gemini** API has the **same request shape**: a model id, a list of messages, a structured response.

```python
from google import genai
client = genai.Client()                          # GOOGLE_API_KEY in env
resp = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Classify this ticket: my screen is cracked",
)
resp.text                                        # -> "hardware"
```

We use **OpenAI** for the rest of the course (M11/M12 agent). Point: the *pattern* is portable; vendors are swappable. Don't marry your code to one.
---
# 1.6 · Tokens · context · cost · latency

| | what it is | rule of thumb |
|---|---|---|
| Token | piece of a word | ≈ ¾ of an English word |
| Context | tokens visible at once | 128k for `gpt-4o-mini` |
| Input cost | per M input tokens | ~$0.15 / M in |
| Output cost | per M output tokens | ~$0.60 / M out |
| Latency | time to first token | ~500 ms TTFT + ~50 tok/s |

One agent step ≈ **500–2000 in + 100–300 out** tokens. A multi-step agent multiplies that — budget per call, cap the steps.
---
<!-- _class: title -->

# Section 2
## Open-source LLM power
models you run yourself — no API key
---
# 2.1 · Why open-source at all

The hosted API is easy — but sometimes you can't or shouldn't use it:

| Reason | Why open-source wins |
|---|---|
| **Privacy / PII** | data never leaves your machine — no third party |
| **Cost at scale** | millions of calls: your hardware beats per-token billing |
| **Offline** | runs with no network |
| **Control** | you own the weights — pin a version, fine-tune freely |

Trade-off: *you* run the infra. For a demo, a laptop CPU is enough.
---
# 2.2 · `pipeline()` — one line to a task

Hugging Face `transformers` wraps "load model → preprocess → infer → postprocess" into **one call**:

```python
from transformers import pipeline
clf = pipeline("zero-shot-classification",
               model="typeform/distilbert-base-uncased-mnli")
clf("my iPhone won't charge", candidate_labels=["urgent", "billing", "hardware"])
# -> {'labels': ['hardware', 'urgent', ...], 'scores': [0.91, 0.06, ...]}
```

Pick the **task string**; the pipeline pulls a suitable model. No prompt engineering — the task *is* the model.

<div class="code-along">▶ Code-along now → notebook: module-10 §2 — zero-shot classify + NER live; ASR / caption / translate shown</div>
---
# 2.3 · Closed vs open — when to reach for which

| | Closed API (OpenAI/Gemini) | Open-source (`transformers`) |
|---|---|---|
| Setup | API key, 1 line | download weights, run infra |
| Best at | broad reasoning, generation, agents | one narrow task, at scale |
| Data | leaves your machine | stays local |
| Cost | per token | hardware up front |

Rule of thumb: **prototype + reason** on a closed API; **a fixed, high-volume task** (classify every ticket) is where a small local model pays off.
---
<!-- _class: title -->

# Section 3
## Your first LLM app
prompt → structured output → **validate**
---
# 3.1 · Context window + the prompt is the spec

The model has **no memory** between calls — everything it knows for *this* call is the **context window** you send. The prompt is the spec; three parts carry 80% of the result:

1. **Role** — who the model is ("assistant for a product catalog")
2. **Constraints** — what it must / must not do
3. **Output shape** — JSON? prose? a single label?

```python
SYSTEM_PROMPT = ("You convert catalog questions into a structured filter. "
                 "Respond with JSON matching the schema; use null for unmentioned fields.")
```

Skip the "you are a world-class expert" theatre — it buys nothing.
---
# 3.2 · Structured output = the extract task, rigorously

Make the answer **machine-readable, not English you re-parse.** Declare the shape as Pydantic (Day-2 returns), ask for JSON mode:

```python
class CatalogQuery(BaseModel):
    category: str | None = Field(None, description="Restrict to this category, or null for all.")
    max_price: float | None = Field(None, ge=0)
    in_stock_only: bool = False
```

```python
resp = client.chat.completions.create(model="gpt-4o-mini", messages=[...],
    response_format={"type": "json_object"})   # JSON mode
```

`Field(description=...)` is the spec the model reads. **Make the LLM speak your schema.**
---
# 3.3 · 🔮 What happens when the LLM returns `{"max_price": -5}`?

Pause. The LLM filled every field — valid JSON, correct types. But `max_price` is **negative**.

Does your code catch this? Where?

---
# 3.4 · Always validate the output

The LLM *promised* JSON in your shape — don't take its word. Parse through Pydantic, exactly like a request body Day 2:

```python
raw = resp.choices[0].message.content
query = CatalogQuery.model_validate_json(raw)   # raises on bad shape AND bad values
```

`Field(ge=0)` on `max_price` rejects `-5` — **the same constraint you wrote 5 minutes ago.** Pydantic is the guardrail for the LLM, not just the API.

Same **boundary discipline** as Day 2: the LLM is just another **untrusted source**. Validate at the edge; the rest of your code gets a clean, typed object.

<div class="code-along">▶ Code-along now → notebook: module-10 §3 — extract a TicketQuery in JSON mode, then validate it. Try removing `ge=0` — watch what gets through.</div>
---
# 3.5 · When the output isn't good enough — the ladder

Climb **only as far as the task needs:**

| Rung | Fix it by… | Reach for it when… |
|---|---|---|
| **Prompt** | clearer role / constraints / examples | first thing, always |
| **RAG** | retrieve facts, inject as context | model lacks *your* knowledge |
| **Fine-tune** | retrain weights on labeled data | one narrow task, high volume, fixed format |

Most tasks never leave rung 1. Fine-tuning teaches a **skill / format**, not facts — and the held-out check it needs **is the golden-eval you build in M12.** *(Shown, not run today.)*
---
# 3.6 · Responsible AI — the minimum

- **PII** — don't send personal data to a third-party LLM without consent + a DPA (this is also a reason to reach for §2's local models)
- **Hallucination** — the model can invent numbers; **verify with a tool before acting**
- **Cost / runaway** — cap `max_steps` on every agent (M11), so a confused loop fails loudly

Not a course on responsible AI — but your boss *will* ask these three.
---
# 3.7 · → M11: the LLM becomes an agent

Today: **one call**, structured + validated. Next module: wrap it in a **loop** and give it **tools** (your `ProductCatalog`).

```text
§3 today         one validated call:  text -> CatalogQuery
M11 next         loop + tools:        question -> [pick tool -> run -> observe] -> answer
```

The validation discipline you just learned is what keeps the loop trustworthy.
---
<!-- _class: lab -->

# 🧪 Lab 10 — Classify a Product, then NL → Filter

**80 min** · open `modules/m10-llm-structured/lab/README.md`

**Part A — open-source (≈20 min):** zero-shot classify a `Product` from its name + description with a local `transformers` pipeline; compare the guess to the real category.

**Part B — your first LLM app (≈60 min):** on your `Product` catalog
- `CatalogQuery` — Pydantic schema with `Field(description=...)`
- `parse_nl_query(prompt)` — one LLM call, JSON mode, Pydantic validation
- `apply_query(query, catalog)` — pure-Python filter over the `ProductCatalog`

End state: typing **"electronics under 5000 in stock"** returns the right rows.
