"""Lab 12 · Test the Agent (catalog.agent) — STARTER SCAFFOLD.

Four classes, one per kind of test an AI system needs. The plumbing below
(the ProductCatalog helper + the FunctionModel helpers) is GIVEN — it's
test setup, not the lesson. Your job is to fill the four test classes,
replacing each ``pytest.fail(...)`` with real asserts.

No OpenAI key required: the LLM is fully mocked via Pydantic AI's
``FunctionModel`` and ``TestModel``. Run with
``unset OPENAI_API_KEY && uv run pytest -q``.
"""

from __future__ import annotations

import json
from pathlib import Path

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
from catalog.models import Product, ProductCatalog

pydantic_ai.models.ALLOW_MODEL_REQUESTS = False


# ============================================================
# GIVEN — a real ProductCatalog seeded with sample data
# (no mocking needed — ProductCatalog is plain Python)
# ============================================================

def _fake_catalog(products: list[Product]) -> ProductCatalog:
    """A real ProductCatalog — no mocking needed."""
    return ProductCatalog(products)


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
        # TODO: Force the agent to call one specific tool, then inspect what it returned.
        #   Hint 1: wrap _force_tool_call("count_by_category") in a FunctionModel, then
        #           use catalog_agent.override(model=...) — search "pydantic ai FunctionModel"
        #   Hint 2: inside the override, use capture_run_messages() to grab the conversation;
        #           look for the message part with part_kind == "tool-return" — its .content
        #           is the tool's return value. Assert it matches the expected counts.
        pytest.fail("TODO: implement test_count_by_category")

    # TODO: add more tool tests using the same pattern as test_count_by_category:
    #   - test_list_products_returns_dicts — force "list_products", check it returns a list
    #         and the first item's name is "USB-C Cable"
    #   - test_search_products_is_case_insensitive — force "search_products" with
    #         term="KEYBOARD", expect one match with id == 2
    #   - test_update_price_mutates — force "update_price" with product_id=1 and
    #         new_price=10.0, check the returned dict has the new price
    #   - test_all_tools_callable_via_test_model — a smoke test: override with TestModel()
    #         (no scripting needed), run the agent, and just assert result.output is truthy


# ============================================================
# 2. Schema tests — Pydantic validation of LLM JSON outputs
#    (same discipline as Day-2/Day-3 model tests)
# ============================================================

class TestCatalogQuerySchema:
    def test_rejects_negative_price(self):
        """A negative max_price fails validation (the schema guards the LLM's JSON)."""
        # TODO: Try to create a CatalogQuery with an invalid value and assert it raises.
        #   Hint 1: search "pytest.raises" — you've used this pattern in Day 3
        #   Hint 2: CatalogQuery(max_price=-5.0) should fail — what exception does
        #           Pydantic raise on invalid data?
        pytest.fail("TODO: implement test_rejects_negative_price")

    # TODO: add more schema tests — these are pure Pydantic, no LLM:
    #   - test_all_fields_optional — construct CatalogQuery() with no args;
    #         category should be None, in_stock_only should be False
    #   - test_apply_query_filters_by_category_and_price — build a CatalogQuery for
    #         Electronics under 1000, pass it to apply_query() with a _fake_catalog,
    #         only product id 1 should survive
    #   - test_apply_query_in_stock_only — filter in_stock_only=True;
    #         ids {1, 2, 3} should remain (Yoga Mat is out of stock)


# ============================================================
# 3. Agent-loop tests — FunctionModel scripts the LLM
#    Use _scripted_calls + capture_run_messages to verify tool order
# ============================================================

class TestAgentLoop:
    def test_single_tool_call_then_answer(self):
        """One tool call, then a final answer → correct tool called, correct output."""
        # TODO: Script the LLM to call one tool then give a final answer. Verify both.
        #   Hint 1: _scripted_calls() takes a list of (tool_name, args) pairs and a
        #           final answer string — wrap it in FunctionModel, then override the agent
        #   Hint 2: inside capture_run_messages(), run the agent; then extract tool-call
        #           parts from the messages (part_kind == "tool-call" has .tool_name) —
        #           assert the sequence is what you scripted, and the answer substring
        #           appears in result.output
        pytest.fail("TODO: implement test_single_tool_call_then_answer")

    # TODO: add more loop tests — same override + capture pattern:
    #   - test_answer_without_tool_calls — write a FunctionModel callback that returns
    #         a TextPart immediately (no tool calls); assert result.output has the text
    #   - test_chained_tool_calls_in_order — script two tools in sequence
    #         (search_products then update_price); assert the tool_calls list matches


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
        # TODO: Drive the agent through the golden case and verify tool calls + answer.
        #   Hint 1: each case dict has "expected_tool_calls" (list of tool names) and
        #           "expected_answer_contains" (substrings). Build a tool_sequence for
        #           _scripted_calls using _arguments_for() to get valid args per tool.
        #   Hint 2: same override + capture pattern as TestAgentLoop — run the agent
        #           with the case's prompt, then assert the tool-call sequence matches
        #           and every expected substring appears in result.output
        pytest.fail("TODO: implement test_case_runs_expected_tools")
