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
    assert "! Opt Freq r2scan-3c D4 def2-mTZVPP NoPop" in text
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
    assert "! r2scan-3c D4 def2-mTZVPP Opt NoPop" in text
    assert "{B 0 1 C}" in text
    assert "%compound" in text
    assert "  New_Step" in text
    assert "  Step_End" in text
    assert "! r2scan-3c D4 def2-mTZVPP OptTS Freq NoPop" in text
    assert "  calc_hess true" in text
    assert "* xyzfile 0 1 water_ts_Compound_1.xyz *" in text
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
    assert "! SP r2scan-3c D4 def2-mTZVPP NoPop" in text
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
    assert "! Opt Freq r2scan-3c D4 def2-mTZVPP NoPop" in text


def test_orca_ts_generation_from_toml(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="orca")
    config_text = config.read_text(encoding="utf-8")
    config_text = config_text.replace(
        "constraint_atoms = [[0, 1]]", "constraint_atoms = [[1, 2]]", 1
    )
    config_text = config_text.replace("calc_hess = true", "calc_hess = false", 1)
    config.write_text(config_text, encoding="utf-8")
    output = tmp_path / "water_from_toml_ts.inp"

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
    assert "! r2scan-3c D4 def2-mTZVPP Opt NoPop" in text
    assert "{B 1 2 C}" in text
    assert "%maxcore 4000" in text
    assert "  nprocs 8" in text
    assert "! r2scan-3c D4 def2-mTZVPP OptTS Freq NoPop" in text
    assert "%maxcore 6000" not in text
    assert "  nprocs 12" not in text
    assert "  calc_hess false" in text


def test_orca_ts_multiple_constraint_pairs(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="ts", engine="orca")
    config_text = config.read_text(encoding="utf-8").replace(
        "constraint_atoms = [[0, 1]]", "constraint_atoms = [[0, 1], [2, 3]]", 1
    )
    config.write_text(config_text, encoding="utf-8")
    output = tmp_path / "water_multi_constraints.inp"

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
    assert "{B 0 1 C}" in text
    assert "{B 2 3 C}" in text


def test_orca_extra_keywords_applied_to_int_and_ts(
    monkeypatch, tmp_path, capsys
) -> None:
    xyz, config = write_example_files(tmp_path, kind="int", engine="orca")
    config_text = config.read_text(encoding="utf-8").replace(
        'base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]',
        'base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]\n'
        'extra_keywords = ["TightSCF", "NormalSCF"]',
        1,
    )
    config.write_text(config_text, encoding="utf-8")

    output_int = tmp_path / "water_extra_int.inp"
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
    assert "! Opt Freq r2scan-3c D4 def2-mTZVPP TightSCF NormalSCF NoPop" in text_int

    config_ts_text = config.read_text(encoding="utf-8").replace(
        'kind = "int"', 'kind = "ts"', 1
    )
    config.write_text(config_ts_text, encoding="utf-8")
    output_ts = tmp_path / "water_extra_ts.inp"
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
    assert "! r2scan-3c D4 def2-mTZVPP Opt TightSCF NormalSCF NoPop" in text_ts
    assert "! r2scan-3c D4 def2-mTZVPP OptTS Freq TightSCF NormalSCF NoPop" in text_ts


def test_orca_smd_applied_to_int_and_ts(monkeypatch, tmp_path, capsys) -> None:
    xyz, config = write_example_files(tmp_path, kind="int", engine="orca")
    config_text = config.read_text(encoding="utf-8").replace(
        'base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]',
        'base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]\n'
        "smd = true\n"
        'smd_solvent = "toluene"',
        1,
    )
    config.write_text(config_text, encoding="utf-8")

    output_int = tmp_path / "water_smd_int.inp"
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
    assert "%cpcm" in text_int
    assert "  SMD true" in text_int
    assert '  SMDsolvent "toluene"' in text_int

    config_ts_text = config.read_text(encoding="utf-8").replace(
        'kind = "int"', 'kind = "ts"', 1
    )
    config.write_text(config_ts_text, encoding="utf-8")
    output_ts = tmp_path / "water_smd_ts.inp"
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
    assert text_ts.count("%cpcm") == 2
    assert text_ts.count("  SMD true") == 2
    assert text_ts.count('  SMDsolvent "toluene"') == 2
