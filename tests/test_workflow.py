import pytest
from test_dates import COMMIT, DATE, RUN

from claim import commitment, dates, record, storage, workflow


def test_freeze(tmp_path, key):
    source, opening = tmp_path / "proof", tmp_path / "opening"
    source.write_bytes(b"proof\r\n\xff")
    digest = workflow.freeze(source, opening, key)
    assert commitment.verify_opening(*storage.load_opening(opening, key), digest)


def test_corrupt_saved_opening(tmp_path, key, monkeypatch):
    source = tmp_path / "proof"
    source.write_bytes(b"original")
    monkeypatch.setattr(storage, "load_opening", lambda *_: (b"corrupt", bytes(32)))
    with pytest.raises(ValueError, match="stored opening does not match"):
        workflow.freeze(source, tmp_path / "opening", key)


def test_seal(tmp_path, key):
    source, directory = tmp_path / "proof", tmp_path / "sealed"
    source.write_bytes(b"proof")
    digest = workflow.seal(source, directory, key, ["Alice"])
    public = record.load_record((directory / "record.json").read_bytes())
    assert public == record.build_record(digest, ["Alice"])


def test_existing_claim_directory(tmp_path, key):
    with pytest.raises(FileExistsError):
        workflow.seal(tmp_path / "missing", tmp_path, key, ["Alice"])


def test_disclose(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    assert {p.name for p in output.iterdir()} == {"proof", "salt", "record.json"}
    assert (output / "proof").read_bytes() == b"proof\r\n\xff"
    assert (output / "record.json").read_bytes() == (
        sealed / "record.json"
    ).read_bytes()


def test_verify(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    public = record.load_record((sealed / "record.json").read_bytes())
    assert workflow.verify(output) == public["commitment"]


def test_verify_dated_disclosure(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    data = record.read_record(output / "record.json")
    dates.save(output, data, DATE, COMMIT, RUN)
    assert workflow.verify(output) == record.load_record(data)["commitment"]


def test_verify_date_for_another_record(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    data = record.read_record(output / "record.json")
    dates.save(output, b" " + data, DATE, COMMIT, RUN)
    with pytest.raises(ValueError, match="date does not match record"):
        workflow.verify(output)


@pytest.mark.parametrize("name", ["proof", "salt", "record.json"])
def test_altered_disclosure(sealed, tmp_path, key, name):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    (output / name).write_bytes(b"changed")
    with pytest.raises(ValueError):
        workflow.verify(output)


def test_mismatched_export(sealed, tmp_path, key):
    path = sealed / "record.json"
    path.write_bytes(record.dump_record(record.build_record("0" * 64, ["Alice"])))
    with pytest.raises(ValueError, match="opening does not match record"):
        workflow.disclose(sealed, tmp_path / "disclosed", key)
    assert not (tmp_path / "disclosed").exists()


def test_disclosure_snapshot(sealed, tmp_path, key):
    output = tmp_path / "disclosed"
    workflow.disclose(sealed, output, key)
    snapshot = workflow.read_disclosure(output)
    (output / "proof").write_bytes(b"changed")
    assert snapshot["proof"] == b"proof\r\n\xff"


def test_record_mismatch(sealed):
    with pytest.raises(ValueError, match="opening does not match record"):
        workflow.check_opening(
            (sealed / "record.json").read_bytes(), b"changed", bytes(32)
        )
