"""Lab 8 · Part B — mock the network. `get_products` calls requests.get; a unit
test must not hit a real server, so patch `catalog.client.requests.get`.

PROVIDED: `_ok_response`. Fill every `# TODO`; run `pytest tests/test_client.py -q`.
Concepts: codealong/module-8 §"Mock the network".
"""

from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from catalog.client import get_products
from catalog.models import Product

ONE_PRODUCT = [{"id": 1, "name": "Cable", "category": "Electronics",
                "price": 499.0, "in_stock": True, "tags": ["usb"]}]


def _ok_response(payload):  # PROVIDED — a fake requests.Response
    resp = MagicMock(spec=requests.Response)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


def test_get_products_returns_typed_products():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response(ONE_PRODUCT)
        #       result = get_products(); assert isinstance(result[0], Product)
        pytest.fail("TODO: implement test_get_products_returns_typed_products")


def test_hits_right_url():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response([]); get_products("http://x")
        #       mock_get.assert_called_once_with("http://x/products", timeout=5)
        pytest.fail("TODO: implement test_hits_right_url")


def test_propagates_network_error():
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.side_effect = requests.ConnectionError("down")
        #       with pytest.raises(requests.ConnectionError): get_products()
        pytest.fail("TODO: implement test_propagates_network_error")


def test_rejects_malformed_response():
    bad = [{"id": 1, "name": "X", "category": "c", "price": -5, "in_stock": True, "tags": []}]
    with patch("catalog.client.requests.get") as mock_get:
        # TODO: mock_get.return_value = _ok_response(bad)
        #       with pytest.raises(ValidationError): get_products()
        pytest.fail("TODO: implement test_rejects_malformed_response")
