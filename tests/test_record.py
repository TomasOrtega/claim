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


@pytest.mark.parametrize(
    "digest", [None, 1, [], "a" * 63, "A" * 64, "g" * 64, "a" * 64 + "\n"]
)
def test_invalid_commitment(public_record, digest):
    public_record["commitment"] = digest
    with pytest.raises(ValueError, match="invalid commitment"):
        record.validate_record(public_record)


@pytest.mark.parametrize("authors", [None, [], "Alice", {"name": "Alice"}, ("Alice",)])
def test_invalid_author_list(public_record, authors):
    public_record["authors"] = authors
    with pytest.raises(ValueError, match="invalid authors"):
        record.validate_record(public_record)


@pytest.mark.parametrize("author", [None, 1, {}, [], "", " \t\n", "\u2003"])
def test_invalid_author(public_record, author):
    public_record["authors"] = [author]
    with pytest.raises(ValueError, match="invalid author name"):
        record.validate_record(public_record)


def test_duplicate_authors(public_record):
    public_record["authors"] = ["Alice", "Alice"]
    with pytest.raises(ValueError, match="duplicate authors"):
        record.validate_record(public_record)


@pytest.mark.parametrize("field", ["salt", "artifact", "key", "filename"])
def test_extra_field(public_record, field):
    with pytest.raises(ValueError, match="invalid record fields"):
        record.validate_record(public_record | {field: "private"})


@pytest.mark.parametrize("field", ["version", "commitment", "authors"])
def test_missing_field(public_record, field):
    del public_record[field]
    with pytest.raises(ValueError, match="invalid record fields"):
        record.validate_record(public_record)


def test_build_record(public_record):
    assert record.build_record("a" * 64, ["Alice", "José"]) == public_record


@pytest.mark.parametrize("value", [None, [], {}, {"salt": "private"}])
def test_invalid_fields(value):
    with pytest.raises(ValueError, match="invalid record fields"):
        record.validate_record(value)
