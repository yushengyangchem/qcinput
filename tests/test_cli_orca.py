import sys

from qcinput.cli import main
from tests.helpers import write_example_files


def test_example_int_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path)
    output = tmp_path / "water_int.inp"

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config), "-o", str(output)],
    )

    exit_code = main()
    captured = capsys.readouterr()
    text = output.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output) in captured.out
    assert "! Opt Freq r2scan-3c D4 def2-mTZVPP" in text
    assert "* xyz 0 1" in text
    assert "O 0.000000 0.000000 0.000000" in text


def test_example_ts_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts")
    output = tmp_path / "water_ts.inp"

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config), "-o", str(output)],
    )

    exit_code = main()
    captured = capsys.readouterr()
    text = output.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output) in captured.out
    assert "! OptTS Freq r2scan-3c D4 def2-mTZVPP" in text
    assert "* xyz 0 1" in text


def test_example_sp_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="sp")
    output = tmp_path / "water_sp.inp"

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config), "-o", str(output)],
    )

    exit_code = main()
    captured = capsys.readouterr()
    text = output.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output) in captured.out
    assert "! SP r2scan-3c D4 def2-mTZVPP" in text
    assert "* xyz 0 1" in text


def test_default_config_path_uses_cwd(monkeypatch, tmp_path, capsys) -> None:
    xyz, _ = write_example_files(tmp_path)
    output = tmp_path / "water.inp"
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "-o", str(output)],
    )

    exit_code = main()
    captured = capsys.readouterr()
    text = output.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output) in captured.out
    assert "! Opt Freq r2scan-3c D4 def2-mTZVPP" in text
