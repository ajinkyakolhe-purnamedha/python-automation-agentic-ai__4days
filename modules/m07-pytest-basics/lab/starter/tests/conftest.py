"""Lab 7 — shared fixtures (PROVIDED — use these, you don't need to edit them).

A fixture is a function that returns test data; ask for it by adding its
name as a parameter to a test, and pytest hands each test its OWN fresh copy.

- `sample_product`  → one fully-valid Product
- `seeded_catalog`  → a ProductCatalog with 3 known products
"""

import pytest

from catalog.models import Product, ProductCatalog


@pytest.fixture
def sample_product():
    return Product(id=1, name="Sample", category="Misc",
                   price=99.0, in_stock=True, tags=["sample"])


@pytest.fixture
def seeded_catalog():
    return ProductCatalog([
        Product(id=10, name="Cable",   category="Electronics", price=499.0),
        Product(id=11, name="Speaker", category="Electronics", price=2499.0),
        Product(id=12, name="Mat",     category="Fitness",     price=1299.0, in_stock=False),
    ])
