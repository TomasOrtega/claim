# Protocol v1

A timestamped commitment is evidence that specific bytes existed by a date.
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
Timestamp the exact record bytes to bind the claimed names and commitment.

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

Publish the record, timestamp evidence and status. Keep the artifact,
salt, unsalted artifact hash and theorem metadata private until disclosure.
Disclose the original artifact and salt alongside the record and timestamp proof.
Keep the encryption key private. Revised proofs need new commitments.

## Status

Claims start sealed. Append disclosure or withdrawal events without
changing the original record or removing claims from author counts. Withdrawal
does not hide an earlier disclosure. Events record operator decisions; they do
not have independently verified dates.

Timestamp status is pending, verified or failed. Only independent verification
establishes the attested date; registry receipt time is separate.
Label private Lean checks as author-reported until independently checked.
