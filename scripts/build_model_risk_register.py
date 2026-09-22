#!/usr/bin/env python3
"""Build synchronized model-risk register artifacts from the governed case input."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/case/model_risks.json"
JSON_OUTPUT = ROOT / "artifacts/model-risk-register.json"
CSV_OUTPUT = ROOT / "artifacts/model-risk-register.csv"
FIELDS = ("risk_id", "category", "risk", "severity", "status", "affected_decision", "linked_assumptions", "linked_conditions", "mitigation", "validation_evidence", "residual_risk", "owner", "disposition_if_unresolved")


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    risks = source["risks"]
    ids = [row["risk_id"] for row in risks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate model-risk IDs")
    for row in risks:
        missing = [field for field in FIELDS if field not in row]
        if missing:
            raise ValueError(f"{row.get('risk_id', 'unknown')}: missing {', '.join(missing)}")
        if row["status"] == "open" and not row["disposition_if_unresolved"]:
            raise ValueError(f"{row['risk_id']}: open risk needs an unresolved disposition")
    payload = {key: source[key] for key in ("schema_version", "case_id", "evidence_class", "method_limit")}
    payload["risks"] = risks
    payload["summary"] = {
        "risk_count": len(risks),
        "open_count": sum(row["status"] == "open" for row in risks),
        "critical_count": sum(row["severity"] == "critical" for row in risks),
        "high_count": sum(row["severity"] == "high" for row in risks),
        "decision_blocking_count": sum("block" in row["disposition_if_unresolved"].lower() or "decline" in row["disposition_if_unresolved"].lower() or "do not fund" in row["disposition_if_unresolved"].lower() for row in risks),
    }
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in risks:
            flat = dict(row)
            flat["linked_assumptions"] = "|".join(row["linked_assumptions"])
            flat["linked_conditions"] = "|".join(row["linked_conditions"])
            writer.writerow(flat)
    print(f"Model-risk register: {len(risks)} open risks; {payload['summary']['critical_count']} critical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
