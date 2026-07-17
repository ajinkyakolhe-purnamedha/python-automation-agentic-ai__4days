"""Catalog model — the Day-1 (Lab 3) end state.

`Product` is a `@dataclass`; `ProductCatalog` is a class whose **methods** are
Lab 1/2's loose functions. The class owns the data + the queries; `storage.py`
handles JSON persistence.

This is the finished Lab 3 — exactly what Day 2 (Lab 4) starts from.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id, bad price)."""


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    in_stock: bool = True
    tags: list[str] = field(default_factory=list)   # NOT `= []` — that list would be shared

    def to_dict(self) -> dict:
        """Serialise to a plain dict. (Day 2's Pydantic model swaps this for model_dump().)"""
        return asdict(self)


class ProductCatalog:
    """An in-memory catalog of Products, keyed by id."""

    def __init__(self, products: list[Product] | None = None) -> None:
        self._items: dict[int, Product] = {}
        for p in products or []:
            self.add(p)

    def add(self, product: Product) -> Product:
        if product.price < 0:
            raise CatalogError(f"Product price must be >= 0, got {product.price}")
        if product.id in self._items:
            raise CatalogError(f"Product id {product.id} already exists")
        self._items[product.id] = product
        logger.info("added product id=%s name=%r", product.id, product.name)
        return product

    def get(self, product_id: int) -> Product:
        if product_id not in self._items:
            raise CatalogError(f"Product id {product_id} not found")
        return self._items[product_id]

    def delete(self, product_id: int) -> Product:
        if product_id not in self._items:
            raise CatalogError(f"Product id {product_id} not found")
        removed = self._items.pop(product_id)
        logger.info("deleted product id=%s", product_id)
        return removed

    def search_by_name(self, term: str) -> list[Product]:
        needle = term.lower()
        return [p for p in self._items.values() if needle in p.name.lower()]

    def filter_by_price(self, max_price: float) -> list[Product]:
        return [p for p in self._items.values() if p.price <= max_price]

    def list_all(self) -> list[Product]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)
