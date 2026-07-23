"""Lab 12 · Test the Agent (catalog.agent) — STARTER SCAFFOLD.

Four classes, one per kind of test an AI system needs. The plumbing below
(the fake APIClient + the LLM-message builders) is GIVEN — it's mocking
boilerplate, not the lesson. Your job is to fill the four test classes,
replacing each `pytest.fail(...)` with real asserts and adding the cases
listed in the comments.

No OpenAI key required: the LLM is fully mocked. Run with
`unset OPENAI_API_KEY && pytest -q`. Concepts: codealong/module-12,
deck §"Testing & Validating AI".
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from catalog.agent import (
    AgentError,
    CatalogAgent,
    CatalogQuery,
    apply_query,
)
from catalog.client import APIClient
from catalog.models import Product, ProductUpdate


# ============================================================
# GIVEN — a fake APIClient backed by a list of Products
# (don't edit; this is the Day-3 mock seam, reused for Day 4)
# ============================================================

def _fake_api(products: list[Product]) -> MagicMock:
    """A MagicMock(spec=APIClient) wired to behave like a working client.

    `spec=APIClient` keeps typos honest — a call to a method the real client
    doesn't have raises instead of silently returning a Mock.
    """
    api = MagicMock(spec=APIClient)
    state = {p.id: p for p in products}

    api.list_products.side_effect = lambda: list(state.values())
    api.get_product.side_effect = lambda pid: state[pid]

    def _update(pid, patch: ProductUpdate):
        updated = state[pid].model_copy(
            update=patch.model_dump(exclude_unset=True)
        )
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


def _make_agent(api=None) -> CatalogAgent:
    """Build a CatalogAgent with a fake api + a placeholder LLM.

    The LLM is a bare MagicMock — each test scripts its responses via
    `.chat.completions.create.side_effect` / `.return_value`.
    """
    api = api or _fake_api(SAMPLE_PRODUCTS)
    llm = MagicMock()
    return CatalogAgent(api_client=api, llm_client=llm, model="test-model")


# --- GIVEN: builders that match OpenAI's response shape ------

def _llm_message(content=None, tool_calls=None):
    """Build a fake OpenAI ChatCompletionMessage shape."""
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = tool_calls or None
    return msg


def _tool_call(call_id: str, name: str, **arguments) -> MagicMock:
    """Build a fake tool-call object: `.id`, `.function.name`, `.function.arguments`."""
    call = MagicMock()
    call.id = call_id
    call.function = MagicMock()
    call.function.name = name
    call.function.arguments = json.dumps(arguments)
    return call


def _llm_response(message) -> MagicMock:
    """Wrap a message in the `.choices[0].message` envelope the SDK returns."""
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


# ============================================================
# 1. Tool tests — the tools are plain Python (Day-3 patterns)
#    Reach a tool's function via: agent.registry.get(name).fn(...)
# ============================================================

class TestTools:
    def test_count_by_category(self):
        """count_by_category() returns deterministic counts over SAMPLE_PRODUCTS."""
        agent = _make_agent()
        # TODO: result = agent.registry.get("count_by_category").fn()
        #       assert result == {"Electronics": 3, "Fitness": 1}
        pytest.fail("TODO: implement test_count_by_category")

    # TODO: add the rest of the tool tests:
    #   - test_list_products_returns_dicts — .fn() is a list; result[0]["name"] == "USB-C Cable"
    #   - test_search_products_is_case_insensitive — fn(term="KEYBOARD") → one hit, id == 2
    #   - test_update_price_mutates — fn(product_id=1, new_price=10.0)["price"] == 10.0
    #   - test_unknown_tool_raises — registry.get("does_not_exist") raises KeyError


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
    #     (build the client with `api = _fake_api(SAMPLE_PRODUCTS)`, then apply_query(q, api))


# ============================================================
# 3. Agent-loop tests — mock the LLM, assert tool order
#    Script responses via .chat.completions.create.side_effect=[...]
# ============================================================

class TestAgentLoop:
    def test_single_tool_call_then_answer(self):
        """One tool call, then a final answer → two steps, correct tool + result."""
        agent = _make_agent()
        # TODO: agent.llm.chat.completions.create.side_effect = [
        #           _llm_response(_llm_message(
        #               tool_calls=[_tool_call("c1", "count_by_category")])),
        #           _llm_response(_llm_message(content="We have 3 Electronics.")),
        #       ]
        #       result = agent.ask("how many electronics?")
        #       assert result.steps == 2
        #       assert [c.tool for c in result.tool_calls] == ["count_by_category"]
        #       assert result.tool_calls[0].result == {"Electronics": 3, "Fitness": 1}
        pytest.fail("TODO: implement test_single_tool_call_then_answer")

    # TODO: add the rest of the loop tests:
    #   - test_answer_without_tool_calls — content-only response → steps == 1, tool_calls == []
    #   - test_chained_tool_calls_in_order — search_products then update_price; assert order +
    #       that tool_calls[-1].arguments == {"product_id": 2, "new_price": 4999.0}
    #   - test_max_steps_hit_raises — make create.return_value ALWAYS a tool call so the loop
    #       never converges; with pytest.raises(AgentError, match="did not converge"): agent.ask(...)
    #   - test_unknown_tool_in_response_returns_error_observation — script a tool_call for
    #       "does_not_exist" then a content answer. The agent records an ERROR OBSERVATION (it does
    #       NOT raise), so the LLM can see the failure and recover:
    #         assert result.tool_calls[0].tool == "does_not_exist"
    #         assert "error" in result.tool_calls[0].result
    #         assert "unknown tool" in result.tool_calls[0].result["error"]


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
    contains the expected substrings. The LLM is fully mocked: each case scripts
    its own tool calls, so this stays deterministic without an API key."""

    @pytest.mark.parametrize(
        "case", _golden_cases(), ids=[c["id"] for c in _golden_cases()],
    )
    def test_case_runs_expected_tools(self, case):
        agent = _make_agent()
        # TODO: build a fake LLM script — one tool call per expected tool, then a
        #       final answer that mentions every required substring:
        #         scripted = []
        #         for i, tool_name in enumerate(case["expected_tool_calls"]):
        #             args = _arguments_for(tool_name)
        #             scripted.append(_llm_response(_llm_message(
        #                 tool_calls=[_tool_call(f"c{i}", tool_name, **args)])))
        #         scripted.append(_llm_response(_llm_message(
        #             content=" ".join(case["expected_answer_contains"]))))
        #         agent.llm.chat.completions.create.side_effect = scripted
        #       result = agent.ask(case["prompt"])
        #       assert [c.tool for c in result.tool_calls] == case["expected_tool_calls"]
        #       for needle in case["expected_answer_contains"]:
        #           assert needle in result.answer
        pytest.fail("TODO: implement test_case_runs_expected_tools")
