# Commitment version 1 vector

`test_commitment.py` uses this synthetic opening:

- Artifact hex: `7468656f72656d3a2031202b2031203d20320a`
- Salt hex: `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f`
- Commitment hex: `d8c1f7f6682114f2e776e755c16f7f73d27ae7546c561ff9679a5ea5e35b25cb`

The expected value was calculated using `openssl dgst -sha256 -binary` for the
artifact digest, then the same command for the prefix, salt and binary digest
concatenated in protocol order. The outer digest was independently checked with
`shasum -a 256`. Neither calculation used the project's implementation.
The predictable salt is test data only; real claims need a fresh random salt.
