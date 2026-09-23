#!/usr/bin/env python3
"""Rebuild and verify the complete MARA-CR-001 reviewer package."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def skip_reason(command: list[str]) -> str | None:
    if command[0] != "node":
        return None
    if shutil.which("node") is None:
        return "node is not installed; keeping the committed output"
    if command[1] == "work/build_workbook.mjs" and not (ROOT / "work/node_modules/@oai/artifact-tool").exists():
        return "work/node_modules/@oai/artifact-tool (private Codex runtime package) is missing; keeping the committed outputs/credit-model.xlsx"
    return None


def run(label: str, command: list[str], env: dict[str, str]) -> None:
    reason = skip_reason(command)
    if reason:
        print(f"\n[{label}] SKIPPED: {reason}", flush=True)
        return
    print(f"\n[{label}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-demo", action="store_true", help="Regenerate the narrated demo with macOS speech synthesis and ffmpeg.")
    args = parser.parse_args()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    py = sys.executable
    steps = [
        ("filing evidence", [py, "scripts/extract_filing_facts.py"]),
        ("liquidity analysis", [py, "scripts/build_liquidity_analysis.py"]),
        ("condition register", [py, "scripts/build_condition_register.py"]),
        ("rating analysis", [py, "scripts/build_rating_analysis.py"]),
        ("base decision", [py, "-m", "credit_risk", "--case-dir", "data/case", "--scenario", "base", "--json-out", "artifacts/decision-record.json"]),
        ("monitoring plan", [py, "scripts/build_monitoring_plan.py"]),
        ("covenant plan", [py, "scripts/build_covenant_plan.py"]),
        ("escalation playbook", [py, "scripts/build_escalation_playbook.py"]),
        ("control matrix", [py, "scripts/build_control_matrix.py"]),
        ("decision lineage", [py, "scripts/build_decision_lineage.py"]),
        ("assumption register", [py, "scripts/build_assumption_register.py"]),
        ("model-risk register", [py, "scripts/build_model_risk_register.py"]),
        ("collateral-call ladder", [py, "scripts/build_collateral_call_ladder.py"]),
        ("diligence plan", [py, "scripts/build_diligence_plan.py"]),
        ("scenario suite", [py, "-m", "credit_risk", "--case-dir", "data/case", "--all-scenarios", "--json-out", "artifacts/scenario-results.json", "--csv-out", "artifacts/scenario-results.csv"]),
        ("scenario attribution", [py, "scripts/build_scenario_attribution.py"]),
        ("threshold analysis", [py, "scripts/build_threshold_analysis.py"]),
        ("what-if contract", [py, "scripts/build_what_if_contract.py"]),
        ("PDF package", [py, "work/build_pdfs.py"]),
        ("committee packet", [py, "work/build_committee_packet.py"]),
        ("workbook", ["node", "work/build_workbook.mjs"]),
        ("workbook audit", [py, "scripts/audit_workbook.py"]),
        ("regression tests", [py, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("reviewer scorecard", [py, "scripts/build_reviewer_scorecard.py"]),
        ("readiness report", [py, "scripts/build_readiness_report.py"]),
        ("decision view", [py, "work/build_decision_view.py"]),
        ("decision-view runtime audit", ["node", "scripts/audit_decision_view.mjs"]),
        ("package metrics", [py, "scripts/build_package_metrics.py"]),
    ]
    if args.with_demo:
        steps.append(("narrated demo", [py, "work/build_demo.py"]))
    steps.extend([
        ("integrity manifest", [py, "scripts/write_integrity_manifest.py"]),
        ("package validation", [py, "scripts/validate_package.py", "--write-report"]),
        ("portable review bundle", [py, "scripts/build_review_bundle.py"]),
    ])
    for label, command in steps:
        run(label, command, env)
    print("\nPackage build complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
