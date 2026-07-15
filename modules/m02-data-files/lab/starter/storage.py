"""Catalog store, queries & persistence — Day 1 Lab 2 (a {id: product} store + files).

Copy into your `catalog/` package and fill the `# TODO`s. Builds on Lab 1's
`make_product`. No classes yet (Module 3). Keep the **type hints** — that's the
best practice from Module 2.

Done-signal: uvx pytest tests/test_lab02.py -v goes green.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from .models import make_product

logger = logging.getLogger(__name__)

CSV_FIELDS = ["id", "name", "category", "price", "in_stock"]   # scalars only — a list doesn't fit a flat cell

# The catalog is now a STORE: a dict keyed by id  ->  {id: product}.


def make_store(products: list[dict]) -> dict[int, dict]:
    """Build a {id: product} store from a list of products."""
    # TODO: dict comprehension — key each product by its id
    ...


def insert(store: dict[int, dict], product: dict) -> None:
    """Add (or replace) a product in the store, keyed by its id."""
    # TODO: store the product under its id key; logger.info the insert
    ...


def fetch(store: dict[int, dict], product_id: int) -> dict:
    """Return the product with `product_id`, or raise LookupError if absent."""
    # TODO: if product_id not in store -> raise LookupError(...); else return it
    ...


def search_by_name(store: dict[int, dict], term: str) -> list[dict]:
    """Products whose name contains `term` (case-insensitive). Use a comprehension."""
    # TODO: comprehension over store.values(); case-insensitive substring match on name
    ...


def filter_by_price(store: dict[int, dict], max_price: float) -> list[dict]:
    """Products with price <= max_price. Use a comprehension."""
    # TODO: comprehension over store.values(); keep where price <= max_price
    ...


def save_json(store: dict[int, dict], path: str | Path) -> None:
    """Write the products to JSON as a list. indent=2."""
    # TODO: json.dumps the store's values() as a list, write it to the path (indent=2)
    ...


def load_json(path: str | Path) -> dict[int, dict]:
    """Read products from JSON and rebuild the store. Missing file -> empty store ({})."""
    # TODO: missing file -> logger.warning and return an empty store ({})
    #       else read the JSON list back and rebuild it via make_store(...)
    ...


def save_csv(store: dict[int, dict], path: str | Path) -> None:
    """Write the products' SCALAR fields to CSV (the `tags` list doesn't fit a flat cell).
    Open with newline=''."""
    # TODO: DictWriter over CSV_FIELDS with extrasaction="ignore" (that's what drops the
    #       tags list); writeheader, then one row per product. Open the file with newline="".
    ...


def load_csv(path: str | Path) -> dict[int, dict]:
    """Read products from CSV, coercing string columns back to real types (tags -> [])."""
    # TODO: missing file -> {}. Else DictReader each row and COERCE the strings back:
    #       id -> int, price -> float, in_stock -> bool ("True" == True). Rebuild via
    #       make_product(...); tags default to [] (CSV didn't store them — that's the lesson).
    ...
