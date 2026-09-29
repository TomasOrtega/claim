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

Disclosure exports `proof` (original bytes), `salt` (32 raw bytes), and `record.json`.
The command prints the claim ID and salt for the disclosure form. Never publish the key.

1. Upload `~/disclosed/proof` to an ordinary public GitHub repository you own.
   You can rename it, for example to `proof.pdf`, without changing its contents.
2. Open the file on GitHub and press `y` to get a [permanent link](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files).
3. Fill in [Disclose a claim](https://github.com/TomasOrtega/claim/issues/new?template=disclose-claim.yml)
   with the claim ID, proof link and salt printed by the command.

The bot downloads the proof, checks the commitment and opens a PR containing only
the link, salt, proof hash and verification date. The original [claim date](dates.md)
stays unchanged. Your repository can hold many proofs; keep published files available.
If using Git to upload them, set `* -text` in `.gitattributes` before adding files
to preserve line endings. Uploading through GitHub's website also preserves bytes.

Corrections need a new issue; editing an issue does not rerun intake.
Keep the encrypted opening and key backed up yourself.

Claim commands refuse existing output files or directories. An interrupted seal can
leave a partial directory; only a successful run produces a complete claim.
Limits: 10 MiB proofs, 14 MiB encrypted openings, 64 KiB records. Files are read
into memory. Private directories use mode `0700`, files `0600`.
