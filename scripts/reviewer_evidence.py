#!/usr/bin/env python3
"""Validation and atomic persistence for independent human-gate evidence."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/review/reviewer-evidence.json"
GATE_IDS = ("HG-01", "HG-02", "HG-03")
OUTCOMES = {"OUTSTANDING", "PASS", "FAIL", "NEEDS_WORK"}
ATTRIBUTION = {"YES", "NO", "ROLE_ONLY"}
REQUIRED_CRITERIA = {"HG-01": 3, "HG-02": 3, "HG-03": 3}


def load(path: Path = LEDGER) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record: dict[str, object], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    gate_id = str(record.get("gate_id", ""))
    outcome = str(record.get("outcome", ""))
    if gate_id not in GATE_IDS:
        errors.append("unknown gate_id")
    if outcome not in OUTCOMES:
        errors.append("invalid outcome")
    if outcome == "OUTSTANDING":
        return errors
    for field in ("reviewer_identifier", "reviewer_role", "reviewed_on", "attribution_permission", "notes", "recorded_at"):
        if not str(record.get(field, "")).strip():
            errors.append(f"{field} is required for a completed review")
    try:
        reviewed = date.fromisoformat(str(record.get("reviewed_on", "")))
        if reviewed > date.today():
            errors.append("reviewed_on cannot be in the future")
    except ValueError:
        errors.append("reviewed_on must be ISO YYYY-MM-DD")
    if str(record.get("attribution_permission", "")) not in ATTRIBUTION:
        errors.append("invalid attribution_permission")
    criteria = record.get("criterion_results", [])
    if not isinstance(criteria, list) or len(criteria) != REQUIRED_CRITERIA.get(gate_id, -1) or any(item not in ("PASS", "FAIL") for item in criteria):
        errors.append("criterion_results must contain one PASS/FAIL value per declared criterion")
    evidence = record.get("evidence_paths", [])
    if not isinstance(evidence, list) or not evidence:
        errors.append("at least one evidence path is required")
    else:
        for relative in evidence:
            candidate = root / str(relative)
            try:
                candidate.resolve().relative_to(root.resolve())
            except ValueError:
                errors.append(f"evidence path escapes project: {relative}")
                continue
            if not candidate.is_file() or candidate.stat().st_size == 0:
                errors.append(f"evidence path is missing or empty: {relative}")
    if outcome == "PASS" and isinstance(criteria, list) and any(item != "PASS" for item in criteria):
        errors.append("PASS outcome requires every criterion to pass")
    return errors


def validate_ledger(payload: dict[str, object], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    records = payload.get("records", [])
    if not isinstance(records, list) or [row.get("gate_id") for row in records] != list(GATE_IDS):
        return ["records must contain HG-01, HG-02, and HG-03 in order"]
    for record in records:
        errors.extend(f"{record.get('gate_id', 'unknown')}: {error}" for error in validate_record(record, root))
    return errors


def gate_passes(record: dict[str, object], root: Path = ROOT) -> bool:
    return record.get("outcome") == "PASS" and not validate_record(record, root)


def write_atomic(payload: dict[str, object], path: Path = LEDGER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        Path(temporary).replace(path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise
