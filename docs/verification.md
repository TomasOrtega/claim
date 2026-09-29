# Check a published claim

The registry checks that published work matches the earlier claim. You can
repeat that check yourself without the author's private key.

Follow [Set up once](storage.md#set-up-once), skipping the key-generation command.
From the project folder, run these commands, replacing `CLAIM_ID` with the ID
shown in the registry:

```sh
uv run python -m claim export-bundle . CLAIM_ID ~/bundle
uv run python -m claim verify ~/bundle
```

The first command downloads the work. The second confirms it matches the claim;
it also works offline. Use a new folder name if `~/bundle` already exists.

This checks the saved file, not the mathematics. See [how dates work](dates.md).
