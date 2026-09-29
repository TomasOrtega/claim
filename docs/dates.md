# Claim dates

We trust GitHub and the registry maintainers. The submission workflow adds
`claims/ID/date.json` in the PR, before review. It contains the exact record's
SHA-256 hash, a commit containing that record, the run URL and GitHub's workflow
creation time in UTC.

Merging or disclosing a claim preserves its date. Reruns reuse an existing PR or
branch. A changed record needs a new submission and date. Issue edits are not
processed; the workflow uses the attachment from the original issue event.

The date is the workflow's creation time, not a commit's author date or the time
of maintainer approval. Claims added manually without a date get one from the
push workflow. Undated claims display “Awaiting CI”.

Exports include `date.json`. If a workflow fails, open its run in GitHub Actions
and rerun it. The failure comment on the issue links to the run.
