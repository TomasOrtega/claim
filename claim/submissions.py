import re
from pathlib import Path
from urllib.request import urlopen

from claim import disclosure, files, record
from claim.limits import MAX_RECORD_BYTES


def attachment_url(body: str) -> str:
    urls = re.findall(r"https?://[^\s<>()]+", body)
    pattern = r"https://github\.com/user-attachments/files/[0-9]+/[\w.-]+\.json"
    if len(urls) != 1 or not re.fullmatch(pattern, urls[0]):
        raise ValueError("attach exactly one GitHub .json file")
    return urls[0]


def download(body: str, output: Path) -> str:
    with urlopen(attachment_url(body), timeout=30) as stream:
        data = stream.read(MAX_RECORD_BYTES + 1)
    if len(data) > MAX_RECORD_BYTES:
        raise ValueError("submission exceeds size limit")
    claim_id = record.record_id(data)
    files.write_private(output / "record.json", data)
    return claim_id


def disclosure_request(body: str) -> dict:
    match = re.fullmatch(
        r"\s*### Claim ID\s+([0-9a-f]{64})\s+"
        r"### Proof URL\s+(\S+)\s+### Salt\s+([0-9a-f]{64})\s*",
        body,
    )
    if match is None:
        raise ValueError("provide a claim ID, pinned proof URL and hexadecimal salt")
    claim_id, url, salt = match.groups()
    disclosure.raw_url(url)
    return {"claim_id": claim_id, "proof_url": url, "salt": salt}
