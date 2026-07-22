"""Module 7 · Section 2 — a test is a function + assert; a fixture gives fresh state.

Run:  pytest -v        (from this folder)
"""

import pytest

from bank import BankAccount, BankError


# 2.1 · No fixture — just build, act, assert. The function name says what it pins.
def test_deposit_increases_balance():
    acct = BankAccount(id=1, owner="Ada", balance=100.0)
    acct.deposit(50)
    assert acct.balance == 150.0


# 2.3 · Same test, but the `account` fixture (from conftest.py) builds the object —
#       requested by parameter name; pytest hands each test its own fresh one.
def test_deposit_via_fixture(account):
    account.deposit(50)
    assert account.balance == 150.0


# A first error-path taste (full treatment in Section 3).
def test_withdraw_more_than_balance_raises(account):
    with pytest.raises(BankError):
        account.withdraw(9999)


# TODO (your turn): write test_deposit_negative_raises — depositing a negative amount
#   should raise BankError. Copy the shape of the test above: pytest.raises + the call.
#   Run `pytest -v` and watch your new test appear green.
