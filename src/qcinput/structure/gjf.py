import re
from pathlib import Path


def load_gjf_text(path: Path) -> str:
    text, _, _ = load_gjf_data(path)
    return text


def load_gjf_data(path: Path) -> tuple[str, int, int]:
    text = path.read_text(encoding="utf-8").strip()
    lines = [line.rstrip() for line in text.splitlines()]
    if not lines:
        raise ValueError("GJF file is empty.")

    charge_mult_idx = _find_charge_multiplicity_index(lines)

    if charge_mult_idx == -1:
        raise ValueError("Cannot find charge/multiplicity line in GJF file.")

    atom_lines: list[str] = []
    for idx, line in enumerate(lines[charge_mult_idx + 1 :], start=charge_mult_idx + 2):
        stripped = line.strip()
        if not stripped:
            if atom_lines:
                break
            continue

        normalized_atom_line = _normalize_atom_line(stripped)
        if normalized_atom_line is None:
            if atom_lines:
                break
            raise ValueError(f"Invalid GJF atom line at line {idx}: '{line}'")
        atom_lines.append(normalized_atom_line)

    if not atom_lines:
        raise ValueError("No geometry section found in GJF file.")

    charge_str, multiplicity_str = lines[charge_mult_idx].strip().split()
    charge = int(charge_str)
    multiplicity = int(multiplicity_str)
    return "\n".join(atom_lines), charge, multiplicity


def _find_charge_multiplicity_index(lines: list[str]) -> int:
    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) != 2:
            continue
        try:
            int(parts[0])
            int(parts[1])
        except ValueError:
            continue

        atom_count = 0
        for next_line in lines[idx + 1 :]:
            stripped = next_line.strip()
            if not stripped:
                if atom_count:
                    break
                continue
            if _normalize_atom_line(stripped) is None:
                break
            atom_count += 1

        if atom_count > 0:
            return idx
    return -1


def _normalize_atom_line(line: str) -> str | None:
    parts = line.split()
    if len(parts) != 4:
        return None

    atom, x, y, z = parts
    if not re.fullmatch(r"^[A-Za-z][A-Za-z0-9]*$", atom):
        return None
    try:
        float(x)
        float(y)
        float(z)
    except ValueError:
        return None
    return " ".join((atom, x, y, z))
