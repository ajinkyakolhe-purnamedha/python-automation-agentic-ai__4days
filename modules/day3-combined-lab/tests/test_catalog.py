"""Topic 1 — pytest basics: assert + discovery, pytest.raises, @parametrize,
fixtures, and tmp_path. Pure logic on real objects — no mocks. (The network is
the only edge that earns a fake; that's test_client.py's job, not this one.)
"""

import pytest
from pydantic import ValidationError

from catalog.models import Product, ProductCatalog, CatalogError
from catalog.storage import save_json, load_json


# §1 — a test is a function named test_* that makes an assert
def test_new_catalog_is_empty():
    assert len(ProductCatalog()) == 0


def test_add_then_get_round_trips(sample_product):
    catalog = ProductCatalog()
    catalog.add(sample_product)
    assert catalog.get(sample_product.id) == sample_product


def test_filter_by_price_returns_expected_rows(seeded_catalog):
    cheap = seeded_catalog.filter_by_price(1000.0)          # Cable 499 only
    assert {p.name for p in cheap} == {"Cable"}


# §2 — assert the failure path; use the narrowest exception; collapse cases
def test_get_missing_id_raises(seeded_catalog):
    with pytest.raises(CatalogError, match="not found"):
        seeded_catalog.get(999)


@pytest.mark.parametrize("field, value", [
    ("name", ""),      # min_length=1
    ("price", -1),     # ge=0
    ("id", 0),         # ge=1
])
def test_rejects_invalid_field(field, value):
    good = dict(id=1, name="Widget", category="Misc", price=9.0)
    good[field] = value
    with pytest.raises(ValidationError):
        Product(**good)


# §3 — tmp_path: a REAL temp file, not a mocked filesystem
def test_storage_round_trips(seeded_catalog, tmp_path):
    path = tmp_path / "catalog.json"
    save_json(seeded_catalog, path)
    loaded = load_json(path)
    assert loaded.list_all() == seeded_catalog.list_all()
