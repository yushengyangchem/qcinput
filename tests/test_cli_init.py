import sys

from qcinput.cli import main


def test_init_config_creates_default_file(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    expected = tmp_path / "qcinput.toml"

    monkeypatch.setattr(sys, "argv", ["qcinput", "init-config"])
    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(expected) in captured.out
    assert expected.exists()
    text = expected.read_text(encoding="utf-8")
    assert "[qcinput]" in text
    assert "[orca]" in text
    assert "[gaussian]" in text


def test_init_config_errors_if_exists_without_force(monkeypatch, tmp_path) -> None:
    config = tmp_path / "qcinput.toml"
    config.write_text("already here\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["qcinput", "init-config"])

    try:
        main()
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected SystemExit when config already exists.")

    assert "already exists" in message
    assert "--force" in message


def test_init_config_force_overwrites_existing_file(
    monkeypatch, tmp_path, capsys
) -> None:
    config = tmp_path / "qcinput.toml"
    config.write_text("old\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", ["qcinput", "init-config", "--force"])
    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(config) in captured.out
    assert "[qcinput]" in config.read_text(encoding="utf-8")


def test_missing_config_error_mentions_init_config(monkeypatch, tmp_path) -> None:
    xyz = tmp_path / "water.xyz"
    xyz.write_text(
        "\n".join(
            [
                "3",
                "water molecule",
                "O 0.000000 0.000000 0.000000",
                "H 0.757000 0.586000 0.000000",
                "H -0.757000 0.586000 0.000000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["qcinput", str(xyz)])

    try:
        main()
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected SystemExit when config is missing.")

    assert "init-config" in message


def test_main_help_shows_init_config(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["qcinput", "--help"])
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert "init-config" in captured.out
