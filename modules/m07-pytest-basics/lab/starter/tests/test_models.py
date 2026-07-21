"""Lab 7 · Part A — test the Pydantic models (catalog.models).

Fill every `# TODO`, replacing the `pytest.fail(...)` line with real asserts.
Run `pytest tests/test_models.py -q` and turn each red test green.

You're pinning the model's *promises*: the Field constraints reject bad data,
and the dict round-trip survives. Concepts: codealong/module-7, deck §"pytest
basics" + §"Testing the catalog".
"""

import pytest
from pydantic import ValidationError

from catalog.models import Product, ProductCreate, ProductUpdate


class TestProductValidation:
    def test_valid_payload(self):
        """A fully-valid payload builds and its fields survive."""
        # TODO: build Product(id=1, name=..., category=..., price=..., tags=["a"])
        #       assert the id and tags came back unchanged
        pytest.fail("TODO: implement test_valid_payload")

    @pytest.mark.parametrize("field, value, err_substring", [
        # TODO: one row per rule you want to pin — (field, bad_value, text in the error)
        #   ("name",  "",  "at least 1 character"),
        #   ("price", -1,  "greater than or equal to 0"),
        #   ("id",    0,   "greater than or equal to 1"),
    ])
    def test_rejects_invalid(self, field, value, err_substring):
        """Each bad field raises ValidationError that names the rule."""
        base = dict(id=1, name="X", category="c", price=10.0)
        base[field] = value
        # TODO: with pytest.raises(ValidationError) as exc: Product(**base)
        #       assert err_substring is in str(exc.value)
        pytest.fail("TODO: implement test_rejects_invalid")

    def test_coerces_string_bools_and_pipe_tags(self):
        """CSV-style strings coerce: "true" → True, "a|b|c" → ["a","b","c"]."""
        # TODO: Product.model_validate({...all string values, "in_stock": "true",
        #       "tags": "a|b|c"}); assert id is an int, in_stock is True, tags is the list
        pytest.fail("TODO: implement test_coerces_string_bools_and_pipe_tags")

    def test_to_dict_roundtrip(self):
        """to_dict() then from_dict() returns an equal Product."""
        # TODO: build a Product p; assert Product.from_dict(p.to_dict()) == p
        pytest.fail("TODO: implement test_to_dict_roundtrip")


class TestProductUpdate:
    def test_all_fields_optional(self):
        """An empty update dumps to {} (nothing set)."""
        # TODO: assert ProductUpdate().model_dump(exclude_unset=True) == {}
        pytest.fail("TODO: implement test_all_fields_optional")

    def test_extra_fields_rejected(self):
        """An unknown field is rejected (the model uses extra='forbid')."""
        # TODO: assert ProductUpdate(price=9.99, unknown_field="oops") raises ValidationError
        pytest.fail("TODO: implement test_extra_fields_rejected")

    def test_partial_update(self):
        """Only the field you set is dumped."""
        # TODO: assert ProductUpdate(price=12.5).model_dump(exclude_unset=True) == {"price": 12.5}
        pytest.fail("TODO: implement test_partial_update")
