"""Module 7 sandbox — the code UNDER TEST (the bank-accounts story).

A real, runnable pytest project on the M3 BankAccount domain — your sandbox to
experiment. Run `pytest -v`, break a test, add your own. Tests live in
test_account.py / test_catalog.py; shared fixtures in conftest.py. This is NOT
the graded lab (that's Product, in ../lab/) — it's a safe place to play.
"""

from __future__ import annotations

from dataclasses import dataclass


class BankError(Exception):
    """Raised on a broken rule: duplicate id, missing id, or a bad amount."""


@dataclass
class BankAccount:
    id: int
    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise BankError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise BankError("insufficient funds")
        self.balance -= amount


class BankCatalog:
    """Accounts keyed by id — the thing Section 3 tests."""

    def __init__(self, accounts: list[BankAccount] | None = None) -> None:
        self._items: dict[int, BankAccount] = {}
        for a in accounts or []:
            self.add(a)

    def add(self, account: BankAccount) -> BankAccount:
        if account.id in self._items:
            raise BankError(f"id {account.id} already exists")
        self._items[account.id] = account
        return account

    def get(self, account_id: int) -> BankAccount:
        if account_id not in self._items:
            raise BankError(f"id {account_id} not found")
        return self._items[account_id]

    def search_by_name(self, term: str) -> list[BankAccount]:
        return [a for a in self._items.values() if term.lower() in a.owner.lower()]

    def __len__(self) -> int:
        return len(self._items)
