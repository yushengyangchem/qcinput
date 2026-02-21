import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QCInputConfig:
    engine: str
    kind: str
    charge: int
    multiplicity: int
    task_keywords: tuple[str, ...]
    nprocs: int | None = None
    maxcore: int | None = None
    base_keywords: tuple[str, ...] = ()
    nprocshared: int | None = None
    mem: str | None = None
    method_basis: str | None = None


def default_config_path() -> Path:
    env_path = os.environ.get("QCINPUT_CONFIG")
    if env_path:
        return Path(env_path).expanduser()
    return Path.cwd() / "qcinput.toml"


def _task_keywords(kind: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if kind == "int":
        return ("Opt", "Freq"), ("Opt", "Freq")
    if kind == "ts":
        return ("OptTS", "Freq"), ("OptTS", "Freq")
    if kind == "sp":
        return ("SP",), ("SP",)
    raise ValueError("Config kind must be one of: int, ts, sp.")


def default_config_toml(kind: str = "int") -> str:
    orca_keywords, gaussian_route = _task_keywords(kind)
    orca_keywords_toml = ", ".join(f'"{kw}"' for kw in orca_keywords)
    gaussian_route_toml = ", ".join(f'"{kw}"' for kw in gaussian_route)
    return f"""[qcinput]
engine = "orca" # or "gaussian"
kind = "{kind}" # int | ts | sp

[molecule]
charge = 0
multiplicity = 1

[orca]
nprocs = 8
maxcore = 4000
base_keywords = ["r2scan-3c", "D4", "def2-mTZVPP"]

[orca.task.{kind}]
keywords = [{orca_keywords_toml}]

[gaussian]
nprocshared = 8
mem = "8GB"
method_basis = "B3LYP/def2TZVP"

[gaussian.task.{kind}]
route = [{gaussian_route_toml}]
"""


def _as_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Config key '{key}' must be an integer.")
    return value


def _as_keyword_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(v, str) for v in value)
    ):
        raise ValueError(f"Config key '{key}' must be a non-empty string list.")
    return tuple(value)


def _as_kind(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if value not in ("int", "ts", "sp"):
        raise ValueError("Config key 'qcinput.kind' must be 'int', 'ts', or 'sp'.")
    return value


def _as_engine(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if value not in ("orca", "gaussian"):
        raise ValueError("Config key 'qcinput.engine' must be 'orca' or 'gaussian'.")
    return value


def _as_nonempty_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Config key '{key}' must be a non-empty string.")
    return value


def _load_orca_config(
    *,
    raw: dict[str, Any],
    molecule: dict[str, Any],
    kind: str,
) -> QCInputConfig:
    orca = raw.get("orca")
    if not isinstance(orca, dict):
        raise ValueError("Missing [orca] table in config.")
    orca_task = orca.get("task")
    if not isinstance(orca_task, dict):
        raise ValueError("Missing [orca.task] table in config.")
    task_section = orca_task.get(kind)
    if not isinstance(task_section, dict):
        raise ValueError(f"Missing [orca.task.{kind}] table in config.")
    return QCInputConfig(
        engine="orca",
        kind=kind,
        charge=_as_int(molecule, "charge"),
        multiplicity=_as_int(molecule, "multiplicity"),
        task_keywords=_as_keyword_list(task_section, "keywords"),
        nprocs=_as_int(orca, "nprocs"),
        maxcore=_as_int(orca, "maxcore"),
        base_keywords=_as_keyword_list(orca, "base_keywords"),
    )


def _load_gaussian_config(
    *,
    raw: dict[str, Any],
    molecule: dict[str, Any],
    kind: str,
) -> QCInputConfig:
    gaussian = raw.get("gaussian")
    if not isinstance(gaussian, dict):
        raise ValueError("Missing [gaussian] table in config.")
    gaussian_task = gaussian.get("task")
    if not isinstance(gaussian_task, dict):
        raise ValueError("Missing [gaussian.task] table in config.")
    task_section = gaussian_task.get(kind)
    if not isinstance(task_section, dict):
        raise ValueError(f"Missing [gaussian.task.{kind}] table in config.")
    return QCInputConfig(
        engine="gaussian",
        kind=kind,
        charge=_as_int(molecule, "charge"),
        multiplicity=_as_int(molecule, "multiplicity"),
        task_keywords=_as_keyword_list(task_section, "route"),
        nprocshared=_as_int(gaussian, "nprocshared"),
        mem=_as_nonempty_str(gaussian, "mem"),
        method_basis=_as_nonempty_str(gaussian, "method_basis"),
    )


def load_config(path: Path) -> QCInputConfig:
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            "Run `qcinput init-config` or pass --config <path>."
        )
    content = path.read_bytes()
    raw = tomllib.loads(content.decode("utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a table.")

    qcinput = raw.get("qcinput")
    molecule = raw.get("molecule")
    if not isinstance(qcinput, dict):
        raise ValueError("Missing [qcinput] table in config.")
    if not isinstance(molecule, dict):
        raise ValueError("Missing [molecule] table in config.")
    engine = _as_engine(qcinput, "engine")
    kind = _as_kind(qcinput, "kind")
    if engine == "orca":
        return _load_orca_config(raw=raw, molecule=molecule, kind=kind)
    return _load_gaussian_config(raw=raw, molecule=molecule, kind=kind)
