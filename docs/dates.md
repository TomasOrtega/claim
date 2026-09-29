# Claim dates

We trust GitHub and the registry maintainers. After a push to `main`, CI adds
`claims/ID/date.json` with the record's SHA-256 hash, pushed commit, run URL and
the workflow's creation time in UTC. It never changes an existing date.

This records when GitHub created the workflow run, not the exact push time.
Claims already present when CI is installed receive that run's date. Commit
author dates are not used. If a run fails, rerun it from GitHub Actions.

## Registry setup

From this checkout, copy the [workflow](../.github/workflows/claim-dates.yml) into
the private registry once:

```sh
mkdir -p ~/claim-private/.github/workflows
cp .github/workflows/claim-dates.yml ~/claim-private/.github/workflows/
git -C ~/claim-private add .github/workflows/claim-dates.yml
git -C ~/claim-private commit -m 'ci: record claim dates'
git -C ~/claim-private push origin main
```

The registry must use `main`, have Actions enabled and allow this workflow to
push to `main`. It runs the tools from `TomasOrtega/claim`'s `main` branch.

Pull the CI commit before exporting the public site. Exports include `date.json`;
undated claims show “Awaiting CI”. Run links in a private registry require access
to that repository. The public date relies on the maintainers' honesty.
