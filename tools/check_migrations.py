"""Validate deterministic SQL migration numbering."""

from __future__ import annotations

import re
from pathlib import Path

MIGRATION_RE = re.compile(r"^(?P<number>\d{3})_.+\.sql$")


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "database" / "migrations"
    migrations = sorted(root.glob("*.sql"))
    numbers: dict[int, Path] = {}

    for path in migrations:
        match = MIGRATION_RE.match(path.name)
        if not match:
            raise SystemExit(f"Invalid migration filename: {path.name}")
        number = int(match.group("number"))
        if number in numbers:
            raise SystemExit(
                f"Duplicate migration number {number:03d}: {numbers[number].name}, {path.name}"
            )
        numbers[number] = path

    if not numbers:
        raise SystemExit("No SQL migrations found")

    print(f"Validated {len(numbers)} migrations: {min(numbers):03d}..{max(numbers):03d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
