# claim
Claim registry for mathematics

Ideally, this repo removes (or dampens) the incentive to publish raw AI-generated proofs immediately, so there is more time to produce a nice exposition.

1. Researchers can privately commit to a theorem/proof without revealing it.
2. Provide a public (and fixed) timestamped claim proving the result existed by that date.
3. Ideally include a Lean verification.
4. Reveal only the commitment authors, not their contents, to discourage mass speculative claims.
5. Allow later disclosure of the key/proof to establish independent discovery if someone else publishes first.

This project is inspired by Gonzalo Cao-Labora's tweets: https://x.com/GonZalocla/status/2104615564291563591.

## Current implementation

The first checkpoint provides in-memory commitments and opening verification.
Signatures, file storage, timestamps, the public registry and Lean checks are
planned. See the [version 1 protocol](docs/protocol.md).

Run Python examples from this checkout with `uv run python`:

```python
from claim.commitment import commit, new_salt, verify_opening

artifact = b"theorem: 1 + 1 = 2\n"
salt = new_salt()
commitment = commit(artifact, salt)
assert verify_opening(artifact, salt, commitment)
```

Keep the exact artifact bytes and salt private until disclosure. The core does
not save them for you. A matching opening establishes a commitment match; it
does not establish a date, mathematical validity or authorship.

Run tests with `uv run pytest` and lint checks with `prek -a --quiet`.
