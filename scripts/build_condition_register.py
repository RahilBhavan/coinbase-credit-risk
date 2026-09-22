#!/usr/bin/env python3
"""Build reviewer-friendly condition-register artifacts from case inputs."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "case" / "conditions.json"
CSV_OUTPUT = ROOT / "artifacts" / "condition-register.csv"
JSON_OUTPUT = ROOT / "artifacts" / "condition-register.json"
FIELDS = (
    "condition_id", "category", "requirement", "evidence_class", "evidence_status",
    "blocking", "owner_role", "timing", "verification_method", "source_id",
)


def main() -> int:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    ids = [row.get("condition_id") for row in rows]
    if not rows or len(ids) != len(set(ids)) or any(set(row) != set(FIELDS) for row in rows):
        raise SystemExit("Condition register requires non-empty, unique, exact-schema rows.")
    statuses = Counter(row["evidence_status"] for row in rows)
    outstanding_blockers = [row["condition_id"] for row in rows if row["blocking"] and row["evidence_status"] != "verified"]
    payload = {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "funding_gate_status": "blocked_pending_conditions" if outstanding_blockers else "cleared_to_fund",
        "condition_count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "outstanding_blocking_conditions": outstanding_blockers,
        "conditions": rows,
        "evidence_boundary": "Statuses describe the current project evidence set, not a real transaction closing process.",
    }
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Condition register: {len(rows)} conditions; {len(outstanding_blockers)} blocking and outstanding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
