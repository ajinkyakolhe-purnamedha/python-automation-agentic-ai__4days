"""Topic 2 — mocking, taught as a contrast. §A runs the cheap FastAPI app FOR
REAL with TestClient (faking a ProductCatalog we already tested proves nothing).
§B MOCKS the network for get_products — the one call a unit test must not make.
Mock the uncontrollable edge; run the cheap thing for real. (Day 4 reuses this
exact judgment to mock the LLM.)
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi.testclient import TestClient
from pydantic import ValidationError

from catalog import server
from catalog.client import get_products
from catalog.models import Product, ProductCatalog
from catalog.storage import seed_products

client = TestClient(server.app)


@pytest.fixture(autouse=True)
def reset_catalog():
    # server.catalog is a module global seeded with 5 products; a POST in one
    # test would leak into the next — reseed before each test.
    server.catalog = ProductCatalog(list(seed_products()))
    yield


# §A — the real app, in-process, no mocks
def test_server_lists_seeded_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_server_missing_id_is_404():
    assert client.get("/products/999").status_code == 404


# §B — mock the network. spec=requests.Response makes the fake honest.
def _ok_response(payload):
    resp = MagicMock(spec=requests.Response)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_get_products_returns_typed_list():
    rows = [{"id": 1, "name": "Cable", "category": "Electronics",
             "price": 499.0, "in_stock": True, "tags": ["usb"]}]
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value = _ok_response(rows)
        result = get_products("http://x")
    assert isinstance(result[0], Product)
    mock_get.assert_called_once_with("http://x/products", timeout=5)


def test_get_products_propagates_network_error():
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("down")
        with pytest.raises(requests.ConnectionError):
            get_products()


def test_get_products_rejects_malformed_row():
    bad = [{"id": 1, "name": "X", "category": "c", "price": -5,
            "in_stock": True, "tags": []}]                     # price -5 < 0
    with patch("catalog.client.requests.get") as mock_get:
        mock_get.return_value = _ok_response(bad)
        with pytest.raises(ValidationError):
            get_products()
