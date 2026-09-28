# Saving a claim

Generate one key with `claim.encryption.new_key()`. Store its ASCII text in a
password manager and a separate secure backup, then reuse it for your projects.
Keep both copies private and check that the backup can decrypt a saved opening.
There is no key recovery service.

Run this from the checkout with `uv run python`, replacing the proof path and
author name. The new claim directory must be outside the checkout. The prompt
accepts your saved key without echoing it.

```python
from getpass import getpass
from pathlib import Path

from claim.commitment import commit, new_salt, verify_opening
from claim.files import create_private_directory, read_limited, write_private
from claim.limits import MAX_ARTIFACT_BYTES
from claim.record import build_record, dump_record
from claim.storage import load_opening, save_opening

key = getpass("Researcher encryption key: ").encode("ascii")
directory = Path.home() / "my-claim"
create_private_directory(directory)
artifact = read_limited(Path.home() / "proof.pdf", MAX_ARTIFACT_BYTES)
salt = new_salt()
record = build_record(commit(artifact, salt), ["Your Name"])
opening = directory / "opening.fernet"
save_opening(opening, artifact, salt, key)
assert verify_opening(*load_opening(opening, key), record["commitment"])
write_private(directory / "record.json", dump_record(record))
```

Back up `opening.fernet`; it contains the exact proof bytes and salt, encrypted
together. `record.json` can be public. Keep its exact bytes for later timestamping.
Existing files are never overwritten. An interrupted run can leave a partial
directory; check that the opening matches the record before publishing it.

To disclose, decrypt the opening and publish the returned proof bytes and salt
with the public record. Anyone can check them with `verify_opening`; they do not
need your key. Editing the source proof never changes an existing opening.

Limits: 10 MiB per proof, 14 MiB per encrypted opening, 64 KiB per public record.
Files are read into memory. New private directories use mode `0700`, files `0600`.
