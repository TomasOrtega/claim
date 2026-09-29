import argparse
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from claim import dates, disclosure, files, record, registry, submissions


def command(*args: str) -> str:
    return subprocess.run(
        args, check=True, capture_output=True, text=True, timeout=60
    ).stdout.strip()


def git(*args: str) -> str:
    return command(
        "git",
        "-c",
        "user.name=github-actions[bot]",
        "-c",
        "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        *args,
    )


def gh(*args: str) -> str:
    return command("gh", *args)


def commit(message: str, *paths: str) -> str:
    git("add", "--", *paths)
    git("commit", "-m", message, "-m", "Assisted-by: Codex:GPT-6")
    return git("rev-parse", "HEAD")


def prepare(
    kind: str,
    source: Path,
    claim_id: str,
    recorded_at: str,
    run_url: str,
    request: dict | None = None,
) -> None:
    root = Path.cwd()
    path = f"claims/{claim_id}"
    if kind == "submit":
        registry.accept(root, source / "record.json")
        snapshot = commit(f"feat: register claim {claim_id}", ".gitattributes", path)
        dates.save(
            root / path,
            registry.read_claim(root / path),
            recorded_at,
            snapshot,
            run_url,
        )
        commit(f"chore: record submission date {claim_id}", f"{path}/date.json")
    else:
        registry.disclose(root, claim_id, request["proof_url"], request["salt"])
        commit(f"feat: disclose claim {claim_id}", path)


def check_existing(
    kind: str, claim_id: str, source: Path, request: dict | None = None
) -> None:
    directory = registry.location(Path.cwd(), claim_id)
    data = registry.read_claim(directory)
    if kind == "submit":
        if data != (source / "record.json").read_bytes():
            raise ValueError("existing branch has a different claim")
        if dates.read(directory, data) is None:
            raise ValueError("existing submission branch has no date")
    else:
        value = disclosure.read(directory, data)
        if any(value[key] != request[key] for key in ("proof_url", "salt")):
            raise ValueError("existing branch has a different disclosure")


def process(kind: str, event: dict, repo: str, run_id: str) -> str:
    if event["action"] != "opened" or event["repository"]["full_name"] != repo:
        raise ValueError("expected a newly opened issue in this repository")
    issue = event["issue"]
    base = event["repository"]["default_branch"]
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    with TemporaryDirectory() as temporary:
        source = Path(temporary)
        body = issue.get("body") or ""
        request = submissions.disclosure_request(body) if kind == "disclose" else None
        claim_id = (
            request["claim_id"] if request else submissions.download(body, source)
        )
        directory = registry.location(Path.cwd(), claim_id) if request else source
        public = record.load_record(record.read_record(directory / "record.json"))
        if public["authors"][0].lower() != issue["user"]["login"].lower():
            raise ValueError("record author must match the submitting GitHub account")
        branch = f"{kind}/{claim_id}"
        existing = gh(
            "pr",
            "list",
            "--repo",
            repo,
            "--head",
            branch,
            "--state",
            "all",
            "--json",
            "url,isCrossRepository",
        )
        for pull in json.loads(existing):
            if not pull["isCrossRepository"]:
                return pull["url"]
        if git("ls-remote", "--heads", "origin", f"refs/heads/{branch}"):
            git("fetch", "origin", f"refs/heads/{branch}")
            git("switch", "--detach", "FETCH_HEAD")
            check_existing(kind, claim_id, source, request)
        else:
            recorded_at = gh(
                "api", f"repos/{repo}/actions/runs/{run_id}", "--jq", ".created_at"
            )
            git("switch", "-c", branch)
            prepare(kind, source, claim_id, recorded_at, run_url, request)
            git("push", "origin", f"HEAD:refs/heads/{branch}")
        verb = "Register" if kind == "submit" else "Disclose"
        body = source / "pr-body.md"
        body.write_text(
            "🤖 AI text below 🤖\n\n"
            f"{verb} claim `{claim_id}` from #{issue['number']}.\n\n"
            f"[Submission workflow]({run_url}).\n\nCloses #{issue['number']}.\n"
        )
        return gh(
            "pr",
            "create",
            "--repo",
            repo,
            "--base",
            base,
            "--head",
            branch,
            "--title",
            f"{verb} claim {claim_id[:12]}",
            "--body-file",
            str(body),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["submit", "disclose"])
    args = parser.parse_args()
    try:
        event = json.loads(
            files.read_limited(Path(os.environ["GITHUB_EVENT_PATH"]), 1024 * 1024)
        )
        url = process(
            args.kind,
            event,
            os.environ["GITHUB_REPOSITORY"],
            os.environ["GITHUB_RUN_ID"],
        )
        print(url)
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
            summary.write(f"[Review the claim PR]({url})\n")
    except subprocess.CalledProcessError as exc:
        parser.exit(1, f"claim: {exc.stderr}\n")
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f"claim: {exc}\n")


if __name__ == "__main__":
    main()
