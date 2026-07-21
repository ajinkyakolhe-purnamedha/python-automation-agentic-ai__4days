"""Lab 7 · Part B — test the ProductCatalog collection class.

Every test follows Arrange → Act → Assert. Use the `seeded_catalog` fixture
(from conftest.py) by naming it as a parameter — you get a fresh 3-product
catalog each time. Fill every `# TODO`; run `pytest tests/test_catalog.py -q`.

Pin BOTH the happy paths (it returns the right rows) AND the error paths
(a rule fires) — `pytest.raises(CatalogError)` passes only if it's raised.
"""

import pytest

from catalog.models import CatalogError, Product, ProductCatalog, ProductUpdate


class TestProductCatalog:
    def test_starts_empty(self):
        """A brand-new ProductCatalog has length 0 and lists nothing."""
        # TODO: c = ProductCatalog(); assert len(c) == 0 and c.list_all() == []
        pytest.fail("TODO: implement test_starts_empty")

    def test_add_and_get(self, seeded_catalog):
        """get(id) returns the product that was seeded."""
        # TODO: assert seeded_catalog.get(10).name == "Cable"
        pytest.fail("TODO: implement test_add_and_get")

    def test_add_rejects_duplicate_id(self, seeded_catalog):
        """Adding an id that already exists raises CatalogError."""
        # TODO: with pytest.raises(CatalogError, match="already exists"):
        #           seeded_catalog.add(Product(id=10, name="dup", category="x", price=1.0))
        pytest.fail("TODO: implement test_add_rejects_duplicate_id")

    def test_get_missing_raises(self, seeded_catalog):
        """get() on an unknown id raises CatalogError."""
        # TODO: with pytest.raises(CatalogError, match="not found"): seeded_catalog.get(999)
        pytest.fail("TODO: implement test_get_missing_raises")

    def test_delete(self, seeded_catalog):
        """delete() returns the removed product and shrinks the catalog."""
        # TODO: removed = seeded_catalog.delete(10); assert removed.id == 10 and len(...) == 2
        pytest.fail("TODO: implement test_delete")

    def test_delete_missing_raises(self, seeded_catalog):
        """delete() on an unknown id raises CatalogError."""
        # TODO: with pytest.raises(CatalogError): seeded_catalog.delete(999)
        pytest.fail("TODO: implement test_delete_missing_raises")


class TestQueries:
    def test_search_by_name_is_case_insensitive(self, seeded_catalog):
        """search_by_name matches regardless of case."""
        # TODO: hits = seeded_catalog.search_by_name("CABLE"); assert {p.id for p in hits} == {10}
        pytest.fail("TODO: implement test_search_by_name_is_case_insensitive")

    def test_filter_by_price(self, seeded_catalog):
        """filter_by_price returns only products at or below the cap."""
        # TODO: cheap = seeded_catalog.filter_by_price(1000.0); assert {p.id for p in cheap} == {10}
        pytest.fail("TODO: implement test_filter_by_price")

    def test_group_by_category(self, seeded_catalog):
        """group_by_category buckets products by their category."""
        # TODO: groups = seeded_catalog.group_by_category()
        #       assert the keys are {"Electronics", "Fitness"} and Electronics has 2
        pytest.fail("TODO: implement test_group_by_category")


class TestUpdate:
    def test_partial_update_changes_only_supplied_fields(self, seeded_catalog):
        """update() changes the fields you pass and leaves the rest alone."""
        # TODO: seeded_catalog.update(10, ProductUpdate(price=9.99))
        #       assert price changed to 9.99 but name/category are unchanged
        pytest.fail("TODO: implement test_partial_update_changes_only_supplied_fields")

    def test_update_missing_id_raises(self, seeded_catalog):
        """update() on an unknown id raises CatalogError."""
        # TODO: with pytest.raises(CatalogError): seeded_catalog.update(999, ProductUpdate(price=1.0))
        pytest.fail("TODO: implement test_update_missing_id_raises")
