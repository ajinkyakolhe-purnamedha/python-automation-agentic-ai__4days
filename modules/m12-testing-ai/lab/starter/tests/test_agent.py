"""Lab 12 · Test the Agent (catalog.agent) — STARTER SCAFFOLD.

Four classes, one per kind of test an AI system needs. The plumbing below
(the fake APIClient + the FunctionModel helpers) is GIVEN — it's mocking
boilerplate, not the lesson. Your job is to fill the four test classes,
replacing each ``pytest.fail(...)`` with real asserts.

No OpenAI key required: the LLM is fully mocked via Pydantic AI's
``FunctionModel`` and ``TestModel``. Run with
``unset OPENAI_API_KEY && uv run pytest -q``.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pydantic_ai
import pytest
from pydantic import ValidationError
from pydantic_ai import ModelResponse, TextPart, ToolCallPart, capture_run_messages
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from catalog.agent import (
    CatalogQuery,
    apply_query,
    catalog_agent,
)
from catalog.client import APIClient
from catalog.models import Product, ProductUpdate

pydantic_ai.models.ALLOW_MODEL_REQUESTS = False


# ============================================================
# GIVEN — a fake APIClient backed by a list of Products
# (don't edit; this is the Day-3 mock seam, reused for Day 4)
# ============================================================

def _fake_api(products: list[Product]) -> MagicMock:
    """A MagicMock(spec=APIClient) wired to behave like a working client."""
    api = MagicMock(spec=APIClient)
    state = {p.id: p for p in products}

    api.list_products.side_effect = lambda: list(state.values())
    api.get_product.side_effect = lambda pid: state[pid]

    def _update(pid, patch: ProductUpdate):
        target = state.get(pid, next(iter(state.values())))
        updated = target.model_copy(
            update=patch.model_dump(exclude_unset=True)
        )
        if pid in state:
            state[pid] = updated
        return updated
    api.update_product.side_effect = _update

    def _count():
        d: dict[str, int] = {}
        for p in state.values():
            d[p.category] = d.get(p.category, 0) + 1
        return d
    api.count_by_category.side_effect = _count

    return api


SAMPLE_PRODUCTS = [
    Product(id=1, name="USB-C Cable",         category="Electronics", price=499.0,  in_stock=True),
    Product(id=2, name="Mechanical Keyboard", category="Electronics", price=5499.0, in_stock=True),
    Product(id=3, name="Bluetooth Speaker",   category="Electronics", price=2499.0, in_stock=True),
    Product(id=4, name="Yoga Mat",            category="Fitness",     price=1299.0, in_stock=False),
]


# ============================================================
# GIVEN — FunctionModel helpers that script the LLM's behaviour
# ============================================================

def _force_tool_call(tool_name: str, **kwargs):
    """Return a FunctionModel callback that calls one tool, then answers."""
    def model_fn(messages, info):
        for msg in messages:
            for part in msg.parts:
                if part.part_kind == "tool-return":
                    return ModelResponse(parts=[TextPart("Done.")])
        return ModelResponse(parts=[ToolCallPart(tool_name, kwargs)])
    return model_fn


def _scripted_calls(tool_sequence: list[tuple[str, dict]], final_answer: str):
    """Return a FunctionModel callback that plays a sequence of tool calls."""
    def model_fn(messages, info):
        tool_returns = sum(
            1 for msg in messages for p in msg.parts if p.part_kind == "tool-return"
        )
        if tool_returns < len(tool_sequence):
            name, args = tool_sequence[tool_returns]
            return ModelResponse(parts=[ToolCallPart(name, args)])
        return ModelResponse(parts=[TextPart(final_answer)])
    return model_fn


# ============================================================
# 1. Tool tests — the tools are plain Python (Day-3 patterns)
#    Force a tool call with FunctionModel, inspect the return
#    in capture_run_messages().
# ============================================================

class TestTools:
    def test_count_by_category(self):
        """count_by_category() returns deterministic counts over SAMPLE_PRODUCTS."""
        # TODO: use _force_tool_call("count_by_category") with FunctionModel,
        #       then find the tool-return in capture_run_messages() and assert:
        #       tool_return.content == {"Electronics": 3, "Fitness": 1}
        pytest.fail("TODO: implement test_count_by_category")

    # TODO: add the rest of the tool tests:
    #   - test_list_products_returns_dicts — force "list_products", check result is a list
    #         with result[0]["name"] == "USB-C Cable"
    #   - test_search_products_is_case_insensitive — force "search_products" with
    #         term="KEYBOARD", result should have one item with id == 2
    #   - test_update_price_mutates — force "update_price" with product_id=1,
    #         new_price=10.0, result["price"] == 10.0
    #   - test_all_tools_callable_via_test_model — TestModel smoke test:
    #         with catalog_agent.override(model=TestModel()):
    #             result = catalog_agent.run_sync("test", deps=api)
    #         assert result.output


# ============================================================
# 2. Schema tests — Pydantic validation of LLM JSON outputs
#    (same discipline as Day-2/Day-3 model tests)
# ============================================================

class TestCatalogQuerySchema:
    def test_rejects_negative_price(self):
        """A negative max_price fails validation (the schema guards the LLM's JSON)."""
        # TODO: with pytest.raises(ValidationError): CatalogQuery(max_price=-5.0)
        pytest.fail("TODO: implement test_rejects_negative_price")

    # TODO: add the rest of the schema tests:
    #   - test_all_fields_optional — CatalogQuery(); category is None, in_stock_only is False
    #   - test_apply_query_filters_by_category_and_price — Electronics & max_price=1000 → {1}
    #   - test_apply_query_in_stock_only — in_stock_only=True → {1, 2, 3} (Yoga Mat is OOS)


# ============================================================
# 3. Agent-loop tests — FunctionModel scripts the LLM
#    Use _scripted_calls + capture_run_messages to verify tool order
# ============================================================

class TestAgentLoop:
    def test_single_tool_call_then_answer(self):
        """One tool call, then a final answer → correct tool called, correct output."""
        # TODO: with catalog_agent.override(model=FunctionModel(
        #           _scripted_calls([("count_by_category", {})],
        #                           "We have 3 Electronics and 1 Fitness product.")
        #       )):
        #           with capture_run_messages() as msgs:
        #               result = catalog_agent.run_sync("how many?", deps=api)
        #       tool_calls = [p.tool_name for msg in msgs for p in msg.parts
        #                     if p.part_kind == "tool-call"]
        #       assert tool_calls == ["count_by_category"]
        #       assert "3 Electronics" in result.output
        pytest.fail("TODO: implement test_single_tool_call_then_answer")

    # TODO: add the rest of the loop tests:
    #   - test_answer_without_tool_calls — FunctionModel that returns text immediately,
    #         no tool calls in messages
    #   - test_chained_tool_calls_in_order — script search_products then update_price;
    #         assert tool_calls == ["search_products", "update_price"]


# ============================================================
# 4. Golden evals — file-driven cases (parametrize the JSON)
# ============================================================

GOLDEN_PATH = Path(__file__).parent / "evals" / "golden_queries.json"


def _golden_cases():
    return json.loads(GOLDEN_PATH.read_text())


def _arguments_for(tool_name: str) -> dict:
    """Minimal args so each tool actually runs against SAMPLE_PRODUCTS."""
    return {
        "search_products": {"term": "speaker"},
        "update_price":    {"product_id": 1, "new_price": 10.0},
    }.get(tool_name, {})


@pytest.mark.eval
class TestGoldenQueries:
    """Drive the agent through canned tool-call sequences and check the answer
    contains the expected substrings. The LLM is mocked via FunctionModel."""

    @pytest.mark.parametrize(
        "case", _golden_cases(), ids=[c["id"] for c in _golden_cases()],
    )
    def test_case_runs_expected_tools(self, case):
        # TODO: build tool_sequence from case["expected_tool_calls"] + _arguments_for,
        #       answer from " ".join(case["expected_answer_contains"]),
        #       then:
        #         with catalog_agent.override(model=FunctionModel(
        #             _scripted_calls(tool_sequence, answer)
        #         )):
        #             with capture_run_messages() as msgs:
        #                 result = catalog_agent.run_sync(case["prompt"], deps=api)
        #         tool_calls = [p.tool_name for msg in msgs for p in msg.parts
        #                       if p.part_kind == "tool-call"]
        #         assert tool_calls == case["expected_tool_calls"]
        #         for needle in case["expected_answer_contains"]:
        #             assert needle in result.output
        pytest.fail("TODO: implement test_case_runs_expected_tools")
