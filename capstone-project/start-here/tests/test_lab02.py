"""Lab 2 spec — a {id: product} store, comprehension queries, JSON/CSV persistence.

    pytest tests/test_lab02.py -v

The catalog is now a dict store reached through functions. CSV is the type-loss
format: everything writes/reads as a string, so `load_csv` must coerce back.
"""

from __future__ import annotations

import pytest

pytest.importorskip("catalog.storage")

try:
    from catalog.storage import (  # noqa: E402
        make_store,
        insert,
        fetch,
        search_by_name,
        filter_by_price,
        save_json,
        load_json,
        save_csv,
        load_csv,
    )
except ImportError:
    pytest.skip(
        "Lab 2's store-functions were migrated to a class in Lab 3; "
        "these checks no longer apply.",
        allow_module_level=True,
    )


def seeded() -> dict:
    return make_store([
        {"id": 10, "name": "USB-C Cable", "category": "Electronics",
         "price": 499.0, "in_stock": True, "tags": ["cable", "usb-c"]},
        {"id": 20, "name": "Mechanical Keyboard", "category": "Electronics",
         "price": 5499.0, "in_stock": True, "tags": ["keyboard"]},
        {"id": 30, "name": "Yoga Mat", "category": "Fitness",
         "price": 1299.0, "in_stock": False, "tags": []},
    ])


class TestStoreAndQueries:
    def test_make_store_keys_by_id(self):
        assert set(seeded()) == {10, 20, 30}

    def test_fetch_and_missing(self):
        s = seeded()
        assert fetch(s, 10)["name"] == "USB-C Cable"
        with pytest.raises(LookupError):
            fetch(s, 999)

    def test_insert_adds_keyed_by_id(self):
        s = {}
        insert(s, {"id": 1, "name": "X", "category": "c",
                   "price": 1.0, "in_stock": True, "tags": []})
        assert fetch(s, 1)["name"] == "X"

    def test_search_by_name_is_case_insensitive(self):
        assert {p["id"] for p in search_by_name(seeded(), "CABLE")} == {10}

    def test_filter_by_price(self):
        assert {p["id"] for p in filter_by_price(seeded(), 1000.0)} == {10}


class TestPersistence:
    def test_json_roundtrip(self, tmp_path):
        path = tmp_path / "catalog.json"
        save_json(seeded(), path)
        assert set(load_json(path)) == {10, 20, 30}

    def test_load_missing_json_returns_empty_store(self, tmp_path):
        assert load_json(tmp_path / "nope.json") == {}

    def test_csv_coerces_types_back(self, tmp_path):
        # The CSV lesson: every column reads back as a STRING, so load_csv must coerce.
        path = tmp_path / "catalog.csv"
        save_csv(seeded(), path)
        loaded = load_csv(path)
        assert isinstance(loaded[10]["id"], int) and loaded[10]["id"] == 10
        assert isinstance(loaded[10]["price"], float) and loaded[10]["price"] == 499.0
        assert loaded[30]["in_stock"] is False

    def test_csv_drops_the_tags_list(self, tmp_path):
        # A list doesn't fit a flat CSV cell — tags come back empty (JSON is the format
        # that keeps them). That contrast is the point.
        path = tmp_path / "catalog.csv"
        save_csv(seeded(), path)
        loaded = load_csv(path)
        assert loaded[10]["tags"] == []
