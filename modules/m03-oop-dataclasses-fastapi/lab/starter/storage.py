"""Catalog persistence — Day 1 Lab 3 (a separate module, not a class method).

Carried over from Lab 2 and updated for objects: serialise a Product via
`to_dict()`, rebuild via `Product(**row)`. The `ProductCatalog` class owns the
data + queries; this module just reads/writes it to disk.

Copy into your `catalog/` package and fill every `# TODO`.
Done-signal: uv run pytest tests/test_lab03.py -v goes green.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Product, ProductCatalog


def save_json(catalog: ProductCatalog, path: str | Path) -> None:
    """Write the catalog's products to JSON as a list (indent=2)."""
    # TODO: Path(path).write_text(
    #           json.dumps([p.to_dict() for p in catalog.list_all()], indent=2))
    ...


def load_json(path: str | Path) -> ProductCatalog:
    """Rebuild a ProductCatalog from JSON. Missing file -> empty catalog ({})."""
    # TODO: if not Path(path).exists(): return ProductCatalog()
    #       rows = json.loads(Path(path).read_text())
    #       return ProductCatalog([Product(**row) for row in rows])
    ...
