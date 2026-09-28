import re


def validate_record(record: dict) -> None:
    if not isinstance(record, dict) or record.keys() != {
        "version",
        "commitment",
        "authors",
    }:
        raise ValueError("invalid record fields")
    if type(record["version"]) is not int or record["version"] != 1:
        raise ValueError("unsupported record version")
    digest = record["commitment"]
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("invalid commitment")
    authors = record["authors"]
    if not isinstance(authors, list) or not authors:
        raise ValueError("invalid authors")
