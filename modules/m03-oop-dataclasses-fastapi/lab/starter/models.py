"""Catalog model — Day 1 Lab 3 (Product becomes a @dataclass; the catalog a class).

The Module-3 refactor: Lab 1/2's product-dicts and loose functions become a typed
`@dataclass Product` and a `ProductCatalog` class whose **methods** are the old
functions. This supersedes Lab 2's `storage.py` (the class now owns persistence too).

Copy into your `catalog/` package and fill every `# TODO`.
Done-signal: pytest tests/test_lab03.py -v goes green.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


class CatalogError(Exception):
    """Raised when a catalog operation fails (duplicate id, missing id, bad price)."""


@dataclass
class Product:
    # TODO: typed fields — id:int, name:str, category:str, price:float,
    #       in_stock:bool=True, tags:list[str]=field(default_factory=list)
    ...


class ProductCatalog:
    """An in-memory catalog of Products, keyed by id."""

    def __init__(self, products: list[Product] | None = None) -> None:
        self._items: dict[int, Product] = {}
        for p in products or []:
            self.add(p)

    def add(self, product: Product) -> Product:
        # TODO: raise CatalogError on negative price and on duplicate id;
        #       then store, logger.info(...), and return the product
        ...

    def get(self, product_id: int) -> Product:
        # TODO: raise CatalogError("...not found...") if missing, else return it
        ...

    def delete(self, product_id: int) -> Product:
        # TODO: raise CatalogError if missing, else pop and return the removed product
        ...

    def search_by_name(self, term: str) -> list[Product]:
        # TODO: comprehension over self._items.values(), case-insensitive name match
        ...

    def filter_by_price(self, max_price: float) -> list[Product]:
        # TODO: comprehension, keep where p.price <= max_price
        ...

    def list_all(self) -> list[Product]:
        # TODO: a list of the stored products
        ...

    def __len__(self) -> int:
        # TODO: how many products are stored?
        ...

    def save_json(self, path: str | Path) -> None:
        # TODO: write [asdict(p) for p in self.list_all()] as JSON, indent=2
        ...


def load_json(path: str | Path) -> ProductCatalog:
    """Build a ProductCatalog from a JSON file (missing file -> empty catalog)."""
    # TODO: if not Path(path).exists(): return ProductCatalog()
    #       rows = json.loads(Path(path).read_text())
    #       return ProductCatalog([Product(**row) for row in rows])
    ...
