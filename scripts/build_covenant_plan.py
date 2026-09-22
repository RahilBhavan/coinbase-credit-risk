#!/usr/bin/env python3
"""Build a synchronized illustrative covenant package from monitoring controls."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "covenant-plan.json"
CSV_OUTPUT = ROOT / "artifacts" / "covenant-plan.csv"


def build() -> dict:
    config = json.loads((CASE / "covenants.json").read_text(encoding="utf-8"))
    monitoring = json.loads((ROOT / "artifacts" / "monitoring-plan.json").read_text(encoding="utf-8"))
    monitor_map = {row["monitor_id"]: row for row in monitoring["rules"]}
    ids = [row["covenant_id"] for row in config["covenants"]]
    monitor_ids = [row["monitor_id"] for row in config["covenants"]]
    if len(ids) != len(set(ids)):
        raise ValueError("covenant IDs must be unique")
    if len(monitor_ids) != len(set(monitor_ids)) or set(monitor_ids) != set(monitor_map):
        raise ValueError("covenants must map one-to-one to monitoring rules")

    rows = []
    for covenant in config["covenants"]:
        monitor = monitor_map[covenant["monitor_id"]]
        rows.append({
            **covenant,
            "current_value": monitor["current_value"],
            "status": monitor["status"],
            "enforceability_status": config["enforceability_status"],
        })
    return {
        "schema_version": "1.0",
        "case_id": monitoring["case_id"],
        "evidence_class": config["evidence_class"],
        "enforceability_status": config["enforceability_status"],
        "method_limit": config["method_limit"],
        "summary": {
            "covenant_count": len(rows),
            "projected_pass_count": sum(row["status"] == "pass_projection" for row in rows),
            "pre_funding_blocked_count": sum(row["status"] == "pre_funding_blocked" for row in rows),
            "not_measured_count": sum(row["status"] == "not_measured" for row in rows),
        },
        "covenants": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = [
        "covenant_id", "covenant_type", "requirement", "threshold", "current_value", "status",
        "test_frequency", "cure_period", "breach_consequence", "owner_role", "monitor_id", "enforceability_status",
    ]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in payload["covenants"])
    print(f"Covenant plan: {payload['summary']['covenant_count']} controls; enforceability={payload['enforceability_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
