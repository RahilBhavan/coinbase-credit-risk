#!/usr/bin/env python3
"""Extract and reconcile cited issuer facts from frozen SEC filings."""

from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "02-research" / "snapshots" / "2026-09-20"
OUTPUT = ROOT / "artifacts" / "issuer-fact-ledger.csv"


@dataclass(frozen=True)
class Fact:
    fact_id: str
    metric: str
    source_id: str
    filename: str
    period_end: str
    extraction: str
    locator: str
    filing_value: Decimal
    model_value: Decimal
    tolerance: Decimal
    unit: str
    precision: str


def text_content(raw: str) -> str:
    without_scripts = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.I | re.S)
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    return " ".join(html.unescape(without_tags).split())


def attributes(raw: str) -> dict[str, str]:
    return {key.lower(): html.unescape(value) for key, _, value in re.findall(r"([\w:-]+)\s*=\s*(['\"])(.*?)\2", raw, flags=re.S)}


def xbrl_value(raw: str, name: str, context: str) -> Decimal:
    pattern = re.compile(r"<ix:nonfraction\b([^>]*)>(.*?)</ix:nonfraction>", re.I | re.S)
    matches: list[tuple[int, Decimal]] = []
    for attribute_text, body in pattern.findall(raw):
        attrs = attributes(attribute_text)
        if attrs.get("name", "").lower() != name.lower() or attrs.get("contextref") != context:
            continue
        display = text_content(body).replace(",", "").replace("—", "0").strip()
        value = Decimal(display) * (Decimal(10) ** int(attrs.get("scale", "0")))
        if attrs.get("sign") == "-":
            value = -value
        decimals = int(attrs.get("decimals", "0")) if attrs.get("decimals", "0").lstrip("-").isdigit() else -999
        matches.append((decimals, value))
    if not matches:
        raise ValueError(f"missing XBRL fact {name} in {context}")
    best_precision = max(decimals for decimals, _ in matches)
    best_values = {value for decimals, value in matches if decimals == best_precision}
    if len(best_values) != 1:
        raise ValueError(f"conflicting highest-precision XBRL values for {name} in {context}: {matches}")
    return best_values.pop()


def narrative_value(text: str, pattern: str) -> Decimal:
    match = re.search(pattern, text, flags=re.I)
    if not match:
        raise ValueError(f"missing narrative pattern: {pattern}")
    return Decimal(match.group(1).replace(",", ""))


def load_model_values() -> dict[str, Decimal]:
    issuer = json.loads((ROOT / "data" / "case" / "issuer_facts.json").read_text(encoding="utf-8"))
    return {
        "cash_and_equivalents_usd": Decimal(issuer["cash_and_equivalents_usd"]),
        "bitcoin_total": Decimal(issuer["bitcoin_total"]),
        "bitcoin_unrestricted": Decimal(issuer["bitcoin_unrestricted"]),
        "debt_usd": Decimal(issuer["debt_usd"]),
    }


def build_facts() -> list[Fact]:
    q_name = "mara-20260630-10q.html"
    k_name = "mara-20251231-10k.html"
    q_raw = (SNAPSHOTS / q_name).read_text(encoding="utf-8", errors="replace")
    k_raw = (SNAPSHOTS / k_name).read_text(encoding="utf-8", errors="replace")
    q_text, k_text = text_content(q_raw), text_content(k_raw)
    model = load_model_values()
    return [
        Fact("FIN-001", "cash_and_equivalents_usd", "SRC-001", q_name, "2026-06-30", "xbrl", "us-gaap:CashAndCashEquivalentsAtCarryingValue context c-3 scale 3", xbrl_value(q_raw, "us-gaap:CashAndCashEquivalentsAtCarryingValue", "c-3"), model["cash_and_equivalents_usd"], Decimal("50000"), "USD", "rounded to nearest $0.1m in model"),
        Fact("FIN-002", "cash_designated_share", "SRC-001", q_name, "2026-06-30", "narrative", "Approximately ([0-9]+)% of cash and cash equivalents", narrative_value(q_text, r"Approximately ([0-9]+)% of cash and cash equivalents") / Decimal("100"), Decimal("0.30"), Decimal("0"), "ratio", "reported approximate percentage"),
        Fact("FIN-003", "bitcoin_total", "SRC-001", q_name, "2026-06-30", "narrative", "held approximately ([0-9,]+) bitcoin", narrative_value(q_text, r"held approximately ([0-9,]+) bitcoin"), model["bitcoin_total"], Decimal("0"), "BTC", "reported count"),
        Fact("FIN-004", "bitcoin_fair_value_usd", "SRC-001", q_name, "2026-06-30", "narrative", "total fair value of $([0-9.]+) billion", narrative_value(q_text, r"total fair value of \$([0-9.]+) billion") * Decimal("1000000000"), Decimal("2100000000"), Decimal("0"), "USD", "reported approximate amount"),
        Fact("FIN-005", "bitcoin_loaned", "SRC-001", q_name, "2026-06-30", "narrative", "loaned out a total of ([0-9,]+) bitcoin", narrative_value(q_text, r"loaned out a total of ([0-9,]+) bitcoin"), Decimal("4742"), Decimal("0"), "BTC", "reported count"),
        Fact("FIN-006", "bitcoin_pledged", "SRC-001", q_name, "2026-06-30", "xbrl", "mara:NumberOfBitcoinsCollateralized context c-3", xbrl_value(q_raw, "mara:NumberOfBitcoinsCollateralized", "c-3"), Decimal("4528"), Decimal("0"), "BTC", "reported count"),
        Fact("FIN-007", "bitcoin_unrestricted", "SRC-001", q_name, "2026-06-30", "narrative", "remaining ([0-9,]+) unrestricted bitcoin", narrative_value(q_text, r"remaining ([0-9,]+) unrestricted bitcoin"), model["bitcoin_unrestricted"], Decimal("0"), "BTC", "reported count"),
        Fact("FIN-008", "debt_usd", "SRC-001", q_name, "2026-06-30", "xbrl", "us-gaap:LongTermDebt context c-3 scale 3", xbrl_value(q_raw, "us-gaap:LongTermDebt", "c-3"), model["debt_usd"], Decimal("50000000"), "USD", "rounded to approximately $2.4bn in model"),
        Fact("FIN-009", "line_of_credit_usd", "SRC-001", q_name, "2026-06-30", "xbrl", "us-gaap:LongTermDebt context c-108 scale 6", xbrl_value(q_raw, "us-gaap:LongTermDebt", "c-108"), Decimal("150000000"), Decimal("0"), "USD", "reported amount"),
        Fact("FIN-010", "december_2026_notes_usd", "SRC-001", q_name, "2026-06-30", "xbrl", "us-gaap:LongTermDebt context c-238 scale 3", xbrl_value(q_raw, "us-gaap:LongTermDebt", "c-238"), Decimal("48100000"), Decimal("50000"), "USD", "rounded to nearest $0.1m in memo"),
        Fact("FIN-011", "operating_cash_flow_usd", "SRC-002", k_name, "2025-12-31", "xbrl", "us-gaap:NetCashProvidedByUsedInOperatingActivities context c-1 scale 3", xbrl_value(k_raw, "us-gaap:NetCashProvidedByUsedInOperatingActivities", "c-1"), Decimal("-802700000"), Decimal("50000"), "USD", "rounded to nearest $0.1m in memo"),
        Fact("FIN-012", "june_2031_notes_current_usd", "SRC-001", q_name, "2026-06-30", "xbrl", "us-gaap:LongTermDebtCurrent context c-244 scale 3", xbrl_value(q_raw, "us-gaap:LongTermDebtCurrent", "c-244"), Decimal("291600000"), Decimal("50000"), "USD", "rounded to nearest $0.1m in memo"),
        Fact("FIN-013", "debt_usd", "SRC-002", k_name, "2025-12-31", "xbrl", "us-gaap:LongTermDebt context c-4 scale 3", xbrl_value(k_raw, "us-gaap:LongTermDebt", "c-4"), Decimal("3600000000"), Decimal("50000000"), "USD", "rounded to approximately $3.6bn in memo"),
    ]


def main() -> int:
    facts = build_facts()
    fieldnames = [
        "fact_id", "metric", "source_id", "snapshot_path", "period_end", "extraction",
        "locator", "filing_value", "model_or_memo_value", "difference", "tolerance",
        "unit", "precision", "status",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for fact in facts:
            difference = abs(fact.filing_value - fact.model_value)
            writer.writerow({
                "fact_id": fact.fact_id,
                "metric": fact.metric,
                "source_id": fact.source_id,
                "snapshot_path": f"02-research/snapshots/2026-09-20/{fact.filename}",
                "period_end": fact.period_end,
                "extraction": fact.extraction,
                "locator": fact.locator,
                "filing_value": str(fact.filing_value),
                "model_or_memo_value": str(fact.model_value),
                "difference": str(difference),
                "tolerance": str(fact.tolerance),
                "unit": fact.unit,
                "precision": fact.precision,
                "status": "PASS" if difference <= fact.tolerance else "FAIL",
            })
    failures = [fact.fact_id for fact in facts if abs(fact.filing_value - fact.model_value) > fact.tolerance]
    print(f"Extracted {len(facts)} filing facts to {OUTPUT.relative_to(ROOT)}")
    print(f"Reconciliation: {len(facts) - len(failures)} PASS, {len(failures)} FAIL")
    if failures:
        print("Failures: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
