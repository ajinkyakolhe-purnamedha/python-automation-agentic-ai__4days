"""LLM-powered Catalog Agent (Day 4) — Lab 10 starter.

Lab 10 builds ONLY the single-shot piece: take a natural-language question,
make the LLM return a **structured** `CatalogQuery` (not English you have to
re-parse), validate it through Pydantic, then run it as a pure-Python filter
over the Day-2 `APIClient`. One LLM call. No agent loop, no tools — that's
Lab 11.

Fill every `raise NotImplementedError` below. Keep the field declarations as
they are: the `Field(description=...)` text is what the LLM reads to decide
how to fill each slot — that *is* the teaching point.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field, ValidationError

from .client import APIClient

logger = logging.getLogger(__name__)


# ============================================================
# LLM client protocol (so tests can pass any duck-typed mock)
# ============================================================

class LLMClient(Protocol):
    """Minimal slice of the OpenAI client interface this lab needs."""
    chat: Any


def default_openai_client() -> LLMClient:
    """Construct a real OpenAI client. Requires OPENAI_API_KEY in env."""
    from openai import OpenAI  # local import — only needed when we run real
    return OpenAI()


# ============================================================
# Structured output: the schema the LLM must speak
# ============================================================

class CatalogQuery(BaseModel):
    """Pydantic schema the LLM must return for NL → query parsing (Lab 10).

    TODO: the four fields are declared for you — DO NOT change their names or
    types (the parser and filter below depend on them). DO sharpen each
    `description=`: the LLM reads it to decide how to fill the field. Vague
    text → vague queries. Be precise about valid values and the null case.
    """

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
# NL query → CatalogQuery (single shot, no agent loop)
# ============================================================

NL_QUERY_SYSTEM = (
    "You convert natural-language product-catalog queries into a structured "
    "filter. Always respond with a JSON object matching the CatalogQuery schema. "
    "Use null for fields the user did not mention."
)


def parse_nl_query(prompt: str, llm_client: Optional[LLMClient] = None,
                   *, model: str = "gpt-4o-mini") -> CatalogQuery:
    """Lab 10: convert a free-form question into a validated CatalogQuery.

    Steps:
      1. client = llm_client or default_openai_client()
      2. call client.chat.completions.create(...) with NL_QUERY_SYSTEM +
         the user prompt, and response_format={"type": "json_object"}
      3. read response.choices[0].message.content (default to "{}")
      4. return CatalogQuery.model_validate_json(raw)  -- never trust the raw
         JSON without validating through Pydantic.
    """
    raise NotImplementedError(
        "TODO: call the LLM in JSON mode, then CatalogQuery.model_validate_json(...)"
    )


def apply_query(query: CatalogQuery, api: APIClient) -> list[dict]:
    """Translate a CatalogQuery into APIClient calls (Lab 10).

    Pure Python — no LLM here. Start from api.list_products(), then narrow by
    each field that is *set* (skip the null ones):
      - query.category        -> p.category matches (case-insensitive)
      - query.max_price        -> p.price <= max_price  (guard for None, since 0 is falsy)
      - query.in_stock_only    -> p.in_stock is True
      - query.name_contains    -> substring of p.name (case-insensitive)
    Return [p.model_dump() for p in items].
    """
    raise NotImplementedError(
        "TODO: filter api.list_products() by the non-null query fields"
    )
