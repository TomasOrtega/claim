from claim import site


def test_author_escaping():
    entry = {
        "id": "a" * 64,
        "authors": ["<script>alert(1)</script>"],
        "status": "sealed",
    }
    html = site.claim_row(entry)
    assert "<script>" not in html and "&lt;script&gt;" in html
