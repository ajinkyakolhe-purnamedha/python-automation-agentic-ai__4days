"""LLM-powered Catalog Agent (Day 4) — Lab 11 STARTER.

You start here with Lab 10 already done: ``CatalogQuery``, ``parse_nl_query``,
and ``apply_query`` are GIVEN below (you built them last lab — no need to
retype). The Pydantic AI agent is also given.

YOUR JOB this lab — fill the four ``@catalog_agent.tool`` function bodies.

Usage (after filling in the tools)::

    from catalog.agent import catalog_agent
    from catalog.client import APIClient

    result = catalog_agent.run_sync(
        "What's our most expensive product?", deps=APIClient()
    )
    print(result.output)
"""

from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent, RunContext

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
# The Catalog Agent — Pydantic AI (GIVEN plumbing)
# ============================================================

SYSTEM_PROMPT = (
    "You are a helpful assistant for a small product catalog. "
    "You have access to tools that let you list, search, count, and "
    "update products. Use them to answer the user's question. "
    "Prefer a single accurate tool call over multiple speculative ones. "
    "When you have enough information, respond in plain language."
)

catalog_agent = Agent(
    deps_type=APIClient,
    instructions=SYSTEM_PROMPT,
)


# ============================================================
# YOUR JOB — fill the four tool bodies below
# ============================================================

@catalog_agent.tool
def list_products(ctx: RunContext[APIClient]) -> list[dict]:
    """Return every product in the catalog."""
    # TODO: return [p.model_dump() for p in ctx.deps.list_products()]
    raise NotImplementedError("TODO: call ctx.deps.list_products() and model_dump() each Product")


@catalog_agent.tool
def search_products(ctx: RunContext[APIClient], term: str) -> list[dict]:
    """Find products whose name contains the given substring (case-insensitive)."""
    # TODO: filter ctx.deps.list_products() by term (case-insensitive),
    #       return model_dump() of each matching product.
    raise NotImplementedError("TODO: filter products by term, return dicts")


@catalog_agent.tool
def count_by_category(ctx: RunContext[APIClient]) -> dict[str, int]:
    """Return a dict mapping each category to its product count."""
    # TODO: return ctx.deps.count_by_category()
    raise NotImplementedError("TODO: call ctx.deps.count_by_category()")


@catalog_agent.tool
def update_price(ctx: RunContext[APIClient], product_id: int, new_price: float) -> dict:
    """Set a product's price. Returns the updated product."""
    # TODO: build a ProductUpdate(price=new_price), call
    #       ctx.deps.update_product(product_id, patch), return .model_dump()
    raise NotImplementedError("TODO: update the product's price, return the updated dict")


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
