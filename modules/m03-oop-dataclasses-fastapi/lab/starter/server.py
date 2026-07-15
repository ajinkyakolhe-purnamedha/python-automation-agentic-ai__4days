"""FastAPI server exposing the Product Catalog (Day 1 Lab 3).

A route is a function with `@app.get`/`@app.post` on top — use the `@` as given
(the Decorators module explains how it works). Map `CatalogError` -> HTTP codes:
missing -> 404, duplicate -> 409, bad payload -> 400.

Run:  uvicorn catalog.server:app --reload
Done-signal: the TestServer class in tests/test_lab03.py.
"""

from __future__ import annotations

import logging
from dataclasses import asdict

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
    # TODO: [asdict(p) for p in catalog.list_all()]
    ...


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    # TODO: try: return asdict(catalog.get(product_id))
    #       except CatalogError as e: raise HTTPException(404, str(e))
    ...


@app.post("/products", status_code=201)
def create_product(payload: dict) -> dict:
    # TODO: build Product(**payload)  (TypeError -> HTTPException(400, ...));
    #       catalog.add(new)          (CatalogError -> HTTPException(409, ...));
    #       return asdict(new)
    ...


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int) -> None:
    # TODO: catalog.delete(product_id); on CatalogError -> HTTPException(404, ...)
    ...
