import re
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import BadZipFile, ZipFile

from claim import files, record, workflow
from claim.limits import MAX_ARTIFACT_BYTES, MAX_RECORD_BYTES


def attachment_url(body: str, extension: str) -> str:
    urls = re.findall(r"https?://[^\s<>()]+", body)
    pattern = r"https://github\.com/user-attachments/files/[0-9]+/[\w.-]+"
    if len(urls) != 1 or not re.fullmatch(pattern + re.escape(extension), urls[0]):
        raise ValueError(f"attach exactly one GitHub {extension} file")
    return urls[0]


def limited(stream, limit: int) -> bytes:
    data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("submission exceeds size limit")
    return data


def disclosure_files(data: bytes) -> dict[str, bytes]:
    limits = {"record.json": MAX_RECORD_BYTES, "proof": MAX_ARTIFACT_BYTES, "salt": 32}
    try:
        with ZipFile(BytesIO(data)) as archive:
            if len(archive.infolist()) != 3 or set(archive.namelist()) != limits.keys():
                raise ValueError("ZIP must contain only record.json, proof and salt")
            contents = {}
            for name, limit in limits.items():
                if archive.getinfo(name).file_size > limit:
                    raise ValueError("submission exceeds size limit")
                with archive.open(name) as stream:
                    contents[name] = limited(stream, limit)
    except (BadZipFile, RuntimeError, NotImplementedError) as exc:
        raise ValueError("invalid disclosure ZIP") from exc
    workflow.check_opening(contents["record.json"], contents["proof"], contents["salt"])
    return contents


def download(kind: str, body: str, output: Path) -> str:
    extension = ".json" if kind == "submit" else ".zip"
    limit = MAX_RECORD_BYTES if kind == "submit" else MAX_ARTIFACT_BYTES + 131072
    url = attachment_url(body, extension)
    with urlopen(url, timeout=30) as stream:
        data = limited(stream, limit)
    contents = {"record.json": data} if kind == "submit" else disclosure_files(data)
    claim_id = record.record_id(contents["record.json"])
    for name, data in contents.items():
        files.write_private(output / name, data)
    return claim_id
