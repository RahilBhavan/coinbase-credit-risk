#!/usr/bin/env python3
"""Build a machine-readable trace from committee claims to evidence and artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "decision-lineage.json"
CSV_OUTPUT = ROOT / "artifacts" / "decision-lineage.csv"


def resolve(payloads: dict, dotted_path: str):
    parts = dotted_path.split(".")
    value = payloads[parts[0]]
    for part in parts[1:]:
        value = value[part]
    return value


def build() -> dict:
    config = json.loads((CASE / "lineage.json").read_text(encoding="utf-8"))
    payloads = {
        "decision": json.loads((ROOT / "artifacts/decision-record.json").read_text(encoding="utf-8")),
        "liquidity": json.loads((ROOT / "artifacts/liquidity-analysis.json").read_text(encoding="utf-8")),
        "monitoring": json.loads((ROOT / "artifacts/monitoring-plan.json").read_text(encoding="utf-8")),
    }
    with (ROOT / "02-research/source-register.csv").open(newline="", encoding="utf-8-sig") as handle:
        sources = {row["source_id"]: row for row in csv.DictReader(handle)}
    ids = [row["node_id"] for row in config["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("lineage node IDs must be unique")
    rows = []
    for node in config["nodes"]:
        missing_sources = sorted(set(node["evidence_ids"]) - set(sources))
        if missing_sources:
            raise ValueError(f"{node['node_id']} has unknown evidence IDs: {missing_sources}")
        artifact_path = ROOT / node["artifact_locator"].split("#", 1)[0]
        if not artifact_path.is_file():
            raise ValueError(f"{node['node_id']} artifact is missing: {artifact_path}")
        rows.append({
            **node,
            "current_value": str(resolve(payloads, node["value_path"])),
            "evidence_classes": sorted({sources[source_id]["evidence_class"] for source_id in node["evidence_ids"]}),
        })
    return {
        "schema_version": "1.0",
        "case_id": payloads["decision"]["case_id"],
        "case_version": payloads["decision"]["case_version"],
        "method_limit": config["method_limit"],
        "summary": {
            "node_count": len(rows),
            "source_link_count": sum(len(row["evidence_ids"]) for row in rows),
            "reported_supported_node_count": sum("reported" in row["evidence_classes"] for row in rows),
            "assumption_exposed_node_count": sum(any(value in {"assumed", "simulated"} for value in row["evidence_classes"]) for row in rows),
        },
        "nodes": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["node_id", "claim_type", "committee_claim", "current_value", "evidence_ids", "evidence_classes", "calculation_or_rule", "artifact_locator", "workbook_locator", "owner_role", "limitation"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["nodes"]:
            writer.writerow({field: "|".join(row[field]) if field in {"evidence_ids", "evidence_classes"} else row[field] for field in fields})
    print(f"Decision lineage: {payload['summary']['node_count']} claims; {payload['summary']['source_link_count']} evidence links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
