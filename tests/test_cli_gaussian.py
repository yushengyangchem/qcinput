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
    assert "%chk=water.chk" in text
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
    assert "%chk=water.chk" in text
    assert "#p B3LYP/def2TZVP Opt=ModRedundant" in text
    assert "B 0 1 F" in text
    assert "--Link1--" in text
    assert (
        "#p B3LYP/def2TZVP Opt=(TS,CalcFC,NoEigenTest,NoFreeze) Freq Geom=AllCheck Guess=Read"
        in text
    )
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
    assert "%chk=water.chk" in text
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


def test_gaussian_ts_missing_constraint_atoms_errors(monkeypatch, tmp_path) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="gaussian")
    config_text = config.read_text(encoding="utf-8").replace(
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n'
        "constraint_atoms = [[0, 1]]\n",
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n',
        1,
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
        raise AssertionError("Expected SystemExit for incomplete gaussian ts config.")

    assert "constraint_atoms" in message or "modredundant" in message


def test_gaussian_ts_supports_multiple_constraint_pairs(
    monkeypatch, tmp_path, capsys
) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="gaussian")
    config_text = config.read_text(encoding="utf-8").replace(
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n'
        "constraint_atoms = [[0, 1]]\n",
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n'
        "constraint_atoms = [[0, 1], [2, 3]]\n",
        1,
    )
    config.write_text(config_text, encoding="utf-8")
    output = tmp_path / "water_ts_multi_constraints.gjf"

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
    assert "B 0 1 F" in text
    assert "B 2 3 F" in text


def test_gaussian_ts_legacy_modredundant_still_supported(
    monkeypatch, tmp_path, capsys
) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="gaussian")
    config_text = config.read_text(encoding="utf-8").replace(
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n'
        "constraint_atoms = [[0, 1]]\n",
        '[gaussian.task.ts]\nstep1_route = ["Opt=ModRedundant"]\n'
        'modredundant = ["B 0 1 F", "B 2 3 F"]\n',
        1,
    )
    config.write_text(config_text, encoding="utf-8")
    output = tmp_path / "water_ts_legacy_modredundant.gjf"

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
    assert "B 0 1 F" in text
    assert "B 2 3 F" in text


def test_gaussian_extra_keywords_applied_to_int_and_ts(
    monkeypatch, tmp_path, capsys
) -> None:
    xyz, config = write_example_files(tmp_path, kind="int", engine="gaussian")
    config_text = config.read_text(encoding="utf-8").replace(
        'method_basis = "B3LYP/def2TZVP"',
        'method_basis = "B3LYP/def2TZVP"\nextra_keywords = ["SCF=Tight", "Int=UltraFine"]',
        1,
    )
    config.write_text(config_text, encoding="utf-8")

    output_int = tmp_path / "water_extra_int.gjf"
    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config), "-o", str(output_int)],
    )
    exit_code = main()
    captured = capsys.readouterr()
    text_int = output_int.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output_int) in captured.out
    assert "#P B3LYP/def2TZVP Opt Freq SCF=Tight Int=UltraFine" in text_int

    config_ts_text = config.read_text(encoding="utf-8").replace(
        'kind = "int"', 'kind = "ts"', 1
    )
    config.write_text(config_ts_text, encoding="utf-8")
    output_ts = tmp_path / "water_extra_ts.gjf"
    monkeypatch.setattr(
        sys,
        "argv",
        ["qcinput", str(xyz), "--config", str(config), "-o", str(output_ts)],
    )
    exit_code = main()
    captured = capsys.readouterr()
    text_ts = output_ts.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(output_ts) in captured.out
    assert "#p B3LYP/def2TZVP Opt=ModRedundant SCF=Tight Int=UltraFine" in text_ts
    assert (
        "#p B3LYP/def2TZVP Opt=(TS,CalcFC,NoEigenTest,NoFreeze) Freq Geom=AllCheck "
        "Guess=Read SCF=Tight Int=UltraFine" in text_ts
    )
