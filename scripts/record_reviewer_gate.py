#!/usr/bin/env python3
"""Record attributable human-gate evidence without weakening readiness controls."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from reviewer_evidence import LEDGER, gate_passes, load, validate_ledger, validate_record, write_atomic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate_id", choices=("HG-01", "HG-02", "HG-03"))
    parser.add_argument("--outcome", required=True, choices=("PASS", "FAIL", "NEEDS_WORK"))
    parser.add_argument("--reviewer-identifier", required=True)
    parser.add_argument("--reviewer-role", required=True)
    parser.add_argument("--reviewed-on", required=True, help="ISO date: YYYY-MM-DD")
    parser.add_argument("--attribution-permission", required=True, choices=("YES", "NO", "ROLE_ONLY"))
    parser.add_argument("--criterion", action="append", required=True, choices=("PASS", "FAIL"), help="Repeat once for each scorecard criterion.")
    parser.add_argument("--evidence-path", action="append", required=True, help="Repeatable path inside this project.")
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()
    payload = load()
    record = {
        "gate_id": args.gate_id, "outcome": args.outcome,
        "reviewer_identifier": args.reviewer_identifier.strip(), "reviewer_role": args.reviewer_role.strip(),
        "reviewed_on": args.reviewed_on, "attribution_permission": args.attribution_permission,
        "criterion_results": args.criterion, "evidence_paths": args.evidence_path,
        "notes": args.notes.strip(), "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    errors = validate_record(record)
    if errors:
        raise SystemExit("Gate evidence rejected: " + "; ".join(errors))
    payload["records"] = [record if row["gate_id"] == args.gate_id else row for row in payload["records"]]
    ledger_errors = validate_ledger(payload)
    if ledger_errors:
        raise SystemExit("Ledger rejected: " + "; ".join(ledger_errors))
    write_atomic(payload, LEDGER)
    print(f"Recorded {args.gate_id}: outcome={args.outcome}; readiness_pass={str(gate_passes(record)).lower()}")
    print("Rebuild with: python3 scripts/build_package.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
