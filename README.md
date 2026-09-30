# claim
Claim registry for mathematics.

Inspired by [Gonzalo Cao-Labora's posts](https://x.com/GonZalocla/status/2104615564291563591), which originally suggested an encryption-based system.

Further comments by [Ricardo Perez-Marco](https://x.com/rperezmarco/status/2105052248430501898) pointed out that we did not need encryption, a simple hash would do.

If you have some work that is not yet publication-ready, but you want to claim you were first to do it, you can use this repository to register your claim.

The recommended workflow is: zip your work, calculate its SHA-256 hash, and post the hash
on your favorite social media (anywhere that doesn't allow you to change the date of the post to the past). The date of the post is your claim date.

## Detailed instructions

1. Put your work in a folder, including authors' names. A personal note: add a Lean formalization, it's going to be helpful for you!
2. Create a ZIP of that folder. Keep that exact ZIP, and back it up so you do not lose it. If you lose it, you will not be able to claim anything.
3. Calculate its SHA-256 hash **locally**:

   macOS:
   ```sh
   shasum -a 256 work.zip
   ```

   Linux:
   ```sh
   sha256sum work.zip
   ```

   Windows PowerShell:
   ```powershell
   (Get-FileHash .\work.zip -Algorithm SHA256).Hash
   ```

4. Copy the 64-character hash and post it publicly. Keep the ZIP private until
   you are ready to reveal your work to the public.

## No social media?

If you do not have socials, you can paste the hash into a [new claim issue](https://github.com/TomasOrtega/claim/issues/new?template=submit-claim.yml).
Paste only the hash, without the filename or command output labels.

A bot copies the hash from the issue's opening event into a PR, attributed to
your GitHub account. The PR's GitHub creation time is your claim date.
It does not need to be merged first.

Open a new issue for a correction or revised work.


## Limits on this repository's bot

Each GitHub account can register **one claim per UTC day**. The repository also
accepts at most **30 new claims per UTC hour** to stay within GitHub's API budget.

We merge claims once a day.

