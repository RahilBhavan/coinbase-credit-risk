#!/usr/bin/env python3
"""Join pre-funding conditions, monitoring, covenants, and escalation paths."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUT = ROOT / "artifacts" / "control-matrix.json"
CSV_OUT = ROOT / "artifacts" / "control-matrix.csv"


def build() -> dict[str, object]:
    config = json.loads((CASE / "control_matrix.json").read_text())
    conditions = {row["condition_id"]: row for row in json.loads((CASE / "conditions.json").read_text())}
    monitoring_payload = json.loads((ROOT / "artifacts" / "monitoring-plan.json").read_text())
    covenant_payload = json.loads((ROOT / "artifacts" / "covenant-plan.json").read_text())
    escalation_payload = json.loads((ROOT / "artifacts" / "escalation-playbook.json").read_text())
    monitors = {row["monitor_id"]: row for row in monitoring_payload["rules"]}
    covenants = {row["monitor_id"]: row for row in covenant_payload["covenants"]}
    escalations = {row["monitor_id"]: row for row in escalation_payload["playbooks"]}
    mappings = config["mappings"]
    mapped_monitors = [row["monitor_id"] for row in mappings]
    if len(mapped_monitors) != len(set(mapped_monitors)) or set(mapped_monitors) != set(monitors):
        raise ValueError("control matrix must map each monitoring rule exactly once")
    referenced_conditions = {item for row in mappings for item in row["condition_ids"]}
    if referenced_conditions != set(conditions):
        raise ValueError("control matrix must cover every pre-funding condition")

    rows = []
    for mapping in mappings:
        monitor_id = mapping["monitor_id"]
        monitor, covenant, escalation = monitors[monitor_id], covenants[monitor_id], escalations[monitor_id]
        condition_rows = [conditions[item] for item in mapping["condition_ids"]]
        rows.append({
            "control_id": f"CTL-{int(monitor_id[-2:]):02d}",
            "control_objective": mapping["control_objective"],
            "condition_ids": mapping["condition_ids"],
            "condition_status": "outstanding" if any(row["evidence_status"] != "verified" for row in condition_rows) else "verified",
            "monitor_id": monitor_id,
            "metric": monitor["metric"],
            "threshold": monitor["threshold"],
            "current_value": monitor["current_value"],
            "current_status": monitor["status"],
            "covenant_id": covenant["covenant_id"],
            "covenant_type": covenant["covenant_type"],
            "cure_period": covenant["cure_period"],
            "playbook_id": escalation["playbook_id"],
            "severity_on_trigger": escalation["severity_on_trigger"],
            "response_sla": escalation["response_sla"],
            "draw_state_on_trigger": escalation["draw_state_on_trigger"],
            "decision_owner": escalation["decision_owner"],
            "exit_criteria": escalation["exit_criteria"],
        })
    return {
        "schema_version": "1.0", "case_id": monitoring_payload["case_id"],
        "evidence_class": config["evidence_class"], "enforceability_status": config["enforceability_status"],
        "activation_state": monitoring_payload["activation_state"], "method_limit": config["method_limit"],
        "summary": {
            "control_count": len(rows), "condition_count": len(conditions),
            "critical_control_count": sum(row["severity_on_trigger"] == "critical" for row in rows),
            "high_control_count": sum(row["severity_on_trigger"] == "high" for row in rows),
            "moderate_control_count": sum(row["severity_on_trigger"] == "moderate" for row in rows),
            "outstanding_condition_control_count": sum(row["condition_status"] == "outstanding" for row in rows),
        },
        "controls": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    fields = list(payload["controls"][0])
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["controls"]:
            writer.writerow({**row, "condition_ids": ";".join(row["condition_ids"])})
    print(f"Control matrix: {payload['summary']['control_count']} controls covering {payload['summary']['condition_count']} conditions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
