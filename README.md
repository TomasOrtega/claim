# claim
Claim registry for mathematics

Ideally, this repo removes (or dampens) the incentive to publish raw AI-generated proofs immediately, so there is more time to produce a nice exposition.

1. Researchers can privately commit to a theorem/proof without revealing it.
2. Record a public claim date through GitHub.
3. Reveal only the commitment authors, not their contents, to discourage mass speculative claims.
4. Allow later disclosure of the proof and salt to establish independent discovery if someone else publishes first.

We suggest researchers add a Lean verification to their claims.

This project is inspired by Gonzalo Cao-Labora's tweets: https://x.com/GonZalocla/status/2104615564291563591.

## Quickstart

Install [uv](https://docs.astral.sh/uv/), then run these commands with your proof
file and name:

```sh
git clone https://github.com/TomasOrtega/claim.git
cd claim
uv run python -m claim keygen ~/researcher.key
uv run python -m claim seal ~/proof.pdf ~/my-claim --key ~/researcher.key --author "Your Name"
```

Generate the key once and reuse it. Keep it in a password manager and a separate
secure backup; losing every copy prevents decryption. Back up `~/my-claim` too.

Submit `~/my-claim` to the [registry](docs/registry.md). CI records its date after
the operator pushes it to GitHub; we trust GitHub and the registry maintainers.
When ready, [publish the proof and salt](docs/storage.md). Never publish the key.

More: [hosting a registry](docs/registry.md), [protocol](docs/protocol.md).
