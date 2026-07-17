"""Typed HTTP client for the catalog API — Day 2 Lab 5.

Drives the FastAPI server from Python. Every method returns a Pydantic
`Product` (or a list of them) — no raw dicts leak out. One private
`_request` funnel owns the retry loop, so a network blip doesn't kill a
bulk-import run. On Day 4, the agent's tools will literally *be* these methods.

You write FOUR bodies: `_request`, `list_products`, `create_product`, and
`count_by_category`. Everything else (`APIError`, `__init__`, `_extract_detail`,
and the `health`/`get_product`/`delete_product` worked examples) is already
filled — read them, they show the exact pattern you repeat.

Done-signal: `APIClient().list_products()` returns `list[Product]`, and a
duplicate POST raises `APIError` (README → Expected output).
Concepts: codealong-m05-rest-requests.ipynb (requests.Session, the _request
funnel, the retry loop, typed returns).
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from .models import Product

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0
DEFAULT_BASE_URL = "http://localhost:8000"

# Retry policy for _request. Only transient faults are retried — see the
# exception tuple below; a 4xx is never in it (module-5, §1.4).
RETRY_TIMES = 3
RETRY_DELAY = 0.2
TRANSIENT_ERRORS = (requests.ConnectionError, requests.Timeout)


class APIError(Exception):
    """Raised when the catalog API returns a non-2xx response.

    A plain Exception on purpose: callers catch APIError without importing
    `requests` (module-5, §"Wrap it in AccountClient").
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class APIClient:
    """CRUD client for the catalog API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # session is injected for tests (Day 3) — defaults to a real pooled Session.
        self._session = session or requests.Session()

    # ---- low-level: every call funnels through here ----

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        # TODO — the funnel (module-5, §3.1) with the retry loop in it (§3.2).
        # Every public method below goes through here, so everything you write
        # once here, they all get for free. Four jobs:
        #
        #   1. TIMEOUT — give kwargs a `timeout` of self.timeout *unless the
        #      caller already passed one*. (dict has a method for exactly this.)
        #
        #   2. URL — join self.base_url and path.
        #
        #   3. SEND, up to RETRY_TIMES times. Send through **self._session**,
        #      never requests.get: the session carries the headers, and the
        #      tests hand you a fake one. As soon as you get a response, stop
        #      looping. If a TRANSIENT_ERRORS fault comes back, only give up on
        #      the final attempt — otherwise wait RETRY_DELAY and go again.
        #
        #   4. CHECK — a non-2xx response becomes APIError(status, detail);
        #      `_extract_detail` below gets you the detail. Otherwise hand the
        #      response back.
        #
        # Think about WHERE job 4 goes relative to the loop. A 4xx must never be
        # retried (§1.4) — the placement is what guarantees it, not a comment.
        ...

    @staticmethod
    def _extract_detail(response: requests.Response) -> str:
        # GIVEN: pull the server's JSON "detail" if present, else the raw text.
        try:
            return response.json().get("detail", response.text)
        except ValueError:
            return response.text or response.reason

    # ---- typed CRUD: each is two lines (call _request, validate into a model) ----

    # GIVEN — worked example. Notice the shape: _request(...).json() → model_validate.
    # Your list_products / create_product repeat exactly this move.
    def get_product(self, product_id: int) -> Product:
        data = self._request("GET", f"/products/{product_id}").json()
        return Product.model_validate(data)

    def health(self) -> dict:
        # GIVEN — same funnel, but /health returns a plain dict (no model to validate).
        return self._request("GET", "/health").json()

    def delete_product(self, product_id: int) -> None:
        # GIVEN — fires the request for its side effect; nothing to validate or return.
        self._request("DELETE", f"/products/{product_id}")

    def list_products(self) -> list[Product]:
        # TODO: same two moves as get_product above — but /products answers with
        #       a LIST of dicts, so every one of them needs validating, not just
        #       the one. (A comprehension; you wrote these in M1.)
        ...

    def create_product(self, payload: Product) -> Product:
        # TODO: POST to /products. `requests` wants the body as `json=<a dict>`,
        #       and what you have is a Product — convert it (module-4, §3.2).
        #       The server echoes the created product back, so finish the same
        #       way get_product does: validate the response into a Product.
        ...

    # ---- a query over the wire (Day 4 calls this one as an agent tool) ----

    def count_by_category(self) -> dict:
        # TODO: how many products in each category?  ->  {"Electronics": 2, "Home": 1}
        #
        #       You have written this before. Lab 3's ProductCatalog.group_by_category()
        #       walked a dict you owned, in memory. This walks the same catalog over
        #       HTTP — and the counting code doesn't change at all. That's the point:
        #       the data moved to another machine and the logic didn't notice.
        #
        #       Build on list_products() above — don't reach for _request yourself.
        #       Every Product it returns is already validated, so .category is safe
        #       to read. Then count: a dict + .get(key, 0) (M1), or collections.Counter.
        #
        #       On Day 4 the agent calls this to answer "how many electronics do we
        #       have?" — your method IS the tool.
        ...

    # --- Stretch (optional): PATCH ---
    # Lab 4 deferred PATCH on the server; this is its client side. Add an
    # update endpoint to server.py, then uncomment. (Needs ProductUpdate —
    # import it inside the method to keep the top of this file import-clean.)
    #
    # def update_product(self, product_id: int, patch) -> Product:
    #     from .models import ProductUpdate  # patch: ProductUpdate
    #     data = self._request(
    #         "PATCH",
    #         f"/products/{product_id}",
    #         json=patch.model_dump(exclude_unset=True),
    #     ).json()
    #     return Product.model_validate(data)


# =====================================================================
# LAB HELPERS — given to you, you do NOT write or edit these.
# Let you drive APIClient with NO server running (no uvicorn). Inject a
# FakeSession and it answers like the real API. Same dependency-injection
# seam Day 3 turns into real mocking.
#
#   from catalog.client import APIClient, FakeSession, FakeResponse, SAMPLE_PRODUCTS
#   c = APIClient(session=FakeSession([FakeResponse(200, SAMPLE_PRODUCTS)]))
#   print(c.list_products())          # -> list[Product], no server needed
# =====================================================================


class FakeResponse:
    """Lab helper. Mimics the bits of requests.Response APIClient touches."""

    def __init__(self, status_code: int, json_body) -> None:
        self.status_code = status_code
        self._json = json_body
        self.text = str(json_body)
        self.reason = "fake"

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def json(self):
        return self._json


class FakeSession:
    """Lab helper. Returns queued outcomes in order; an Exception in the queue
    is raised instead (simulates a network blip, so you can see the retry work).
    Once one item is left, it's reused for every further call."""

    def __init__(self, outcomes) -> None:
        self._outcomes = list(outcomes)
        self.headers = {}      # APIClient may set auth headers here
        self.calls = 0         # count requests — proves the retry loop actually retried

    def request(self, method, url, **kwargs):
        self.calls += 1
        item = self._outcomes.pop(0) if len(self._outcomes) > 1 else self._outcomes[0]
        if isinstance(item, Exception):
            raise item
        return item


# Sample data so the example above runs as-is.
SAMPLE_PRODUCTS = [
    {"id": 1, "name": "USB-C Cable", "category": "Electronics",
     "price": 499.0, "in_stock": True, "tags": ["cable", "usb-c"]},
    {"id": 2, "name": "Mechanical Keyboard", "category": "Electronics",
     "price": 5499.0, "in_stock": True, "tags": ["mech"]},
]
