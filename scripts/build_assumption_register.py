#!/usr/bin/env python3
"""Build a governed register for every case assumption source."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "assumption-register.json"
CSV_OUTPUT = ROOT / "artifacts" / "assumption-register.csv"


def build() -> dict:
    config = json.loads((CASE / "assumption_governance.json").read_text(encoding="utf-8"))
    with (ROOT / "02-research/source-register.csv").open(newline="", encoding="utf-8-sig") as handle:
        sources = {row["source_id"]: row for row in csv.DictReader(handle)}
    lineage_ids = {row["node_id"] for row in json.loads((ROOT / "artifacts/decision-lineage.json").read_text(encoding="utf-8"))["nodes"]}
    expected = {source_id for source_id in sources if source_id.startswith("ASM-C")}
    ids = [row["assumption_id"] for row in config["assumptions"]]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError("assumption governance must map one-to-one to ASM-C source records")
    rows = []
    for row in config["assumptions"]:
        source = sources[row["assumption_id"]]
        if source["evidence_class"] not in {"assumed", "simulated"}:
            raise ValueError(f"{row['assumption_id']} is not assumption-class evidence")
        if set(row["downstream_lineage_nodes"]) - lineage_ids:
            raise ValueError(f"{row['assumption_id']} references an unknown lineage node")
        rows.append({**row, "evidence_class": source["evidence_class"], "source_claim": source["input_or_claim"]})
    return {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "method_limit": config["method_limit"],
        "summary": {
            "assumption_count": len(rows),
            "critical_count": sum(row["materiality"] == "critical" for row in rows),
            "high_count": sum(row["materiality"] == "high" for row in rows),
            "unvalidated_count": sum(row["validation_status"] == "unvalidated" for row in rows),
            "downstream_lineage_link_count": sum(len(row["downstream_lineage_nodes"]) for row in rows),
        },
        "assumptions": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["assumption_id", "assumption", "evidence_class", "materiality", "validation_status", "owner_role", "workbook_inputs", "source_claim", "validation_method", "challenge_trigger", "downstream_lineage_nodes"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["assumptions"]:
            writer.writerow({field: "|".join(row[field]) if field == "downstream_lineage_nodes" else row[field] for field in fields})
    print(f"Assumption register: {payload['summary']['assumption_count']} assumptions; unvalidated={payload['summary']['unvalidated_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
