"""Lab 5 spec — the typed `APIClient` and its retry loop.

    pytest tests/test_lab05.py -v

Skips until `catalog/client.py` exists. Uses a tiny fake session — the same
dependency-injection seam your client is built around — so no live server is
needed (Day 3 turns this into real mocking).
"""

from __future__ import annotations

import pytest


class _FakeResponse:
    def __init__(self, status_code, json_body):
        self.status_code = status_code
        self._json = json_body
        self.text = str(json_body)
        self.reason = "fake"

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def json(self):
        return self._json


class _FakeSession:
    """Returns queued outcomes in order; an Exception in the queue is raised
    (lets us simulate a transient network failure for the retry-loop check)."""

    def __init__(self, outcomes):
        self._outcomes = list(outcomes)
        self.headers = {}
        self.calls = 0

    def request(self, method, url, **kwargs):
        self.calls += 1
        item = self._outcomes.pop(0) if len(self._outcomes) > 1 else self._outcomes[0]
        if isinstance(item, Exception):
            raise item
        return item


PRODUCTS = [
    {"id": 1, "name": "Cable", "category": "Electronics",
     "price": 499.0, "in_stock": True, "tags": ["usb"]},
    {"id": 2, "name": "Keyboard", "category": "Electronics",
     "price": 5499.0, "in_stock": True, "tags": ["mech"]},
]

# Spans three categories (one of them a single item) so count_by_category has
# something real to group — PRODUCTS above is all-Electronics on purpose.
MIXED_PRODUCTS = PRODUCTS + [
    {"id": 3, "name": "Bottle", "category": "Home",
     "price": 899.0, "in_stock": True, "tags": []},
    {"id": 4, "name": "Yoga Mat", "category": "Fitness",
     "price": 1299.0, "in_stock": False, "tags": []},
    {"id": 5, "name": "Lamp", "category": "Home",
     "price": 1499.0, "in_stock": True, "tags": []},
]


class TestAPIClient:
    def test_apierror_exposes_status_and_detail(self):
        c = pytest.importorskip("catalog.client")
        err = c.APIError(404, "not found")
        assert err.status_code == 404 and err.detail == "not found"

    def test_list_products_returns_typed_models(self):
        c = pytest.importorskip("catalog.client")
        models = pytest.importorskip("catalog.models")
        client = c.APIClient(session=_FakeSession([_FakeResponse(200, PRODUCTS)]))
        result = client.list_products()
        assert all(isinstance(p, models.Product) for p in result)   # not raw dicts
        assert [p.id for p in result] == [1, 2]

    def test_create_product_returns_typed_model(self):
        c = pytest.importorskip("catalog.client")
        models = pytest.importorskip("catalog.models")
        client = c.APIClient(session=_FakeSession([_FakeResponse(201, PRODUCTS[0])]))
        payload = models.Product(
            id=1, name="Cable", category="Electronics", price=499.0, tags=["usb"]
        )
        result = client.create_product(payload)
        assert isinstance(result, models.Product)   # not a raw dict
        assert result.id == 1

    def test_count_by_category_groups_the_catalog(self):
        c = pytest.importorskip("catalog.client")
        pytest.importorskip("catalog.models")
        client = c.APIClient(session=_FakeSession([_FakeResponse(200, MIXED_PRODUCTS)]))
        assert client.count_by_category() == {"Electronics": 2, "Home": 2, "Fitness": 1}

    def test_count_by_category_on_an_empty_catalog(self):
        c = pytest.importorskip("catalog.client")
        pytest.importorskip("catalog.models")
        client = c.APIClient(session=_FakeSession([_FakeResponse(200, [])]))
        assert client.count_by_category() == {}   # no products, no categories — not a crash

    def test_non_2xx_raises_apierror(self):
        c = pytest.importorskip("catalog.client")
        pytest.importorskip("catalog.models")
        client = c.APIClient(session=_FakeSession([_FakeResponse(409, {"detail": "dup"})]))
        with pytest.raises(c.APIError) as excinfo:
            client.list_products()
        assert excinfo.value.status_code == 409

    def test_retry_recovers_from_transient_error(self):
        c = pytest.importorskip("catalog.client")
        pytest.importorskip("catalog.models")
        import requests

        session = _FakeSession([
            requests.ConnectionError("boom"),
            requests.ConnectionError("boom"),
            _FakeResponse(200, PRODUCTS),
        ])
        result = c.APIClient(session=session).list_products()
        assert len(result) == 2
        assert session.calls == 3   # proves the retry loop runs in _request (2 fails + 1 ok)
