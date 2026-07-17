"""Lab 3 spec — @dataclass Product, the ProductCatalog class, and the FastAPI server.

    pytest tests/test_lab03.py -v

The server tests drive the app in-process with FastAPI's TestClient (no uvicorn,
no curl).
"""

from __future__ import annotations

import dataclasses

import pytest

pytest.importorskip("catalog.models")

try:
    from catalog.models import CatalogError, Product, ProductCatalog  # noqa: E402
    from catalog.storage import load_json, save_json  # noqa: E402
except ImportError:
    pytest.skip(
        "Lab 3 not built yet (catalog.models missing @dataclass Product / "
        "ProductCatalog, or catalog.storage missing load_json / save_json).",
        allow_module_level=True,
    )

if not dataclasses.is_dataclass(Product):
    pytest.skip(
        "Product migrated to a Pydantic model in Lab 4; Lab 3's @dataclass specs retire.",
        allow_module_level=True,
    )


class TestProduct:
    def test_is_a_dataclass_with_expected_fields(self):
        assert dataclasses.is_dataclass(Product)
        names = {f.name for f in dataclasses.fields(Product)}
        assert {"id", "name", "category", "price", "in_stock", "tags"} <= names

    def test_in_stock_defaults_true_and_tags_default_empty(self):
        p = Product(1, "X", "c", 10.0)
        assert p.in_stock is True
        assert p.tags == []

    def test_tags_are_not_shared_between_instances(self):
        a, b = Product(1, "A", "c", 1.0), Product(2, "B", "c", 1.0)
        a.tags.append("x")
        assert b.tags == []


class TestProductCatalog:
    @pytest.fixture
    def cat(self):
        return ProductCatalog([
            Product(10, "USB-C Cable", "Electronics", 499.0, True, ["cable"]),
            Product(20, "Mechanical Keyboard", "Electronics", 5499.0, True, ["kb"]),
            Product(30, "Yoga Mat", "Fitness", 1299.0, False, []),
        ])

    def test_add_get_and_len(self, cat):
        assert cat.get(10).name == "USB-C Cable"
        assert len(cat) == 3

    def test_add_rejects_duplicate_id(self, cat):
        with pytest.raises(CatalogError):
            cat.add(Product(10, "dup", "x", 1.0))

    def test_add_rejects_negative_price(self):
        with pytest.raises(CatalogError):
            ProductCatalog().add(Product(1, "X", "c", -1.0))

    def test_get_missing_raises(self, cat):
        with pytest.raises(CatalogError):
            cat.get(999)

    def test_delete_returns_removed_and_shrinks(self, cat):
        assert cat.delete(10).id == 10
        assert len(cat) == 2

    def test_search_and_filter(self, cat):
        assert {p.id for p in cat.search_by_name("CABLE")} == {10}
        assert {p.id for p in cat.filter_by_price(1000.0)} == {10}

    def test_json_roundtrip(self, tmp_path, cat):
        path = tmp_path / "catalog.json"
        save_json(cat, path)
        loaded = load_json(path)
        assert {p.id for p in loaded.list_all()} == {10, 20, 30}

    def test_load_missing_file_is_empty_catalog(self, tmp_path):
        assert len(load_json(tmp_path / "nope.json")) == 0


class TestServer:
    @pytest.fixture
    def client(self):
        pytest.importorskip("catalog.server")
        testclient = pytest.importorskip("fastapi.testclient")
        from catalog.server import app
        return testclient.TestClient(app)

    def test_health_reports_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_list_returns_seeded_products(self, client):
        r = client.get("/products")
        assert r.status_code == 200
        assert len(r.json()) == 5

    def test_get_missing_id_is_404(self, client):
        assert client.get("/products/999").status_code == 404

    def test_create_then_duplicate_is_409(self, client):
        payload = {"id": 99, "name": "Test", "category": "Misc", "price": 42.0}
        assert client.post("/products", json=payload).status_code == 201
        assert client.post("/products", json=payload).status_code == 409
