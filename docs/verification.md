# Verify a disclosure

Download the claim's record, proof, salt and `.ots` receipts into one directory,
or obtain an `export-bundle` directory. Keep all bytes unchanged.

```sh
uv run python -m claim verify ~/bundle
uv run python -m claim verify-time ~/bundle/record.json ~/bundle/RECEIPT.ots
```

The first command checks the commitment. The second checks one receipt against
Bitcoin Core; see [node setup and pending receipts](timestamps.md). A successful
timestamp verifies existence by the reported block date. Try other receipts if
one is pending; neither a file date nor a registry status replaces this check.

Read the original `record.json` for the claimed author names. Names and operator
events are not identity checks. A matching commitment and timestamp do not
establish mathematical correctness or independent discovery.
