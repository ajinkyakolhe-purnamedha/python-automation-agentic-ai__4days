"""FastAPI server exposing the Product Catalog (Day 1 Lab 3).

A route is a function with `@app.get`/`@app.post` on top — a decorator you *use*
(the `@` hands your function to FastAPI; you never write your own). Map
`CatalogError` -> HTTP codes: missing -> 404, duplicate -> 409, bad payload -> 400.

Run:  uv run uvicorn catalog.server:app --reload
Done-signal: the TestServer class in tests/test_lab03.py.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from .models import CatalogError, Product, ProductCatalog

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

SEED = [
    Product(1, "USB-C Cable", "Electronics", 499.0, True, ["cable", "usb-c"]),
    Product(2, "Mechanical Keyboard", "Electronics", 5499.0, True, ["keyboard", "mech"]),
    Product(3, "Steel Water Bottle", "Home", 899.0, True, ["bottle", "steel"]),
    Product(4, "Yoga Mat", "Fitness", 1299.0, False, ["mat", "yoga"]),
    Product(5, "Bluetooth Speaker", "Electronics", 2499.0, True, ["speaker", "bt"]),
]

app = FastAPI(title="Product Catalog", version="0.1.0")
catalog = ProductCatalog(list(SEED))


@app.get("/health")
def health() -> dict:
    # TODO: {"status": "ok", "count": <how many products>}
    ...


@app.get("/products")
def list_products() -> list[dict]:
    # TODO: serialise every product from catalog.list_all() (to_dict) into a list
    ...


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    # TODO: return the product's to_dict(); map a missing-id CatalogError -> HTTPException(404)
    ...


@app.post("/products", status_code=201)
def create_product(payload: dict) -> dict:
    # TODO: build a Product from the payload (bad body TypeError -> 400);
    #       add it to the catalog (duplicate id CatalogError -> 409); return its to_dict()
    ...


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int) -> None:
    # TODO: catalog.delete(product_id); on CatalogError -> HTTPException(404, ...)
    ...
