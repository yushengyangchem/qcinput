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
                'base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]',
                "",
                "[qcinput]",
                f'engine = "{engine}"',
                f'kind = "{kind}"',
                "",
                "[orca.task.int]",
                'keywords = ["Opt", "Freq"]',
                "",
                "[orca.task.ts]",
                'keywords = ["OptTS", "Freq"]',
                "",
                "[orca.task.sp]",
                'keywords = ["SP"]',
                "",
                "[gaussian]",
                "nprocshared = 8",
                'mem = "8GB"',
                'method_basis = "B3LYP/def2TZVP"',
                "",
                "[gaussian.task.int]",
                'route = ["Opt", "Freq"]',
                "",
                "[gaussian.task.ts]",
                'route = ["OptTS", "Freq"]',
                "",
                "[gaussian.task.sp]",
                'route = ["SP"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return xyz, config
