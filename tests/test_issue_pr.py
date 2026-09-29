import json
import subprocess
from io import BytesIO
from pathlib import Path

import pytest
from test_dates import DATE
from test_git_registry import git
from test_submissions import URL, disclosure_body

from claim import dates, issue_pr, record, registry, submissions, workflow

REPO = "example/registry"
LATER = "2026-10-01T00:00:00Z"


@pytest.fixture
def automation(tmp_path, monkeypatch):
    root, remote = tmp_path / "checkout", tmp_path / "remote.git"
    root.mkdir()
    git(root, "init", "-b", "main")
    (root / "README.md").write_text("Registry\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "initial registry")
    git(root, "clone", "--bare", root, remote)
    git(root, "remote", "add", "origin", remote)
    monkeypatch.chdir(root)
    monkeypatch.setenv("GIT_CONFIG_COUNT", "2")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "commit.gpgsign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_1", "false")
    state = {"prs": {}, "uploads": {}, "bodies": [], "fail": False}

    def gh(*args):
        if args[0] == "api":
            return DATE if args[1].endswith("/123") else LATER
        branch = args[args.index("--head") + 1]
        if args[:2] == ("pr", "list"):
            own = state["prs"].get(branch)
            foreign = state.get("foreign_pr")
            return json.dumps(
                ([{"url": foreign, "isCrossRepository": True}] if foreign else [])
                + ([{"url": own, "isCrossRepository": False}] if own else [])
            )
        assert args[:2] == ("pr", "create")
        assert args[args.index("--base") + 1] == "main"
        assert git(root, "ls-remote", "--heads", "origin", branch).stdout
        if state["fail"]:
            state["fail"] = False
            raise subprocess.CalledProcessError(1, ["gh"], stderr="temporary error")
        body = Path(args[args.index("--body-file") + 1]).read_text()
        state["bodies"].append(body)
        url = f"https://github.com/{REPO}/pull/{len(state['prs']) + 1}"
        state["prs"][branch] = url
        return url

    monkeypatch.setattr(issue_pr, "gh", gh)
    monkeypatch.setattr(
        submissions, "urlopen", lambda url, **kw: BytesIO(state["uploads"][url])
    )
    return root, state


def event(url, number=1):
    return {
        "action": "opened",
        "repository": {"full_name": REPO, "default_branch": "main"},
        "issue": {"number": number, "body": f"### Attachment\n\n[file]({url})"},
    }


def disclosure_event(claim_id, published, number=2):
    payload = event("", number)
    payload["issue"]["body"] = disclosure_body(claim_id, *published)
    return payload


def merge(root, branch):
    git(root, "switch", "main")
    git(root, "merge", "--no-ff", branch, "-m", "merge claim PR")
    git(root, "push", "origin", "main")


def test_submit_then_disclose_prs(automation, sealed, disclosed, published, tmp_path):
    root, state = automation
    data = (sealed / "record.json").read_bytes()
    claim_id = record.record_id(data)
    state["uploads"][URL] = data
    assert issue_pr.process("submit", event(URL), REPO, "123").endswith("/pull/1")
    directory = registry.location(root, claim_id)
    assert {p.name for p in directory.iterdir()} == {"record.json", "date.json"}
    saved = (directory / "date.json").read_bytes()
    date = json.loads(saved)
    assert date["recorded_at"] == DATE
    assert (
        git(root, "show", f"{date['commit']}:claims/{claim_id}/record.json").stdout
        == data
    )
    assert state["bodies"][0].startswith("🤖 AI text below 🤖\n")
    assert "Closes #1" in state["bodies"][0]
    merge(root, f"submit/{claim_id}")
    head = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    assert dates.record_push(root, head, LATER, date["run_url"]) == 0
    assert (directory / "date.json").read_bytes() == saved

    payload = disclosure_event(claim_id, published)
    assert issue_pr.process("disclose", payload, REPO, "124").endswith("/pull/2")
    assert (directory / "date.json").read_bytes() == saved
    assert set(
        git(root, "diff", "--name-only", "main...HEAD").stdout.decode().splitlines()
    ) == {f"claims/{claim_id}/disclosure.json", f"claims/{claim_id}/events/0001.json"}
    proof_hash = git(root, "hash-object", disclosed / "proof").stdout.decode().strip()
    assert proof_hash not in git(root, "rev-list", "--objects", "--all").stdout.decode()
    merge(root, f"disclose/{claim_id}")
    registry.bundle(root, claim_id, tmp_path / "bundle")
    assert (
        workflow.verify(tmp_path / "bundle") == record.load_record(data)["commitment"]
    )


def test_rerun_keeps_date_and_pr(automation, sealed):
    root, state = automation
    data = (sealed / "record.json").read_bytes()
    state["uploads"][URL] = data
    url = issue_pr.process("submit", event(URL), REPO, "123")
    branch = f"submit/{record.record_id(data)}"
    head = git(root, "rev-parse", branch).stdout
    git(root, "switch", "main")
    assert issue_pr.process("submit", event(URL, 3), REPO, "124") == url
    assert git(root, "rev-parse", branch).stdout == head
    assert len(state["prs"]) == 1


def test_fork_pr_does_not_replace_bot_pr(automation, sealed):
    _, state = automation
    state["uploads"][URL] = (sealed / "record.json").read_bytes()
    state["foreign_pr"] = f"https://github.com/{REPO}/pull/999"
    assert issue_pr.process("submit", event(URL), REPO, "123").endswith("/pull/1")
    assert len(state["prs"]) == 1


def test_retry_after_push_keeps_original_date(automation, sealed):
    root, state = automation
    data = (sealed / "record.json").read_bytes()
    state["uploads"][URL] = data
    state["fail"] = True
    with pytest.raises(subprocess.CalledProcessError):
        issue_pr.process("submit", event(URL), REPO, "123")
    original = (
        registry.location(root, record.record_id(data)) / "date.json"
    ).read_bytes()
    git(root, "switch", "main")
    assert issue_pr.process("submit", event(URL), REPO, "124").endswith("/pull/1")
    assert (
        registry.location(root, record.record_id(data)) / "date.json"
    ).read_bytes() == original


def test_new_record_gets_new_date(automation, sealed):
    root, state = automation
    data = (sealed / "record.json").read_bytes()
    state["uploads"][URL] = data
    issue_pr.process("submit", event(URL), REPO, "123")
    git(root, "switch", "main")
    changed = record.dump_record(record.load_record(data) | {"authors": ["Bob"]})
    new_url = URL.replace("/123/", "/124/")
    state["uploads"][new_url] = changed
    issue_pr.process("submit", event(new_url, 2), REPO, "124")
    date = dates.read(registry.location(root, record.record_id(changed)), changed)
    assert date["recorded_at"] == LATER
    assert len(state["prs"]) == 2


def test_edited_issue_is_not_processed(automation):
    _, state = automation
    edited = event(URL) | {"action": "edited"}
    with pytest.raises(ValueError, match="newly opened issue"):
        issue_pr.process("submit", edited, REPO, "123")
    assert not state["prs"]


def test_invalid_disclosure_does_not_push(automation, sealed, disclosed, published):
    root, state = automation
    claim_id = registry.accept(root, sealed / "record.json")
    git(root, "add", ".")
    git(root, "commit", "-m", "register claim")
    git(root, "push", "origin", "main")
    (disclosed / "proof").write_bytes(b"wrong")
    before = git(root, "ls-remote", "origin").stdout
    with pytest.raises(ValueError, match="opening does not match"):
        issue_pr.process("disclose", disclosure_event(claim_id, published), REPO, "123")
    assert git(root, "ls-remote", "origin").stdout == before
    assert not state["prs"]


def test_workflow_entrypoint(automation, sealed, tmp_path, monkeypatch, capsys):
    _, state = automation
    state["uploads"][URL] = (sealed / "record.json").read_bytes()
    payload, summary = tmp_path / "event.json", tmp_path / "summary.md"
    payload.write_text(json.dumps(event(URL)))
    for name, value in {
        "GITHUB_EVENT_PATH": payload,
        "GITHUB_STEP_SUMMARY": summary,
        "GITHUB_REPOSITORY": REPO,
        "GITHUB_RUN_ID": "123",
    }.items():
        monkeypatch.setenv(name, str(value))
    monkeypatch.setattr("sys.argv", ["claim.issue_pr", "submit"])
    issue_pr.main()
    assert capsys.readouterr().out.strip() == f"https://github.com/{REPO}/pull/1"
    assert f"https://github.com/{REPO}/pull/1" in summary.read_text()


def test_disclosure_retry_keeps_verification(automation, sealed, published):
    root, state = automation
    claim_id = registry.accept(root, sealed / "record.json")
    git(root, "add", ".")
    git(root, "commit", "-m", "register claim")
    git(root, "push", "origin", "main")
    payload = disclosure_event(claim_id, published)
    state["fail"] = True
    with pytest.raises(subprocess.CalledProcessError):
        issue_pr.process("disclose", payload, REPO, "123")
    path = registry.location(root, claim_id) / "disclosure.json"
    original = path.read_bytes()
    git(root, "switch", "main")
    url = issue_pr.process("disclose", payload, REPO, "124")
    assert path.read_bytes() == original
    git(root, "switch", "main")
    assert issue_pr.process("disclose", payload, REPO, "124") == url
    assert len(state["prs"]) == 1
