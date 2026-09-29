# claim
Claim registry for mathematics

Ideally, this repo removes (or dampens) the incentive to publish raw AI-generated proofs immediately, so there is more time to produce a nice exposition.

1. Researchers can privately commit to a theorem/proof without revealing it.
2. Record a public claim date through GitHub.
3. Reveal only the submitting GitHub account, not the claim's contents, to discourage mass speculative claims.
4. Allow later disclosure of the proof and salt to establish independent discovery if someone else publishes first.

We suggest researchers add a Lean verification to their claims.

This project is inspired by Gonzalo Cao-Labora's tweets: https://x.com/GonZalocla/status/2104615564291563591.

## Quickstart

Install [uv](https://docs.astral.sh/uv/), then run these commands with your proof
file and GitHub username:

```sh
git clone https://github.com/TomasOrtega/claim.git
cd claim
uv run python -m claim keygen ~/researcher.key
uv run python -m claim seal ~/proof.pdf ~/my-claim --key ~/researcher.key --author YOUR_GITHUB_USERNAME
```

Each claim has one registry author: the GitHub user submitting it.
List coauthors in the proof text before sealing it.

Generate the key once and reuse it. Keep it in a password manager and a separate
secure backup; losing every copy prevents decryption. Back up `~/my-claim` too.

Upload only `~/my-claim/record.json` using [Submit a claim](https://github.com/TomasOrtega/claim/issues/new?template=submit-claim.yml).
A bot opens a PR on your behalf with the claim and its date, before maintainer review.
The GitHub account opening the issue must match the record's author.
We trust GitHub and the registry maintainers to record dates honestly.
When ready, [publish the proof and salt](docs/storage.md). Never publish the key.

See the [protocol](docs/protocol.md).
