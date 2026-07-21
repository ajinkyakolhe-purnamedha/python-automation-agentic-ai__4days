"""Module 8 · Section 5 — test the import workflow: mock the client, assert the report.

Run:  pytest -m "not integration" -v
"""

from client import APIError
from import_accounts import import_accounts


class FakeClient:
    """Mock-style client: creates accounts, but 409s on a duplicate id."""

    def __init__(self, dup_ids=()):
        self._dup = set(dup_ids)
        self.created = []

    def create_account(self, account):
        if account.id in self._dup:
            raise APIError(409, "duplicate")
        self.created.append(account)
        return account


ROWS = [
    {"id": 1, "owner": "Ada", "balance": 1500.0},   # valid — but id 1 is a duplicate
    {"id": 2, "owner": "Lin", "balance": 800.0},     # valid — created
    {"id": 3, "owner": "", "balance": -5},           # invalid — empty owner, negative balance
]


def test_report_separates_three_buckets():
    report = import_accounts(ROWS, FakeClient(dup_ids={1}))
    s = report["summary"]
    assert s["created"] == 1             # id 2
    assert s["validation_errors"] == 1   # id 3 (never reached the client)
    assert s["api_errors"] == 1          # id 1 (well-formed, server rejected)


def test_validation_error_records_the_row():
    report = import_accounts(ROWS, FakeClient(dup_ids={1}))
    first = report["validation_errors"][0]
    assert "row" in first and "errors" in first
