from pathlib import Path


def write_example_files(
    tmp_path: Path, *, kind: str = "int", engine: str = "orca"
) -> tuple[Path, Path]:
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
    config = tmp_path / "qcinput.toml"
    config.write_text(
        "\n".join(
            [
                "[molecule]",
                "charge = 0",
                "multiplicity = 1",
                "",
                "[orca]",
                "nprocs = 8",
                "maxcore = 4000",
                "",
                "[qcinput]",
                f'engine = "{engine}"',
                f'kind = "{kind}"',
                "",
                "[orca.task.int]",
                'base_keywords = ["B3LYP", "def2-TZVP"]',
                'keywords = ["Opt", "Freq"]',
                "",
                "[orca.task.ts]",
                'base_keywords = ["B3LYP", "def2-TZVP"]',
                'step1_keywords = ["Opt"]',
                'step2_keywords = ["OptTS", "Freq"]',
                "constraint_atoms = [[0, 1]]",
                "calc_hess = true",
                "",
                "[orca.task.sp]",
                'base_keywords = ["B3LYP", "def2-TZVP"]',
                'keywords = ["SP"]',
                "",
                "[gaussian]",
                "nprocshared = 8",
                'mem = "8GB"',
                "",
                "[gaussian.task.int]",
                'base_keywords = ["B3LYP/def2TZVP"]',
                'route = ["Opt", "Freq"]',
                "",
                "[gaussian.task.ts]",
                'base_keywords = ["B3LYP/def2TZVP"]',
                'step1_route = ["Opt=ModRedundant"]',
                "constraint_atoms = [[0, 1]]",
                'step2_route = ["Opt=(TS,CalcFC,NoEigenTest,NoFreeze)", "Freq", "Geom=AllCheck", "Guess=Read"]',
                "",
                "[gaussian.task.sp]",
                'base_keywords = ["B3LYP/def2TZVP"]',
                'route = ["SP"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return xyz, config
