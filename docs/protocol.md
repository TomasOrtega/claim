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

## Signed records (planned)

The UTF-8 JSON body contains `version: 1`, `commitment` and `authors`.
Each author has a nonempty `name` and an Ed25519 `public_key` (64 lowercase hex
characters). Require at least one author and unique keys. Every author signs
`b"claim:record:v1\0" + body_bytes`.

The JSON envelope contains `body` (standard base64 of the original bytes) and
`signatures`, each with `public_key` and `signature` (128 lowercase hex characters).
Require exactly one valid signature per author. Reject duplicate JSON keys,
extra fields, unknown versions, wrong types and invalid encodings.

The record ID is the lowercase hex SHA-256 of the final envelope bytes.
Timestamp those bytes; edits require a new record and timestamp. Verify signatures
against the original body bytes. Check key-to-person identities separately.

## Disclosure

Publish the signed record, ID, timestamp evidence and status. Keep the artifact,
salt, unsalted artifact hash and theorem metadata private until disclosure.
Disclose the original artifact and salt alongside the record and timestamp proof.
Keep signing keys private. Revised proofs need new commitments.
