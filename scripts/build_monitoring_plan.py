#!/usr/bin/env python3
"""Build a deterministic post-close monitoring design from case inputs."""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "case"
JSON_OUTPUT = ROOT / "artifacts" / "monitoring-plan.json"
CSV_OUTPUT = ROOT / "artifacts" / "monitoring-plan.csv"


def build() -> dict:
    config = json.loads((CASE / "monitoring.json").read_text(encoding="utf-8"))
    decision = json.loads((ROOT / "artifacts" / "decision-record.json").read_text(encoding="utf-8"))
    ids = [row["monitor_id"] for row in config["rules"]]
    if len(ids) != len(set(ids)):
        raise ValueError("monitoring IDs must be unique")
    recommended = Decimal(decision["recommended_amount_usd"])
    accrued = Decimal(json.loads((CASE / "facility.json").read_text(encoding="utf-8"))["accrued_amount_usd"])
    proceeds = Decimal(decision["available_proceeds_usd"])
    concentration_cap = Decimal(decision["caps_usd"]["concentration"])
    projected_coverage = proceeds / (recommended + accrued)
    outstanding = len(decision["outstanding_blocking_conditions"])

    rows = []
    for rule in config["rules"]:
        row = dict(rule)
        if rule["monitor_id"] == "MON-01":
            row.update(current_value=f"{projected_coverage.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)}x", status="pass_projection")
        elif rule["monitor_id"] == "MON-02":
            row.update(current_value=f"{outstanding} blocking conditions outstanding", status="pre_funding_blocked")
        elif rule["monitor_id"] == "MON-07":
            headroom = concentration_cap - recommended
            row.update(current_value=f"${headroom.quantize(Decimal('0.01')):,.2f}", status="pass_projection" if headroom >= 0 else "breach_projection")
        else:
            row.update(current_value="not measured — private evidence required", status="not_measured")
        rows.append(row)
    return {
        "schema_version": "1.0",
        "case_id": decision["case_id"],
        "activation_state": config["activation_state"],
        "method_limit": config["method_limit"],
        "summary": {
            "rule_count": len(rows),
            "pass_projection_count": sum(row["status"] == "pass_projection" for row in rows),
            "pre_funding_blocked_count": sum(row["status"] == "pre_funding_blocked" for row in rows),
            "not_measured_count": sum(row["status"] == "not_measured" for row in rows),
        },
        "rules": rows,
    }


def main() -> int:
    payload = build()
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["monitor_id", "metric", "threshold", "current_value", "status", "frequency", "owner_role", "source_ids", "breach_action", "escalation"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rules"]:
            writer.writerow({**{field: row[field] for field in fields if field != "source_ids"}, "source_ids": "|".join(row["source_ids"])})
    print(f"Monitoring plan: {payload['summary']['rule_count']} rules; activation={payload['activation_state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
