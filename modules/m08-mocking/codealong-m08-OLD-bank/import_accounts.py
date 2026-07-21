"""Module 8 · Section 5 — the import workflow UNDER TEST (a mini version of M6).

Takes its `client` by injection — so a test feeds it a fake client and asserts
the report's three buckets. Validation errors come from the real Pydantic model.
"""

from __future__ import annotations

from pydantic import ValidationError

from client import APIError, BankAccount


def import_accounts(rows, client) -> dict:
    """Validate each row, create the good ones via `client`, sort failures into buckets."""
    created, validation_errors, api_errors = [], [], []
    for n, row in enumerate(rows):
        try:
            account = BankAccount.model_validate(row)
        except ValidationError as exc:
            validation_errors.append({"row": n, "errors": exc.errors()})   # bad data — never sent
            continue
        try:
            client.create_account(account)
            created.append(account.id)
        except APIError as exc:
            api_errors.append({"row": n, "status": exc.status_code})       # server said no

    return {
        "summary": {"created": len(created),
                    "validation_errors": len(validation_errors),
                    "api_errors": len(api_errors)},
        "created": created,
        "validation_errors": validation_errors,
        "api_errors": api_errors,
    }
