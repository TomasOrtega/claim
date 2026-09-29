import pytest
from test_dates import DATE, RUN
from test_git_registry import git

from claim import cli, dates, record, registry


@pytest.fixture
def pushed(accepted):
    root, claim_id = accepted
    git(root, "init", "-b", "main")
    git(root, "add", ".")
    git(root, "commit", "-m", "accept claim")
    commit = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    return root, claim_id, commit


def test_date_pushed_claim_once(pushed):
    root, claim_id, commit = pushed
    assert dates.record_push(root, commit, DATE, RUN) == 1
    directory = registry.location(root, claim_id)
    saved = (directory / "date.json").read_bytes()
    assert dates.record_push(root, commit, "2026-10-01T00:00:00Z", RUN) == 0
    assert (directory / "date.json").read_bytes() == saved


def test_later_claim_is_not_backdated(pushed):
    root, claim_id, commit = pushed
    original = registry.read_claim(registry.location(root, claim_id))
    data = record.load_record(original) | {"authors": ["Later author"]}
    data = record.dump_record(data)
    later = registry.location(root, record.record_id(data))
    later.mkdir(parents=True)
    (later / "record.json").write_bytes(data)
    git(root, "add", ".")
    git(root, "commit", "-m", "later submission")
    dates.record_push(root, commit, DATE, RUN)
    assert not (later / "date.json").exists()


def test_changed_pushed_record(pushed):
    root, claim_id, commit = pushed
    path = registry.location(root, claim_id) / "record.json"
    path.write_bytes(b" " + path.read_bytes())
    with pytest.raises(ValueError, match="pushed record"):
        dates.record_push(root, commit, DATE, RUN)


def test_date_command(pushed, capsys):
    root, _, commit = pushed
    assert cli.main(["date-claims", str(root), commit, DATE, RUN]) == 0
    assert capsys.readouterr().out.strip() == "1"


def test_disclosure_preserves_claim_date(pushed, published):
    root, claim_id, commit = pushed
    dates.record_push(root, commit, DATE, RUN)
    path = registry.location(root, claim_id) / "date.json"
    original = path.read_bytes()
    registry.disclose(root, claim_id, *published)
    git(root, "add", ".")
    git(root, "commit", "-m", "disclose claim")
    commit = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    assert dates.record_push(root, commit, "2026-10-01T00:00:00Z", RUN) == 0
    assert path.read_bytes() == original


def add_claim(root, author):
    source = root / "incoming.json"
    source.write_bytes(record.dump_record(record.build_record("a" * 64, [author])))
    claim_id = registry.accept(root, source)
    source.unlink()
    git(root, "add", ".")
    git(root, "commit", "-m", "add claim")
    return claim_id, git(root, "rev-parse", "HEAD").stdout.decode().strip()


def test_date_scan_reads_only_new_records(pushed, monkeypatch):
    root, original_id, _ = pushed
    claim_id, commit = add_claim(root, "Bob")
    calls = []
    original = dates.git

    def tracked(root, *args):
        calls.append(args)
        return original(root, *args)

    monkeypatch.setattr(dates, "git", tracked)
    assert dates.record_push(root, commit, DATE, RUN) == 1
    assert len([args for args in calls if args[0] == "show"]) == 1
    assert not (registry.location(root, original_id) / "date.json").exists()
    assert (registry.location(root, claim_id) / "date.json").exists()


def test_date_push_includes_every_commit_in_range(pushed):
    root, original_id, before = pushed
    first, _ = add_claim(root, "Bob")
    second, commit = add_claim(root, "Carol")
    assert dates.record_push(root, commit, DATE, RUN, before=before) == 2
    for claim_id in (first, second):
        assert (registry.location(root, claim_id) / "date.json").exists()
    assert not (registry.location(root, original_id) / "date.json").exists()


def test_date_merge_compares_first_parent(pushed):
    root, original_id, _ = pushed
    git(root, "switch", "-c", "submission")
    claim_id, _ = add_claim(root, "Bob")
    git(root, "switch", "main")
    git(root, "merge", "--no-ff", "submission", "-m", "merge claim")
    commit = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    assert dates.record_push(root, commit, DATE, RUN) == 1
    assert (registry.location(root, claim_id) / "date.json").exists()
    assert not (registry.location(root, original_id) / "date.json").exists()


def test_initial_branch_push_dates_all_new_records(pushed):
    root, _, _ = pushed
    _, commit = add_claim(root, "Bob")
    assert dates.record_push(root, commit, DATE, RUN, before="0" * 40) == 2


def test_invalid_before_commit(pushed):
    root, _, commit = pushed
    with pytest.raises(ValueError, match="invalid previous commit"):
        dates.record_push(root, commit, DATE, RUN, before="--all")


def test_date_range_in_shallow_checkout(pushed, tmp_path):
    root, original_id, before = pushed
    first, _ = add_claim(root, "Bob")
    second, commit = add_claim(root, "Carol")
    checkout = tmp_path / "shallow"
    git(root, "clone", "--no-local", "--depth=1", root, checkout)
    git(checkout, "fetch", "--no-tags", "--depth=2", "origin", commit)
    git(checkout, "fetch", "--no-tags", "--depth=1", "origin", before)
    assert dates.record_push(checkout, commit, DATE, RUN, before=before) == 2
    assert (
        git(checkout, "rev-parse", "--is-shallow-repository").stdout.strip() == b"true"
    )
    assert not (registry.location(checkout, original_id) / "date.json").exists()
    for claim_id in (first, second):
        assert (registry.location(checkout, claim_id) / "date.json").exists()


def test_record_in_wrong_hash_bucket_is_rejected(pushed):
    root, claim_id, _ = pushed
    directory = registry.location(root, claim_id)
    wrong_prefix = "01" if claim_id[:2] == "00" else "00"
    target = root / "claims" / wrong_prefix / claim_id[2:4] / claim_id
    target.parent.mkdir(parents=True, exist_ok=True)
    directory.rename(target)
    git(root, "add", ".")
    git(root, "commit", "-m", "move claim to wrong bucket")
    commit = git(root, "rev-parse", "HEAD").stdout.decode().strip()
    with pytest.raises(ValueError, match="invalid claim path"):
        dates.record_push(root, commit, DATE, RUN)
