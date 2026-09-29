# Verify a disclosure

Download the claim's record, proof, salt and `date.json` into one directory,
or obtain an `export-bundle` directory. Keep all bytes unchanged.

```sh
uv run python -m claim verify ~/bundle
```

This checks that the proof and salt match the commitment. If `date.json` is
present, it also checks that it refers to the same record. The date itself is
trusted to GitHub and the registry maintainers; the command does not authenticate
it. See [claim dates](dates.md).

Read the original `record.json` for the claimed author names. Names and operator
events are not identity checks. A matching commitment and recorded date do not
establish mathematical correctness or independent discovery.
