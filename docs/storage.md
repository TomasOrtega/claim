# Local commands

Run from this checkout. Keep private files outside it. Replace the paths and name:

```sh
uv run python -m claim keygen ~/researcher.key
uv run python -m claim seal ~/proof.pdf ~/my-claim --key ~/researcher.key --author "Your Name"
uv run python -m claim disclose ~/my-claim ~/disclosed --key ~/researcher.key
uv run python -m claim verify ~/disclosed
```

Proofs can be PDFs, Lean source files or ZIP archives. Their bytes are preserved
unchanged; checking their correctness is the researcher's responsibility.

Generate the key once; reuse it across projects. Store its 44-character ASCII text
in a password manager and a separate secure backup. Check that the backup can
decrypt a saved opening. Losing all copies makes encrypted proofs unrecoverable.

Repeat `--author` for coauthors. Sealing writes `opening.fernet` and `record.json`.
Back up the encrypted opening too. Only the record can be public before disclosure.

Disclosure exports `proof` (original bytes), `salt` (32 raw bytes), and the unchanged
`record.json`. Publish these files; never publish the key. Verification needs no key.
The registry keeps the [claim date](dates.md) separately. To submit a disclosure:

```sh
uv run python -m zipfile -c ~/disclosure.zip ~/disclosed/record.json ~/disclosed/proof ~/disclosed/salt
```

Attach `~/disclosure.zip` to [Disclose a claim](https://github.com/TomasOrtega/claim/issues/new?template=disclose-claim.yml).
Uploading publishes the proof and salt immediately. The bot checks the commitment
and opens a PR for review. Corrections need a new issue; editing an issue does not
rerun intake. Keep the encrypted opening and key backed up yourself.

Claim commands refuse existing output files or directories. An interrupted seal can
leave a partial directory; only a successful run produces a complete claim.
Limits: 10 MiB proofs, 14 MiB encrypted openings, 64 KiB records. Files are read
into memory. Private directories use mode `0700`, files `0600`.
