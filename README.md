# claim
Claim registry for mathematics

Ideally, this repo removes (or dampens) the incentive to publish raw AI-generated proofs immediately, so there is more time to produce a nice exposition.

1. Researchers can privately commit to a theorem/proof without revealing it.
2. Provide a public (and fixed) timestamped claim proving the result existed by that date.
3. Ideally include a Lean verification.
4. Reveal only the commitment authors, not their contents, to discourage mass speculative claims.
5. Allow later disclosure of the proof and salt to establish independent discovery if someone else publishes first.

This project is inspired by Gonzalo Cao-Labora's tweets: https://x.com/GonZalocla/status/2104615564291563591.

## Current implementation

The library creates commitments, saves encrypted proofs with their salts, and
builds public records with self-declared author names. Use the [CLI](docs/storage.md)
to seal, disclose and verify claims, and [timestamp](docs/timestamps.md) public
records. Operators can [accept claims and export a public registry](docs/registry.md).
Lean checks are next. See the [protocol](docs/protocol.md).

Run Python examples from this checkout with `uv run python`:

```python
from claim.commitment import commit, new_salt, verify_opening

artifact = b"theorem: 1 + 1 = 2\n"
salt = new_salt()
commitment = commit(artifact, salt)
assert verify_opening(artifact, salt, commitment)
```

One researcher encryption key can protect many projects. Keep it in a password
manager and a separate secure backup. Losing every copy makes encrypted proofs
unrecoverable. Back up the encrypted files too. Publish only the proof and salt
when disclosing a claim; never publish the key.

A matching opening establishes a commitment match, not a date, mathematical
validity or authorship.

Run tests with `uv run pytest` and lint checks with `prek -a --quiet`.
