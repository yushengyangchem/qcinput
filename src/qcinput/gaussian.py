from pathlib import Path

from qcinput import __generator_banner__
from qcinput.config import QCInputConfig


def render_gaussian_input(
    *,
    xyz_text: str,
    config: QCInputConfig,
    source_structure_name: str,
) -> str:
    if config.nprocshared is None or config.mem is None or config.method_basis is None:
        raise ValueError("Gaussian config is incomplete.")
    chk_name = f"{Path(source_structure_name).stem}.chk"
    route = " ".join(
        (config.method_basis, *config.task_keywords, *config.gaussian_extra_keywords)
    )
    lines = [
        f"%chk={chk_name}",
        f"%NProcShared={config.nprocshared}",
        f"%Mem={config.mem}",
        f"#P {route}",
        "",
        __generator_banner__,
        "",
        f"{config.charge} {config.multiplicity}",
        xyz_text,
        "",
        "",
        "",
    ]
    return "\n".join(lines)


def render_gaussian_two_step_ts_input(
    *,
    xyz_text: str,
    config: QCInputConfig,
    source_structure_name: str,
) -> str:
    if config.nprocshared is None or config.mem is None or config.method_basis is None:
        raise ValueError("Gaussian config is incomplete.")
    if (
        not config.gaussian_ts_step1_route
        or not config.gaussian_ts_modredundant
        or not config.gaussian_ts_step2_route
    ):
        raise ValueError("Gaussian ts config is incomplete.")

    chk_name = f"{Path(source_structure_name).stem}.chk"
    step1_route = " ".join(
        (
            config.method_basis,
            *config.gaussian_ts_step1_route,
            *config.gaussian_extra_keywords,
        )
    )
    step2_route = " ".join(
        (
            config.method_basis,
            *config.gaussian_ts_step2_route,
            *config.gaussian_extra_keywords,
        )
    )
    lines = [
        f"%chk={chk_name}",
        f"%nprocshared={config.nprocshared}",
        f"%mem={config.mem}",
        f"#p {step1_route}",
        "",
        __generator_banner__,
        "",
        f"{config.charge} {config.multiplicity}",
        xyz_text,
        "",
    ]
    lines.extend(config.gaussian_ts_modredundant)
    lines.extend(
        [
            "",
            "--Link1--",
            f"%chk={chk_name}",
            f"%nprocshared={config.nprocshared}",
            f"%mem={config.mem}",
            f"#p {step2_route}",
            "",
            "",
        ]
    )
    return "\n".join(lines)
