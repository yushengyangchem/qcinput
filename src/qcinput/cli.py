import argparse
import sys
from dataclasses import replace
from pathlib import Path

from qcinput import __homepage__, __version__
from qcinput.config import default_config_path, default_config_toml, load_config
from qcinput.gaussian import render_gaussian_input, render_gaussian_two_step_ts_input
from qcinput.orca import render_orca_input, render_orca_two_step_ts_input
from qcinput.structure import load_structure

SUPPORTED_STRUCTURE_SUFFIXES = (".xyz", ".gjf")


def _merge_keywords(*keyword_groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for group in keyword_groups:
        for kw in group:
            if kw not in merged:
                merged.append(kw)
    return tuple(merged)


def _add_generate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "structures",
        type=Path,
        nargs="*",
        help="Path(s) to structure file(s) (.xyz or .gjf).",
    )
    parser.add_argument(
        "--input-dir",
        dest="input_dirs",
        type=Path,
        action="append",
        default=[],
        help="Directory containing structure files (.xyz or .gjf). Can be passed multiple times.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=default_config_path(),
        help="Path to TOML config file. Default: ./qcinput.toml",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for a single input file. Default: <structure_stem>.inp|.gjf by engine",
    )
    output_group.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to write generated files into. Created automatically if needed.",
    )


def _collect_directory_structures(path: Path) -> list[Path]:
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_dir():
        raise ValueError(f"Input path is not a directory: {path}")
    return sorted(
        child
        for child in path.iterdir()
        if child.is_file() and child.suffix.lower() in SUPPORTED_STRUCTURE_SUFFIXES
    )


def _collect_structure_paths(args: argparse.Namespace) -> list[Path]:
    structure_paths = list(args.structures)
    for input_dir in args.input_dirs:
        structure_paths.extend(_collect_directory_structures(input_dir))
    if not structure_paths:
        raise ValueError(
            "No input structures provided. Pass one or more structure files, "
            "or use --input-dir with a directory containing .xyz/.gjf files."
        )
    return structure_paths


def _add_init_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-k",
        "--kind",
        choices=("int", "ts", "sp"),
        default="int",
        help="Default active kind in generated config. Choices: int, ts, sp.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=default_config_path(),
        help="Output TOML path. Default: ./qcinput.toml",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite the target file if it already exists.",
    )


def build_root_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qcinput",
        description="Generate ORCA or Gaussian input files from XYZ/GJF structures.",
        epilog="Default behavior: `qcinput <path/to/structure.xyz|.gjf>` is treated as `qcinput generate <path/to/structure.xyz|.gjf>`.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}\nHomepage: {__homepage__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate an input file from an XYZ/GJF structure.",
    )
    _add_generate_args(generate_parser)

    init_parser = subparsers.add_parser(
        "init-config",
        help="Write a starter qcinput.toml in the current directory.",
        description="Write a starter qcinput.toml in the current directory.",
    )
    _add_init_config_args(init_parser)
    return parser


def run_init_config(args: argparse.Namespace) -> int:
    path = args.output
    if path.exists() and not args.force:
        raise SystemExit(
            f"error: Config file already exists: {path}. Use --force to overwrite."
        )
    path.write_text(default_config_toml(args.kind), encoding="utf-8")
    print(path)
    return 0


def run_generate(args: argparse.Namespace) -> int:
    try:
        structure_paths = _collect_structure_paths(args)
        if len(structure_paths) > 1 and args.output is not None:
            raise ValueError(
                "--output can only be used with a single input structure. "
                "For multiple inputs, use each input stem or pass --output-dir."
            )

        if args.output_dir is not None:
            args.output_dir.mkdir(parents=True, exist_ok=True)

        out_paths: list[Path] = []
        base_config = load_config(args.config)
        for structure_path in structure_paths:
            structure = load_structure(structure_path)
            config = base_config
            if (
                structure.source_format == "gjf"
                and structure.charge is not None
                and structure.multiplicity is not None
            ):
                if (
                    config.charge != structure.charge
                    or config.multiplicity != structure.multiplicity
                ):
                    raise ValueError(
                        "GJF charge/multiplicity mismatch with config: "
                        f"gjf={structure.charge}/{structure.multiplicity}, "
                        f"config={config.charge}/{config.multiplicity}. "
                        "Please align [molecule] in config with the GJF file."
                    )
                config = replace(
                    config,
                    charge=structure.charge,
                    multiplicity=structure.multiplicity,
                )
            default_suffix = ".inp" if config.engine == "orca" else ".gjf"
            if args.output is not None:
                out_path = args.output
            elif args.output_dir is not None:
                out_path = args.output_dir / f"{structure_path.stem}{default_suffix}"
            else:
                out_path = structure_path.with_name(
                    f"{structure_path.stem}{default_suffix}"
                )

            if config.engine == "orca":
                if config.kind == "ts":
                    if not config.orca_ts_constraint_atoms:
                        raise ValueError("ORCA ts config is missing constraint_atoms.")
                    if (
                        config.nprocs is None
                        or config.maxcore is None
                        or config.orca_ts_calc_hess is None
                    ):
                        raise ValueError("ORCA ts config is incomplete.")
                    # ORCA compound task writes <input_stem>_Compound_1.xyz after step 1.
                    step2_xyzfile_name = f"{out_path.stem}_Compound_1.xyz"
                    inp_text = render_orca_two_step_ts_input(
                        xyz_text=structure.xyz_text,
                        step2_xyzfile_name=step2_xyzfile_name,
                        charge=config.charge,
                        multiplicity=config.multiplicity,
                        step1_keywords=_merge_keywords(
                            config.base_keywords,
                            config.orca_ts_step1_keywords,
                            config.orca_extra_keywords,
                        ),
                        step2_keywords=_merge_keywords(
                            config.base_keywords,
                            config.orca_ts_step2_keywords,
                            config.orca_extra_keywords,
                        ),
                        constraint_atom_pairs=config.orca_ts_constraint_atoms,
                        nprocs=config.nprocs,
                        maxcore=config.maxcore,
                        calc_hess=config.orca_ts_calc_hess,
                        smd=config.orca_smd,
                        smd_solvent=config.orca_smd_solvent,
                    )
                else:
                    inp_text = render_orca_input(
                        xyz_text=structure.xyz_text,
                        config=config,
                    )
            else:
                if config.kind == "ts":
                    inp_text = render_gaussian_two_step_ts_input(
                        xyz_text=structure.xyz_text,
                        config=config,
                        source_structure_name=structure_path.name,
                    )
                else:
                    inp_text = render_gaussian_input(
                        xyz_text=structure.xyz_text,
                        config=config,
                        source_structure_name=structure_path.name,
                    )
            out_path.write_text(inp_text, encoding="utf-8")
            out_paths.append(out_path)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    for out_path in out_paths:
        print(out_path)
    return 0


def main() -> int:
    argv = sys.argv[1:]
    parser = build_root_parser()
    if argv and argv[0] not in {
        "generate",
        "init-config",
        "-h",
        "--help",
        "-V",
        "--version",
    }:
        argv = ["generate", *argv]
    args = parser.parse_args(argv)
    if args.command == "init-config":
        return run_init_config(args)
    if args.command == "generate":
        return run_generate(args)
    parser.print_help()
    return 0
