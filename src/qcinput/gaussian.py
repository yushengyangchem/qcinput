from pathlib import Path

from qcinput import __generator_banner__
from qcinput.config import QCInputConfig


def render_gaussian_input(
    *,
    xyz_text: str,
    config: QCInputConfig,
    source_structure_name: str,
) -> str:
    if (
        config.nprocshared is None
        or config.mem is None
        or not config.gaussian_base_keywords
    ):
        raise ValueError("Gaussian config is incomplete.")
    chk_name = f"{Path(source_structure_name).stem}.chk"
    keywords = " ".join(
        (
            *config.gaussian_base_keywords,
            *config.task_keywords,
            *config.gaussian_extra_keywords,
        )
    )
    lines = [
        f"%chk={chk_name}",
        f"%NProcShared={config.nprocshared}",
        f"%Mem={config.mem}",
        f"#P {keywords}",
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
    if (
        config.nprocshared is None
        or config.mem is None
        or not config.gaussian_base_keywords
    ):
        raise ValueError("Gaussian config is incomplete.")
    if (
        not config.gaussian_ts_step1_keywords
        or not config.gaussian_ts_modredundant
        or not config.gaussian_ts_step2_keywords
    ):
        raise ValueError("Gaussian ts config is incomplete.")

    chk_name = f"{Path(source_structure_name).stem}.chk"
    step1_keywords = " ".join(
        (
            *config.gaussian_base_keywords,
            *config.gaussian_ts_step1_keywords,
            *config.gaussian_extra_keywords,
        )
    )
    step2_keywords = " ".join(
        (
            *config.gaussian_base_keywords,
            *config.gaussian_ts_step2_keywords,
            *config.gaussian_extra_keywords,
        )
    )
    lines = [
        f"%chk={chk_name}",
        f"%nprocshared={config.nprocshared}",
        f"%mem={config.mem}",
        f"#p {step1_keywords}",
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
            f"#p {step2_keywords}",
            "",
            "",
        ]
    )
    return "\n".join(lines)
