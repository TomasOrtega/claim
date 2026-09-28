def validate_record(record: dict) -> None:
    if not isinstance(record, dict) or record.keys() != {
        "version",
        "commitment",
        "authors",
    }:
        raise ValueError("invalid record fields")
    if type(record["version"]) is not int or record["version"] != 1:
        raise ValueError("unsupported record version")
