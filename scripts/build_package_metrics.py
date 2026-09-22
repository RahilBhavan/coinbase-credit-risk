#!/usr/bin/env python3
"""Build a deterministic inventory of the review package's measurable surface."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
JSON_OUTPUT = ROOT / "artifacts" / "package-metrics.json"
MD_OUTPUT = ROOT / "artifacts" / "package-metrics.md"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def csv_rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def workbook_metrics() -> tuple[int, int]:
    with zipfile.ZipFile(ROOT / "outputs/credit-model.xlsx") as book:
        workbook = ElementTree.fromstring(book.read("xl/workbook.xml"))
        sheet_count = len(workbook.findall("m:sheets/m:sheet", NS))
        formula_count = 0
        for name in book.namelist():
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                formula_count += len(ElementTree.fromstring(book.read(name)).findall(".//m:f", NS))
    return sheet_count, formula_count


def regression_test_count() -> int:
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def tuple_constant_count(path: str, name: str) -> int:
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            value = ast.literal_eval(node.value)
            return len(value)
    raise ValueError(f"{name} not found in {path}")


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def passed_human_gate_count(readiness: dict[str, object]) -> int:
    return sum(row.get("status") == "PASS" for row in readiness.get("human_gates", []))


def main() -> int:
    sheet_count, formula_count = workbook_metrics()
    audit_rows = csv_rows("artifacts/workbook-audit.csv")
    decision_summary = load("artifacts/decision-view-audit.json")["summary"]
    readiness = load("artifacts/readiness-report.json")
    packet_audit = load("artifacts/committee-packet-audit.json")
    scorecard_audit = load("artifacts/reviewer-scorecard-audit.json")
    payload = {
        "schema_version": "1.0", "case_id": "MARA-CR-001", "case_version": "1.0.0",
        "workbook": {"sheet_count": sheet_count, "formula_count": formula_count,
                     "audit_check_count": len(audit_rows),
                     "audit_pass_count": sum(row.get("status") == "PASS" for row in audit_rows)},
        "decision_view": {"what_if_vector_count": decision_summary["vector_count"],
                          "collateral_call_row_count": decision_summary["collateral_call_row_count"],
                          "control_chain_count": decision_summary["control_matrix_row_count"],
                          "required_id_count": decision_summary["required_id_count"],
                          "runtime_failure_count": decision_summary["failure_count"]},
        "decision_support": {"scenario_count": len(load("artifacts/scenario-results.json")),
                             "source_count": len(csv_rows("artifacts/source-register.csv")),
                             "condition_count": len(load("data/case/conditions.json")),
                             "monitoring_rule_count": len(load("data/case/monitoring.json")["rules"]),
                             "covenant_count": len(load("data/case/covenants.json")["covenants"]),
                             "escalation_count": len(load("data/case/escalations.json")["playbooks"]),
                             "control_mapping_count": len(load("data/case/control_matrix.json")["mappings"]),
                             "model_risk_count": len(load("data/case/model_risks.json")["risks"])},
        "review": {"local_criteria_count": len(readiness["criteria"]),
                   "local_criteria_verified": sum(row["status"] == "VERIFIED_LOCAL" for row in readiness["criteria"]),
                   "human_gate_count": len(readiness["human_gates"]),
                   "human_gates_passed": passed_human_gate_count(readiness),
                   "ready_to_share": readiness["ready_to_share"],
                   "regression_test_count": regression_test_count(),
                   "committee_packet_pages": packet_audit["page_count"],
                   "committee_packet_bookmarks": len(packet_audit["bookmark_titles"]),
                   "reviewer_scorecard_pages": scorecard_audit["page_count"]},
        "package": {"integrity_manifest_file_count": tuple_constant_count("scripts/write_integrity_manifest.py", "INCLUDED"),
                    "portable_bundle_artifact_count": tuple_constant_count("scripts/build_review_bundle.py", "FILES")},
        "artifact_sha256": {path: sha256(path) for path in (
            "outputs/committee-packet.pdf", "outputs/credit-model.xlsx",
            "outputs/decision-view.html", "outputs/reviewer-scorecard.pdf")},
    }
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    w, d, s, r, p = (payload[key] for key in ("workbook", "decision_view", "decision_support", "review", "package"))
    lines = ["# Package metrics", "", "Generated from the current package artifacts. Do not edit these counts by hand.", "",
             "| Surface | Current measure |", "|---|---:|",
             f"| Workbook sheets | {w['sheet_count']} |", f"| Workbook formulas | {w['formula_count']} |",
             f"| Workbook audit checks passed | {w['audit_pass_count']} / {w['audit_check_count']} |",
             f"| Regression tests discovered | {r['regression_test_count']} |", f"| Scenarios | {s['scenario_count']} |",
             f"| Registered sources | {s['source_count']} |", f"| Blocking conditions | {s['condition_count']} |",
             f"| Governed model risks | {s['model_risk_count']} |",
             f"| Control mappings | {s['control_mapping_count']} |", f"| Decision-view required IDs | {d['required_id_count']} |",
             f"| Decision-view runtime failures | {d['runtime_failure_count']} |",
             f"| Committee packet pages / bookmarks | {r['committee_packet_pages']} / {r['committee_packet_bookmarks']} |",
             f"| Local criteria verified | {r['local_criteria_verified']} / {r['local_criteria_count']} |",
             f"| Human gates passed | {r['human_gates_passed']} / {r['human_gate_count']} |",
             f"| Ready to share | {str(r['ready_to_share']).lower()} |",
             f"| Integrity-manifest files | {p['integrity_manifest_file_count']} |",
             f"| Portable-bundle artifacts | {p['portable_bundle_artifact_count']} |", "",
             "The JSON companion contains the full machine-readable inventory and hashes of the four primary review outputs."]
    MD_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Package metrics: {w['sheet_count']} sheets, {w['audit_check_count']} workbook checks, {r['regression_test_count']} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
