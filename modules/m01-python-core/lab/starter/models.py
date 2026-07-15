"""Catalog data model — Day 1 Lab 1 (a product is a dict; the catalog is a list).

Copy this into your working folder's `catalog/` package and fill every `# TODO`.
No classes yet — just dicts and functions (Module 3 turns these into a class).
Done-signal: uvx pytest tests/test_lab01.py -v goes green.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# A product is a plain dict with these fields:
#   id:int, name:str, category:str, price:float, in_stock:bool, tags:list[str]
# A "catalog" is just a list of those product dicts.


def make_product(id, name, category, price, in_stock=True, tags=None):
    """Build and return a product dict.

    `tags` defaults to a NEW empty list each call (never `tags=[]` — that would
    share one list across every product; use the None sentinel).
    """
    # TODO: return the 6-field product dict; give tags a fresh list per call via the
    #       None sentinel (never tags=[] — the shared-list trap test_tags_are_not_shared checks)
    ...


def add_product(catalog, product):
    """Append `product` to the `catalog` list and return it.

    Raise ValueError if the price is negative, or if a product with the same id
    is already in the catalog.
    """
    # TODO: reject price < 0; loop the catalog to reject a duplicate id;
    #       then append, logger.info(...), and return the product
    ...


def find_product(catalog, product_id):
    """Return the product with `product_id`, or raise LookupError if absent."""
    # TODO: loop the catalog; return the match; raise LookupError(f"...") if none
    ...


def search_by_name(catalog, term):
    """Return a list of products whose name contains `term` (case-insensitive)."""
    # TODO: keep products whose name contains term, case-insensitive
    ...


def list_products(catalog):
    """Return all products (a list copy, so callers can't mutate ours)."""
    # TODO: return a copy of the catalog list
    ...
