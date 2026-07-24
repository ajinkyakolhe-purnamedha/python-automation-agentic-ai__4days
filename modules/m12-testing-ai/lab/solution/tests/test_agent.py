"""Lab 12 · Test the Agent — SOLUTION (answer key).

Four classes, matching the four kinds of test an AI system needs.
All run without an API key via Pydantic AI's FunctionModel and TestModel.
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
# Helpers — a real ProductCatalog (no mocking needed)
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
# FunctionModel helpers — script the LLM's tool calls
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
# 1. Tool tests — deterministic Python (Day 3 patterns)
# ============================================================

class TestTools:
    def test_list_products_returns_dicts(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(_force_tool_call("list_products"))):
            with capture_run_messages() as msgs:
                catalog_agent.run_sync("list all", deps=catalog)
        tool_return = [
            p for msg in msgs for p in msg.parts if p.part_kind == "tool-return"
        ][0]
        data = tool_return.content
        assert isinstance(data, list)
        assert data[0]["name"] == "USB-C Cable"

    def test_search_products_is_case_insensitive(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(_force_tool_call("search_products", term="KEYBOARD"))):
            with capture_run_messages() as msgs:
                catalog_agent.run_sync("find keyboard", deps=catalog)
        tool_return = [
            p for msg in msgs for p in msg.parts if p.part_kind == "tool-return"
        ][0]
        data = tool_return.content
        assert len(data) == 1
        assert data[0]["id"] == 2

    def test_count_by_category(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(_force_tool_call("count_by_category"))):
            with capture_run_messages() as msgs:
                catalog_agent.run_sync("count", deps=catalog)
        tool_return = [
            p for msg in msgs for p in msg.parts if p.part_kind == "tool-return"
        ][0]
        data = tool_return.content
        assert data == {"Electronics": 3, "Fitness": 1}

    def test_update_price_mutates(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(
            _force_tool_call("update_price", product_id=1, new_price=10.0)
        )):
            with capture_run_messages() as msgs:
                catalog_agent.run_sync("update price", deps=catalog)
        tool_return = [
            p for msg in msgs for p in msg.parts if p.part_kind == "tool-return"
        ][0]
        data = tool_return.content
        assert data["price"] == 10.0

    def test_all_tools_callable_via_test_model(self):
        """TestModel calls every registered tool with default args — smoke test."""
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=TestModel()):
            result = catalog_agent.run_sync("test", deps=catalog)
        assert result.output


# ============================================================
# 2. Structured output schema tests
# ============================================================

class TestCatalogQuerySchema:
    def test_all_fields_optional(self):
        q = CatalogQuery()
        assert q.category is None
        assert q.in_stock_only is False

    def test_rejects_negative_price(self):
        with pytest.raises(ValidationError):
            CatalogQuery(max_price=-5.0)

    def test_apply_query_filters_by_category_and_price(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        q = CatalogQuery(category="Electronics", max_price=1000.0)
        result = apply_query(q, catalog)
        assert {p["id"] for p in result} == {1}

    def test_apply_query_in_stock_only(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        result = apply_query(CatalogQuery(in_stock_only=True), catalog)
        assert {p["id"] for p in result} == {1, 2, 3}


# ============================================================
# 3. Agent-loop tests — FunctionModel scripts the LLM
# ============================================================

class TestAgentLoop:
    def test_answer_without_tool_calls(self):
        def just_answer(messages, info):
            return ModelResponse(parts=[TextPart("No tools needed, the answer is 42.")])

        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(just_answer)):
            result = catalog_agent.run_sync("nothing to do", deps=catalog)
        assert "42" in result.output

    def test_single_tool_call_then_answer(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(
            _scripted_calls([("count_by_category", {})], "We have 3 Electronics and 1 Fitness product.")
        )):
            with capture_run_messages() as msgs:
                result = catalog_agent.run_sync("how many electronics?", deps=catalog)
        tool_calls = [
            p.tool_name for msg in msgs for p in msg.parts if p.part_kind == "tool-call"
        ]
        assert tool_calls == ["count_by_category"]
        assert "3 Electronics" in result.output

    def test_chained_tool_calls_in_order(self):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        with catalog_agent.override(model=FunctionModel(
            _scripted_calls(
                [("search_products", {"term": "keyboard"}),
                 ("update_price", {"product_id": 2, "new_price": 4999.0})],
                "Updated the keyboard to 4999.",
            )
        )):
            with capture_run_messages() as msgs:
                result = catalog_agent.run_sync("drop the keyboard to 4999", deps=catalog)
        tool_calls = [
            p.tool_name for msg in msgs for p in msg.parts if p.part_kind == "tool-call"
        ]
        assert tool_calls == ["search_products", "update_price"]
        assert "4999" in result.output


# ============================================================
# 4. Golden eval cases — driven from a JSON file
# ============================================================

GOLDEN_PATH = Path(__file__).parent / "evals" / "golden_queries.json"


def _golden_cases():
    return json.loads(GOLDEN_PATH.read_text())


def _arguments_for(tool_name: str) -> dict:
    """Minimal args so the tool actually runs against SAMPLE_PRODUCTS."""
    return {
        "search_products": {"term": "speaker"},
        "update_price":    {"product_id": 1, "new_price": 10.0},
    }.get(tool_name, {})


@pytest.mark.eval
class TestGoldenQueries:
    """Drives the agent through canned tool-call sequences and checks the answer
    contains expected substrings. The LLM is mocked via FunctionModel."""

    @pytest.mark.parametrize(
        "case", _golden_cases(), ids=[c["id"] for c in _golden_cases()],
    )
    def test_case_runs_expected_tools(self, case):
        catalog = _fake_catalog(SAMPLE_PRODUCTS)
        tool_sequence = [
            (name, _arguments_for(name)) for name in case["expected_tool_calls"]
        ]
        answer = " ".join(case["expected_answer_contains"])

        with catalog_agent.override(model=FunctionModel(
            _scripted_calls(tool_sequence, answer)
        )):
            with capture_run_messages() as msgs:
                result = catalog_agent.run_sync(case["prompt"], deps=catalog)

        tool_calls = [
            p.tool_name for msg in msgs for p in msg.parts if p.part_kind == "tool-call"
        ]
        assert tool_calls == case["expected_tool_calls"]
        for needle in case["expected_answer_contains"]:
            assert needle in result.output
