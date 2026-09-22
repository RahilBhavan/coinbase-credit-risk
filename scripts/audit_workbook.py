#!/usr/bin/env python3
"""Audit workbook inputs, formulas, and cached outputs against the decision engine."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "outputs" / "credit-model.xlsx"
REPORT = ROOT / "artifacts" / "workbook-audit.csv"
sys.path.insert(0, str(ROOT / "src"))

from credit_risk.engine import evaluate_all  # noqa: E402


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True)
class Cell:
    value: str
    formula: str | None
    kind: str | None


def load_workbook(path: Path) -> dict[str, dict[str, Cell]]:
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{{{PKG_REL}}}Relationship")
        }
        sheets: dict[str, dict[str, Cell]] = {}
        for sheet in workbook.findall(f".//{{{MAIN}}}sheet"):
            name = sheet.attrib["name"]
            rel_id = sheet.attrib[f"{{{DOC_REL}}}id"]
            target = targets[rel_id]
            member = target.lstrip("/") if target.startswith("/") else f"xl/{target}"
            root = ET.fromstring(archive.read(member))
            cells: dict[str, Cell] = {}
            for element in root.findall(f".//{{{MAIN}}}c"):
                address = element.attrib["r"]
                formula = element.findtext(f"{{{MAIN}}}f")
                value = element.findtext(f"{{{MAIN}}}v") or ""
                cells[address] = Cell(value=value, formula=formula, kind=element.attrib.get("t"))
            sheets[name] = cells
        return sheets


def number(cell: Cell) -> Decimal:
    return Decimal(cell.value)


def add_check(rows: list[dict[str, str]], check_id: str, check: str, expected: object, actual: object, evidence: str) -> None:
    expected_text, actual_text = str(expected), str(actual)
    rows.append({
        "check_id": check_id,
        "status": "PASS" if expected == actual else "FAIL",
        "check": check,
        "expected": expected_text,
        "actual": actual_text,
        "evidence": evidence,
    })


def main() -> int:
    sheets = load_workbook(WORKBOOK)
    checks: list[dict[str, str]] = []
    formula_count = sum(1 for cells in sheets.values() for cell in cells.values() if cell.formula)
    add_check(checks, "W-001", "Workbook sheet set", "Assumptions,Collateral,Conditions,Control Matrix,Covenants,Escalations,Financials,Liquidity,Model Risks,Monitoring,Portfolio,Rating,Scenarios,Sensitivity,Sources,Summary", ",".join(sorted(sheets)), "xl/workbook.xml")
    add_check(checks, "W-002", "Formula count", 265, formula_count, "xl/worksheets/*.xml")

    rating = json.loads((ROOT / "data/case/rating.json").read_text())
    for index, expected_row in enumerate(rating["factors"], start=7):
        actual = (sheets["Rating"][f"C{index}"].value, number(sheets["Rating"][f"E{index}"]), number(sheets["Rating"][f"F{index}"]))
        expected = (expected_row["factor_id"], Decimal(expected_row["weight"]), Decimal(expected_row["score"]))
        add_check(checks, f"W-R{index - 6:02d}", f"Rating factor {expected_row['factor_id']} matches case input", expected, actual, f"Rating!C{index}:F{index}")
    add_check(checks, "W-R06", "Rating weighted score", Decimal("3.1"), number(sheets["Rating"]["D15"]), "Rating!D15")
    add_check(checks, "W-R07", "Rating grade", "3 / Watchful", sheets["Rating"]["D16"].value, "Rating!D16")

    monitoring = json.loads((ROOT / "artifacts/monitoring-plan.json").read_text())
    for index, expected_row in enumerate(monitoring["rules"], start=7):
        actual = (sheets["Monitoring"][f"C{index}"].value, sheets["Monitoring"][f"G{index}"].value.lower().replace(" ", "_").replace("-", "_"))
        expected = (expected_row["monitor_id"], expected_row["status"])
        add_check(checks, f"W-M{index - 6:02d}", f"Monitoring rule {expected_row['monitor_id']} status matches plan", expected, actual, f"Monitoring!C{index}:G{index}")
    for offset, expected in enumerate((8, 2, 1, 5), start=18):
        add_check(checks, f"W-M{offset}", f"Monitoring summary D{offset}", expected, int(number(sheets["Monitoring"][f"D{offset}"])), f"Monitoring!D{offset}")

    covenant_plan = json.loads((ROOT / "artifacts/covenant-plan.json").read_text())
    for index, expected_row in enumerate(covenant_plan["covenants"], start=7):
        actual = (sheets["Covenants"][f"C{index}"].value, sheets["Covenants"][f"H{index}"].value.lower().replace(" ", "_").replace("-", "_"), sheets["Covenants"][f"M{index}"].value)
        expected = (expected_row["covenant_id"], expected_row["status"], expected_row["monitor_id"])
        add_check(checks, f"W-C{index - 6:02d}", f"Covenant {expected_row['covenant_id']} matches plan", expected, actual, f"Covenants!C{index}:M{index}")
    for offset, expected in enumerate((8, 2, 1, 5), start=18):
        add_check(checks, f"W-C{offset}", f"Covenant summary D{offset}", expected, int(number(sheets["Covenants"][f"D{offset}"])), f"Covenants!D{offset}")

    escalation = json.loads((ROOT / "artifacts/escalation-playbook.json").read_text())
    for index, expected_row in enumerate(escalation["playbooks"], start=7):
        actual = (sheets["Escalations"][f"C{index}"].value, sheets["Escalations"][f"H{index}"].value.lower().replace(" ", "_").replace("-", "_"), sheets["Escalations"][f"M{index}"].value, sheets["Escalations"][f"N{index}"].value)
        expected = (expected_row["playbook_id"], expected_row["current_status"], expected_row["monitor_id"], expected_row["covenant_id"])
        add_check(checks, f"W-E{index - 6:02d}", f"Escalation {expected_row['playbook_id']} matches response plan", expected, actual, f"Escalations!C{index}:N{index}")
    for offset, expected in enumerate((8, 3, 4, 1, 1, 5), start=19):
        add_check(checks, f"W-E{offset}", f"Escalation summary D{offset}", expected, int(number(sheets["Escalations"][f"D{offset}"])), f"Escalations!D{offset}")

    control_matrix = json.loads((ROOT / "artifacts/control-matrix.json").read_text())
    summary_values = (8, 9, 3, 4, 8)
    for row_number, expected in enumerate(summary_values, start=7):
        add_check(checks, f"W-CM-S{row_number - 6:02d}", f"Control matrix summary D{row_number}", expected, int(number(sheets["Control Matrix"][f"D{row_number}"])), f"Control Matrix!D{row_number}")
    for row_number, expected_row in enumerate(control_matrix["controls"], start=15):
        actual = (
            sheets["Control Matrix"][f"C{row_number}"].value,
            sheets["Control Matrix"][f"E{row_number}"].value,
            sheets["Control Matrix"][f"F{row_number}"].value,
            sheets["Control Matrix"][f"G{row_number}"].value,
            sheets["Control Matrix"][f"I{row_number}"].value,
            sheets["Control Matrix"][f"K{row_number}"].value,
            sheets["Control Matrix"][f"N{row_number}"].value,
        )
        expected = (
            expected_row["control_id"], ", ".join(expected_row["condition_ids"]), expected_row["condition_status"],
            expected_row["monitor_id"], expected_row["covenant_id"], expected_row["playbook_id"], expected_row["decision_owner"],
        )
        add_check(checks, f"W-CM{row_number - 14:02d}", f"Control matrix row {expected_row['control_id']} matches artifact", expected, actual, f"Control Matrix!C{row_number}:O{row_number}")

    model_risks = json.loads((ROOT / "artifacts/model-risk-register.json").read_text())
    for row_number, expected in enumerate((8, 3, 4, 4), start=7):
        add_check(checks, f"W-MR-S{row_number - 6:02d}", f"Model-risk summary D{row_number}", expected, int(number(sheets["Model Risks"][f"D{row_number}"])), f"Model Risks!D{row_number}")
    for row_number, expected_row in enumerate(model_risks["risks"], start=15):
        actual = (
            sheets["Model Risks"][f"C{row_number}"].value,
            sheets["Model Risks"][f"D{row_number}"].value,
            sheets["Model Risks"][f"F{row_number}"].value,
            sheets["Model Risks"][f"G{row_number}"].value,
            sheets["Model Risks"][f"I{row_number}"].value,
            sheets["Model Risks"][f"J{row_number}"].value,
            sheets["Model Risks"][f"N{row_number}"].value,
        )
        expected = (
            expected_row["risk_id"], expected_row["category"], expected_row["severity"], expected_row["status"],
            ", ".join(expected_row["linked_assumptions"]) or "None",
            ", ".join(expected_row["linked_conditions"]) or "None", expected_row["owner"],
        )
        add_check(checks, f"W-MR{row_number - 14:02d}", f"Model-risk row {expected_row['risk_id']} matches artifact", expected, actual, f"Model Risks!C{row_number}:O{row_number}")

    assumption_register = json.loads((ROOT / "artifacts/assumption-register.json").read_text())
    for index, expected_row in enumerate(assumption_register["assumptions"], start=45):
        actual = (sheets["Assumptions"][f"C{index}"].value, sheets["Assumptions"][f"D{index}"].value.lower(), sheets["Assumptions"][f"E{index}"].value.lower())
        expected = (expected_row["assumption_id"], expected_row["materiality"], expected_row["validation_status"])
        add_check(checks, f"W-A{index - 44:02d}", f"Assumption {expected_row['assumption_id']} governance matches register", expected, actual, f"Assumptions!C{index}:E{index}")

    conditions = json.loads((ROOT / "data/case/conditions.json").read_text())
    add_check(checks, "W-003", "Summary funding gate links to Conditions", "'Conditions'!D10", sheets["Summary"]["D16"].formula, "Summary!D16")
    add_check(checks, "W-004", "Workbook condition count", len(conditions), int(number(sheets["Conditions"]["D8"])), "Conditions!D8")
    add_check(checks, "W-005", "Workbook outstanding-condition count", len(conditions), int(number(sheets["Conditions"]["D9"])), "Conditions!D9")
    add_check(checks, "W-006", "Workbook funding gate", "BLOCKED PENDING CONDITIONS", sheets["Conditions"]["D10"].value, "Conditions!D10")
    add_check(checks, "W-007", "Workbook funding-gate formula", 'IF(D9>0,"BLOCKED PENDING CONDITIONS","CLEARED TO FUND")', sheets["Conditions"]["D10"].formula, "Conditions!D10")
    for index, expected_row in enumerate(conditions, start=14):
        actual = "|".join([
            sheets["Conditions"][f"C{index}"].value,
            sheets["Conditions"][f"G{index}"].value.lower(),
            sheets["Conditions"][f"J{index}"].value,
            sheets["Conditions"][f"K{index}"].value.lower(),
        ])
        expected = "|".join([
            expected_row["condition_id"], expected_row["evidence_status"],
            expected_row["source_id"], "yes" if expected_row["blocking"] else "no",
        ])
        add_check(checks, f"W-08{index - 13}", f"Condition {expected_row['condition_id']} matches case register", expected, actual, f"Conditions!C{index}:K{index}")

    facility = json.loads((ROOT / "data/case/facility.json").read_text())
    collateral = json.loads((ROOT / "data/case/collateral.json").read_text())[0]
    policy = json.loads((ROOT / "data/case/policy.json").read_text())
    assumption_map = {
        "D8": facility["requested_commitment_usd"], "D9": facility["funded_exposure_usd"],
        "D10": facility["accrued_amount_usd"], "D12": facility["required_coverage_ratio"],
        "D13": policy["obligor_cap_usd"], "D14": policy["recommendation_increment_usd"], "D18": collateral["quantity"],
        "D19": collateral["quoted_price_usd"], "D20": "0.02", "D21": Decimal(collateral["execution_cost_bps"]) / Decimal("10000"),
        "D22": collateral["earliest_usable_hours"], "D23": Decimal(policy["delay_cost_bps_per_hour"]) / Decimal("10000"),
        "D24": collateral["fixed_cost_usd"], "D32": policy["single_name_cap_usd"],
    }
    for index, (address, expected) in enumerate(assumption_map.items(), 10):
        add_check(checks, f"W-{index:03d}", f"Assumption {address} matches case input", Decimal(str(expected)), number(sheets["Assumptions"][address]), f"Assumptions!{address}")

    base = evaluate_all(ROOT / "data" / "case")[0]
    summary_expected = {
        "D8": base["requested_amount_usd"], "D10": base["caps_usd"]["obligor"],
        "D11": base["caps_usd"]["collateral"], "D12": base["caps_usd"]["single_name"],
        "D13": base["caps_usd"]["concentration"], "D14": base["recommended_amount_usd"],
        "D18": base["available_proceeds_usd"], "D19": base["available_proceeds_usd"],
        "D20": base["exposure_usd"], "D21": base["shortfall_usd"],
        "D22": base["recommended_pro_forma_exposure_usd"],
        "D23": base["recommended_pro_forma_coverage_surplus_usd"],
    }
    for index, (address, expected) in enumerate(summary_expected.items(), 30):
        add_check(checks, f"W-{index:03d}", f"Summary {address} matches engine base case", Decimal(expected), number(sheets["Summary"][address]), f"Summary!{address}")
    add_check(checks, "W-040", "Summary binding formula", 'IF(D9="YES",0,FLOOR(MIN(D8,D10:D13),\'Assumptions\'!D14))', sheets["Summary"]["D14"].formula, "Summary!D14")

    collateral_calls = json.loads((ROOT / "artifacts/collateral-call-ladder.json").read_text())
    for row_number, expected_row in enumerate(collateral_calls["rows"], start=38):
        actual = (
            number(sheets["Collateral"][f"C{row_number}"]),
            number(sheets["Collateral"][f"D{row_number}"]),
            sheets["Collateral"][f"F{row_number}"].value.replace(" ", "_"),
            number(sheets["Collateral"][f"H{row_number}"]),
            number(sheets["Collateral"][f"I{row_number}"]).quantize(Decimal("0.01")),
            number(sheets["Collateral"][f"L{row_number}"]),
        )
        expected = (
            Decimal(expected_row["price_stress_pct"]),
            Decimal(expected_row["available_proceeds_usd"]),
            expected_row["status"],
            Decimal(expected_row["covenant_headroom_usd"]),
            Decimal(expected_row["top_up_required_usdc"]),
            Decimal(expected_row["rounded_coverage_compliant_commitment_usd"]),
        )
        add_check(checks, f"W-CC{row_number - 37:02d}", f"Collateral-call row {row_number - 37} matches governed ladder", expected, actual, f"Collateral!C{row_number}:L{row_number}")
    add_check(checks, "W-CC08", "Exact modeled breach stress", Decimal(collateral_calls["exact_modeled_breach_price_stress_pct"]), number(sheets["Collateral"]["D46"]), "Collateral!D46")

    scenario_rows = {"base": 7, "collateral_down_30": 8, "route_delay_24h": 9, "route_failure": 10}
    for scenario in evaluate_all(ROOT / "data" / "case"):
        if scenario["scenario_id"] not in scenario_rows:
            continue
        row = scenario_rows[scenario["scenario_id"]]
        expected_values = {
            f"K{row}": scenario["available_proceeds_usd"],
            f"L{row}": scenario["caps_usd"]["collateral"],
            f"M{row}": scenario["exposure_usd"],
            f"N{row}": scenario["shortfall_usd"],
        }
        for address, expected in expected_values.items():
            check_id = f"W-{50 + row:03d}-{address[0]}"
            add_check(checks, check_id, f"Scenario {scenario['scenario_id']} {address[0]} matches engine", Decimal(expected), number(sheets["Scenarios"][address]), f"Scenarios!{address}")

    with (ROOT / "artifacts" / "issuer-fact-ledger.csv").open(newline="", encoding="utf-8") as handle:
        ledger = {row["fact_id"]: row for row in csv.DictReader(handle)}
    workbook_fact_cells = {
        "FIN-001": "E7", "FIN-002": "E8", "FIN-003": "E9", "FIN-004": "E10",
        "FIN-005": "E11", "FIN-006": "E12", "FIN-007": "E13", "FIN-008": "E17",
        "FIN-009": "E18", "FIN-010": "E19", "FIN-011": "E20", "FIN-012": "E21", "FIN-013": "E22",
    }
    for fact_id, address in workbook_fact_cells.items():
        add_check(checks, f"W-07{fact_id[-2:]}", f"Workbook {fact_id} matches fact ledger", Decimal(ledger[fact_id]["model_or_memo_value"]), number(sheets["Financials"][address]), f"Financials!{address}")

    liquidity = json.loads((ROOT / "artifacts/liquidity-analysis.json").read_text())
    for index, expected_row in enumerate(liquidity["rows"], start=7):
        actual = (sheets["Liquidity"][f"C{index}"].value, number(sheets["Liquidity"][f"E{index}"]))
        expected = (expected_row["line_id"], Decimal(expected_row["amount_usd"]))
        add_check(checks, f"W-L{index - 6:02d}", f"Liquidity line {expected_row['line_id']} matches analysis", expected, actual, f"Liquidity!C{index}:E{index}")

    surface = json.loads((ROOT / "artifacts/threshold-analysis.json").read_text())["decision_surface"]["cells"]
    surface_map = {
        (Decimal(row["collateral_quantity_usdc"]), Decimal(row["price_stress_pct"])): Decimal(row["recommended_amount_usd"])
        for row in surface
    }
    sensitivity_checks = {
        "D8": (Decimal("2000000"), Decimal("0")),
        "E10": (Decimal("4000000"), Decimal("0.02")),
        "H10": (Decimal("4000000"), Decimal("0.20")),
        "K10": (Decimal("4000000"), Decimal("0.50")),
        "K12": (Decimal("6000000"), Decimal("0.50")),
    }
    for index, (address, key) in enumerate(sensitivity_checks.items(), start=1):
        add_check(checks, f"W-S{index:02d}", f"Sensitivity {address} matches decision surface", surface_map[key], number(sheets["Sensitivity"][address]), f"Sensitivity!{address}")

    with REPORT.open("w", newline="", encoding="utf-8") as handle:
        workbook_hash = hashlib.sha256(WORKBOOK.read_bytes()).hexdigest()
        for row in checks:
            row["workbook_sha256"] = workbook_hash
        writer = csv.DictWriter(handle, fieldnames=["check_id", "status", "check", "expected", "actual", "evidence", "workbook_sha256"])
        writer.writeheader()
        writer.writerows(checks)
    failures = [row for row in checks if row["status"] == "FAIL"]
    print(f"Workbook audit: {len(checks) - len(failures)} PASS, {len(failures)} FAIL")
    for row in failures:
        print(f"{row['check_id']} {row['check']}: expected {row['expected']}, got {row['actual']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
