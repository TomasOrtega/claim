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
