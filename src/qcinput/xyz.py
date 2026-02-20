from pathlib import Path


def load_xyz_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    lines = [line.rstrip() for line in text.splitlines()]
    if len(lines) < 3:
        raise ValueError("XYZ file must contain at least 3 lines.")

    try:
        atom_count = int(lines[0].strip())
    except ValueError as exc:
        raise ValueError("The first line of XYZ must be atom count.") from exc

    atom_lines = lines[2:]
    if atom_count != len(atom_lines):
        raise ValueError(
            f"XYZ atom count mismatch: header={atom_count}, geometry lines={len(atom_lines)}."
        )

    for idx, line in enumerate(atom_lines, start=3):
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"Invalid XYZ atom line at line {idx}: '{line}'")
        _, x, y, z = parts
        try:
            float(x)
            float(y)
            float(z)
        except ValueError as exc:
            raise ValueError(f"Invalid coordinates at line {idx}: '{line}'") from exc

    return "\n".join(atom_lines)
