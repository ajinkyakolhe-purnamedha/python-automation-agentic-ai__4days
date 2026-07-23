"""LLM-powered Catalog Agent (Day 4) — Lab 10 SOLUTION (answer key).

The single-shot piece: take a natural-language question, make the LLM return a
**structured** `CatalogQuery` (not English you re-parse), validate it through
Pydantic, then run it as a pure-Python filter over the Day-2 `APIClient`.
One LLM call. No agent loop, no tools — that's Lab 11.

This is the reference answer for `starter/catalog/agent.py`: the two function
bodies (`parse_nl_query`, `apply_query`) are filled in; everything else matches
the starter. Uses the OpenAI API (set OPENAI_API_KEY).
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

    The `description=` on each field is what the LLM reads to decide how to fill
    the slot — it doubles as the instruction AND the validation target. Each one
    states the valid values and what `null` means.
    """

    category: Optional[str] = Field(
        default=None,
        description="Restrict to this product category (e.g. 'Electronics', 'Books'), or null for all categories.",
    )
    max_price: Optional[float] = Field(
        default=None, ge=0,
        description="Inclusive upper price bound in INR (e.g. 5000), or null for no price limit.",
    )
    in_stock_only: bool = Field(
        default=False,
        description="True to return only products currently in stock; false to include out-of-stock.",
    )
    name_contains: Optional[str] = Field(
        default=None,
        description="Case-insensitive substring the product name must contain (e.g. 'cable'), or null for any name.",
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
    """Convert a free-form question into a validated CatalogQuery (one LLM call)."""
    client = llm_client or default_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": NL_QUERY_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},   # force parseable JSON
    )
    raw = response.choices[0].message.content or "{}"
    try:
        return CatalogQuery.model_validate_json(raw)   # validate at the boundary
    except ValidationError:
        logger.warning("LLM returned invalid CatalogQuery: %s", raw)
        raise


def apply_query(query: CatalogQuery, api: APIClient) -> list[dict]:
    """Translate a CatalogQuery into APIClient calls — pure Python, no LLM."""
    items = api.list_products()
    if query.category:
        items = [p for p in items if p.category.lower() == query.category.lower()]
    if query.max_price is not None:                # guard None — 0 is a valid bound
        items = [p for p in items if p.price <= query.max_price]
    if query.in_stock_only:
        items = [p for p in items if p.in_stock]
    if query.name_contains:
        needle = query.name_contains.lower()
        items = [p for p in items if needle in p.name.lower()]
    return [p.model_dump() for p in items]
