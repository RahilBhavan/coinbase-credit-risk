#!/usr/bin/env python3
"""Build a transparent ordinal rating bridge from declared case inputs."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "case" / "rating.json"
JSON_OUTPUT = ROOT / "artifacts" / "rating-analysis.json"
CSV_OUTPUT = ROOT / "artifacts" / "rating-analysis.csv"


def calculate(payload: dict) -> dict:
    factors = payload["factors"]
    total_weight = sum((Decimal(row["weight"]) for row in factors), Decimal("0"))
    if total_weight != Decimal("1"):
        raise ValueError(f"rating weights sum to {total_weight}, expected 1")
    ids = [row["factor_id"] for row in factors]
    if len(ids) != len(set(ids)):
        raise ValueError("rating factor IDs must be unique")
    weighted_score = sum((Decimal(row["weight"]) * Decimal(row["score"]) for row in factors), Decimal("0"))
    if any(not Decimal("1") <= Decimal(row["score"]) <= Decimal("5") for row in factors):
        raise ValueError("rating factor scores must be between 1 and 5")
    matches = [band for band in payload["scale"] if Decimal(band["minimum"]) <= weighted_score <= Decimal(band["maximum"])]
    if len(matches) != 1:
        raise ValueError(f"weighted score {weighted_score} maps to {len(matches)} rating bands")
    factor_rows = []
    for row in factors:
        factor_rows.append({**row, "weighted_contribution": str((Decimal(row["weight"]) * Decimal(row["score"])).quantize(Decimal("0.00")))})
    return {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "evidence_class": payload["evidence_class"],
        "weighted_score": str(weighted_score.quantize(Decimal("0.00"))),
        "illustrative_rating": matches[0]["grade"],
        "factors": factor_rows,
        "scale": payload["scale"],
        "method_limit": payload["method_limit"],
    }


def main() -> int:
    result = calculate(json.loads(SOURCE.read_text(encoding="utf-8")))
    JSON_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["factor_id", "factor", "weight", "score", "weighted_contribution", "evidence_ids", "rationale", "improvement_evidence", "deterioration_trigger"]
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in result["factors"]:
            writer.writerow({**row, "evidence_ids": "|".join(row["evidence_ids"])})
    print(f"Rating analysis: {len(result['factors'])} factors; score {result['weighted_score']} -> {result['illustrative_rating']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
