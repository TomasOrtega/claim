import pytest

from claim import record


@pytest.fixture
def public(tmp_path):
    path = tmp_path / "record.json"
    path.write_bytes(record.dump_record(record.build_record("a" * 64, ["Alice"])))
    return path
