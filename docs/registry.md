# Registry

Use a dedicated checkout of a private GitHub repository. An operator reviews each
submission and runs intake; there is no automatic approval or identity check.
Public name counts provide accountability, not reliable per-person quotas.
Install the [claim date workflow](dates.md#registry-setup) once before intake.

The submission directory must contain only `record.json` and `opening.fernet`.
Never send the researcher key.

```sh
uv run python -m claim accept ~/claim-private ~/submission
git -C ~/claim-private add .gitattributes claims
git -C ~/claim-private commit -m 'feat: register claim'
git -C ~/claim-private push origin main
```

`accept` prints the claim ID: SHA-256 of the exact record bytes. Records and
ciphertext are saved under `claims/ID/`. Existing claims cannot be overwritten.
Intake checks encryption framing; only the researcher can authenticate and decrypt
the opening.

Generated `.gitattributes` disables Git's line-ending conversion so record bytes
stay unchanged. Keep that file unchanged.

Wait for the date workflow to finish, then pull its commit and export:

```sh
git -C ~/claim-private pull --ff-only
uv run python -m claim export-index ~/claim-private ~/public-export
```

Exports use a fresh directory outside the registry. They contain author records,
dates, counts, JSON and HTML. Proofs and salts appear only after disclosure.

Copy the export, including `.gitattributes` and `.nojekyll`, into a separate public
repository. Publish its root using [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
Publish only after export succeeds; interrupted commands can leave partial output.

Keep a separate clone of the private repository as a backup. Test a restore by
running `disclose` on `claims/ID/` with the researcher's backup key, then `verify`
on the disclosure. The key must be backed up separately from the repository.

## Disclosure and withdrawal

Check the researcher's request before recording an event. Anyone with a copy of
a disclosure can submit it; the software does not authenticate the requester.

```sh
uv run python -m claim accept-disclosure ~/claim-private CLAIM_ID ~/disclosed
uv run python -m claim export-bundle ~/claim-private CLAIM_ID ~/bundle
uv run python -m claim withdraw ~/claim-private CLAIM_ID
```

Disclosure checks the original record, proof and salt. Events are appended;
withdrawal keeps the original record, disclosed files and author counts. Commit
the updated private registry, then export and publish a fresh public site.

The bundle contains the record, proof, salt, date if available, and event history.
It needs no encryption key. Follow [independent verification](verification.md).
