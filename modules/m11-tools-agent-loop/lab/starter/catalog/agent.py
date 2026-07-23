"""LLM-powered Catalog Agent (Day 4) — Lab 11 STARTER.

You start here with Lab 10 already done: `CatalogQuery`, `parse_nl_query`,
and `apply_query` are GIVEN below (you built them last lab — no need to
retype). The plumbing (`ToolSpec`, `ToolRegistry`, the result dataclasses)
is also given.

YOUR JOB this lab — fill the three `NotImplementedError` / `# TODO` pieces:

  * `CatalogAgent._build_registry`  — register the FOUR tools
  * `CatalogAgent.ask`              — the plan → act → observe loop
  * `CatalogAgent._invoke_tool`     — look up + run a tool, return its result

## The Tool/Agent loop

    user prompt
        │
        ▼
    LLM(messages, tools)
        │
        ├── tool_calls? ──> run each tool, append observation, loop
        │
        └── final answer  ──> return AgentResult

## Why the LLM client is injected

`CatalogAgent(api_client, llm_client=...)` accepts any object that quacks
like `openai.OpenAI` (i.e. has `.chat.completions.create(...)`). That's the
seam tests use to mock the LLM — exactly the same pattern Day 3 used to
mock `requests.Session`. Uses the OpenAI API (set OPENAI_API_KEY).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol

from pydantic import BaseModel, Field, ValidationError

from .client import APIClient

logger = logging.getLogger(__name__)


# ============================================================
# Structured outputs (built in Lab 10 — GIVEN)
# ============================================================

class CatalogQuery(BaseModel):
    """Pydantic schema the LLM must return for NL → query parsing (Lab 10)."""

    category: Optional[str] = Field(
        default=None,
        description="Restrict to this category (e.g. 'Electronics'), or null for all.",
    )
    max_price: Optional[float] = Field(
        default=None, ge=0,
        description="Upper price bound in INR, or null for no bound.",
    )
    in_stock_only: bool = Field(
        default=False,
        description="If true, only return products currently in stock.",
    )
    name_contains: Optional[str] = Field(
        default=None,
        description="Substring (case-insensitive) the product name must contain.",
    )


# ============================================================
# Tool registration (GIVEN — this is plumbing, not the lesson)
# ============================================================

@dataclass
class ToolSpec:
    name: str
    description: str
    parameters_schema: dict
    fn: Callable[..., Any]

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


class ToolRegistry:
    """Collects ToolSpecs declared with `@registry.tool(...)`."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def tool(self, *, name: str, description: str, parameters: dict):
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self._tools[name] = ToolSpec(
                name=name,
                description=description,
                parameters_schema=parameters,
                fn=fn,
            )
            return fn
        return decorator

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"tool {name!r} not registered")
        return self._tools[name]

    def all(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def openai_schemas(self) -> list[dict]:
        return [t.to_openai_schema() for t in self._tools.values()]


# ============================================================
# LLM client protocol (so tests can pass any duck-typed mock)
# ============================================================

class LLMClient(Protocol):
    """Minimal slice of the OpenAI client interface this agent needs."""
    chat: Any


def default_openai_client() -> LLMClient:
    """Construct a real OpenAI client. Requires OPENAI_API_KEY in env."""
    from openai import OpenAI  # local import — only needed when we run real
    return OpenAI()


# ============================================================
# Agent result objects (GIVEN)
# ============================================================

class AgentError(Exception):
    """Raised when the agent loop hits a hard failure (max steps, bad tool name…)."""


@dataclass
class ToolCallRecord:
    tool: str
    arguments: dict
    result: Any


@dataclass
class AgentResult:
    answer: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    steps: int = 0


# ============================================================
# CatalogAgent — YOU build the three marked methods
# ============================================================

SYSTEM_PROMPT = (
    "You are a helpful assistant for a small product catalog. "
    "You have access to tools that let you list, search, count, add, and "
    "update products. Use them to answer the user's question. "
    "Prefer a single accurate tool call over multiple speculative ones. "
    "When you have enough information, respond in plain language."
)


class CatalogAgent:
    def __init__(
        self,
        api_client: APIClient,
        llm_client: Optional[LLMClient] = None,
        *,
        model: str = "gpt-4o-mini",
        max_steps: int = 5,
    ) -> None:
        self.api = api_client
        self.llm = llm_client or default_openai_client()
        self.model = model
        self.max_steps = max_steps
        self.registry = self._build_registry()

    # -------- tool implementations (each is just Python on top of APIClient) --------

    def _build_registry(self) -> ToolRegistry:
        registry = ToolRegistry()

        # TODO: register the four tools on `registry` using @registry.tool(...).
        #   Each decorated function calls self.api and returns JSON-friendly
        #   values (dicts/lists of dicts — model_dump() your Products!).
        #
        #   1. list_products()            -> [p.model_dump() for p in self.api.list_products()]
        #        params: {"type": "object", "properties": {}, "additionalProperties": False}
        #   2. search_products(term)      -> products whose name contains `term` (case-insensitive)
        #        params: term: string (required)
        #   3. count_by_category()        -> self.api.count_by_category()
        #        params: {} (none)
        #   4. update_price(product_id, new_price) -> self.api.update_product(...).model_dump()
        #        params: product_id: integer, new_price: number (>= 0) (both required)
        #
        # Example shape (the `@` pattern from Day-1 `@dataclass`/`@app.get` returns —
        # the registry stamps metadata onto each function and stores a ToolSpec):
        #
        #   @registry.tool(
        #       name="list_products",
        #       description="Return every product in the catalog as a list of dicts.",
        #       parameters={"type": "object", "properties": {}, "additionalProperties": False},
        #   )
        #   def list_products() -> list[dict]:
        #       return [p.model_dump() for p in self.api.list_products()]

        return registry  # currently empty — register the four tools above first

    # -------- the loop --------

    def ask(self, user_prompt: str) -> AgentResult:
        raise NotImplementedError(
            "TODO: plan→act→observe loop; see steps. "
            "Seed messages with SYSTEM_PROMPT + the user turn, then loop up to "
            "self.max_steps: call self.llm.chat.completions.create(model=, "
            "messages=, tools=self.registry.openai_schemas()). No tool_calls -> "
            "return AgentResult(answer, tool_calls=log, steps=step). Otherwise "
            "append the assistant message (WITH its tool_calls), run each tool "
            "via self._invoke_tool, and append a {'role':'tool', "
            "'tool_call_id': call.id, ...} message for EACH call. "
            "If you fall out of the loop, raise AgentError."
        )

    def _invoke_tool(self, name: str, arguments_json: str) -> Any:
        raise NotImplementedError(
            "TODO: look up the tool, run it, return result or {'error':...}. "
            "Wrap self.registry.get(name) in try/except KeyError -> "
            "return {'error': f'unknown tool: {name!r}'}. Then _parse_args the "
            "JSON string and call spec.fn(**kwargs). Wrap the call in try/except "
            "Exception -> return {'error': f'{type(exc).__name__}: {exc}'} so the "
            "LLM sees the failure instead of the loop crashing."
        )


def _parse_args(arguments_json: str) -> dict:
    if not arguments_json:
        return {}
    try:
        return json.loads(arguments_json)
    except json.JSONDecodeError:
        return {}


# ============================================================
# Lab 10: NL query → CatalogQuery (single shot, no agent loop) — GIVEN
# ============================================================

NL_QUERY_SYSTEM = (
    "You convert natural-language product-catalog queries into a structured "
    "filter. Always respond with a JSON object matching the CatalogQuery schema. "
    "Use null for fields the user did not mention."
)


def parse_nl_query(prompt: str, llm_client: Optional[LLMClient] = None,
                   *, model: str = "gpt-4o-mini") -> CatalogQuery:
    """Lab 10: convert a free-form question into a validated CatalogQuery."""
    client = llm_client or default_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": NL_QUERY_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    try:
        return CatalogQuery.model_validate_json(raw)
    except ValidationError:
        # Surface the raw output for debugging.
        logger.warning("LLM returned invalid CatalogQuery: %s", raw)
        raise


def apply_query(query: CatalogQuery, api: APIClient) -> list[dict]:
    """Translate a CatalogQuery into APIClient calls (Lab 10)."""
    items = api.list_products()
    if query.category:
        items = [p for p in items if p.category.lower() == query.category.lower()]
    if query.max_price is not None:
        items = [p for p in items if p.price <= query.max_price]
    if query.in_stock_only:
        items = [p for p in items if p.in_stock]
    if query.name_contains:
        needle = query.name_contains.lower()
        items = [p for p in items if needle in p.name.lower()]
    return [p.model_dump() for p in items]
