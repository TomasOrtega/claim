from claim import site


def test_author_escaping():
    entry = {
        "id": "a" * 64,
        "authors": ["<script>alert(1)</script>"],
        "status": "sealed",
        "timestamp": {"status": "pending"},
        "receipts": ["b" * 64 + ".ots"],
    }
    html = site.claim_row(entry)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "pending" in html and '.ots"' in html


def test_timestamp_label():
    assert site.timestamp_label({"status": "pending"}) == "pending"
    assert (
        site.timestamp_label(
            {"status": "verified", "unix_time": 1432827678, "block_height": 358391}
        )
        == "2015-05-28 UTC (block 358391)"
    )
