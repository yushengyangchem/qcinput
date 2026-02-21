import argparse
import sys
from pathlib import Path

from qcinput import __homepage__, __version__
from qcinput.config import default_config_path, default_config_toml, load_config
from qcinput.gaussian import render_gaussian_input
from qcinput.orca import render_orca_input
from qcinput.xyz import load_xyz_text


def _add_generate_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("xyz", type=Path, help="Path to an XYZ file.")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=default_config_path(),
        help="Path to TOML config file. Default: ./qcinput.toml",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path. Default: <xyz_stem>.inp|.gjf by engine",
    )


def _add_init_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-k",
        "--kind",
        choices=("int", "ts", "sp"),
        default="int",
        help="Template kind to initialize. Choices: int, ts, sp.",
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
        description="Generate ORCA or Gaussian input files from XYZ structures.",
        epilog="Default behavior: `qcinput <path/to/structure.xyz>` is treated as `qcinput generate <path/to/structure.xyz>`.",
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
        help="Generate an input file from an XYZ structure.",
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
        xyz_text = load_xyz_text(args.xyz)
        config = load_config(args.config)
        default_suffix = ".inp" if config.engine == "orca" else ".gjf"
        out_path = args.output or args.xyz.with_name(f"{args.xyz.stem}{default_suffix}")
        if config.engine == "orca":
            inp_text = render_orca_input(
                xyz_text=xyz_text,
                config=config,
                source_xyz_name=args.xyz.name,
            )
        else:
            inp_text = render_gaussian_input(
                xyz_text=xyz_text,
                config=config,
                source_xyz_name=args.xyz.name,
            )
        out_path.write_text(inp_text, encoding="utf-8")
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc

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
