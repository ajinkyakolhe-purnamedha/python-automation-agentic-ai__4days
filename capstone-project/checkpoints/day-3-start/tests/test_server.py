"""Lab 8 · Part A — test the server FOR REAL, in-process (no mocks).

TestClient runs the FastAPI app with a real ProductCatalog. The app holds
`catalog` as a module global seeded with 5 products, so a POST leaks between
tests — the PROVIDED autouse `reset_catalog` fixture reseeds before each.

Fill every `# TODO`; run `pytest tests/test_server.py -q`.
"""

import pytest
from fastapi.testclient import TestClient

from catalog import server
from catalog.models import ProductCatalog
from catalog.storage import seed_products

client = TestClient(server.app)


@pytest.fixture(autouse=True)
def reset_catalog():  # PROVIDED — keeps tests isolated; do not edit
    server.catalog = ProductCatalog(list(seed_products()))
    yield


def test_health_reports_seed_count():
    # TODO: r = client.get("/health"); assert r.status_code == 200
    #       assert r.json() == {"status": "ok", "count": 5}
    pytest.fail("TODO: implement test_health_reports_seed_count")


def test_list_returns_seed():
    # TODO: r = client.get("/products"); assert r.status_code == 200 and len(r.json()) == 5
    pytest.fail("TODO: implement test_list_returns_seed")


def test_create_then_get_roundtrip():
    # TODO: POST /products {"id":900,"name":"Test","category":"QA","price":12.0} -> 201
    #       then GET /products/900 -> 200 and json()["name"] == "Test"
    pytest.fail("TODO: implement test_create_then_get_roundtrip")


def test_missing_returns_404():
    # TODO: assert client.get("/products/999").status_code == 404
    pytest.fail("TODO: implement test_missing_returns_404")


def test_duplicate_returns_409():
    # TODO: POST an id that is already seeded (id 1) -> 409
    pytest.fail("TODO: implement test_duplicate_returns_409")
