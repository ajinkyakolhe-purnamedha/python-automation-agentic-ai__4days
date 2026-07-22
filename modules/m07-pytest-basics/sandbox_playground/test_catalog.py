"""Module 7 · Section 3 — test the catalog: Arrange-Act-Assert, happy paths, errors.

Run:  pytest -v        (from this folder)
"""

import pytest

from bank import BankAccount, BankError


# 3.1 · Arrange → Act → Assert — one behavior per test.
def test_add_then_get_returns_it(catalog):
    acct = BankAccount(id=9, owner="Sam2", balance=40.0)   # Arrange
    catalog.add(acct)                                      # Act
    assert catalog.get(9).owner == "Sam2"                  # Assert


# 3.2 · Happy paths, off the clean `catalog` fixture.
def test_search_finds_by_name(catalog):
    assert {a.id for a in catalog.search_by_name("ada")} == {1}


def test_len_counts_seeded_accounts(catalog):
    assert len(catalog) == 3


# 3.3 · Error paths — assert the rule actually fires.
def test_duplicate_id_raises(catalog):
    with pytest.raises(BankError):
        catalog.add(BankAccount(id=1, owner="dup", balance=0.0))


def test_get_missing_id_raises(catalog):
    with pytest.raises(BankError):
        catalog.get(999)


# TODO (your turn): write test_search_is_case_insensitive — search_by_name("ADA")
#   should still find Ada. Assert on the returned account's id or owner.
# TODO (your turn): try tmp_path — write a line to (tmp_path / "note.txt"), read it
#   back, and assert it round-trips. `tmp_path` is a built-in fixture; just add it as
#   a parameter, no import needed.
