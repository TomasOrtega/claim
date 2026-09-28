def validate_record(record: dict) -> None:
    if not isinstance(record, dict) or record.keys() != {
        "version",
        "commitment",
        "authors",
    }:
        raise ValueError("invalid record fields")
