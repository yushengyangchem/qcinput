from qcinput import __generator_banner__
from qcinput.config import QCInputConfig


def _with_nopop(keywords: tuple[str, ...]) -> str:
    if any(keyword.casefold() == "nopop" for keyword in keywords):
        return " ".join(keywords)
    return " ".join((*keywords, "NoPop"))


def render_orca_input(
    *,
    xyz_text: str,
    config: QCInputConfig,
) -> str:
    if config.nprocs is None or config.maxcore is None:
        raise ValueError("ORCA config is incomplete.")
    keywords = _with_nopop(
        (*config.task_keywords, *config.base_keywords, *config.orca_extra_keywords)
    )
    lines = [
        f"# {__generator_banner__}",
        f"! {keywords}",
        "%pal",
        f"  nprocs {config.nprocs}",
        "end",
        f"%maxcore {config.maxcore}",
    ]
    if config.orca_smd:
        lines.extend(
            [
                "%cpcm",
                "  SMD true",
                f'  SMDsolvent "{config.orca_smd_solvent}"',
                "end",
            ]
        )
    lines.extend(
        [
            f"* xyz {config.charge} {config.multiplicity}",
            xyz_text,
            "*",
            "",
        ]
    )
    return "\n".join(lines)


def render_orca_two_step_ts_input(
    *,
    xyz_text: str,
    step2_xyzfile_name: str,
    charge: int,
    multiplicity: int,
    step1_keywords: tuple[str, ...],
    step2_keywords: tuple[str, ...],
    constraint_atom_pairs: tuple[tuple[int, int], ...],
    nprocs: int,
    maxcore: int,
    calc_hess: bool,
    smd: bool,
    smd_solvent: str,
) -> str:
    step1_kw = _with_nopop(step1_keywords)
    step2_kw = _with_nopop(step2_keywords)
    calc_hess_value = "true" if calc_hess else "false"
    lines = [
        f"# {__generator_banner__}",
        "%pal",
        f"  nprocs {nprocs}",
        "end",
        f"%maxcore {maxcore}",
        "%compound",
        "  New_Step",
        f"    ! {step1_kw}",
    ]
    if smd:
        lines.extend(
            [
                "    %cpcm",
                "      SMD true",
                f'      SMDsolvent "{smd_solvent}"',
                "    end",
            ]
        )
    lines.extend(
        [
            "    %geom",
            "      Constraints",
        ]
    )
    for atom_i, atom_j in constraint_atom_pairs:
        lines.append(f"        {{B {atom_i} {atom_j} C}}")
    lines.extend(
        [
            "      end",
            "    end",
            f"    * xyz {charge} {multiplicity}",
            xyz_text,
            "    *",
            "  Step_End",
            "",
            "  New_Step",
            f"    ! {step2_kw}",
        ]
    )
    if smd:
        lines.extend(
            [
                "    %cpcm",
                "      SMD true",
                f'      SMDsolvent "{smd_solvent}"',
                "    end",
            ]
        )
    lines.extend(
        [
            "    %geom",
            f"      calc_hess {calc_hess_value}",
            "    end",
            f"    * xyzfile {charge} {multiplicity} {step2_xyzfile_name} *",
            "  Step_End",
            "end",
            "",
        ]
    )
    return "\n".join(lines)
