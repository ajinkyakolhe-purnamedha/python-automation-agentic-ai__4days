"""Module 8 code-along — the code UNDER TEST: the AccountClient (bank-accounts story).

Given. The instructor writes the *tests* live — fake/mock session (§2), parametrized
status codes (§3), forced failures (§4), the import report (§5) — then runs pytest.
The client takes its `session` by injection; that seam is what lets you test it
with no server. `@retry` on `_request` makes every call resilient to transient errors.
"""

from __future__ import annotations

import functools
import time

from pydantic import BaseModel, Field


class BankAccount(BaseModel):
    id: int = Field(ge=1)
    owner: str = Field(min_length=1)
    balance: float = Field(ge=0)


class APIError(Exception):
    def __init__(self, status_code: int, detail: str = ""):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


def retry(times: int = 3, delay: float = 0.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


class AccountClient:
    def __init__(self, base_url: str = "http://server", session=None):
        self.base_url = base_url
        self._session = session                       # injected — real in prod, fake in tests

    @retry(times=3, delay=0.0, exceptions=(ConnectionError, TimeoutError))
    def _request(self, method: str, path: str, **kw):
        resp = self._session.request(method, self.base_url + path, timeout=5, **kw)
        if not resp.ok:
            raise APIError(resp.status_code, getattr(resp, "text", ""))
        return resp

    def list_accounts(self) -> list[BankAccount]:
        data = self._request("GET", "/accounts").json()
        return [BankAccount.model_validate(r) for r in data]

    def get_account(self, account_id: int) -> BankAccount:
        return BankAccount.model_validate(self._request("GET", f"/accounts/{account_id}").json())

    def create_account(self, account: BankAccount) -> BankAccount:
        data = self._request("POST", "/accounts", json=account.model_dump()).json()
        return BankAccount.model_validate(data)


# ---- test helpers (given) — a stub session, no network ----

class FakeResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def json(self):
        return self._payload


class FakeSession:
    """A stub: returns one canned (status, payload) for any request."""

    def __init__(self, status: int, payload):
        self.status = status
        self.payload = payload

    def request(self, method, url, **kw):
        return FakeResponse(self.status, self.payload)
