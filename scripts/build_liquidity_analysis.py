#!/usr/bin/env python3
"""Build a conservative public-data liquidity bridge from reconciled filing facts."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "artifacts" / "issuer-fact-ledger.csv"
JSON_OUTPUT = ROOT / "artifacts" / "liquidity-analysis.json"
CSV_OUTPUT = ROOT / "artifacts" / "liquidity-analysis.csv"


def calculate(values: dict[str, Decimal]) -> dict:
    cash = values["FIN-001"]
    designated = cash * values["FIN-002"]
    available_screen = cash - designated
    identified_due = values["FIN-009"] + values["FIN-010"]
    residual_before_put = available_screen - identified_due
    potential_put = values["FIN-012"]
    residual_after_put = residual_before_put - potential_put
    rows = [
        ("LIQ-01", "Reported cash and cash equivalents", cash, "SRC-001", "reported"),
        ("LIQ-02", "Less: cash designated for Exaion operations", -designated, "SRC-001", "calculated from reported approximate share"),
        ("LIQ-03", "Cash after designation screen", available_screen, "SRC-001", "calculated"),
        ("LIQ-04", "Less: line of credit due within 12 months", -values["FIN-009"], "SRC-001", "reported"),
        ("LIQ-05", "Less: December 2026 notes", -values["FIN-010"], "SRC-001", "reported"),
        ("LIQ-06", "Residual before potential holder put", residual_before_put, "SRC-001", "calculated"),
        ("LIQ-07", "Less: June 2031 notes classified current for June 2027 put", -potential_put, "SRC-001", "reported potential obligation"),
        ("LIQ-08", "Residual after potential holder put", residual_after_put, "SRC-001", "calculated sensitivity"),
        ("LIQ-09", "2025 operating cash used", values["FIN-011"], "SRC-002", "reported historical reference"),
    ]
    return {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "as_of_date": "2026-06-30",
        "residual_before_potential_put_usd": f"{residual_before_put:.2f}",
        "residual_after_potential_put_usd": f"{residual_after_put:.2f}",
        "rows": [
            {"line_id": line_id, "line_item": line_item, "amount_usd": f"{amount:.2f}", "source_id": source_id, "evidence_class": evidence_class}
            for line_id, line_item, amount, source_id, evidence_class in rows
        ],
        "method_limit": "This is a static public-data screen, not a borrowing-entity cash forecast. It excludes cash inflows, operating needs, capex, taxes, entity restrictions beyond the stated designation, and unlisted obligations. The holder put is a sensitivity, not an assertion that it will be exercised.",
    }


def load_values() -> dict[str, Decimal]:
    with LEDGER.open(newline="", encoding="utf-8-sig") as handle:
        rows = {row["fact_id"]: row for row in csv.DictReader(handle)}
    required = {"FIN-001", "FIN-002", "FIN-009", "FIN-010", "FIN-011", "FIN-012"}
    missing = required - set(rows)
    if missing:
        raise ValueError(f"missing liquidity facts: {sorted(missing)}")
    if any(rows[fact_id]["status"] != "PASS" for fact_id in required):
        raise ValueError("liquidity bridge requires passing fact reconciliations")
    return {fact_id: Decimal(rows[fact_id]["model_or_memo_value"]) for fact_id in required}


def main() -> int:
    payload = calculate(load_values())
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["line_id", "line_item", "amount_usd", "source_id", "evidence_class"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["rows"])
    pre_put = Decimal(payload["residual_before_potential_put_usd"])
    post_put = Decimal(payload["residual_after_potential_put_usd"])
    post_display = f"(${abs(post_put):,.2f})" if post_put < 0 else f"${post_put:,.2f}"
    print(f"Liquidity analysis: pre-put ${pre_put:,.2f}; post-put {post_display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
