from datetime import UTC, datetime
from html import escape


def timestamp_label(status: dict) -> str:
    if status["status"] != "verified":
        return status["status"]
    date = datetime.fromtimestamp(status["unix_time"], UTC).strftime("%Y-%m-%d UTC")
    return f"{date} (block {status['block_height']})"


def claim_row(entry: dict) -> str:
    claim_id = escape(entry["id"])
    authors = ", ".join(escape(name) for name in entry["authors"])
    evidence = " ".join(
        f'<a href="./{claim_id}/{escape(name)}">receipt {i}</a>'
        for i, name in enumerate(entry["receipts"], 1)
    )
    date = escape(timestamp_label(entry["timestamp"]))
    return f'<tr><td><a href="./{claim_id}/record.json">{claim_id[:12]}</a></td><td>{authors}</td><td>{escape(entry["status"])}</td><td>{date}</td><td>{evidence}</td></tr>'


def render(index: dict) -> str:
    rows = "\n".join(claim_row(entry) for entry in index["claims"])
    counts = "".join(
        f"<li>{escape(name)}: {count}</li>" for name, count in index["authors"].items()
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claim registry</title><body><h1>Claim registry</h1>
<p>Names are self-declared. Verified dates attest to files.</p>
<table><thead><tr><th>Claim</th><th>Authors</th><th>State</th><th>Timestamp</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Claims per name</h2><ul>{counts}</ul><p><a href="index.json">Download index</a></p></body></html>"""
