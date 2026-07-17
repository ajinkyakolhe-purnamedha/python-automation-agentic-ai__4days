"""Catalog persistence — Day 2 Lab 4: the same two functions, now Pydantic.

Lab 3's `storage.py`, with one idea changed. The module keeps its job (the
`ProductCatalog` owns the data + queries; this reads/writes it to disk) and
keeps its signatures. All that moves is the two lines that touch a `Product`:
one on the way out, one on the way in.

The way in is the upgrade worth pausing on. Lab 3 trusted the file completely
— whatever was on disk became a Product, unchecked. Pydantic gives you a way
in that validates instead, so a hand-edited catalog.json with price=-5 fails
on load, right here, rather than poisoning the catalog silently.

Copy into your `catalog/` package and fill every `# TODO`.
Done-signal: uv run pytest tests/test_lab04.py -v goes green.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Product, ProductCatalog


def save_json(catalog: ProductCatalog, path: str | Path) -> None:
    """Write the catalog's products to JSON as a list (indent=2)."""
    # TODO: exactly your Lab 3 function, with one word changed. Lab 3 called
    #       `p.to_dict()` on each product — a Pydantic model doesn't have that.
    #       Find the method that turns a model into a plain dict (module-4, §3.2).
    ...


def load_json(path: str | Path) -> ProductCatalog:
    """Rebuild a ProductCatalog from JSON. Missing file -> empty catalog."""
    # TODO: again your Lab 3 function — missing file still means an empty
    #       ProductCatalog(). The one change is how each row becomes a Product:
    #       Lab 3 used `Product(**row)`, which trusted the file completely. Use
    #       the *validating* way in instead (module-4, §3.1), so a hand-edited
    #       file with a bad price fails here rather than silently loading.
    ...
