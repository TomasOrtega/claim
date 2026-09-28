from html import escape


def claim_row(entry: dict) -> str:
    claim_id = escape(entry["id"])
    authors = ", ".join(escape(name) for name in entry["authors"])
    return f'<tr><td><a href="./{claim_id}/record.json">{claim_id[:12]}</a></td><td>{authors}</td><td>{escape(entry["status"])}</td></tr>'
