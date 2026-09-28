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
