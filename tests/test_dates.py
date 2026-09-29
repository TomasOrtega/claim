import json

import pytest

from claim import dates, record

DATE = "2026-09-29T12:34:56Z"
COMMIT = "a" * 40
RUN = "https://github.com/example/registry/actions/runs/123"


def test_date_preserves_record_and_first_date(sealed):
    data = record.read_record(sealed / "record.json")
    assert dates.read(sealed, data) is None
    assert dates.save(sealed, data, DATE, COMMIT, RUN)
    original = (sealed / "date.json").read_bytes()
    assert not dates.save(sealed, data, "2026-10-01T00:00:00Z", "b" * 40, RUN)
    assert (sealed / "date.json").read_bytes() == original
    assert record.read_record(sealed / "record.json") == data


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("record_sha256", "b" * 64),
        ("recorded_at", "yesterday"),
        ("commit", "main"),
        ("run_url", "javascript:alert(1)"),
    ],
)
def test_invalid_date(sealed, field, value):
    data = record.read_record(sealed / "record.json")
    dates.save(sealed, data, DATE, COMMIT, RUN)
    saved = json.loads((sealed / "date.json").read_bytes())
    saved[field] = value
    (sealed / "date.json").write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        dates.read(sealed, data)
