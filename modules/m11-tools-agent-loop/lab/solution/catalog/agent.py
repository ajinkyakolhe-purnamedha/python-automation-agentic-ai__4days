"""LLM-powered Catalog Agent (Day 4) — Lab 11 SOLUTION (answer key).

The reference answer for ``starter/catalog/agent.py``: the four
``@catalog_agent.tool`` function bodies are filled in.

Built with **Pydantic AI** — schema auto-derived from type hints +
docstrings, no hand-written JSON dicts. ``RunContext[ProductCatalog]``
injects the catalog (the mock seam).

Usage::

    from catalog.agent import catalog_agent
    from catalog.models import ProductCatalog
    from catalog.storage import seed_products

    result = catalog_agent.run_sync(
        "What's our most expensive product?",
        deps=ProductCatalog(seed_products()),
        model="google:gemini-2.5-flash",   # or "openai:gpt-4o-mini"
    )
    print(result.output)
"""

from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext

from .models import ProductCatalog, ProductUpdate

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
# The Catalog Agent — Pydantic AI
# ============================================================

SYSTEM_PROMPT = (
    "You are a helpful assistant for a small product catalog. "
    "You have access to tools that let you list, search, count, and "
    "update products. Use them to answer the user's question. "
    "Prefer a single accurate tool call over multiple speculative ones. "
    "When you have enough information, respond in plain language."
)

catalog_agent = Agent(
    deps_type=ProductCatalog,
    instructions=SYSTEM_PROMPT,
)


@catalog_agent.tool
def list_products(ctx: RunContext[ProductCatalog]) -> list[dict]:
    """Return every product in the catalog."""
    return [p.model_dump() for p in ctx.deps.list_all()]


@catalog_agent.tool
def search_products(ctx: RunContext[ProductCatalog], term: str) -> list[dict]:
    """Find products whose name contains the given substring (case-insensitive)."""
    return [p.model_dump() for p in ctx.deps.search_by_name(term)]


@catalog_agent.tool
def count_by_category(ctx: RunContext[ProductCatalog]) -> dict[str, int]:
    """Return a dict mapping each category to its product count."""
    groups = ctx.deps.group_by_category()
    return {cat: len(products) for cat, products in groups.items()}


@catalog_agent.tool
def update_price(ctx: RunContext[ProductCatalog], product_id: int, new_price: float) -> dict:
    """Set a product's price. Returns the updated product."""
    from .models import CatalogError
    try:
        return ctx.deps.update(product_id, ProductUpdate(price=new_price)).model_dump()
    except CatalogError as e:
        return {"error": str(e)}


# ============================================================
# Lab 10: NL query → CatalogQuery (single shot, no agent loop) — GIVEN
# ============================================================

NL_QUERY_SYSTEM = (
    "You convert natural-language product-catalog queries into a structured "
    "filter. Always respond with a JSON object matching the CatalogQuery schema. "
    "Use null for fields the user did not mention."
)


def parse_nl_query(prompt: str, llm_client=None,
                   *, model: str = "gpt-4o-mini") -> CatalogQuery:
    """Lab 10: convert a free-form question into a validated CatalogQuery."""
    if llm_client is None:
        from openai import OpenAI
        llm_client = OpenAI()
    response = llm_client.chat.completions.create(
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
        logger.warning("LLM returned invalid CatalogQuery: %s", raw)
        raise


def apply_query(query: CatalogQuery, catalog: ProductCatalog) -> list[dict]:
    """Translate a CatalogQuery into catalog queries (Lab 10)."""
    items = catalog.list_all()
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
