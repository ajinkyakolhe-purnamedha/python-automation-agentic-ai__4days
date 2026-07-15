"""Tiny argparse CLI for the catalog — Day 1 Lab 1.

The argparse plumbing is given (boilerplate, not the lesson). Fill the command
bodies marked `# TODO`. `search` / `save` / `load` arrive in Lab 2.

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
    catalog = seed_catalog()
    # TODO: print each product as one row, then a "<n> products" footer
    ...
    return 0


def cmd_add(args):
    catalog = seed_catalog()
    # TODO: make_product(...) from args + add_product(...);
    #       on ValueError print "ERROR: ..." to stderr and return 1
    ...
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="catalog")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(fn=cmd_list)

    p_add = sub.add_parser("add")
    p_add.add_argument("id", type=int)
    p_add.add_argument("name")
    p_add.add_argument("category")
    p_add.add_argument("price", type=float)
    p_add.set_defaults(fn=cmd_add)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
