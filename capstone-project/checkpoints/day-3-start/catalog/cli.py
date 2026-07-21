"""Tiny CLI for the catalog (Day 1 Lab 1 / Lab 2).

Usage:
    python -m catalog.cli list
    python -m catalog.cli add 10 "Notebook" Stationery 199
    python -m catalog.cli search keyboard
    python -m catalog.cli save catalog.json
    python -m catalog.cli load catalog.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from .models import CatalogError, Product, ProductCatalog
from .storage import load_json, save_json, seed_products

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_PATH = Path("catalog.json")


def _load():
    if DEFAULT_PATH.exists():
        return load_json(DEFAULT_PATH)
    return ProductCatalog(list(seed_products()))


def cmd_list(args):
    catalog = _load()
    for p in catalog.list_all():
        print(f"  {p.id:>3}  {p.name:<28} {p.category:<14} ₹{p.price:>8.2f}  "
              f"{'in stock' if p.in_stock else 'OOS'}")
    print(f"\n{len(catalog)} products")
    return 0


def cmd_add(args):
    catalog = _load()
    try:
        catalog.add(Product(id=args.id, name=args.name, category=args.category, price=args.price))
    except CatalogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    save_json(catalog, DEFAULT_PATH)
    return 0


def cmd_search(args):
    catalog = _load()
    hits = catalog.search_by_name(args.term)
    print(json.dumps([p.to_dict() for p in hits], indent=2))
    return 0


def cmd_save(args):
    catalog = _load()
    save_json(catalog, args.path)
    return 0


def cmd_load(args):
    catalog = load_json(args.path)
    print(f"loaded {len(catalog)} products")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="catalog")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")

    p_add = sub.add_parser("add")
    p_add.add_argument("id", type=int)
    p_add.add_argument("name")
    p_add.add_argument("category")
    p_add.add_argument("price", type=float)

    sub.add_parser("search").add_argument("term")
    sub.add_parser("save").add_argument("path")
    sub.add_parser("load").add_argument("path")

    return parser


# Map each sub-command name to the function that runs it.
COMMANDS = {
    "list": cmd_list,
    "add": cmd_add,
    "search": cmd_search,
    "save": cmd_save,
    "load": cmd_load,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    return COMMANDS[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
