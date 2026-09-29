from claim import site


def test_registry_page():
    html = site.render({"claims": [], "authors": {"Alice & Bob": 2}})
    assert "Alice &amp; Bob: 2" in html and "index.json" in html


def test_disclosure_links():
    entry = {
        "id": "a" * 64,
        "authors": ["Alice"],
        "status": "withdrawn",
        "timestamp": {"status": "pending"},
        "receipts": [],
        "events": ["disclosed", "withdrawn"],
    }
    html = site.claim_row(entry)
    assert '/proof"' in html and '/salt"' in html and "events/0002.json" in html


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
