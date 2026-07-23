"""Lab 11 · Part A — let the LLM process your code's output (standalone).

Direction: code → LLM. Your APIClient produces raw product data; instead of
writing formatting/aggregation code, hand it to the LLM and let it synthesize
the answer — first as free text, then as a *validated* CatalogSummary.

This is the agent's "observe" step on its own. Part B wraps it in a loop.

Run (needs the API server up + an OpenAI key):
    pip install openai
    export OPENAI_API_KEY=sk-...
    uvicorn catalog.server:app --reload     # in another terminal
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
    # TODO: client = llm_client or default_openai_client()
    # TODO: call client.chat.completions.create(model=model, messages=[...]) with a
    #       user message that embeds json.dumps(products) and asks for a 2-sentence summary.
    # TODO: return response.choices[0].message.content
    raise NotImplementedError


def summarize_structured(products: list[dict], llm_client: Optional[Any] = None,
                         *, model: str = "gpt-4o-mini") -> CatalogSummary:
    """1b · Same input → a *validated* CatalogSummary (JSON mode + Pydantic)."""
    # TODO: client = llm_client or default_openai_client()
    # TODO: call create(...) with response_format={"type": "json_object"} asking for
    #       a CatalogSummary as JSON, embedding json.dumps(products).
    # TODO: raw = response.choices[0].message.content or "{}"
    # TODO: return CatalogSummary.model_validate_json(raw)   # validate the LLM's output
    raise NotImplementedError


def main() -> None:
    from catalog.client import APIClient
    products = [p.model_dump() for p in APIClient().list_products()]
    print(summarize_free_text(products))
    print(summarize_structured(products))


if __name__ == "__main__":
    main()
