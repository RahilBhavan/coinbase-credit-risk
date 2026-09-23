#!/usr/bin/env python3
"""Build and verify a deterministic, portable reviewer handoff ZIP."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "review-package.zip"
FIXED_TIME = (2026, 9, 20, 12, 0, 0)
FILES = (
    "outputs/committee-packet.pdf",
    "outputs/credit-model.xlsx",
    "outputs/credit-memo.pdf",
    "outputs/opposing-memo.pdf",
    "outputs/reviewer-brief.pdf",
    "outputs/reviewer-scorecard.pdf",
    "outputs/decision-view.html",
    "outputs/demo.mp4",
    "artifacts/demo-audit.json",
    "artifacts/decision-record.json",
    "artifacts/package-metrics.json",
    "artifacts/package-metrics.md",
    "artifacts/assumption-register.csv",
    "artifacts/assumption-register.json",
    "artifacts/decision-view-audit.json",
    "artifacts/decision-lineage.csv",
    "artifacts/decision-lineage.json",
    "artifacts/diligence-plan.csv",
    "artifacts/diligence-plan.json",
    "artifacts/liquidity-analysis.csv",
    "artifacts/liquidity-analysis.json",
    "artifacts/monitoring-plan.csv",
    "artifacts/monitoring-plan.json",
    "artifacts/model-risk-register.csv",
    "artifacts/model-risk-register.json",
    "artifacts/external-review-kit.md",
    "artifacts/condition-register.csv",
    "artifacts/condition-register.json",
    "artifacts/collateral-call-ladder.csv",
    "artifacts/collateral-call-ladder.json",
    "artifacts/committee-packet-audit.json",
    "artifacts/control-matrix.csv",
    "artifacts/control-matrix.json",
    "artifacts/current-opportunity-check.md",
    "artifacts/covenant-plan.csv",
    "artifacts/covenant-plan.json",
    "artifacts/escalation-playbook.csv",
    "artifacts/escalation-playbook.json",
    "artifacts/rating-analysis.csv",
    "artifacts/rating-analysis.json",
    "artifacts/reviewer-scorecard-audit.json",
    "artifacts/reviewer-scorecard.csv",
    "artifacts/reviewer-scorecard.json",
    "artifacts/reviewer-scorecard.md",
    "artifacts/scenario-results.csv",
    "artifacts/scenario-results.json",
    "artifacts/scenario-attribution.csv",
    "artifacts/scenario-attribution.json",
    "artifacts/threshold-analysis.csv",
    "artifacts/threshold-analysis.json",
    "artifacts/source-register.csv",
    "artifacts/issuer-fact-ledger.csv",
    "artifacts/workbook-audit.csv",
    "artifacts/what-if-contract.json",
    "artifacts/validation-report.md",
    "artifacts/readiness-report.md",
    "artifacts/readiness-report.json",
    "artifacts/reproducibility.md",
    "artifacts/feedback-log.md",
    "artifacts/package-integrity.json",
    "data/review/reviewer-evidence.json",
)


START_HERE_TEMPLATE = """# Start here: MARA-CR-001 reviewer package

This is a hypothetical student credit-risk case. MARA is not represented as a Coinbase customer. The facility, collateral, policy limits, Base route, rating, and portfolio are fictional.

## Recommended review path

1. Open `outputs/committee-packet.pdf` for the decision, strongest opposing view, and reviewer question.
2. Open `outputs/decision-view.html` for scenario comparisons, decision thresholds, and the collateral-call cure ladder.
3. Inspect `outputs/credit-model.xlsx` for spreadsheet logic and sources.
4. Read `artifacts/readiness-report.md`, `artifacts/validation-report.md`, and `artifacts/package-metrics.md` before relying on any result.
5. Review `artifacts/liquidity-analysis.csv` for the public-data repayment screen and its limitations.
6. Review `artifacts/condition-register.csv`; all nine conditions currently block funding.
7. Review `artifacts/covenant-plan.csv` for the draft test, cure, consequence, owner, and linked monitoring rule.
8. Review `artifacts/escalation-playbook.csv` for response timing, draw state, decision ownership, required evidence, and exit criteria.
9. Use the live what-if lab in `outputs/decision-view.html`; its four boundary cases are declared in `artifacts/what-if-contract.json`.
10. Review `artifacts/scenario-attribution.csv` for quantified base deltas, binding drivers, and scenario-specific resolution evidence.
11. Review `artifacts/decision-lineage.csv` to trace committee claims to evidence, logic, artifacts, workbook cells, owners, and limitations.
12. Review `artifacts/diligence-plan.csv` for execution waves, parallel lanes, dependencies, decision impact, and completion evidence.
13. Review `artifacts/assumption-register.csv` for materiality, ownership, validation methods, challenge triggers, and downstream decision impact.
14. Review `artifacts/collateral-call-ladder.csv` for the modeled coverage breach point, cure amounts, and covenant-compliant commitment step-downs.
15. Review `artifacts/control-matrix.csv` to trace every pre-funding condition through its monitoring rule, draft covenant, escalation playbook, authority, and exit criteria.
16. Review `artifacts/model-risk-register.csv` for known model limitations, mitigations, evidence requirements, owners, and the required disposition if unresolved.
17. Use `artifacts/external-review-kit.md` and `outputs/reviewer-scorecard.pdf` to execute and document the independent human gates that remain outstanding without treating generated forms as validation.
19. Record completed gate evidence with `scripts/record_reviewer_gate.py`; the command rejects incomplete or unretained evidence and never treats local checks as human review.
21. Use `artifacts/reproducibility.md` to rebuild or independently reproduce the $3.09648 million collateral cap.

## Decision in one line

Conditionally approve no more than $3.0 million only after ownership, first priority, enforceable control, and the Base-to-cash route are evidenced; otherwise decline.

## Evidence boundary

Local verification is {local_state}, but the package is not legally validated, production-ready, or ready for a real credit decision. Governed readiness currently records {passed_count} of {gate_count} human gates passed and {outstanding_count} outstanding; ready to share is {ready_to_share}. Review the evidence ledger and readiness report for the exact gate-level state.

`BUNDLE-MANIFEST.json` lists every included file with its byte length and SHA-256 digest.
"""


def build_start_here(readiness: dict[str, object]) -> str:
    gates = readiness["human_gates"]
    passed_count = sum(row.get("status") == "PASS" for row in gates)
    outstanding_count = sum(row.get("status") == "OUTSTANDING" for row in gates)
    if passed_count + outstanding_count != len(gates):
        raise ValueError("readiness contains an unsupported human-gate status")
    return START_HERE_TEMPLATE.format(
        passed_count=passed_count,
        outstanding_count=outstanding_count,
        gate_count=len(gates),
        local_state="complete" if readiness.get("local_acceptance_verified") else "incomplete",
        ready_to_share="YES" if readiness.get("ready_to_share") else "NO",
    )


def evidence_boundary(readiness: dict[str, object]) -> str:
    gates = readiness["human_gates"]
    passed_count = sum(row.get("status") == "PASS" for row in gates)
    local = "locally verified" if readiness.get("local_acceptance_verified") else "local verification incomplete"
    return f"{local}; {passed_count} of {len(gates)} human gates passed; legal validation outstanding"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(bundle: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    bundle.writestr(info, data)


def main() -> int:
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Missing bundle inputs: " + ", ".join(missing))

    payloads = {name: (ROOT / name).read_bytes() for name in FILES}
    readiness = json.loads(payloads["artifacts/readiness-report.json"])
    start_here = build_start_here(readiness)
    manifest = {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "purpose": "portable reviewer handoff",
        "evidence_boundary": evidence_boundary(readiness),
        "files": {
            name: {"bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(payloads.items())
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with zipfile.ZipFile(OUTPUT, "w") as bundle:
        add_bytes(bundle, "START-HERE.md", start_here.encode())
        add_bytes(bundle, "BUNDLE-MANIFEST.json", manifest_bytes)
        for name, data in sorted(payloads.items()):
            add_bytes(bundle, name, data)

    with zipfile.ZipFile(OUTPUT) as bundle:
        corrupt = bundle.testzip()
        names = set(bundle.namelist())
        expected = set(FILES) | {"START-HERE.md", "BUNDLE-MANIFEST.json"}
        if corrupt or names != expected:
            raise SystemExit(f"Bundle verification failed: corrupt={corrupt!r}; names_match={names == expected}")
        embedded = json.loads(bundle.read("BUNDLE-MANIFEST.json"))
        for name, metadata in embedded["files"].items():
            data = bundle.read(name)
            if len(data) != metadata["bytes"] or sha256(data) != metadata["sha256"]:
                raise SystemExit(f"Bundle verification failed for {name}")

    print(f"Review bundle: {len(FILES)} artifacts + guide + manifest -> {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
