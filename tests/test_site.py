from claim import site


def test_registry_page():
    html = site.render({"claims": [], "authors": {"Alice & Bob": 2}})
    assert "Alice &amp; Bob: 2" in html and "index.json" in html


def test_disclosure_links():
    entry = {
        "id": "a" * 64,
        "authors": ["Alice"],
        "status": "withdrawn",
        "date": None,
        "events": ["disclosed", "withdrawn"],
    }
    html = site.claim_row(entry)
    assert '/proof"' in html and '/salt"' in html and "events/0002.json" in html


def test_author_escaping():
    entry = {
        "id": "a" * 64,
        "authors": ["<script>alert(1)</script>"],
        "status": "sealed",
        "date": None,
    }
    html = site.claim_row(entry)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "Awaiting CI" in html
