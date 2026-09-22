#!/usr/bin/env python3
"""Build a deterministic breach-response playbook from monitoring and covenant controls."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "escalation-playbook.json"
CSV_OUTPUT = ROOT / "artifacts" / "escalation-playbook.csv"


def current_response(status: str) -> str:
    return {
        "pass_projection": "projection_only_no_incident",
        "pre_funding_blocked": "resolve_pre_funding_blocker",
        "not_measured": "obtain_private_evidence_before_activation",
    }[status]


def build() -> dict:
    config = json.loads((CASE / "escalations.json").read_text(encoding="utf-8"))
    monitoring = json.loads((ROOT / "artifacts" / "monitoring-plan.json").read_text(encoding="utf-8"))
    covenants = json.loads((ROOT / "artifacts" / "covenant-plan.json").read_text(encoding="utf-8"))
    monitor_map = {row["monitor_id"]: row for row in monitoring["rules"]}
    covenant_map = {row["covenant_id"]: row for row in covenants["covenants"]}
    rows = config["playbooks"]
    ids = [row["playbook_id"] for row in rows]
    monitor_ids = [row["monitor_id"] for row in rows]
    covenant_ids = [row["covenant_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("playbook IDs must be unique")
    if len(monitor_ids) != len(set(monitor_ids)) or set(monitor_ids) != set(monitor_map):
        raise ValueError("playbooks must map one-to-one to monitoring rules")
    if len(covenant_ids) != len(set(covenant_ids)) or set(covenant_ids) != set(covenant_map):
        raise ValueError("playbooks must map one-to-one to covenants")
    if any(covenant_map[row["covenant_id"]]["monitor_id"] != row["monitor_id"] for row in rows):
        raise ValueError("playbook covenant and monitoring links must agree")

    built = []
    for row in rows:
        monitor = monitor_map[row["monitor_id"]]
        built.append({
            **row,
            "current_value": monitor["current_value"],
            "current_status": monitor["status"],
            "current_response": current_response(monitor["status"]),
        })
    return {
        "schema_version": "1.0",
        "case_id": monitoring["case_id"],
        "evidence_class": config["evidence_class"],
        "activation_state": config["activation_state"],
        "method_limit": config["method_limit"],
        "summary": {
            "playbook_count": len(built),
            "critical_count": sum(row["severity_on_trigger"] == "critical" for row in built),
            "high_count": sum(row["severity_on_trigger"] == "high" for row in built),
            "moderate_count": sum(row["severity_on_trigger"] == "moderate" for row in built),
            "blocked_current_count": sum(row["current_status"] == "pre_funding_blocked" for row in built),
            "private_evidence_required_count": sum(row["current_status"] == "not_measured" for row in built),
        },
        "playbooks": built,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = [
        "playbook_id", "monitor_id", "covenant_id", "severity_on_trigger", "response_sla",
        "draw_state_on_trigger", "decision_owner", "current_value", "current_status",
        "current_response", "required_evidence", "exit_criteria",
    ]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in payload["playbooks"])
    print(f"Escalation playbook: {payload['summary']['playbook_count']} responses; activation={payload['activation_state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
