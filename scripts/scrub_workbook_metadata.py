#!/usr/bin/env python3
"""Replace generator branding in xlsx theme names and document properties."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOKS = [ROOT / "outputs" / "credit-model.xlsx"]
BRANDING = re.compile(rb"ChatGPT|OpenAI|Codex")
REPLACEMENTS = {"xl/theme/": b"Office", "docProps/": b"Rahil Bhavan"}


def scrub(path: Path) -> bool:
    """Rewrite branded members in place; every other member keeps its bytes and timestamp."""
    with zipfile.ZipFile(path) as source:
        members = [(info, source.read(info)) for info in source.infolist()]
    changed = False
    cleaned = []
    for info, data in members:
        for prefix, replacement in REPLACEMENTS.items():
            if info.filename.startswith(prefix):
                updated = BRANDING.sub(replacement, data)
                changed |= updated != data
                data = updated
        cleaned.append((info, data))
    if not changed:
        return False
    temporary = path.with_name(path.name + ".tmp")
    with zipfile.ZipFile(temporary, "w") as target:
        for info, data in cleaned:
            target.writestr(info, data)
    temporary.replace(path)
    return True


def main() -> int:
    paths = [Path(arg) for arg in sys.argv[1:]] or DEFAULT_WORKBOOKS
    for path in paths:
        print(f"{path}: {'scrubbed' if scrub(path) else 'clean'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
