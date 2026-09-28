import pytest

from claim import cli, record, timestamp


@pytest.fixture
def public(tmp_path):
    path = tmp_path / "record.json"
    path.write_bytes(record.dump_record(record.build_record("a" * 64, ["Alice"])))
    return path


def test_stamp(public, tmp_path, monkeypatch):
    monkeypatch.setattr(timestamp, "stamp", lambda _: b"receipt")
    output = tmp_path / "receipt.ots"
    assert cli.main(["stamp", str(public), str(output)]) == 0
    assert output.read_bytes() == b"receipt"
