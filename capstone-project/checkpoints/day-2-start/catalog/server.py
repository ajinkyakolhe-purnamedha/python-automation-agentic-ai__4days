"""FastAPI server exposing the Product Catalog — the Day-1 (Lab 3) end state.

A route is a function with `@app.get`/`@app.post` on top — a decorator you *use*
(the `@` hands your function to FastAPI; you never write your own). `CatalogError`
maps to HTTP: missing -> 404, duplicate -> 409, bad payload (TypeError) -> 400.

Run:  uv run uvicorn catalog.server:app --reload
Lab 4 types these routes with Pydantic and the manual 400 disappears.
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
    return {"status": "ok", "count": len(catalog)}


@app.get("/products")
def list_products() -> list[dict]:
    return [p.to_dict() for p in catalog.list_all()]


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    try:
        return catalog.get(product_id).to_dict()
    except CatalogError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/products", status_code=201)
def create_product(payload: dict) -> dict:
    try:
        product = Product(**payload)          # bad/missing keys -> TypeError
    except TypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        return catalog.add(product).to_dict()  # duplicate id -> CatalogError
    except CatalogError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int) -> None:
    try:
        catalog.delete(product_id)
    except CatalogError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
