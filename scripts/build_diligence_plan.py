#!/usr/bin/env python3
"""Build an acyclic, decision-linked diligence execution plan."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "diligence-plan.json"
CSV_OUTPUT = ROOT / "artifacts" / "diligence-plan.csv"


def waves(tasks: list[dict]) -> dict[str, int]:
    remaining = {row["condition_id"]: set(row["depends_on"]) for row in tasks}
    result: dict[str, int] = {}
    wave = 1
    while remaining:
        ready = sorted(condition_id for condition_id, dependencies in remaining.items() if dependencies.issubset(result))
        if not ready:
            raise ValueError("diligence dependencies contain a cycle or unknown condition")
        for condition_id in ready:
            result[condition_id] = wave
            del remaining[condition_id]
        wave += 1
    return result


def build() -> dict:
    config = json.loads((CASE / "diligence.json").read_text(encoding="utf-8"))
    conditions = json.loads((ROOT / "artifacts" / "condition-register.json").read_text(encoding="utf-8"))["conditions"]
    lineage = json.loads((ROOT / "artifacts" / "decision-lineage.json").read_text(encoding="utf-8"))["nodes"]
    condition_map = {row["condition_id"]: row for row in conditions}
    lineage_ids = {row["node_id"] for row in lineage}
    task_ids = [row["condition_id"] for row in config["tasks"]]
    if len(task_ids) != len(set(task_ids)) or set(task_ids) != set(condition_map):
        raise ValueError("diligence tasks must map one-to-one to conditions")
    if any(set(row["depends_on"]) - set(condition_map) for row in config["tasks"]):
        raise ValueError("diligence dependency references an unknown condition")
    if any(set(row["affected_lineage_nodes"]) - lineage_ids for row in config["tasks"]):
        raise ValueError("diligence task references an unknown lineage node")
    wave_map = waves(config["tasks"])
    rows = []
    for task in config["tasks"]:
        condition = condition_map[task["condition_id"]]
        unmet = [dependency for dependency in task["depends_on"] if condition_map[dependency]["evidence_status"] != "verified"]
        current_action = "complete" if condition["evidence_status"] == "verified" else f"waiting_on:{'|'.join(unmet)}" if unmet else "ready_to_start"
        rows.append({**task, "wave": wave_map[task["condition_id"]], "current_action": current_action, "evidence_status": condition["evidence_status"], "owner_role": condition["owner_role"], "requirement": condition["requirement"], "verification_method": condition["verification_method"]})
    return {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "funding_gate_status": "blocked_pending_conditions",
        "method_limit": config["method_limit"],
        "summary": {
            "task_count": len(rows),
            "critical_count": sum(row["priority"] == "critical" for row in rows),
            "high_count": sum(row["priority"] == "high" for row in rows),
            "parallel_lane_count": len({row["parallel_lane"] for row in rows}),
            "wave_one_count": sum(row["wave"] == 1 for row in rows),
            "dependency_blocked_count": sum(row["current_action"].startswith("waiting_on:") for row in rows),
            "ready_to_start_count": sum(row["current_action"] == "ready_to_start" for row in rows),
        },
        "tasks": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["condition_id", "wave", "parallel_lane", "priority", "current_action", "evidence_status", "owner_role", "requirement", "verification_method", "depends_on", "decision_impact", "failure_consequence", "affected_lineage_nodes", "completion_output"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["tasks"]:
            writer.writerow({field: "|".join(row[field]) if field in {"depends_on", "affected_lineage_nodes"} else row[field] for field in fields})
    print(f"Diligence plan: {payload['summary']['task_count']} tasks; ready={payload['summary']['ready_to_start_count']}; waiting={payload['summary']['dependency_blocked_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
