from claim import cli


def test_export_command(accepted, tmp_path):
    root, _ = accepted
    output = tmp_path / "public"
    assert cli.main(["export-index", str(root), str(output)]) == 0
    assert (output / "index.html").exists()


def test_accept_command(sealed, receipt, tmp_path, capsys):
    root = tmp_path / "registry"
    assert cli.main(["accept", str(root), str(sealed), str(receipt)]) == 0
    claim_id = capsys.readouterr().out.strip()
    assert (root / "claims" / claim_id / "record.json").read_bytes() == (
        sealed / "record.json"
    ).read_bytes()
