# claim

Record a mathematical proof with a date while keeping the proof private.

The aim is to give researchers time to check their work and write a clear
explanation before publishing, including when they use AI. When you later share
the original proof, others can check that it matches your earlier record.

Your GitHub username and the submission date are public. The proof stays private
until you choose to share it. Each claim has one account responsible for it;
put all authors' names in the proof itself before creating the claim.

## Quickstart

1. **Prepare your claim.** Follow the [setup guide](docs/storage.md) to save an
   encrypted copy of your proof and create a small public file called `record.json`.
   This currently requires running a few commands on your computer.
2. **Submit the public file.** Sign in with the GitHub account you used during
   setup, then attach only `record.json` to [Submit a claim](https://github.com/TomasOrtega/claim/issues/new?template=submit-claim.yml).
   The system records a date and sends your submission to the maintainers for review.
3. **Share your proof when ready.** Follow the [publishing instructions](docs/storage.md)
   to put the original proof in your own public GitHub repository and link it to
   your claim. Its original date stays unchanged.

Your private key unlocks the saved proof. Keep it in a password manager and a
separate secure backup, and back up the saved claim folder too. Never share the
key: if you lose every copy, the encrypted proof cannot be recovered.

The registry does not check whether a proof is correct. We trust GitHub and the
maintainers to record dates honestly. We encourage including a proof checked
with Lean, a tool for verifying mathematics.

For technical details, see the [protocol](docs/protocol.md).

Inspired by [Gonzalo Cao-Labora's posts](https://x.com/GonZalocla/status/2104615564291563591).
