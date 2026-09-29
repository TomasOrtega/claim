from claim import events


def test_no_events(tmp_path):
    assert events.read(tmp_path) == []


def test_append(tmp_path):
    events.append(tmp_path, "disclosed")
    first = (tmp_path / "events" / "0001.json").read_bytes()
    events.append(tmp_path, "withdrawn")
    assert events.read(tmp_path) == ["disclosed", "withdrawn"]
    assert (tmp_path / "events" / "0001.json").read_bytes() == first
