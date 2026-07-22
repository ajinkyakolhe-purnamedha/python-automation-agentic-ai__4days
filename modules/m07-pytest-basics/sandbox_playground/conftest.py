"""Module 7 code-along — shared fixtures (Section 2.3).

pytest auto-loads conftest.py and makes these fixtures available to every test
file in this folder. A test asks for one by naming it as a parameter; pytest
re-runs the fixture for each test, so everyone gets a CLEAN slate.
"""

import pytest

from bank import BankAccount, BankCatalog


@pytest.fixture
def account():
    """A fresh single account."""
    return BankAccount(id=1, owner="Ada", balance=100.0)


@pytest.fixture
def catalog():
    """A fresh, seeded catalog — every test starts from the same clean state."""
    return BankCatalog([
        BankAccount(1, "Ada", 1500.0),
        BankAccount(2, "Lin", 0.0),
        BankAccount(3, "Sam", 40.0),
    ])
