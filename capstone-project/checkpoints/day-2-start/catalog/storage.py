"""Catalog persistence — the Day-1 (Lab 3) end state.

A separate module, not a class method: `ProductCatalog` owns the data + queries;
this reads/writes it to disk. Serialise a Product via `to_dict()`, rebuild it via
`Product(**row)`.

Lab 4 changes exactly two lines here — to `model_dump()` / `model_validate()`.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Product, ProductCatalog


def save_json(catalog: ProductCatalog, path: str | Path) -> None:
    """Write the catalog's products to JSON as a list (indent=2)."""
    rows = [p.to_dict() for p in catalog.list_all()]
    Path(path).write_text(json.dumps(rows, indent=2))


def load_json(path: str | Path) -> ProductCatalog:
    """Rebuild a ProductCatalog from JSON. Missing file -> empty catalog."""
    path = Path(path)
    if not path.exists():
        return ProductCatalog()
    rows = json.loads(path.read_text())
    return ProductCatalog([Product(**row) for row in rows])
