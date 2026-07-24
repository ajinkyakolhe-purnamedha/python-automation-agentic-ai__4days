"""Lab 11 · Part A — let the LLM process your code's output (SOLUTION).

Direction: code → LLM. Your ProductCatalog produces raw product data; the LLM
synthesizes the answer — free text, then a validated CatalogSummary. This is
the agent's "observe" step on its own; Part B wraps it in a loop.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from pydantic import BaseModel, Field, ValidationError


def default_openai_client():
    from openai import OpenAI
    return OpenAI()


class CatalogSummary(BaseModel):
    total_products: int = Field(description="How many products are in the catalog.")
    categories: list[str] = Field(description="Distinct category names present.")
    most_expensive: str = Field(description="Name of the highest-priced product.")
    headline: str = Field(description="One-line natural-language summary for a dashboard.")


def summarize_free_text(products: list[dict], llm_client: Optional[Any] = None,
                        *, model: str = "gpt-4o-mini") -> str:
    client = llm_client or default_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user",
                   "content": "Summarize this product catalog for a manager in 2 sentences:\n"
                              + json.dumps(products, indent=2)}],
    )
    return response.choices[0].message.content


def summarize_structured(products: list[dict], llm_client: Optional[Any] = None,
                         *, model: str = "gpt-4o-mini") -> CatalogSummary:
    client = llm_client or default_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user",
                   "content": "Summarize this catalog as CatalogSummary JSON:\n"
                              + json.dumps(products, indent=2)}],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    return CatalogSummary.model_validate_json(raw)


def main() -> None:
    from catalog.models import ProductCatalog
    from catalog.storage import seed_products
    products = [p.model_dump() for p in ProductCatalog(seed_products()).list_all()]
    print(summarize_free_text(products))
    print(summarize_structured(products))


if __name__ == "__main__":
    main()
