import pytest

from claim import events


def test_no_events(tmp_path):
    assert events.read(tmp_path) == []


def test_duplicate_event(tmp_path):
    events.append(tmp_path, "withdrawn")
    with pytest.raises(ValueError, match="duplicate"):
        events.append(tmp_path, "withdrawn")


@pytest.mark.parametrize(
    "name,data", [("0002.json", b'{"event":"withdrawn"}\n'), ("0001.json", b"{}")]
)
def test_invalid_history(tmp_path, name, data):
    (tmp_path / "events").mkdir()
    (tmp_path / "events" / name).write_bytes(data)
    with pytest.raises(ValueError, match="invalid claim event"):
        events.read(tmp_path)


def test_append(tmp_path):
    events.append(tmp_path, "disclosed")
    first = (tmp_path / "events" / "0001.json").read_bytes()
    events.append(tmp_path, "withdrawn")
    assert events.read(tmp_path) == ["disclosed", "withdrawn"]
    assert (tmp_path / "events" / "0001.json").read_bytes() == first
