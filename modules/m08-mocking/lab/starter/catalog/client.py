"""Day-3 tiny network client — the one thing M08 mocks.

NOT the M05 APIClient: no retry, no Session, no APIError. One call that leaves
the machine (`requests.get`), returning typed Products.

Copy into your `catalog/` package. Then write tests that mock `requests.get`.
"""

import requests

from .models import Product

DEFAULT_BASE_URL = "http://localhost:8000"


def get_products(base_url: str = DEFAULT_BASE_URL) -> list[Product]:
    """Fetch every product from the catalog API. Returns typed Products."""
    response = requests.get(f"{base_url}/products", timeout=5)
    response.raise_for_status()
    return [Product.model_validate(row) for row in response.json()]
