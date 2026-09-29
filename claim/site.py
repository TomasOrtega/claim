from html import escape


def claim_row(entry: dict) -> str:
    claim_id = escape(entry["id"])
    authors = ", ".join(escape(name) for name in entry["authors"])
    date = "Awaiting CI"
    evidence = ""
    if entry["date"] is not None:
        date = escape(entry["date"]["recorded_at"])
        evidence = f'<a href="./{claim_id}/date.json">date</a> <a href="{escape(entry["date"]["run_url"])}">CI run</a>'
    if "disclosed" in entry.get("events", []):
        evidence += f' <a href="./{claim_id}/proof">proof</a> <a href="./{claim_id}/salt">salt</a>'
    evidence += " ".join(
        f' <a href="./{claim_id}/events/{i:04d}.json">{escape(event)}</a>'
        for i, event in enumerate(entry.get("events", []), 1)
    )
    return f'<tr><td><a href="./{claim_id}/record.json">{claim_id[:12]}</a></td><td>{authors}</td><td>{escape(entry["status"])}</td><td>{date}</td><td>{evidence}</td></tr>'


def render(index: dict) -> str:
    rows = "\n".join(claim_row(entry) for entry in index["claims"])
    counts = "".join(
        f"<li>{escape(name)}: {count}</li>" for name, count in index["authors"].items()
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claim registry</title>
<style>body{{font:16px system-ui;max-width:70rem;margin:3rem auto;padding:0 1rem;color:#222}}table{{width:100%;border-collapse:collapse}}th,td{{padding:.6rem;text-align:left;border-bottom:1px solid #ddd;vertical-align:top}}a{{color:#1255a8}}.claims{{overflow-x:auto}}</style>
<body><h1>Claim registry</h1>
<p>Names are self-declared. Dates are recorded by the registry's CI.</p>
<div class="claims"><table><thead><tr><th>Claim</th><th>Authors</th><th>State</th><th>Recorded (UTC)</th><th>Files</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Claims per name</h2><ul>{counts}</ul><p><a href="index.json">Download index</a></p></body></html>"""
