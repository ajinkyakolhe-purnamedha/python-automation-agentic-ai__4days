"""LLM-powered Catalog Agent (Day 4) — Lab 10 starter.

Lab 10 builds ONLY the single-shot piece: take a natural-language question,
make the LLM return a **structured** `CatalogQuery` (not English you have to
re-parse), validate it through Pydantic, then run it as a pure-Python filter
over the `ProductCatalog`. One LLM call. No agent loop, no tools — that's
Lab 11.

Fill every `raise NotImplementedError` below. Keep the field declarations as
they are: the `Field(description=...)` text is what the LLM reads to decide
how to fill each slot — that *is* the teaching point.
"""

from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

from .models import ProductCatalog

logger = logging.getLogger(__name__)


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


def parse_nl_query(prompt: str, llm_client=None,
                   *, model: str = "gpt-4o-mini") -> CatalogQuery:
    """Lab 10: convert a free-form question into a validated CatalogQuery."""
    # TODO: Make one LLM call that returns JSON, then validate it as a CatalogQuery.
    #   Hint 1: use llm_client (or create an OpenAI() client if None), call
    #           chat.completions.create with NL_QUERY_SYSTEM as the system message
    #           and the user's prompt — search "openai json mode" for the format arg
    #   Hint 2: the LLM returns raw JSON text — never trust it directly;
    #           Pydantic's .model_validate_json() validates + parses in one step
    raise NotImplementedError


def apply_query(query: CatalogQuery, catalog: ProductCatalog) -> list[dict]:
    """Translate a CatalogQuery into catalog queries — pure Python, no LLM."""
    # TODO: Start from all products, then narrow by each non-null query field.
    #   Hint 1: catalog.list_all() gives you every Product; check each query field
    #           (category, max_price, in_stock_only, name_contains) and filter only
    #           when the field is set — careful: max_price=0 is valid, don't skip it
    #   Hint 2: compare strings case-insensitively (.lower()); return dicts not
    #           Pydantic objects (same conversion you'll use in Lab 11's tools)
    raise NotImplementedError
