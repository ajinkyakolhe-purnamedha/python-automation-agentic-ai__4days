"""Typed HTTP client for the catalog API (Day 2 Lab 5).

Drives the FastAPI server from `server.py` end-to-end. Every method returns
a Pydantic `Product` (or list of them), so callers stay typed all the way
down — no raw dicts leak out of this module.
"""

import time

import requests

from .models import Product, ProductCreate, ProductUpdate

DEFAULT_TIMEOUT = 5.0
DEFAULT_BASE_URL = "http://localhost:8000"


class APIError(Exception):
    """Raised when the catalog API returns a non-2xx response."""

    def __init__(self, status_code, detail):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class APIClient:
    """CRUD client for the catalog API."""

    def __init__(self, base_url=DEFAULT_BASE_URL, timeout=DEFAULT_TIMEOUT, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    # ---- low-level ----

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        for attempt in range(1, 4):
            try:
                response = self._session.request(method, url, **kwargs)
                break
            except (requests.ConnectionError, requests.Timeout):
                if attempt == 3:
                    raise
                time.sleep(0.2)
        if not response.ok:
            raise APIError(response.status_code, self._extract_detail(response))
        return response

    @staticmethod
    def _extract_detail(response):
        # The API usually returns {"detail": "..."}; fall back to raw text.
        try:
            body = response.json()
        except ValueError:
            return response.text or response.reason
        return body.get("detail", response.text)

    # ---- typed CRUD ----

    def health(self):
        return self._request("GET", "/health").json()

    def list_products(self) -> list[Product]:
        rows = self._request("GET", "/products").json()
        return [Product.model_validate(row) for row in rows]

    def get_product(self, product_id) -> Product:
        data = self._request("GET", f"/products/{product_id}").json()
        return Product.model_validate(data)

    def create_product(self, payload: ProductCreate) -> Product:
        data = self._request("POST", "/products", json=payload.model_dump()).json()
        return Product.model_validate(data)

    def update_product(self, product_id, patch: ProductUpdate) -> Product:
        changes = patch.model_dump(exclude_unset=True)
        data = self._request("PATCH", f"/products/{product_id}", json=changes).json()
        return Product.model_validate(data)

    def delete_product(self, product_id):
        self._request("DELETE", f"/products/{product_id}")

    # ---- extra helper the Day-4 agent calls as a tool ----

    def count_by_category(self) -> dict:
        counts = {}
        for product in self.list_products():
            counts[product.category] = counts.get(product.category, 0) + 1
        return counts
