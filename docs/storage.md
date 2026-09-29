# Create and publish a claim

## Set up once

Install [Git](https://git-scm.com/downloads) and [uv](https://docs.astral.sh/uv/).
Open a terminal and paste these commands:

```sh
git clone https://github.com/TomasOrtega/claim.git
cd claim
uv run python -m claim keygen ~/researcher.key
```

`researcher.key` unlocks your saved work. Keep it in a password manager and a
separate secure backup. Reuse it for future claims. Never share it; losing every
copy makes the encrypted work unrecoverable.

## Create a claim

Put all authors' names in your work before saving it. Use a PDF or other file
under 10 MB. Replace `~/work.pdf` with your file's location and
`YOUR_GITHUB_USERNAME` with the account you will submit from:

```sh
uv run python -m claim seal ~/work.pdf ~/my-claim --key ~/researcher.key --author YOUR_GITHUB_USERNAME
```

In your home folder, find `my-claim/record.json`. Drag it into
[Submit a claim](https://github.com/TomasOrtega/claim/issues/new?template=submit-claim.yml).
GitHub uploads the file and inserts a link in the text box.

Keep the rest of `my-claim` private and backed up. Choose a new folder name for
each claim. The registry lists only your GitHub account; coauthors stay in the work.

## Decrypt and publish

Whenever you want to make your work public, run this from the `claim` folder:

```sh
uv run python -m claim disclose ~/my-claim ~/disclosed --key ~/researcher.key
```

This recovers your original work as `~/disclosed/proof` and prints a **Claim ID**
and **Salt**. The salt is a code that lets others check your earlier claim.

1. Create a public [GitHub repository](https://github.com/new) under your account
   and upload `~/disclosed/proof`. You can rename it, for example to `work.pdf`;
   keep its contents unchanged.
2. Open the uploaded file on GitHub, press **y**, and copy the address.
3. From the same account, open [Disclose a claim](https://github.com/TomasOrtega/claim/issues/new?template=disclose-claim.yml).
   Paste the address, claim ID and salt into the form.

Your [original claim date](dates.md) stays unchanged. Keep the published file
available and your private key secret.
