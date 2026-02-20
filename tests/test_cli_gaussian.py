import sys

from qcinput.cli import main
from tests.helpers import write_example_files


def test_example_gaussian_int_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="int", engine="gaussian")
    output = tmp_path / "water_int.gjf"

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
    assert "#P B3LYP/def2TZVP Opt Freq" in text
    assert "0 1" in text


def test_example_gaussian_ts_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="gaussian")
    output = tmp_path / "water_ts.gjf"

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
    assert "#P B3LYP/def2TZVP OptTS Freq" in text
    assert "0 1" in text


def test_example_gaussian_sp_generation(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="sp", engine="gaussian")
    output = tmp_path / "water_sp.gjf"

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
    assert "%NProcShared=8" in text
    assert "%Mem=8GB" in text
    assert "#P B3LYP/def2TZVP SP" in text
    assert "0 1" in text


def test_gaussian_default_output_suffix(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="sp", engine="gaussian")
    expected_output = tmp_path / "water.gjf"

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config)],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(expected_output) in captured.out
    assert expected_output.exists()


def test_gaussian_missing_method_basis_errors(monkeypatch, tmp_path) -> None:
    xyz, config = write_example_files(tmp_path, kind="sp", engine="gaussian")
    config_text = config.read_text(encoding="utf-8").replace(
        'method_basis = "B3LYP/def2TZVP"\n', "", 1
    )
    config.write_text(config_text, encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config)],
    )

    try:
        main()
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected SystemExit for missing gaussian.method_basis.")

    assert "method_basis" in message
