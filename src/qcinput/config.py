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
    orca_extra_keywords: tuple[str, ...] = ()
    orca_smd: bool = False
    orca_smd_solvent: str = "toluene"
    nprocshared: int | None = None
    mem: str | None = None
    method_basis: str | None = None
    gaussian_extra_keywords: tuple[str, ...] = ()
    orca_ts_step1_keywords: tuple[str, ...] = ()
    orca_ts_step2_keywords: tuple[str, ...] = ()
    orca_ts_constraint_atoms: tuple[tuple[int, int], ...] = ()
    orca_ts_step1_nprocs: int | None = None
    orca_ts_step1_maxcore: int | None = None
    orca_ts_step2_nprocs: int | None = None
    orca_ts_step2_maxcore: int | None = None
    orca_ts_calc_hess: bool | None = None
    gaussian_ts_step1_route: tuple[str, ...] = ()
    gaussian_ts_modredundant: tuple[str, ...] = ()
    gaussian_ts_step2_route: tuple[str, ...] = ()


def default_config_path() -> Path:
    env_path = os.environ.get("QCINPUT_CONFIG")
    if env_path:
        return Path(env_path).expanduser()
    return Path.cwd() / "qcinput.toml"


def _task_keywords(kind: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if kind == "int":
        return ("Opt", "Freq"), ("Opt", "Freq")
    if kind == "sp":
        return ("SP",), ("SP",)
    raise ValueError("Config kind must be one of: int, ts, sp.")


def default_config_toml(kind: str = "int") -> str:
    if kind == "ts":
        return """[qcinput]
engine = "orca" # "orca" or "gaussian"
kind = "ts"

[molecule]
charge = 0
multiplicity = 1

[orca]
nprocs = 8
maxcore = 4000
base_keywords = ["r2scan-3c"]
extra_keywords = []
smd = false
smd_solvent = "toluene"

[orca.task.ts]
step1_keywords = ["Opt"]
step2_keywords = ["OptTS", "Freq"]
constraint_atoms = [[0, 1]]
step1_nprocs = 36
step1_maxcore = 3555
step2_nprocs = 16
step2_maxcore = 8000
calc_hess = true

[gaussian]
nprocshared = 8
mem = "32GB"
method_basis = "B3LYP/def2SVP"
extra_keywords = []

[gaussian.task.ts]
step1_route = ["Opt=ModRedundant"]
constraint_atoms = [[0, 1]]
step2_route = ["Opt=(TS,CalcFC,NoEigenTest,NoFreeze)", "Freq", "Geom=AllCheck", "Guess=Read"]
"""

    orca_keywords, gaussian_route = _task_keywords(kind)
    orca_keywords_toml = ", ".join(f'"{kw}"' for kw in orca_keywords)
    gaussian_route_toml = ", ".join(f'"{kw}"' for kw in gaussian_route)
    return f"""[qcinput]
engine = "orca" # "orca" or "gaussian"
kind = "{kind}"

[molecule]
charge = 0
multiplicity = 1

[orca]
nprocs = 8
maxcore = 4000
base_keywords = ["r2scan-3c"]
extra_keywords = []
smd = false
smd_solvent = "toluene"

[orca.task.{kind}]
keywords = [{orca_keywords_toml}]

[gaussian]
nprocshared = 8
mem = "32GB"
method_basis = "B3LYP/def2SVP"
extra_keywords = []

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


def _as_optional_keyword_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    if key not in data:
        return ()
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError(f"Config key '{key}' must be a string list.")
    return tuple(value)


def _as_optional_bool(data: dict[str, Any], key: str, *, default: bool) -> bool:
    if key not in data:
        return default
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"Config key '{key}' must be a boolean.")
    return value


def _as_optional_nonempty_str(data: dict[str, Any], key: str, *, default: str) -> str:
    if key not in data:
        return default
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Config key '{key}' must be a non-empty string.")
    return value


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


def _as_nonempty_str_or_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return (value,)
    if (
        isinstance(value, list)
        and value
        and all(isinstance(v, str) and v.strip() for v in value)
    ):
        return tuple(value)
    raise ValueError(
        f"Config key '{key}' must be a non-empty string or non-empty string list."
    )


def _as_bool(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"Config key '{key}' must be a boolean.")
    return value


def _as_int_pair_list(data: dict[str, Any], key: str) -> tuple[tuple[int, int], ...]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Config key '{key}' must be [i, j] or [[i, j], [k, l], ...].")
    if len(value) == 2 and all(isinstance(v, int) for v in value):
        return ((value[0], value[1]),)
    pairs: list[tuple[int, int]] = []
    for idx, item in enumerate(value):
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not all(isinstance(v, int) for v in item)
        ):
            raise ValueError(
                f"Config key '{key}' contains invalid pair at index {idx}; "
                "each pair must be [i, j]."
            )
        pairs.append((item[0], item[1]))
    return tuple(pairs)


def _gaussian_modredundant_lines(
    task_section: dict[str, Any],
) -> tuple[str, ...]:
    if "constraint_atoms" in task_section:
        pairs = _as_int_pair_list(task_section, "constraint_atoms")
        return tuple(f"B {atom_i} {atom_j} F" for atom_i, atom_j in pairs)
    if "modredundant" in task_section:
        return _as_nonempty_str_or_list(task_section, "modredundant")
    raise ValueError(
        "Gaussian ts config requires either 'constraint_atoms' or 'modredundant'."
    )


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
    if kind == "ts":
        orca_smd = _as_optional_bool(orca, "smd", default=False)
        orca_smd_solvent = _as_optional_nonempty_str(
            orca, "smd_solvent", default="toluene"
        )
        if orca_smd and not orca_smd_solvent:
            raise ValueError("Config key 'orca.smd_solvent' must be set when smd=true.")
        return QCInputConfig(
            engine="orca",
            kind=kind,
            charge=_as_int(molecule, "charge"),
            multiplicity=_as_int(molecule, "multiplicity"),
            task_keywords=(),
            nprocs=_as_int(orca, "nprocs"),
            maxcore=_as_int(orca, "maxcore"),
            base_keywords=_as_keyword_list(orca, "base_keywords"),
            orca_extra_keywords=_as_optional_keyword_list(orca, "extra_keywords"),
            orca_smd=orca_smd,
            orca_smd_solvent=orca_smd_solvent,
            orca_ts_step1_keywords=_as_keyword_list(task_section, "step1_keywords"),
            orca_ts_step2_keywords=_as_keyword_list(task_section, "step2_keywords"),
            orca_ts_constraint_atoms=_as_int_pair_list(
                task_section, "constraint_atoms"
            ),
            orca_ts_step1_nprocs=_as_int(task_section, "step1_nprocs"),
            orca_ts_step1_maxcore=_as_int(task_section, "step1_maxcore"),
            orca_ts_step2_nprocs=_as_int(task_section, "step2_nprocs"),
            orca_ts_step2_maxcore=_as_int(task_section, "step2_maxcore"),
            orca_ts_calc_hess=_as_bool(task_section, "calc_hess"),
        )
    orca_smd = _as_optional_bool(orca, "smd", default=False)
    orca_smd_solvent = _as_optional_nonempty_str(orca, "smd_solvent", default="toluene")
    if orca_smd and not orca_smd_solvent:
        raise ValueError("Config key 'orca.smd_solvent' must be set when smd=true.")
    return QCInputConfig(
        engine="orca",
        kind=kind,
        charge=_as_int(molecule, "charge"),
        multiplicity=_as_int(molecule, "multiplicity"),
        task_keywords=_as_keyword_list(task_section, "keywords"),
        nprocs=_as_int(orca, "nprocs"),
        maxcore=_as_int(orca, "maxcore"),
        base_keywords=_as_keyword_list(orca, "base_keywords"),
        orca_extra_keywords=_as_optional_keyword_list(orca, "extra_keywords"),
        orca_smd=orca_smd,
        orca_smd_solvent=orca_smd_solvent,
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
    if kind == "ts":
        return QCInputConfig(
            engine="gaussian",
            kind=kind,
            charge=_as_int(molecule, "charge"),
            multiplicity=_as_int(molecule, "multiplicity"),
            task_keywords=(),
            nprocshared=_as_int(gaussian, "nprocshared"),
            mem=_as_nonempty_str(gaussian, "mem"),
            method_basis=_as_nonempty_str(gaussian, "method_basis"),
            gaussian_extra_keywords=_as_optional_keyword_list(
                gaussian, "extra_keywords"
            ),
            gaussian_ts_step1_route=_as_keyword_list(task_section, "step1_route"),
            gaussian_ts_modredundant=_gaussian_modredundant_lines(task_section),
            gaussian_ts_step2_route=_as_keyword_list(task_section, "step2_route"),
        )
    return QCInputConfig(
        engine="gaussian",
        kind=kind,
        charge=_as_int(molecule, "charge"),
        multiplicity=_as_int(molecule, "multiplicity"),
        task_keywords=_as_keyword_list(task_section, "route"),
        nprocshared=_as_int(gaussian, "nprocshared"),
        mem=_as_nonempty_str(gaussian, "mem"),
        method_basis=_as_nonempty_str(gaussian, "method_basis"),
        gaussian_extra_keywords=_as_optional_keyword_list(gaussian, "extra_keywords"),
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
