from claim import cli


def test_accept_command(sealed, receipt, tmp_path, capsys):
    root = tmp_path / "registry"
    assert cli.main(["accept", str(root), str(sealed), str(receipt)]) == 0
    claim_id = capsys.readouterr().out.strip()
    assert (root / "claims" / claim_id / "record.json").read_bytes() == (
        sealed / "record.json"
    ).read_bytes()
