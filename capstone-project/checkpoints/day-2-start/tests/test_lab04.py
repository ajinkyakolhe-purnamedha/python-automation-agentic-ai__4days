"""Lab 4 spec — Product becomes a Pydantic model; the FastAPI server is typed.

    pytest tests/test_lab04.py -v

Tests **skip** until Product is a Pydantic BaseModel, then go red → green. The
server tests run the app in-process with FastAPI's TestClient (no uvicorn).
"""

from __future__ import annotations

import pytest

pytest.importorskip("catalog.models")

try:
    from catalog.models import CatalogError, Product, ProductCatalog
    from catalog.storage import load_json, save_json
    from pydantic import BaseModel, ValidationError
except ImportError:
    pytest.skip("Lab 4 not built yet (Product / storage helpers missing).", allow_module_level=True)

if not (isinstance(Product, type) and issubclass(Product, BaseModel)):
    pytest.skip("Product is not a Pydantic model yet (Lab 4 step 1).", allow_module_level=True)


class TestModel:
    def test_coerces_string_numbers(self):
        p = Product.model_validate({"id": "1", "name": "Widget", "category": "Misc", "price": "9.50"})
        assert p.id == 1 and p.price == 9.5         # strings coerced to int / float

    def test_rejects_empty_name(self):
        with pytest.raises(ValidationError):
            Product.model_validate({"id": 1, "name": "", "category": "x", "price": 5})

    def test_rejects_negative_price(self):
        with pytest.raises(ValidationError):
            Product.model_validate({"id": 1, "name": "X", "category": "x", "price": -5})

    def test_rejects_id_below_one(self):
        with pytest.raises(ValidationError):
            Product.model_validate({"id": 0, "name": "X", "category": "x", "price": 5})

    def test_dump_validate_roundtrip(self):
        p = Product(id=1, name="A", category="C", price=10.0)
        assert Product.model_validate(p.model_dump()) == p


class TestCatalog:
    @pytest.fixture
    def cat(self):
        return ProductCatalog([
            Product(id=10, name="USB-C Cable", category="Electronics", price=499.0),
            Product(id=20, name="Yoga Mat", category="Fitness", price=1299.0, in_stock=False),
        ])

    def test_add_duplicate_raises(self, cat):
        with pytest.raises(CatalogError):
            cat.add(Product(id=10, name="dup", category="x", price=1.0))

    def test_get_missing_raises(self, cat):
        with pytest.raises(CatalogError):
            cat.get(999)

    def test_search_and_filter(self, cat):
        assert {p.id for p in cat.search_by_name("cable")} == {10}
        assert {p.id for p in cat.filter_by_price(1000.0)} == {10}

    def test_json_roundtrip(self, tmp_path, cat):
        path = tmp_path / "catalog.json"
        save_json(cat, path)
        assert {p.id for p in load_json(path).list_all()} == {10, 20}


class TestServer:
    @pytest.fixture
    def client(self):
        pytest.importorskip("catalog.server")
        testclient = pytest.importorskip("fastapi.testclient")
        from catalog.server import app
        return testclient.TestClient(app)

    def test_bad_post_is_422(self, client):
        r = client.post("/products", json={"id": 51, "name": "", "category": "x", "price": -1})
        assert r.status_code == 422            # Pydantic rejects bad input at the boundary

    def test_health_survives_the_pydantic_migration(self, client):
        # Lab 3's /health route must still be there: Lab 6's importer pings it to
        # fail fast. Lab 3's spec retires here, so this is what keeps it honest.
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"

    def test_list_products_works(self, client):
        r = client.get("/products")
        assert r.status_code == 200 and isinstance(r.json(), list)

    def test_get_one_product_works(self, client):
        first_id = client.get("/products").json()[0]["id"]
        r = client.get(f"/products/{first_id}")
        assert r.status_code == 200 and r.json()["id"] == first_id

    def test_create_then_duplicate_is_409(self, client):
        body = {"id": 77, "name": "Test", "category": "Misc", "price": 42.0}
        assert client.post("/products", json=body).status_code == 201
        assert client.post("/products", json=body).status_code == 409
