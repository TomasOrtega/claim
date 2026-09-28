import pytest

from claim import record


@pytest.fixture
def public_record():
    return {"version": 1, "commitment": "a" * 64, "authors": ["Alice", "José"]}


def test_valid_record(public_record):
    record.validate_record(public_record)


@pytest.mark.parametrize("value", [None, [], {}, {"salt": "private"}])
def test_invalid_fields(value):
    with pytest.raises(ValueError, match="invalid record fields"):
        record.validate_record(value)
