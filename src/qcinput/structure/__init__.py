from dataclasses import dataclass
from pathlib import Path

from qcinput.structure.gjf import load_gjf_data
from qcinput.structure.xyz import load_xyz_text


@dataclass(frozen=True)
class StructureData:
    xyz_text: str
    charge: int | None
    multiplicity: int | None
    source_format: str


def load_structure(path: Path) -> StructureData:
    suffix = path.suffix.lower()
    if suffix == ".xyz":
        return StructureData(
            xyz_text=load_xyz_text(path),
            charge=None,
            multiplicity=None,
            source_format="xyz",
        )
    if suffix == ".gjf":
        xyz_text, charge, multiplicity = load_gjf_data(path)
        return StructureData(
            xyz_text=xyz_text,
            charge=charge,
            multiplicity=multiplicity,
            source_format="gjf",
        )
    raise ValueError(
        f"Unsupported input file suffix '{path.suffix}'. Supported suffixes: .xyz, .gjf."
    )


def load_structure_text(path: Path) -> str:
    return load_structure(path).xyz_text
