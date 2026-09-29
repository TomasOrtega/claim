# How claims work

Creating a claim saves an encrypted copy of your work and a small public record.
You keep the encrypted copy and its private key. The registry receives only the
public record and adds a date.

Each record names one GitHub account: the person submitting the claim.
Put all coauthors' names in the work before creating it.

Whenever you want, decrypt and publish the original work. The registry checks
that it matches your earlier record and saves a link to it. Editing the work
requires a new claim.

Dates rely on GitHub and the maintainers. The registry does not check mathematical
correctness or decide who discovered a result first. See [your claim date](dates.md).

<details>
<summary>Technical format (version 1)</summary>

For work bytes `A`, a random 32-byte salt `S`, and SHA-256 `H`:

```text
C = H(b"claim:commit:v1\0" || S || H(A))
```

Use raw digests internally and lowercase hexadecimal for `C`.

- `record.json` contains `version: 1`, `commitment: C` and `authors`: a list with one
  GitHub username. Its exact bytes determine the claim ID (SHA-256). Reject
  duplicate keys, extra fields and invalid types.
- The private file uses Fernet to encrypt `b"claim:opening:v1\0" || S || A`.
  One key can be reused across claims.
- `date.json` contains `record_sha256`, `commit`, `run_url` and `recorded_at`:
  GitHub's workflow creation time in UTC.
- `disclosure.json` contains `proof_url` (pinned to a full GitHub commit), `salt`
  (hexadecimal), `proof_sha256` and `verified_at` (UTC). Proof files stay in the
  author's repository.
- Disclosure and withdrawal are recorded without deleting earlier records.
  Withdrawal keeps the claim in the count for its GitHub user.

Limits: 10 MiB for work, 14 MiB for its encrypted copy, and 64 KiB for a record.

</details>
