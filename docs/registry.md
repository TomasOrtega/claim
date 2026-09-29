# Registry commands

Normal intake uses the **Submit a claim** and **Disclose a claim** issue forms.
Both open PRs for review. Submission adds only the public record and its date;
disclosure checks the proof and salt against an existing record. Researchers
keep their encrypted openings and keys.

Review and merge the bot's PR. The date is already recorded, so review delays
do not delay the claim date. Corrections require a new issue. A failed job can be
rerun from GitHub Actions without creating a second PR or changing a saved date.

For manual intake, run these commands from the registry checkout:

```sh
uv run python -m claim accept . ~/my-claim/record.json
uv run python -m claim accept-disclosure . CLAIM_ID ~/disclosed
uv run python -m claim withdraw . CLAIM_ID
```

`accept` prints the claim ID, SHA-256 of the exact record bytes. Existing records
cannot be overwritten. Commit and push manual changes; undated records receive
a date from the push workflow. Keep `.gitattributes` unchanged to preserve bytes.

Names are self-declared. Check disclosure and withdrawal requests before merging;
the software does not authenticate the requester. Withdrawal keeps the record,
earlier disclosures and author counts.

```sh
uv run python -m claim export-index . ~/public-export
uv run python -m claim export-bundle . CLAIM_ID ~/bundle
```

Use fresh output directories. Publish the completed site export, including
`.gitattributes` and `.nojekyll`. Bundles contain the record, proof, salt, date
if available, and event history. Follow [independent verification](verification.md).
