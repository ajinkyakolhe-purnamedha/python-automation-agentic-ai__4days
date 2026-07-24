"""Lab 11 · Part A — let the LLM process your code's output (standalone).

Direction: code → LLM. Your ProductCatalog produces raw product data; instead
of writing formatting/aggregation code, hand it to the LLM and let it
synthesize the answer — first as free text, then as a *validated*
CatalogSummary.

This is the agent's "observe" step on its own. Part B wraps it in a loop.

Run (needs an OpenAI key — no server needed):
    pip install openai
    export OPENAI_API_KEY=sk-...
    python summarize_catalog.py

Fill every `# TODO`.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError


def default_openai_client():
    """Real OpenAI client. Requires OPENAI_API_KEY. Injected so tests can mock it."""
    from openai import OpenAI
    return OpenAI()


# The structured shape the LLM must synthesize from raw product dicts.
class CatalogSummary(BaseModel):
    total_products: int = Field(description="How many products are in the catalog.")
    categories: list[str] = Field(description="Distinct category names present.")
    most_expensive: str = Field(description="Name of the highest-priced product.")
    headline: str = Field(description="One-line natural-language summary for a dashboard.")


def summarize_free_text(products: list[dict], llm_client: Optional[Any] = None,
                        *, model: str = "gpt-4o-mini") -> str:
    """1a · Raw product dicts in → a plain-English answer. No aggregation code."""
    # TODO: Send the product data to the LLM and return its plain-text summary.
    #   Hint 1: use llm_client (or default_openai_client() if None), call
    #           chat.completions.create — embed json.dumps(products) in a user message
    #           asking for a 2-sentence summary
    #   Hint 2: the response object has .choices[0].message.content — that's your return
    raise NotImplementedError


def summarize_structured(products: list[dict], llm_client: Optional[Any] = None,
                         *, model: str = "gpt-4o-mini") -> CatalogSummary:
    """1b · Same input → a *validated* CatalogSummary (JSON mode + Pydantic)."""
    # TODO: Same as free_text, but force JSON output and validate through Pydantic.
    #   Hint 1: add response_format={"type": "json_object"} to the create() call —
    #           search "openai json mode" — and ask the LLM to return CatalogSummary fields
    #   Hint 2: the LLM returns a raw JSON string; pass it to
    #           CatalogSummary.model_validate_json() to get a typed, validated object
    raise NotImplementedError


def main() -> None:
    from catalog.models import ProductCatalog
    from catalog.storage import seed_products
    products = [p.model_dump() for p in ProductCatalog(seed_products()).list_all()]
    print(summarize_free_text(products))
    print(summarize_structured(products))


if __name__ == "__main__":
    main()
