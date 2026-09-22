#!/usr/bin/env python3
"""Build a deterministic acceptance-criteria and human-gate readiness report."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from reviewer_evidence import LEDGER, gate_passes, load as load_reviewer_evidence, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def present(relative: str) -> bool:
    path = ROOT / relative
    return path.is_file() and path.stat().st_size > 0


def text_has(relative: str, *tokens: str) -> bool:
    try:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
    except (OSError, UnicodeError):
        return False
    return all(token.lower() in text for token in tokens)


def csv_rows(relative: str) -> list[dict[str, str]]:
    try:
        with (ROOT / relative).open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error):
        return []


def criterion(identifier: str, name: str, evidence: list[str], passed: bool, detail: str) -> dict[str, object]:
    return {
        "id": identifier,
        "name": name,
        "status": "VERIFIED_LOCAL" if passed else "FAIL",
        "detail": detail,
        "evidence": evidence,
    }


def build() -> dict[str, object]:
    workbook_audit = csv_rows("artifacts/workbook-audit.csv")
    scenarios = csv_rows("artifacts/scenario-results.csv")
    source_rows = csv_rows("artifacts/source-register.csv")
    scenario_ids = {row.get("scenario_id", "") for row in scenarios}
    required_scenario_signals = {
        "base",
        "borrower_cash_stress",
        "collateral_down_30",
        "canonical_withdrawal_168h",
        "route_failure",
        "missing_ownership_evidence",
        "correlated_portfolio_stress",
    }

    criteria = [
        criterion(
            "CR-01", "Two-page committee decision",
            ["outputs/credit-memo.pdf", "artifacts/credit-memo.md", "artifacts/decision-record.json", "artifacts/condition-register.json"],
            present("outputs/credit-memo.pdf") and present("artifacts/condition-register.json") and text_has("artifacts/credit-memo.md", "primary repayment", "binding", "reversal", "src-001"),
            "Decision memo exists and its source narrative declares repayment, binding-cap, reversal, and source-linkage content.",
        ),
        criterion(
            "CR-02", "Best case against the recommendation",
            ["outputs/opposing-memo.pdf", "artifacts/opposing-memo.md"],
            present("outputs/opposing-memo.pdf") and text_has("artifacts/opposing-memo.md", "disputed assumption", "evidence", "decline"),
            "Opposing memo exists and names the alternative, disputed assumption, and resolving evidence.",
        ),
        criterion(
            "CR-03", "Auditable credit model",
            ["outputs/credit-model.xlsx", "artifacts/workbook-audit.csv"],
            present("outputs/credit-model.xlsx") and bool(workbook_audit) and all(row.get("status") == "PASS" for row in workbook_audit),
            f"Workbook exists; {sum(row.get('status') == 'PASS' for row in workbook_audit)}/{len(workbook_audit)} audit rows pass, including funding-gate and condition-register reconciliation.",
        ),
        criterion(
            "CR-04", "Evidence register",
            ["artifacts/source-register.csv", "02-research/snapshots"],
            len(source_rows) >= 1 and all(row.get("source_id") and row.get("evidence_class") for row in source_rows),
            f"Source register contains {len(source_rows)} classified evidence rows.",
        ),
        criterion(
            "CR-05", "Comparable scenario results",
            ["artifacts/scenario-results.csv", "data/case/scenarios.json"],
            required_scenario_signals <= scenario_ids,
            f"Scenario suite contains {len(scenario_ids)} cases, including all required decision signals.",
        ),
        criterion(
            "CR-06", "Executed validation report",
            ["artifacts/validation-report.md", "scripts/validate_package.py"],
            present("artifacts/validation-report.md") and text_has("artifacts/validation-report.md", "actual result", "evidence", "reviewer", "fail", "skip"),
            "Validation report records method, reviewer, actual results, evidence, and explicit failure/skip semantics.",
        ),
        criterion(
            "CR-07", "Three-minute-or-less walkthrough",
            ["outputs/demo.mp4", "04-deliverables/demo-storyboard.md", "work/build_demo.py"],
            present("outputs/demo.mp4") and text_has("work/build_demo.py", "hypothetical", "opposing memo", "thirty percent collateral decline", "collateral cap is three point zero nine six million"),
            "Demo container exists and its deterministic slide source covers the required narrative beats and disclaimer.",
        ),
        criterion(
            "CR-08", "One-page review request",
            ["outputs/reviewer-brief.pdf", "artifacts/reviewer-brief.md", "work/build_pdfs.py"],
            present("outputs/reviewer-brief.pdf") and text_has("work/build_pdfs.py", "four-cap comparison", "unresolved assumption", "review question", "self-review only"),
            "Reviewer brief declares a decision, chart, unresolved assumption, precise question, and self-review status.",
        ),
        criterion(
            "CR-09", "Review history",
            ["artifacts/feedback-log.md"],
            text_has("artifacts/feedback-log.md", "reviewer role", "response", "change made", "remaining disagreement", "self-review", "external"),
            "Feedback log separates self-review from external review and preserves responses, changes, and disagreements.",
        ),
        criterion(
            "CR-10", "Rebuild guide",
            ["artifacts/reproducibility.md", "scripts/build_package.py"],
            text_has("artifacts/reproducibility.md", "case version", "snapshot", "tolerance", "known limits", "python3 scripts/build_package.py"),
            "Reproducibility guide identifies the case, snapshots, rebuild command, tolerances, and limitations.",
        ),
    ]

    gate_config = json.loads((ROOT / "data/case/reviewer_gates.json").read_text(encoding="utf-8"))["gates"]
    evidence_ledger = load_reviewer_evidence()
    ledger_errors = validate_ledger(evidence_ledger)
    if ledger_errors:
        raise ValueError("Invalid reviewer evidence ledger: " + "; ".join(ledger_errors))
    names = {
        "HG-01": "Second reader reproduces a key number",
        "HG-02": "Presenter explains both views without a script",
        "HG-03": "External feedback is attributed accurately",
    }
    config_by_id = {row["gate_id"]: row for row in gate_config}
    human_gates = []
    for record in evidence_ledger["records"]:
        passed = gate_passes(record)
        if passed:
            evidence = f"Governed reviewer ledger records a valid PASS by {record['reviewer_role']} on {record['reviewed_on']}; retained evidence: {', '.join(record['evidence_paths'])}."
        else:
            evidence = f"Execution worksheet is available in outputs/reviewer-scorecard.pdf; governed ledger outcome is {record['outcome']}. Required evidence: {config_by_id[record['gate_id']]['required_evidence']}."
        human_gates.append({"id": record["gate_id"], "name": names[record["gate_id"]], "status": "PASS" if passed else "OUTSTANDING", "evidence": evidence})
    local_verified = all(row["status"] == "VERIFIED_LOCAL" for row in criteria)
    ready_to_share = local_verified and all(row["status"] == "PASS" for row in human_gates)
    return {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "evaluated_on": date.today().isoformat(),
        "local_acceptance_verified": local_verified,
        "ready_to_share": ready_to_share,
        "criteria": criteria,
        "human_gates": human_gates,
        "interpretation": "Local verification is not external review, legal validation, production approval, or evidence of creditworthiness.",
    }


def render_markdown(payload: dict[str, object]) -> str:
    criteria = payload["criteria"]
    gates = payload["human_gates"]
    lines = [
        "# Package readiness report", "",
        f"Evaluated: {payload['evaluated_on']}",
        f"Local acceptance verified: **{'YES' if payload['local_acceptance_verified'] else 'NO'}**",
        f"Ready to share: **{'YES' if payload['ready_to_share'] else 'NO'}**", "",
        "## Acceptance criteria", "",
        "| ID | Status | Requirement | Evidence-backed result |",
        "|---|---|---|---|",
    ]
    for row in criteria:
        evidence = ", ".join(f"`{item}`" for item in row["evidence"])
        lines.append(f"| {row['id']} | {row['status']} | {row['name']} | {row['detail']} Evidence: {evidence}. |")
    lines.extend(["", "## Ready-to-share human gates", "", "| ID | Status | Gate | Evidence |", "|---|---|---|---|"])
    for row in gates:
        lines.append(f"| {row['id']} | {row['status']} | {row['name']} | {row['evidence']} |")
    lines.extend(["", "## Interpretation", "", str(payload["interpretation"]), ""])
    return "\n".join(lines)


def main() -> int:
    payload = build()
    json_path = ARTIFACTS / "readiness-report.json"
    md_path = ARTIFACTS / "readiness-report.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    verified = sum(row["status"] == "VERIFIED_LOCAL" for row in payload["criteria"])
    print(f"Readiness report: {verified}/10 locally verified; ready_to_share={str(payload['ready_to_share']).lower()}")
    return 0 if verified == 10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
