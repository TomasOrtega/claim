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
    later.mkdir()
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
