# Protocol v1

We trust GitHub and the registry maintainers to record claim dates honestly.
Correctness, authorship and independent discovery require separate evidence.

## Commitment

For artifact bytes `A`, a fresh 32-byte salt `S` and SHA-256 `H`:

```text
C = H(b"claim:commit:v1\0" || S || H(A))
```

Hash raw digests; encode `C` as 64 lowercase hexadecimal characters. Preserve
artifact bytes unchanged, including line endings. Empty and binary inputs work.
Generate salts with `secrets.token_bytes(32)`; other lengths raise `ValueError`.
Opening recomputes `C` and checks for an exact match.

## Public records

A UTF-8 JSON record contains `version: 1`, `commitment` and `authors`, a nonempty
list of distinct, nonblank names. Names are self-declared; there are no accounts
or identity checks. Reject duplicate JSON keys, extra fields and invalid types.
The claim ID is SHA-256 of the exact record bytes, including the author names.

CI adds a separate `date.json` containing the record hash, pushed commit, run URL
and GitHub's workflow creation time in UTC. Existing dates are kept unchanged.
See [claim dates](dates.md).

## Encrypted storage

One researcher key can encrypt many projects. Use Fernet from `cryptography` to
encrypt `b"claim:opening:v1\0" || S || A`. Its library supplies fresh randomness
and checks authentication before decryption. The format exposes ciphertext length
and encryption time, not the proof or salt. [Fernet format](https://cryptography.io/en/stable/fernet/)

Generate the key with `Fernet.generate_key()`. Keep two secure copies in separate
places, such as a password manager and an encrypted backup. Never put it in the
project repository or publish it. Losing every copy makes encrypted claims
unrecoverable. This is an encryption key, not a signing key or a commitment salt.

## Disclosure

Publish the record, date and status. Keep the artifact,
salt, unsalted artifact hash and theorem metadata private until disclosure.
Disclose the original artifact and salt alongside the record and date.
Keep the encryption key private. Revised proofs need new commitments.

## Status

Claims start sealed. Append disclosure or withdrawal events without
changing the original record or removing claims from author counts. Withdrawal
does not hide an earlier disclosure. Events record operator decisions; they do
not have recorded dates.

Undated claims display “Awaiting CI”.
