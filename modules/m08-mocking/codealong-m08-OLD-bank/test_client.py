"""Module 8 · §2–§4 — testing the AccountClient with doubles, parametrize, forced failures.

Run:  pytest -m "not integration" -v     # fast: mocked, no server
      pytest -m integration -v           # needs a live server on :8000
"""

import pytest
from unittest.mock import Mock

from client import AccountClient, APIError, BankAccount, FakeSession

ACCOUNTS = [{"id": 1, "owner": "Ada", "balance": 1500.0},
            {"id": 2, "owner": "Lin", "balance": 800.0}]


# §2.1 — a hand-written FAKE session (stub): a canned response, no network.
def test_fake_session_returns_typed_models():
    accts = AccountClient(session=FakeSession(200, ACCOUNTS)).list_accounts()
    assert all(isinstance(a, BankAccount) for a in accts)   # not raw dicts
    assert [a.id for a in accts] == [1, 2]


# §2.2 / 2.3 — unittest.mock builds the double AND records the call.
def test_mock_records_the_request():
    session = Mock()
    session.request.return_value = Mock(ok=True, status_code=200, json=lambda: ACCOUNTS)
    AccountClient(session=session).list_accounts()
    session.request.assert_called_with("GET", "http://server/accounts", timeout=5)


# §3.2 — parametrize across status codes: every non-2xx raises APIError.
@pytest.mark.parametrize("status", [400, 404, 409, 500])
def test_non_2xx_raises_apierror(status):
    client = AccountClient(session=FakeSession(status, {"detail": "no"}))
    with pytest.raises(APIError) as exc:
        client.list_accounts()
    assert exc.value.status_code == status


# §4.1 — force a transient failure; prove @retry recovers (you can't do this live).
def test_retry_recovers_from_transient_error():
    session = Mock()
    session.request.side_effect = [ConnectionError(), ConnectionError(),
                                   Mock(ok=True, json=lambda: ACCOUNTS)]
    accts = AccountClient(session=session).list_accounts()
    assert len(accts) == 2
    assert session.request.call_count == 3       # 2 fails + 1 success


# §4.2 — a 4xx is NEVER retried (it isn't a network error): called exactly once.
def test_4xx_is_not_retried():
    session = Mock()
    session.request.return_value = Mock(ok=False, status_code=404, text="x")
    with pytest.raises(APIError):
        AccountClient(session=session).list_accounts()
    assert session.request.call_count == 1


# §3.3 — an integration test that DOES hit a live server (skipped in the fast run).
@pytest.mark.integration
def test_against_live_server():
    import requests
    client = AccountClient(base_url="http://localhost:8000", session=requests.Session())
    assert isinstance(client.list_accounts(), list)
