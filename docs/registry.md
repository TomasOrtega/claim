# For maintainers

Researchers can follow the [create and publish guide](storage.md).

Each submission opens a pull request for review. Check it and merge it to accept
the claim. The date is already recorded, so waiting for review does not delay it.
Merged branches are deleted automatically.

The forms check that the submitter's GitHub account matches the record.
For a manually opened pull request or a withdrawal request, check that yourself.
Coauthors belong in the work's text.

If an automatic check fails, rerun the original run in GitHub Actions.
If someone needs to correct their submission, ask them to open a new issue.

<details>
<summary>Manual commands and repository settings</summary>

Run these from the project folder. Replace the capitalized values with those
from the claim; use new output folders.

```sh
uv run python -m claim accept . ~/my-claim/record.json
uv run python -m claim accept-disclosure . CLAIM_ID PROOF_URL SALT
uv run python -m claim withdraw . CLAIM_ID
uv run python -m claim export-index . ~/public-export
```

Commit and push manual changes. Withdrawal keeps the original record and any
published disclosure. Keep `.gitattributes` unchanged to preserve file contents.

In **Settings → Actions → General**, enable **Allow GitHub Actions to create
and approve pull requests**. Our workflows create requests; maintainers merge them.

</details>
