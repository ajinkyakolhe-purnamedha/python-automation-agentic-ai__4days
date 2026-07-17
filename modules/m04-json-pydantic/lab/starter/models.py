"""Catalog model — Day 2 Lab 4: @dataclass -> Pydantic.

Yesterday `Product` was a `@dataclass` (free `__init__`/`__repr__`, but NO
validation). Today it becomes a Pydantic `BaseModel` — same fields, **validated
on construction** — and the FastAPI server gets automatic 422s + a rich `/docs`.

`ProductCatalog` is **given**: it's the class you wrote in Lab 3, unchanged.
That's the point of today — the catalog doesn't care that its Products got
validated, so it doesn't move. Here you write exactly one thing: the `Product`
model. (Persistence lives in `storage.py`, as it has since Lab 3 — that's the
layering: this module is the domain core, that one is the disk.)

Fill the one `# TODO`. Done-signal: pytest tests/test_lab04.py -v goes green.
Concepts: codealong-m04-json-pydantic.ipynb (BaseModel, Field,
model_validate/model_dump).
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id)."""


class Product(BaseModel):
    # TODO: the same six fields Lab 3's dataclass had — but each one now carries
    #       its RULE, not just its type. `Field(...)` is where a rule lives
    #       (module-4, §2.1; the code-along has the syntax).
    #
    #         id        int        must be at least 1
    #         name      str        at least 1 character — no empty names
    #         category  str        at least 1 character
    #         price     float      at least 0. NOT "greater than 0": a free
    #                              item is legal; a negative one is not.
    #         in_stock  bool       defaults to True
    #         tags      list[str]  defaults to an empty list
    #
    #       That last one bit you in Lab 3: a bare `= []` is shared by every
    #       instance. Pydantic's `Field` takes the same escape hatch the
    #       dataclass did, for the same reason.
    ...


class ProductCatalog:
    """In-memory catalog keyed by id.

    GIVEN — this is your Lab 3 class, carried over as-is. It now holds Pydantic
    Products instead of dataclass ones, and needed no changes to do it. Read
    `add` though: Lab 3's manual negative-price check is **gone**, because the
    `Product` model above rejects a bad price before `add` ever sees it. The
    duplicate-id rule stays — that's a *catalog* rule, not a *field* rule.
    """

    def __init__(self, products: list[Product] | None = None) -> None:
        self._items: dict[int, Product] = {}
        for p in products or []:
            self.add(p)

    def add(self, product: Product) -> Product:
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
