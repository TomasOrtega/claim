from claim import events


def test_no_events(tmp_path):
    assert events.read(tmp_path) == []
