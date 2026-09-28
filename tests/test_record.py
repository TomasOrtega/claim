import pytest

from claim import record


@pytest.fixture
def public_record():
    return {"version": 1, "commitment": "a" * 64, "authors": ["Alice", "José"]}


def test_valid_record(public_record):
    record.validate_record(public_record)


@pytest.mark.parametrize("version", [0, 2, True, 1.0, "1", None])
def test_invalid_version(public_record, version):
    public_record["version"] = version
    with pytest.raises(ValueError, match="unsupported record version"):
        record.validate_record(public_record)


@pytest.mark.parametrize("value", [None, [], {}, {"salt": "private"}])
def test_invalid_fields(value):
    with pytest.raises(ValueError, match="invalid record fields"):
        record.validate_record(value)
