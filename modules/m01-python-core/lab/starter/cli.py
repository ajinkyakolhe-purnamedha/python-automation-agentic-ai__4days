"""Tiny CLI for the catalog — Day 1 Lab 1.

The whole CLI is **given** — argparse plumbing and the `list` command are
boilerplate, not the lesson. Once your `models.py` functions work, this runs
as-is. (Lab 2 adds `search` / `save` / `load`.)

Run:  python -m catalog.cli list
"""

from __future__ import annotations

import argparse
import logging

from .models import make_product, add_product, list_products

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def seed_catalog():
    """A fresh catalog (list) with 5 demo products."""
    catalog = []
    for fields in [
        (1, "USB-C Cable", "Electronics", 499.0, True, ["cable", "usb-c"]),
        (2, "Mechanical Keyboard", "Electronics", 5499.0, True, ["keyboard", "mech"]),
        (3, "Steel Water Bottle", "Home", 899.0, True, ["bottle", "steel"]),
        (4, "Yoga Mat", "Fitness", 1299.0, False, ["mat", "yoga"]),
        (5, "Bluetooth Speaker", "Electronics", 2499.0, True, ["speaker", "bt"]),
    ]:
        add_product(catalog, make_product(*fields))
    return catalog


def cmd_list(args):
    """Print each product as a row, then a total footer."""
    catalog = seed_catalog()
    for p in list_products(catalog):
        stock = "in stock" if p["in_stock"] else "OOS"
        print(f"{p['id']:>3}  {p['name']:<22} {p['category']:<12} ₹{p['price']:>8.2f}  {stock}")
    print(f"\n{len(catalog)} products")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="catalog")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
