# Registry commands

Normal intake uses the **Submit a claim** and **Disclose a claim** issue forms.
Both open PRs for review. Submission adds only the public record and its date;
disclosure checks an author-hosted proof and salt against an existing record.
The registry stores only the proof link, salt, hash and verification date.
Researchers keep their encrypted openings and keys.

Each record lists one GitHub user. Both workflows require that account to open
the issue that creates the PR. Coauthors are listed in the proof text before sealing.

GitHub requires **Settings → Actions → General → Allow GitHub Actions to create
and approve pull requests**. These workflows create PRs; review and merge stay
manual.

Review and merge the bot's PR. The date is already recorded, so review delays
do not delay the claim date. Corrections require a new issue. A failed job can be
rerun from GitHub Actions without creating a second PR or changing a saved date.

For manual intake, run these commands from the registry checkout:

```sh
uv run python -m claim accept . ~/my-claim/record.json
uv run python -m claim accept-disclosure . CLAIM_ID PROOF_URL SALT
uv run python -m claim withdraw . CLAIM_ID
```

`accept` prints the claim ID, SHA-256 of the exact record bytes. Existing records
cannot be overwritten. Commit and push manual changes; undated records receive
a date from the push workflow. Keep `.gitattributes` unchanged to preserve bytes.
`PROOF_URL` must be a public GitHub file link pinned to a full commit hash.
`SALT` is the 64-character hexadecimal value printed by `claim disclose`.

For manual PRs, check that the record's username matches the person opening the PR.
Check withdrawal requests against the same account. Withdrawal keeps the record,
earlier disclosures and counts per GitHub user.

```sh
uv run python -m claim export-index . ~/public-export
uv run python -m claim export-bundle . CLAIM_ID ~/bundle
```

Use fresh output directories. Publish the completed site export, including
`.gitattributes` and `.nojekyll`. Site exports link to proofs without downloading them.
Bundle export downloads and verifies one proof for offline use, alongside the
record, salt, dates and events. It fails if the proof is unavailable or changed.
Follow [independent verification](verification.md).
