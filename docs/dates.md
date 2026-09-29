# Claim dates

We trust GitHub and the registry maintainers. After a push to `main`, CI adds
`claims/ID/date.json` with the record's SHA-256 hash, pushed commit, run URL and
the workflow's creation time in UTC. It never changes an existing date.

This records when GitHub created the workflow run, not the exact push time.
Commit author dates are not used. If a run fails, rerun it from GitHub Actions.

Pull the CI commit before exporting the public site. Exports include `date.json`;
undated claims show “Awaiting CI”. Run links in a private registry require access
to that repository. The public date relies on the maintainers' honesty.
