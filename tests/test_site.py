from test_dates import DATE, RUN
from test_disclosure import PROOF_URL

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
        "disclosure": {"proof_url": PROOF_URL},
    }
    html = site.claim_row(entry)
    assert (
        PROOF_URL in html and '/disclosure.json"' in html and "events/0002.json" in html
    )


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


def test_recorded_date():
    entry = {
        "id": "a" * 64,
        "authors": ["Alice"],
        "status": "sealed",
        "date": {"recorded_at": DATE, "run_url": RUN},
    }
    html = site.claim_row(entry)
    assert DATE in html and RUN in html and 'date.json"' in html
