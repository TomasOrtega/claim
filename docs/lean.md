# Lean checks

Optional checks support Lean 4.34.0. Use a ZIP with `lean-toolchain`,
`lake-manifest.json`, the Lake configuration and sources at its root. Include
dependencies as vendored path packages. Omit `.git` and build outputs. Limits
are 10 MiB compressed, 128 MiB expanded and 20,000 entries.

Try the included example:

```sh
(cd examples/lean && zip /tmp/proof.zip lean-toolchain lake-manifest.json lakefile.toml Proof.lean)
uv run python -m claim check-lean /tmp/proof.zip Proof result --trusted-local
uv run python -m claim seal /tmp/proof.zip ~/lean-claim --key ~/researcher.key --author "Your Name"
```

`--trusted-local` executes the project's build on your computer. Use it only for
your own trusted sources, never for uploads. Install the pinned toolchain with
`elan toolchain install leanprover/lean4:v4.34.0` first.

The JSON report binds the check to the archive's SHA-256 hash. Keep the archive
unchanged when sealing it. Reports contain theorem details; keep them private
until disclosure. Local checks are author-reported, with no public certification.

## After disclosure

First [verify the opening and timestamp](verification.md). Then check the
disclosed archive on a separate verifier machine, using an image you built:

```sh
docker build -f docker/lean.Dockerfile -t claim-lean docker
LEAN_IMAGE=$(docker image inspect --format '{{.Id}}' claim-lean)
uv run python -m claim check-lean ~/bundle/proof Proof result --image "$LEAN_IMAGE"
```

Build and verification run in separate containers with no network, read-only
inputs, a non-root user and resource limits. Only compiled Lean objects cross
between them. The registry never executes submitted projects. Docker availability
is required; there is no fallback to local execution. Each stage has a time limit
of about five minutes, 4 GiB memory and 1 GiB scratch space.

The checker replays declarations through Lean's kernel and audits the selected
theorem's dependencies. Only `propext`, `Classical.choice` and `Quot.sound` are
allowed axioms. `sorry`, extra axioms and missing declarations fail. Inspect the
statement and sources to confirm they express the intended mathematics. Neither
a Lean check nor a saved report authenticates the author.

Local integration tests: `CLAIM_TEST_LEAN=1 uv run pytest tests/test_lean_integration.py`.
Container integration: `CLAIM_TEST_LEAN_IMAGE="$LEAN_IMAGE" uv run pytest tests/test_lean_container_integration.py`.
The container path is implemented but has not been run here: Docker's engine
was unavailable.
