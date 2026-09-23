#!/usr/bin/env python3
"""Write deterministic SHA-256 metadata for the reviewable package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "package-integrity.json"
INCLUDED = (
    "artifacts/credit-memo.md",
    "artifacts/assumption-register.csv",
    "artifacts/assumption-register.json",
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
    "artifacts/decision-record.json",
    "artifacts/demo-audit.json",
    "artifacts/decision-view-audit.json",
    "artifacts/decision-lineage.csv",
    "artifacts/decision-lineage.json",
    "artifacts/diligence-plan.csv",
    "artifacts/diligence-plan.json",
    "artifacts/issuer-fact-ledger.csv",
    "artifacts/liquidity-analysis.csv",
    "artifacts/liquidity-analysis.json",
    "artifacts/monitoring-plan.csv",
    "artifacts/monitoring-plan.json",
    "artifacts/model-risk-register.csv",
    "artifacts/model-risk-register.json",
    "artifacts/external-review-kit.md",
    "artifacts/opposing-memo.md",
    "artifacts/package-metrics.json",
    "artifacts/package-metrics.md",
    "artifacts/readiness-report.json",
    "artifacts/readiness-report.md",
    "artifacts/rating-analysis.csv",
    "artifacts/rating-analysis.json",
    "artifacts/reviewer-scorecard-audit.json",
    "artifacts/reviewer-scorecard.csv",
    "artifacts/reviewer-scorecard.json",
    "artifacts/reviewer-scorecard.md",
    "artifacts/reviewer-brief.md",
    "artifacts/scenario-results.csv",
    "artifacts/scenario-results.json",
    "artifacts/scenario-attribution.csv",
    "artifacts/scenario-attribution.json",
    "artifacts/source-register.csv",
    "artifacts/threshold-analysis.csv",
    "artifacts/threshold-analysis.json",
    "artifacts/workbook-audit.csv",
    "artifacts/what-if-contract.json",
    "data/case/collateral.json",
    "data/case/assumption_governance.json",
    "data/case/conditions.json",
    "data/case/collateral_calls.json",
    "data/case/control_matrix.json",
    "data/case/covenants.json",
    "data/case/escalations.json",
    "data/case/facility.json",
    "data/case/governance.json",
    "data/case/issuer_facts.json",
    "data/case/monitoring.json",
    "data/case/model_risks.json",
    "data/case/lineage.json",
    "data/case/diligence.json",
    "data/case/policy.json",
    "data/case/portfolio.json",
    "data/case/rating.json",
    "data/case/reviewer_gates.json",
    "data/case/scenarios.json",
    "data/review/reviewer-evidence.json",
    "outputs/credit-memo.pdf",
    "outputs/credit-model.xlsx",
    "outputs/committee-packet.pdf",
    "outputs/decision-view.html",
    "outputs/demo.mp4",
    "outputs/opposing-memo.pdf",
    "outputs/reviewer-brief.pdf",
    "outputs/reviewer-scorecard.pdf",
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    missing = [name for name in INCLUDED if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Missing package files: " + ", ".join(missing))
    payload = {
        "schema_version": "1.0",
        "case_id": "MARA-CR-001",
        "case_version": "1.0.0",
        "hash_algorithm": "sha256",
        "files": {
            name: {"bytes": (ROOT / name).stat().st_size, "sha256": digest(ROOT / name)}
            for name in INCLUDED
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Integrity manifest: {len(INCLUDED)} files -> {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
