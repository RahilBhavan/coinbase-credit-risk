#!/usr/bin/env python3
"""Normalize xlsx theme names, document-property authorship, relationship ids, and member timestamps."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOKS = [ROOT / "outputs" / "credit-model.xlsx"]
AUTHOR = b"Rahil Bhavan"
THEME_NAME = re.compile(rb'(<a:(?:theme|clrScheme|fontScheme|fmtScheme)\b[^>]*?\bname=")[^"]*"')
PROPERTY = re.compile(rb"(<(Application|Company|dc:creator|cp:lastModifiedBy)>)[^<]*(</\2>)")
# The workbook writer assigns random relationship ids and wall-clock timestamps; pin both so rebuilds are byte-identical.
RANDOM_REL_ID = re.compile(rb'Id="(R[0-9a-f]{16})"')
FIXED_TIME = (2026, 9, 20, 12, 0, 0)


def scrub(path: Path) -> bool:
    """Rewrite the workbook in place with normalized metadata; return whether any byte changed."""
    original = path.read_bytes()
    with zipfile.ZipFile(path) as source:
        members = [(info, source.read(info)) for info in source.infolist()]
    rel_ids: dict[bytes, bytes] = {}
    for info, data in members:
        if info.filename.endswith(".rels"):
            for match in RANDOM_REL_ID.finditer(data):
                rel_ids.setdefault(match.group(1), b"rIdX%d" % (len(rel_ids) + 1))
    cleaned = []
    for info, data in members:
        if info.filename.startswith("xl/theme/"):
            data = THEME_NAME.sub(rb'\1Office"', data)
        elif info.filename.startswith("docProps/"):
            data = PROPERTY.sub(rb"\1" + AUTHOR + rb"\3", data)
        if rel_ids and info.filename.endswith((".xml", ".rels")):
            data = RANDOM_REL_ID.sub(lambda m: b'Id="' + rel_ids[m.group(1)] + b'"', data)
            for old, new in rel_ids.items():
                data = data.replace(b'"' + old + b'"', b'"' + new + b'"')
        fixed = zipfile.ZipInfo(info.filename, FIXED_TIME)
        fixed.compress_type = info.compress_type
        fixed.external_attr = info.external_attr
        fixed.create_system = info.create_system
        cleaned.append((fixed, data))
    temporary = path.with_name(path.name + ".tmp")
    with zipfile.ZipFile(temporary, "w") as target:
        for info, data in cleaned:
            target.writestr(info, data)
    if temporary.read_bytes() == original:
        temporary.unlink()
        return False
    temporary.replace(path)
    return True


def main() -> int:
    paths = [Path(arg) for arg in sys.argv[1:]] or DEFAULT_WORKBOOKS
    for path in paths:
        print(f"{path}: {'scrubbed' if scrub(path) else 'clean'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
