# Timestamps

Timestamp the exact public record. Creating a receipt needs network access:

```sh
uv run python -m claim stamp ~/my-claim/record.json ~/record.ots
```

The receipt starts pending. After Bitcoin confirmation, save an upgraded copy:

```sh
uv run python -m claim upgrade ~/my-claim/record.json ~/record.ots ~/upgraded.ots
uv run python -m claim verify-time ~/my-claim/record.json ~/upgraded.ots
```

Verification needs a synced Bitcoin Core mainnet node with RPC enabled. The client
uses its local configuration and cookie. A pruned node works. See the
[OpenTimestamps requirements](https://github.com/opentimestamps/opentimestamps-client#requirements).
Researchers can create receipts without running a node.

`verify-time` returns JSON: `pending`, or `verified` with the Bitcoin block height
and Unix block time. Only verified receipts exit successfully. Errors exit nonzero.
Upgrading a receipt alone does not verify it. If confirmation is still pending,
upgrade fails without changing the original; retry later with a new output path.

Publish the record and receipt together. Keep both original and upgraded receipts.
Changing any record byte invalidates its receipt. Disclosure also publishes the
proof and salt; verification of the opening and timestamp are separate commands.
