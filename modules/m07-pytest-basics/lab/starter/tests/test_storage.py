"""Lab 7 · Part C — storage round-trips on a REAL temp file (pytest's tmp_path).

`tmp_path` is a built-in fixture: a fresh temp directory per test. This is the
right tool for file I/O — you verify real serialization, you do NOT mock the
filesystem (that's an anti-pattern; mocks are for M08's network edge).

Fill each `# TODO`, replace `pytest.fail(...)`, run `pytest tests/test_storage.py -q`.
"""

import pytest

from catalog.models import Product, ProductCatalog
from catalog.storage import save_json, load_json


def test_json_roundtrip(tmp_path):
    """save_json then load_json returns an equal catalog."""
    cat = ProductCatalog([
        Product(id=1, name="Cable", category="Electronics", price=499.0),
        Product(id=2, name="Mat", category="Fitness", price=1299.0, in_stock=False),
    ])
    path = tmp_path / "catalog.json"
    # TODO: save_json(cat, path); loaded = load_json(path)
    #       assert loaded.list_all() == cat.list_all()
    pytest.fail("TODO: implement test_json_roundtrip")


def test_load_missing_file_returns_empty(tmp_path):
    """load_json on a non-existent path returns an empty catalog, not a crash."""
    # TODO: loaded = load_json(tmp_path / "nope.json"); assert len(loaded) == 0
    pytest.fail("TODO: implement test_load_missing_file_returns_empty")
