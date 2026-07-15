"""Lab 1 spec — a Product is a dict; the catalog is a list of them (Day 1 Lab 1).

This is your target. Run it and watch it fail, then make it green:

    pytest tests/test_lab01.py -v

Until you create `catalog/models.py` the whole module *skips* (not fails).
"""

from __future__ import annotations

import pytest

pytest.importorskip("catalog.models")

try:
    from catalog.models import (  # noqa: E402
        make_product,
        add_product,
        find_product,
        search_by_name,
        list_products,
    )
except ImportError:
    pytest.skip(
        "Lab 1's dict-functions were migrated to a class in Lab 3; "
        "these checks no longer apply.",
        allow_module_level=True,
    )


class TestProductDict:
    def test_make_product_returns_dict_with_all_fields(self):
        p = make_product(1, "Cable", "Electronics", 499.0)
        assert isinstance(p, dict)
        assert {"id", "name", "category", "price", "in_stock", "tags"} <= set(p)

    def test_in_stock_defaults_true_and_tags_default_empty(self):
        p = make_product(1, "X", "c", 10.0)
        assert p["in_stock"] is True
        assert p["tags"] == []

    def test_tags_are_not_shared_between_products(self):
        # tags default via the None sentinel, NOT tags=[]
        a = make_product(1, "A", "c", 1.0)
        b = make_product(2, "B", "c", 1.0)
        a["tags"].append("x")
        assert b["tags"] == []


class TestCatalogFunctions:
    def test_add_and_find(self):
        cat = []
        add_product(cat, make_product(10, "Cable", "Electronics", 499.0))
        assert find_product(cat, 10)["name"] == "Cable"

    def test_list_returns_all_as_copy(self):
        cat = []
        for i in range(3):
            add_product(cat, make_product(i, f"P{i}", "c", 1.0))
        out = list_products(cat)
        assert len(out) == 3
        out.clear()                 # mutating the returned list...
        assert len(list_products(cat)) == 3   # ...must not affect the catalog

    def test_add_rejects_duplicate_id(self):
        cat = []
        add_product(cat, make_product(1, "A", "c", 1.0))
        with pytest.raises(ValueError):
            add_product(cat, make_product(1, "dup", "c", 1.0))

    def test_add_rejects_negative_price(self):
        with pytest.raises(ValueError):
            add_product([], make_product(1, "X", "c", -1.0))

    def test_find_missing_raises_lookuperror(self):
        with pytest.raises(LookupError):
            find_product([], 999)

    def test_search_by_name_is_case_insensitive_substring(self):
        cat = []
        add_product(cat, make_product(1, "USB-C Cable", "Electronics", 499.0))
        add_product(cat, make_product(2, "Keyboard", "Electronics", 5499.0))
        names = [p["name"] for p in search_by_name(cat, "cable")]
        assert names == ["USB-C Cable"]
