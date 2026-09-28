# Registry

Use a dedicated checkout of a private GitHub repository. An operator reviews each
submission and runs intake; there is no automatic approval or identity check.
Public name counts provide accountability, not reliable per-person quotas.

The submission directory must contain only `record.json` and `opening.fernet`.
Send the timestamp receipt separately. Never send the researcher key.

```sh
uv run python -m claim accept ~/claim-private ~/submission ~/record.ots
uv run python -m claim add-receipt ~/claim-private CLAIM_ID ~/upgraded.ots
uv run python -m claim export-index ~/claim-private ~/public-export
```

`accept` prints the claim ID: SHA-256 of the exact record bytes. Records and
ciphertext are saved under `claims/ID/`; receipts are kept by their own hashes.
Existing claims and receipts cannot be overwritten. Intake checks encryption
framing; only the researcher can authenticate and decrypt the opening.

Commit `.gitattributes` and `claims/` and push to the private repository after
successful intake. Generated `.gitattributes` disables Git's line-ending
conversion so records keep their timestamps. Keep that file unchanged.

Exports use a fresh directory outside the registry. They contain author records,
timestamp receipts, counts, JSON and HTML. Timestamp status is recomputed: pending,
verified, or failed. A node connection failure cannot produce a verified date.

Copy the export, including `.gitattributes` and `.nojekyll`, into a separate public
repository. Publish its root using [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
Publish only after export succeeds; interrupted commands can leave partial output.

Keep a separate clone of the private repository as a backup. Test a restore by
running `disclose` on `claims/ID/` with the researcher's backup key, then `verify`
on the disclosure. The key must be backed up separately from the repository.
