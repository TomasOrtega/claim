from claim import cli


def test_bundle_command(accepted, disclosed, tmp_path):
    root, claim_id = accepted
    cli.main(["accept-disclosure", str(root), claim_id, str(disclosed)])
    assert cli.main(["withdraw", str(root), claim_id]) == 0
    assert (
        cli.main(["export-bundle", str(root), claim_id, str(tmp_path / "bundle")]) == 0
    )
    assert cli.main(["verify", str(tmp_path / "bundle")]) == 0


def test_disclosure_command(accepted, disclosed):
    root, claim_id = accepted
    assert cli.main(["accept-disclosure", str(root), claim_id, str(disclosed)]) == 0
    assert (root / "claims" / claim_id / "disclosure" / "proof").exists()


def test_export_command(accepted, tmp_path):
    root, _ = accepted
    output = tmp_path / "public"
    assert cli.main(["export-index", str(root), str(output)]) == 0
    assert (output / "index.html").exists()


def test_accept_command(sealed, tmp_path, capsys):
    root = tmp_path / "registry"
    assert cli.main(["accept", str(root), str(sealed / "record.json")]) == 0
    claim_id = capsys.readouterr().out.strip()
    assert (root / "claims" / claim_id / "record.json").read_bytes() == (
        sealed / "record.json"
    ).read_bytes()
