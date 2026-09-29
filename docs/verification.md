# Verify a disclosure

From a registry checkout, download a verification bundle:

```sh
uv run python -m claim export-bundle . CLAIM_ID ~/bundle
```

This fetches the author-hosted proof and checks its hash. The bundle includes
the original record, proof, raw salt and saved dates. Verification then works offline:

```sh
uv run python -m claim verify ~/bundle
```

This checks that the proof and salt match the commitment. If `date.json` is
present, it also checks that it refers to the same record. The date itself is
trusted to GitHub and the registry maintainers; the command does not authenticate
it. See [claim dates](dates.md).

The salt in `disclosure.json` is hexadecimal; the bundle's `salt` file contains
the decoded 32 bytes. `verified_at` records when the proof was checked, not when
the original claim was submitted. Proof availability depends on its author's repository.

Read the original `record.json` for the claimed author names. Names and operator
events are not identity checks. A matching commitment and recorded date do not
establish mathematical correctness or independent discovery.
