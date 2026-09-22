#!/usr/bin/env python3
"""Deterministic, standard-library validation for the credit-risk package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from reviewer_evidence import gate_passes, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = (
    "01-brief",
    "02-research",
    "03-design",
    "04-deliverables",
    "05-validation",
    "06-execution",
    "artifacts",
)
EXPECTED_OUTPUTS = (
    "credit-memo.pdf",
    "committee-packet.pdf",
    "opposing-memo.pdf",
    "credit-model.xlsx",
    "source-register.csv",
    "scenario-results.csv",
    "demo.mp4",
    "reviewer-brief.pdf",
    "reviewer-scorecard.pdf",
    "feedback-log.md",
    "reproducibility.md",
    "decision-view.html",
)
SOURCE_COLUMNS = {
    "source_id",
    "input_or_claim",
    "evidence_class",
    "source_url_or_assumption",
    "published_at",
    "retrieved_at",
    "limitations",
}
SCENARIO_COLUMNS = {
    "scenario_id",
    "requested_amount_usd",
    "recommended_amount_usd",
    "available_proceeds_usd",
    "exposure_usd",
    "shortfall_usd",
    "recommended_pro_forma_exposure_usd",
    "recommended_pro_forma_coverage_surplus_usd",
    "binding_cap",
}
FACT_CLASSES = {"reported", "observed", "calculated"}
FICTION_CLASSES = {"assumed", "simulated"}
JSON_REQUIRED_KEYS = {
    "facility.json": {"case_id", "case_version", "evidence_class", "requested_commitment_usd", "funded_exposure_usd", "required_coverage_ratio"},
    "issuer_facts.json": {"issuer_id", "as_of_date", "evidence_class", "source_id"},
    "policy.json": {"evidence_class", "maximum_commitment_usd", "single_name_cap_usd"},
    "portfolio.json": {"evidence_class", "exposures"},
    "governance.json": {"evidence_class", "illustrative_rating", "rating_rationale", "reversal_trigger", "source_coverage_rate", "preparer", "review_status"},
    "conditions.json": set(),
    "rating.json": {"evidence_class", "scale", "factors", "method_limit"},
    "monitoring.json": {"evidence_class", "activation_state", "method_limit", "rules"},
    "model_risks.json": {"evidence_class", "method_limit", "risks"},
    "covenants.json": {"evidence_class", "enforceability_status", "method_limit", "covenants"},
    "escalations.json": {"evidence_class", "activation_state", "method_limit", "playbooks"},
    "lineage.json": {"method_limit", "nodes"},
    "diligence.json": {"method_limit", "tasks"},
    "assumption_governance.json": {"method_limit", "assumptions"},
    "collateral_calls.json": {"evidence_class", "stress_levels_pct", "method_limit"},
    "control_matrix.json": {"evidence_class", "enforceability_status", "mappings", "method_limit"},
    "reviewer_gates.json": {"evidence_class", "gates", "method_limit"},
}


@dataclass(frozen=True)
class Result:
    check_id: str
    status: str
    check: str
    actual: str
    evidence: str


def result(check_id: str, status: str, check: str, actual: str, evidence: Path | str) -> Result:
    try:
        evidence_text = str(Path(evidence).resolve().relative_to(ROOT))
    except (ValueError, TypeError):
        evidence_text = str(evidence)
    return Result(check_id, status, check, actual, evidence_text)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("missing header")
        return reader.fieldnames, list(reader)


def decimal(value: str) -> Decimal:
    return Decimal(value.replace(",", "").replace("$", "").strip())


def check_structure() -> list[Result]:
    results: list[Result] = []
    missing = [name for name in REQUIRED_DIRS if not (ROOT / name).is_dir()]
    results.append(result("S-01", "FAIL" if missing else "PASS", "Required project directories exist",
                          f"Missing: {', '.join(missing)}" if missing else "All required directories exist.", ROOT))
    required_docs = (
        "README.md",
        "01-brief/decision-brief.md",
        "02-research/source-register.csv",
        "03-design/architecture.md",
        "03-design/data-model.md",
        "04-deliverables/deliverables.md",
        "05-validation/validation-plan.md",
        "06-execution/first-build.md",
        "artifacts/manifest.md",
    )
    absent = [name for name in required_docs if not (ROOT / name).is_file()]
    results.append(result("S-02", "FAIL" if absent else "PASS", "Core planning documents exist",
                          f"Missing: {', '.join(absent)}" if absent else "All core planning documents exist.", ROOT))
    return results


def check_source_register() -> list[Result]:
    path = ROOT / "02-research/source-register.csv"
    if not path.exists():
        return [result("E-01", "FAIL", "Source register schema and evidence separation", "Source register is missing.", path)]
    try:
        fields, rows = read_csv(path)
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        return [result("E-01", "FAIL", "Source register schema and evidence separation", f"Cannot parse CSV: {exc}", path)]
    missing = sorted(SOURCE_COLUMNS - set(fields))
    empty_ids = [str(index + 2) for index, row in enumerate(rows) if not row.get("source_id", "").strip()]
    duplicate_ids = sorted({row["source_id"] for row in rows if row.get("source_id") and sum(r.get("source_id") == row["source_id"] for r in rows) > 1})
    invalid_classes = sorted({row.get("evidence_class", "") for row in rows if row.get("evidence_class", "") not in FACT_CLASSES | FICTION_CLASSES})
    mixed = []
    for index, row in enumerate(rows, start=2):
        source_id = row.get("source_id", "")
        evidence_class = row.get("evidence_class", "")
        locator = row.get("source_url_or_assumption", "")
        if evidence_class in FACT_CLASSES and not (locator.startswith("https://") or source_id.startswith("ROLE-")):
            mixed.append(str(index))
        if evidence_class in FICTION_CLASSES and locator.startswith("https://"):
            mixed.append(str(index))
    problems = []
    if missing:
        problems.append("missing columns " + ", ".join(missing))
    if empty_ids:
        problems.append("empty source_id rows " + ", ".join(empty_ids))
    if duplicate_ids:
        problems.append("duplicate IDs " + ", ".join(duplicate_ids))
    if invalid_classes:
        problems.append("invalid evidence classes " + ", ".join(invalid_classes))
    if mixed:
        problems.append("fact/fiction locator mismatch rows " + ", ".join(sorted(set(mixed))))
    results = [result("E-01", "FAIL" if problems else "PASS", "Source register schema and evidence separation",
                      "; ".join(problems) if problems else f"Parsed {len(rows)} rows with unique IDs and separated fact/fiction locators.", path)]

    snapshot_failures = []
    verified = 0
    for row in rows:
        snapshot = row.get("snapshot_path", "").strip()
        expected_hash = row.get("snapshot_sha256", "").strip().lower()
        if not snapshot and not expected_hash:
            continue
        source_id = row.get("source_id", "unknown")
        if not snapshot or not expected_hash:
            snapshot_failures.append(f"{source_id}: incomplete snapshot metadata")
            continue
        snapshot_path = ROOT / snapshot
        if not snapshot_path.is_file():
            snapshot_failures.append(f"{source_id}: missing {snapshot}")
            continue
        actual_hash = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            snapshot_failures.append(f"{source_id}: SHA-256 mismatch")
            continue
        verified += 1
    results.append(result("E-02", "FAIL" if snapshot_failures else "PASS", "Frozen source snapshots match registered hashes",
                          "; ".join(snapshot_failures) if snapshot_failures else f"Verified {verified} immutable source snapshot(s).", ROOT / "02-research/snapshots"))

    artifact_register = ROOT / "artifacts/source-register.csv"
    registers_match = artifact_register.is_file() and path.read_bytes() == artifact_register.read_bytes()
    results.append(result("E-03", "PASS" if registers_match else "FAIL", "Design and artifact source registers are identical",
                          "Registers match byte-for-byte." if registers_match else "Registers have diverged or the artifact copy is missing.", artifact_register))
    return results


def check_fact_ledger() -> list[Result]:
    path = ROOT / "artifacts" / "issuer-fact-ledger.csv"
    required_columns = {
        "fact_id", "metric", "source_id", "snapshot_path", "period_end", "filing_value",
        "model_or_memo_value", "difference", "tolerance", "unit", "status",
    }
    if not path.is_file():
        return [result("E-04", "FAIL", "Frozen filing facts reconcile to model and memo values", "Issuer fact ledger is missing.", path)]
    try:
        fields, rows = read_csv(path)
        missing = sorted(required_columns - set(fields))
        failures = []
        if missing:
            failures.append("missing columns " + ", ".join(missing))
        ids = [row.get("fact_id", "") for row in rows]
        if len(ids) != len(set(ids)):
            failures.append("duplicate fact IDs")
        for row in rows:
            fact_id = row.get("fact_id", "unknown")
            try:
                difference = decimal(row["difference"])
                tolerance = decimal(row["tolerance"])
                if difference > tolerance or row.get("status") != "PASS":
                    failures.append(f"{fact_id}: reconciliation failed")
            except (KeyError, InvalidOperation):
                failures.append(f"{fact_id}: invalid numeric reconciliation fields")
            snapshot = row.get("snapshot_path", "")
            if not snapshot or not (ROOT / snapshot).is_file():
                failures.append(f"{fact_id}: snapshot missing")

        issuer = json.loads((ROOT / "data/case/issuer_facts.json").read_text(encoding="utf-8"))
        by_metric = {row["metric"]: row for row in rows if row.get("period_end") == issuer.get("as_of_date")}
        for metric in ("cash_and_equivalents_usd", "bitcoin_total", "bitcoin_unrestricted", "debt_usd"):
            row = by_metric.get(metric)
            if not row:
                failures.append(f"missing current model metric {metric}")
                continue
            if decimal(str(issuer[metric])) != decimal(row["model_or_memo_value"]):
                failures.append(f"{metric}: ledger does not match issuer_facts.json")
        actual = "; ".join(failures) if failures else f"Reconciled {len(rows)} extracted filing facts; all model differences are within declared tolerances."
        return [result("E-04", "FAIL" if failures else "PASS", "Frozen filing facts reconcile to model and memo values", actual, path)]
    except (OSError, csv.Error, UnicodeError, ValueError, json.JSONDecodeError, KeyError, InvalidOperation) as exc:
        return [result("E-04", "FAIL", "Frozen filing facts reconcile to model and memo values", f"Cannot validate ledger: {exc}", path)]


def check_workbook_audit() -> list[Result]:
    path = ROOT / "artifacts" / "workbook-audit.csv"
    workbook_path = ROOT / "outputs" / "credit-model.xlsx"
    if not path.is_file() or not workbook_path.is_file():
        return [result("E-05", "FAIL", "Workbook audit matches the current workbook", "Workbook or audit report is missing.", path)]
    try:
        _, rows = read_csv(path)
        current_hash = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
        failures = [row.get("check_id", "unknown") for row in rows if row.get("status") != "PASS"]
        hashes = {row.get("workbook_sha256", "") for row in rows}
        problems = []
        if not rows:
            problems.append("audit contains no checks")
        if failures:
            problems.append("failed checks: " + ", ".join(failures))
        if hashes != {current_hash}:
            problems.append("audit hash does not match current workbook")
        actual = "; ".join(problems) if problems else f"Verified {len(rows)} passing checks against workbook SHA-256 {current_hash}."
        return [result("E-05", "FAIL" if problems else "PASS", "Workbook audit matches the current workbook", actual, path)]
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        return [result("E-05", "FAIL", "Workbook audit matches the current workbook", f"Cannot validate workbook audit: {exc}", path)]


def check_integrity_manifest() -> list[Result]:
    path = ROOT / "artifacts" / "package-integrity.json"
    if not path.is_file():
        return [result("E-06", "FAIL", "Package integrity manifest matches review files", "Integrity manifest is missing.", path)]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        files = payload.get("files", {})
        problems = []
        if payload.get("hash_algorithm") != "sha256" or not isinstance(files, dict) or not files:
            problems.append("invalid manifest schema")
        for name, metadata in files.items():
            target = ROOT / name
            if not target.is_file():
                problems.append(f"missing {name}")
                continue
            data = target.read_bytes()
            if metadata.get("bytes") != len(data):
                problems.append(f"size mismatch {name}")
            if metadata.get("sha256") != hashlib.sha256(data).hexdigest():
                problems.append(f"hash mismatch {name}")
        actual = "; ".join(problems) if problems else f"Verified SHA-256 and byte length for {len(files)} package file(s)."
        return [result("E-06", "FAIL" if problems else "PASS", "Package integrity manifest matches review files", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError) as exc:
        return [result("E-06", "FAIL", "Package integrity manifest matches review files", f"Cannot validate integrity manifest: {exc}", path)]


def check_threshold_analysis() -> list[Result]:
    path = ROOT / "artifacts" / "threshold-analysis.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        declines = {key: decimal(value) for key, value in payload["max_price_decline_for_target"].items()}
        quantities = {key: decimal(value) for key, value in payload["required_collateral_quantity_for_target"].items()}
        required_targets = {"2000000", "3000000", "4000000", "5000000"}
        problems = []
        if set(declines) != required_targets or set(quantities) != required_targets:
            problems.append("target set is incomplete")
        ordered = ["2000000", "3000000", "4000000", "5000000"]
        if all(key in quantities for key in ordered) and any(quantities[left] >= quantities[right] for left, right in zip(ordered, ordered[1:])):
            problems.append("required collateral is not increasing with target limit")
        if all(key in declines for key in ordered) and any(declines[left] < declines[right] for left, right in zip(ordered, ordered[1:])):
            problems.append("price tolerance increases with a higher target limit")
        if payload.get("maximum_non_collateral_limit_name") != "concentration" or decimal(payload.get("maximum_non_collateral_limit_usd", "0")) != Decimal("4000000"):
            problems.append("non-collateral limiting cap is not the expected $4m concentration cap")
        if payload.get("full_request_feasible_under_current_caps") is not False:
            problems.append("full-request feasibility should be false under current caps")
        surface = payload.get("decision_surface", {})
        cells = surface.get("cells", [])
        if len(cells) != 40:
            problems.append("decision surface does not contain 40 cells")
        else:
            grid = {(decimal(row["collateral_quantity_usdc"]), decimal(row["price_stress_pct"])): decimal(row["recommended_amount_usd"]) for row in cells}
            for quantity in map(decimal, surface.get("quantity_axis_usdc", [])):
                limits = [grid[(quantity, decimal(stress))] for stress in surface.get("price_stress_axis_pct", [])]
                if any(left < right for left, right in zip(limits, limits[1:])):
                    problems.append(f"recommendation increases with stress at {quantity} USDC")
            for stress in map(decimal, surface.get("price_stress_axis_pct", [])):
                limits = [grid[(decimal(quantity), stress)] for quantity in surface.get("quantity_axis_usdc", [])]
                if any(left > right for left, right in zip(limits, limits[1:])):
                    problems.append(f"recommendation decreases with quantity at {stress} stress")
        actual = "; ".join(problems) if problems else "Verified four break-even targets, the $4m concentration ceiling, and a monotonic 40-cell decision surface."
        return [result("E-07", "FAIL" if problems else "PASS", "Threshold analysis is internally consistent", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, InvalidOperation, TypeError) as exc:
        return [result("E-07", "FAIL", "Threshold analysis is internally consistent", f"Cannot validate threshold analysis: {exc}", path)]


def check_machine_readable_files() -> list[Result]:
    results: list[Result] = []
    csv_paths = sorted(path for path in ROOT.rglob("*.csv") if "prior-plans" not in path.parts)
    csv_failures = []
    for path in csv_paths:
        try:
            fields, _ = read_csv(path)
            if len(fields) != len(set(fields)):
                csv_failures.append(f"{path.relative_to(ROOT)}: duplicate headers")
        except (OSError, csv.Error, UnicodeError, ValueError) as exc:
            csv_failures.append(f"{path.relative_to(ROOT)}: {exc}")
    results.append(result("D-01", "FAIL" if csv_failures else "PASS", "Project CSV files parse with unique headers",
                          "; ".join(csv_failures) if csv_failures else f"Parsed {len(csv_paths)} CSV file(s).", ROOT))
    json_paths = sorted(ROOT.rglob("*.json"))
    json_failures = []
    for path in json_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            required = JSON_REQUIRED_KEYS.get(path.name)
            if required:
                if not isinstance(payload, dict):
                    json_failures.append(f"{path.relative_to(ROOT)}: expected object")
                else:
                    missing = sorted(required - set(payload))
                    if missing:
                        json_failures.append(f"{path.relative_to(ROOT)}: missing keys {', '.join(missing)}")
                    if path.name == "policy.json" and not ({"btc_concentration_limit", "collateral_asset_concentration_limit"} & set(payload)):
                        json_failures.append(f"{path.relative_to(ROOT)}: missing a collateral concentration limit")
            if path.name in {"collateral.json", "conditions.json", "scenarios.json"}:
                if not isinstance(payload, list) or not payload:
                    json_failures.append(f"{path.relative_to(ROOT)}: expected non-empty array")
            records = payload if isinstance(payload, list) else [payload]
            for index, record in enumerate(records):
                if isinstance(record, dict) and "evidence_class" in record and record["evidence_class"] not in FACT_CLASSES | FICTION_CLASSES:
                    json_failures.append(f"{path.relative_to(ROOT)}[{index}]: invalid evidence_class")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            json_failures.append(f"{path.relative_to(ROOT)}: {exc}")
    status = "SKIP" if not json_paths else ("FAIL" if json_failures else "PASS")
    actual = "No JSON artifacts are present." if not json_paths else ("; ".join(json_failures) if json_failures else f"Parsed {len(json_paths)} JSON file(s).")
    results.append(result("D-02", status, "Project JSON files parse", actual, ROOT))
    return results


def check_cross_artifact_consistency() -> list[Result]:
    source_path = ROOT / "02-research/source-register.csv"
    issuer_path = ROOT / "data/case/issuer_facts.json"
    facility_path = ROOT / "data/case/facility.json"
    if not issuer_path.exists() and not facility_path.exists():
        return [result("X-01", "SKIP", "Case inputs agree with registered evidence and project decision",
                       "Case input files are not yet available.", ROOT / "data/case")]
    failures = []
    if issuer_path.exists() and source_path.exists():
        try:
            issuer = json.loads(issuer_path.read_text(encoding="utf-8"))
            _, source_rows = read_csv(source_path)
            registered_ids = {row.get("source_id", "") for row in source_rows}
            source_id = issuer.get("source_id") if isinstance(issuer, dict) else None
            if not source_id or source_id not in registered_ids:
                failures.append(f"issuer source_id {source_id!r} is absent from the source register")
            if isinstance(issuer, dict) and issuer.get("evidence_class") != "reported":
                failures.append("issuer facts are not labeled reported")
        except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
            failures.append(f"could not compare issuer facts and source register: {exc}")
    if facility_path.exists():
        try:
            facility = json.loads(facility_path.read_text(encoding="utf-8"))
            amount = decimal(str(facility["requested_commitment_usd"]))
            if amount != Decimal("5000000"):
                failures.append(f"requested commitment is {amount}, expected the designed $5,000,000 case")
            if facility.get("evidence_class") not in FICTION_CLASSES:
                failures.append("facility is not labeled assumed or simulated")
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, InvalidOperation, TypeError) as exc:
            failures.append(f"could not validate facility decision input: {exc}")
    results = [result("X-01", "FAIL" if failures else "PASS", "Case inputs agree with registered evidence and project decision",
                      "; ".join(failures) if failures else "Issuer source is registered, facility is fictional, and requested commitment is $5,000,000.", ROOT / "data/case")]
    guide_path = ROOT / "artifacts/reproducibility.md"
    collateral_path = ROOT / "data/case/collateral.json"
    if not guide_path.exists() or not collateral_path.exists():
        results.append(result("X-02", "SKIP", "Executable collateral case agrees with reproducibility guide",
                              "The guide or collateral input is unavailable.", ROOT / "artifacts"))
        return results
    comparison_failures = []
    try:
        guide = guide_path.read_text(encoding="utf-8")
        collateral = json.loads(collateral_path.read_text(encoding="utf-8"))
        assets = {str(row.get("asset", "")).upper() for row in collateral if isinstance(row, dict)} if isinstance(collateral, list) else set()
        stated_assets = {
            match.upper()
            for match in re.findall(r"quantity:\s*[^;\n]*?fictional\s+([A-Z0-9-]+)", guide, flags=re.IGNORECASE)
        }
        if stated_assets and assets != stated_assets:
            comparison_failures.append(f"guide collateral {sorted(stated_assets)} differs from executable collateral {sorted(assets)}")
        facility = json.loads(facility_path.read_text(encoding="utf-8")) if facility_path.exists() else {}
        case_id = facility.get("case_id") if isinstance(facility, dict) else None
        guide_case_ids = set(re.findall(r"\bMARA-[A-Z0-9-]+\b", guide))
        if case_id and guide_case_ids and case_id not in guide_case_ids:
            comparison_failures.append(f"executable case_id {case_id!r} differs from guide case ID(s) {sorted(guide_case_ids)}")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        comparison_failures.append(f"could not compare collateral case and guide: {exc}")
    results.append(result("X-02", "FAIL" if comparison_failures else "PASS", "Executable collateral case agrees with reproducibility guide",
                          "; ".join(comparison_failures) if comparison_failures else "Case ID and collateral asset agree.", guide_path))
    return results


def check_decision_record() -> list[Result]:
    path = ROOT / "artifacts" / "decision-record.json"
    required = {
        "case_id", "case_version", "scenario_id", "decision", "requested_amount_usd",
        "recommended_amount_usd", "caps_usd", "binding_cap", "hard_blockers", "conditions",
        "available_proceeds_usd", "shortfall_usd", "illustrative_rating", "rating_rationale",
        "reversal_trigger", "source_coverage_rate", "source_coverage_scope", "preparer",
        "review_status", "calculation_trace",
        "condition_register", "outstanding_blocking_conditions", "funding_gate_status",
        "rating_score", "rating_factors", "rating_scale", "rating_method_limit",
        "exposure_basis", "recommended_pro_forma_exposure_usd", "recommended_pro_forma_coverage_surplus_usd",
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        missing = sorted(required - set(payload))
        problems = ["missing fields " + ", ".join(missing)] if missing else []
        trace = payload.get("calculation_trace", {})
        if trace.get("rounded_recommended_amount_usd") != payload.get("recommended_amount_usd"):
            problems.append("calculation trace does not reproduce recommended amount")
        if decimal(payload.get("source_coverage_rate", "0")) != Decimal("1"):
            problems.append("material public-fact source coverage is not 100%")
        if "outstanding" not in payload.get("review_status", "").lower():
            problems.append("review status does not preserve outstanding independent review")
        lot_total = sum((decimal(row["available_proceeds_usd"]) for row in payload.get("collateral_lots", [])), Decimal("0"))
        if lot_total != decimal(payload.get("available_proceeds_usd", "0")):
            problems.append("lot proceeds do not sum to total available proceeds")
        condition_ids = {row.get("condition_id") for row in payload.get("condition_register", [])}
        outstanding = set(payload.get("outstanding_blocking_conditions", []))
        if len(condition_ids) != 9 or None in condition_ids:
            problems.append("condition register does not contain nine unique IDs")
        if payload.get("decision") != "decline" and outstanding and payload.get("funding_gate_status") != "blocked_pending_conditions":
            problems.append("conditional decision does not preserve the pre-funding gate")
        if "requested fully drawn recovery case" not in payload.get("exposure_basis", ""):
            problems.append("recovery exposure basis is not explicit")
        pro_forma = decimal(payload.get("recommended_pro_forma_exposure_usd", "0"))
        facility = json.loads((ROOT / "data/case/facility.json").read_text(encoding="utf-8"))
        accrued = decimal(facility["accrued_amount_usd"])
        expected_pro_forma = decimal(payload.get("recommended_amount_usd", "0")) + accrued if payload.get("decision") != "decline" else Decimal("0")
        if pro_forma != expected_pro_forma:
            problems.append("recommended pro forma exposure does not reconcile")
        expected_surplus = max(Decimal("0"), decimal(payload.get("available_proceeds_usd", "0")) - pro_forma)
        if decimal(payload.get("recommended_pro_forma_coverage_surplus_usd", "0")) != expected_surplus:
            problems.append("recommended pro forma coverage surplus does not reconcile")
        factors = payload.get("rating_factors", [])
        contributions = sum((decimal(row["weighted_contribution"]) for row in factors), Decimal("0"))
        if len(factors) != 5 or contributions != decimal(payload.get("rating_score", "0")):
            problems.append("rating factors do not reconcile to the rating score")
        actual = "; ".join(problems) if problems else "Decision record includes governance fields and a reconciled calculation trace."
        return [result("X-03", "FAIL" if problems else "PASS", "Decision record satisfies the declared output contract", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, InvalidOperation, KeyError, TypeError) as exc:
        return [result("X-03", "FAIL", "Decision record satisfies the declared output contract", f"Cannot validate decision record: {exc}", path)]


def check_rating_analysis() -> list[Result]:
    path = ROOT / "artifacts" / "rating-analysis.json"
    csv_path = ROOT / "artifacts" / "rating-analysis.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, rows = read_csv(csv_path)
        governance = json.loads((ROOT / "data/case/governance.json").read_text(encoding="utf-8"))
        factors = payload.get("factors", [])
        problems = []
        if len(factors) != 5 or len(rows) != 5:
            problems.append("expected five synchronized rating factors")
        if sum((decimal(row["weight"]) for row in factors), Decimal("0")) != Decimal("1"):
            problems.append("rating weights do not sum to 1")
        if sum((decimal(row["weighted_contribution"]) for row in factors), Decimal("0")) != decimal(payload.get("weighted_score", "0")):
            problems.append("factor contributions do not sum to weighted score")
        if payload.get("weighted_score") != "3.10" or payload.get("illustrative_rating") != "3 / Watchful":
            problems.append("base rating does not equal declared 3.10 / Watchful result")
        if payload.get("illustrative_rating") != governance.get("illustrative_rating"):
            problems.append("rating output differs from governance record")
        if "not statistically calibrated" not in payload.get("method_limit", ""):
            problems.append("method limitation is not explicit")
        actual = "; ".join(problems) if problems else "Five weighted factors reconcile to 3.10 / Watchful with explicit evidence and method limits."
        return [result("X-07", "FAIL" if problems else "PASS", "Illustrative rating bridge is transparent and reconciled", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, InvalidOperation, KeyError, TypeError) as exc:
        return [result("X-07", "FAIL", "Illustrative rating bridge is transparent and reconciled", f"Cannot validate rating analysis: {exc}", path)]


def check_monitoring_plan() -> list[Result]:
    path = ROOT / "artifacts" / "monitoring-plan.json"
    csv_path = ROOT / "artifacts" / "monitoring-plan.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        rules = payload.get("rules", [])
        problems = []
        ids = [row.get("monitor_id") for row in rules]
        if len(rules) != 8 or len(ids) != len(set(ids)) or len(csv_rows) != len(rules):
            problems.append("expected eight unique synchronized monitoring rules")
        expected = {"pass_projection": 2, "pre_funding_blocked": 1, "not_measured": 5}
        actual_counts = {status: sum(row.get("status") == status for row in rules) for status in expected}
        if actual_counts != expected:
            problems.append(f"status counts differ: {actual_counts}")
        if payload.get("activation_state") != "pre_funding_blocked":
            problems.append("monitoring activation does not preserve the blocked pre-funding state")
        if any(not row.get("owner_role") or not row.get("breach_action") or not row.get("escalation") for row in rules):
            problems.append("a monitoring rule lacks an owner, breach action, or escalation")
        if "not executed borrower reporting" not in payload.get("method_limit", ""):
            problems.append("method limitation does not distinguish design from observed monitoring")
        actual = "; ".join(problems) if problems else "Eight owned monitoring rules separate projected passes, the pre-funding blocker, and five unmeasured private-evidence metrics."
        return [result("X-08", "FAIL" if problems else "PASS", "Monitoring design is actionable without implying observed compliance", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-08", "FAIL", "Monitoring design is actionable without implying observed compliance", f"Cannot validate monitoring plan: {exc}", path)]


def check_liquidity_analysis() -> list[Result]:
    path = ROOT / "artifacts" / "liquidity-analysis.json"
    csv_path = ROOT / "artifacts" / "liquidity-analysis.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        rows = payload.get("rows", [])
        problems = []
        if len(rows) != 9 or len(csv_rows) != 9:
            problems.append("expected nine synchronized liquidity bridge rows")
        if payload.get("residual_before_potential_put_usd") != "96810000.00":
            problems.append("pre-put residual does not equal $96.81 million")
        if payload.get("residual_after_potential_put_usd") != "-194790000.00":
            problems.append("post-put residual does not equal negative $194.79 million")
        if any(row.get("source_id") not in {"SRC-001", "SRC-002"} for row in rows):
            problems.append("liquidity row lacks a registered public source")
        limit = payload.get("method_limit", "")
        if "not a borrowing-entity cash forecast" not in limit or "sensitivity" not in limit:
            problems.append("method limitation does not preserve forecast and holder-put boundaries")
        actual = "; ".join(problems) if problems else "Nine-row public-data bridge reconciles to $96.81m before and negative $194.79m after the potential holder put, with forecast limitations explicit."
        return [result("X-09", "FAIL" if problems else "PASS", "Public-data liquidity bridge is reconciled and bounded", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-09", "FAIL", "Public-data liquidity bridge is reconciled and bounded", f"Cannot validate liquidity analysis: {exc}", path)]


def check_condition_register() -> list[Result]:
    path = ROOT / "artifacts" / "condition-register.json"
    csv_path = ROOT / "artifacts" / "condition-register.csv"
    required_fields = {
        "condition_id", "category", "requirement", "evidence_class", "evidence_status",
        "blocking", "owner_role", "timing", "verification_method", "source_id",
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        fields, rows = read_csv(csv_path)
        problems = []
        conditions = payload.get("conditions", [])
        ids = [row.get("condition_id") for row in conditions]
        if len(conditions) != 9 or len(ids) != len(set(ids)):
            problems.append("expected nine unique conditions")
        if set(fields) != required_fields or len(rows) != len(conditions):
            problems.append("CSV schema or row count differs from JSON")
        if payload.get("funding_gate_status") != "blocked_pending_conditions":
            problems.append("current evidence set does not preserve blocked funding state")
        if set(payload.get("outstanding_blocking_conditions", [])) != set(ids):
            problems.append("outstanding blocker list does not cover all current conditions")
        if any(row.get("evidence_status") != "outstanding" or row.get("blocking") is not True for row in conditions):
            problems.append("a current condition is not explicitly blocking and outstanding")
        actual = "; ".join(problems) if problems else "Nine uniquely identified pre-funding conditions remain blocking and outstanding in synchronized CSV and JSON artifacts."
        return [result("X-06", "FAIL" if problems else "PASS", "Condition register preserves the pre-funding evidence gate", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, ValueError, TypeError) as exc:
        return [result("X-06", "FAIL", "Condition register preserves the pre-funding evidence gate", f"Cannot validate condition register: {exc}", path)]


def check_covenant_plan() -> list[Result]:
    path = ROOT / "artifacts" / "covenant-plan.json"
    csv_path = ROOT / "artifacts" / "covenant-plan.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        monitoring = json.loads((ROOT / "artifacts/monitoring-plan.json").read_text(encoding="utf-8"))
        rows = payload.get("covenants", [])
        problems = []
        ids = [row.get("covenant_id") for row in rows]
        monitor_ids = [row.get("monitor_id") for row in rows]
        expected_monitors = {row.get("monitor_id") for row in monitoring.get("rules", [])}
        if len(rows) != 8 or len(ids) != len(set(ids)) or len(csv_rows) != len(rows):
            problems.append("expected eight unique synchronized covenant controls")
        if len(monitor_ids) != len(set(monitor_ids)) or set(monitor_ids) != expected_monitors:
            problems.append("covenants do not map one-to-one to monitoring rules")
        if payload.get("enforceability_status") != "draft_only":
            problems.append("covenant package does not preserve draft-only enforceability")
        if any(not row.get("cure_period") or not row.get("breach_consequence") or not row.get("owner_role") for row in rows):
            problems.append("a covenant lacks cure, consequence, or ownership")
        summary = payload.get("summary", {})
        if summary != {"covenant_count": 8, "projected_pass_count": 2, "pre_funding_blocked_count": 1, "not_measured_count": 5}:
            problems.append(f"covenant status counts differ: {summary}")
        limit = payload.get("method_limit", "")
        if "not executed" not in limit or "not" not in limit.lower() or "Coinbase policy" not in limit:
            problems.append("method limitation does not preserve execution, legal-review, and policy boundaries")
        actual = "; ".join(problems) if problems else "Eight draft-only covenants map one-to-one to monitoring rules with explicit cure and breach consequences."
        return [result("X-10", "FAIL" if problems else "PASS", "Covenant package is complete, synchronized, and bounded", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-10", "FAIL", "Covenant package is complete, synchronized, and bounded", f"Cannot validate covenant plan: {exc}", path)]


def check_escalation_playbook() -> list[Result]:
    path = ROOT / "artifacts" / "escalation-playbook.json"
    csv_path = ROOT / "artifacts" / "escalation-playbook.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        monitoring = json.loads((ROOT / "artifacts/monitoring-plan.json").read_text(encoding="utf-8"))
        covenants = json.loads((ROOT / "artifacts/covenant-plan.json").read_text(encoding="utf-8"))
        rows = payload.get("playbooks", [])
        problems = []
        ids = [row.get("playbook_id") for row in rows]
        monitor_ids = [row.get("monitor_id") for row in rows]
        covenant_ids = [row.get("covenant_id") for row in rows]
        expected_monitors = {row.get("monitor_id") for row in monitoring.get("rules", [])}
        expected_covenants = {row.get("covenant_id") for row in covenants.get("covenants", [])}
        linked = {row.get("covenant_id"): row.get("monitor_id") for row in covenants.get("covenants", [])}
        if len(rows) != 8 or len(ids) != len(set(ids)) or len(csv_rows) != len(rows):
            problems.append("expected eight unique synchronized response playbooks")
        if len(monitor_ids) != len(set(monitor_ids)) or set(monitor_ids) != expected_monitors:
            problems.append("playbooks do not map one-to-one to monitoring rules")
        if len(covenant_ids) != len(set(covenant_ids)) or set(covenant_ids) != expected_covenants:
            problems.append("playbooks do not map one-to-one to covenants")
        if any(linked.get(row.get("covenant_id")) != row.get("monitor_id") for row in rows):
            problems.append("covenant and monitoring links disagree")
        required = ("severity_on_trigger", "response_sla", "draw_state_on_trigger", "decision_owner", "required_evidence", "exit_criteria", "current_response")
        if any(any(not row.get(field) for field in required) for row in rows):
            problems.append("a response path lacks timing, authority, evidence, or closure criteria")
        expected_summary = {"playbook_count": 8, "critical_count": 3, "high_count": 4, "moderate_count": 1, "blocked_current_count": 1, "private_evidence_required_count": 5}
        if payload.get("summary") != expected_summary:
            problems.append(f"response summary differs: {payload.get('summary')}")
        if payload.get("activation_state") != "pre_funding_blocked" or "No incident is open" not in payload.get("method_limit", ""):
            problems.append("current-state boundary does not distinguish design from an observed incident")
        actual = "; ".join(problems) if problems else "Eight response playbooks map one-to-one across monitoring and covenants with explicit timing, authority, evidence, and exit criteria."
        return [result("X-11", "FAIL" if problems else "PASS", "Escalation playbook is synchronized, actionable, and bounded", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-11", "FAIL", "Escalation playbook is synchronized, actionable, and bounded", f"Cannot validate escalation playbook: {exc}", path)]


def check_what_if_contract() -> list[Result]:
    path = ROOT / "artifacts" / "what-if-contract.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        runtime_audit = json.loads((ROOT / "artifacts" / "decision-view-audit.json").read_text(encoding="utf-8"))
        problems = []
        vectors = payload.get("test_vectors", [])
        if [row.get("vector_id") for row in vectors] != ["base", "price_down_50", "route_delay_24h", "ownership_blocker"]:
            problems.append("expected four ordered boundary vectors")
        base = vectors[0].get("expected", {}) if vectors else {}
        blocked = vectors[-1].get("expected", {}) if vectors else {}
        if base.get("available_proceeds_usd") != "3870600.00" or base.get("recommended_amount_usd") != "3000000.00":
            problems.append("base vector does not reconcile to the decision record")
        if blocked.get("recommended_amount_usd") != "0.00" or blocked.get("binding_cap") != "hard_blocker":
            problems.append("hard-blocker vector does not force a decline and zero recommendation")
        expected_bounds = {"quantity_usdc", "price_stress_pct", "additional_route_delay_hours", "execution_cost_bps"}
        if set(payload.get("bounds", {})) != expected_bounds:
            problems.append("simulator bounds are incomplete")
        limit = payload.get("method_limit", "")
        if "not a credit approval" not in limit or "authority to fund" not in limit:
            problems.append("simulator method limit omits approval or funding boundaries")
        if runtime_audit.get("summary") != {"vector_count": 4, "collateral_call_row_count": 7, "control_matrix_row_count": 8, "model_risk_row_count": 8, "human_gate_count": 3, "required_id_count": 79, "failure_count": 0}:
            problems.append("shipped JavaScript runtime audit is missing or failed")
        outstanding_count = runtime_audit.get("readiness_result", {}).get("outstanding_count")
        actual = "; ".join(problems) if problems else f"Four engine-derived boundary vectors, seven collateral-call rows, eight control chains, eight filterable model risks, and three governed human gates ({outstanding_count} outstanding) reconcile in the shipped JavaScript; all 79 interactive IDs are unique."
        return [result("X-12", "FAIL" if problems else "PASS", "Interactive what-if contract is bounded and reconciled", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, IndexError) as exc:
        return [result("X-12", "FAIL", "Interactive what-if contract is bounded and reconciled", f"Cannot validate what-if contract: {exc}", path)]


def check_scenario_attribution() -> list[Result]:
    path = ROOT / "artifacts" / "scenario-attribution.json"
    csv_path = ROOT / "artifacts" / "scenario-attribution.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        scenarios = json.loads((ROOT / "artifacts" / "scenario-results.json").read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        problems = []
        if len(rows) != 11 or len(csv_rows) != 11 or {row.get("scenario_id") for row in rows} != {row.get("scenario_id") for row in scenarios}:
            problems.append("attribution does not cover all eleven engine scenarios")
        if {row.get("severity_rank") for row in rows} != set(range(1, 12)):
            problems.append("severity ranks are not unique and complete")
        expected_summary = {"scenario_count": 11, "same_limit_count": 2, "reduced_limit_count": 5, "decline_count": 4, "hard_blocker_scenario_count": 3, "maximum_recommendation_loss_usd": "3000000.00"}
        if payload.get("summary") != expected_summary:
            problems.append(f"attribution summary differs: {payload.get('summary')}")
        if any(not row.get("primary_driver") or not row.get("resolution_evidence") for row in rows):
            problems.append("a scenario lacks a driver or resolution-evidence path")
        limit = payload.get("method_limit", "")
        if "not a probability" not in limit or "new decision rule" not in limit:
            problems.append("attribution method limit omits predictive or decision-rule boundaries")
        actual = "; ".join(problems) if problems else "All eleven scenarios carry quantified base deltas, unique severity ranks, binding drivers, and resolution evidence without adding a new decision rule."
        return [result("X-13", "FAIL" if problems else "PASS", "Scenario attribution is complete, quantified, and bounded", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-13", "FAIL", "Scenario attribution is complete, quantified, and bounded", f"Cannot validate scenario attribution: {exc}", path)]


def check_decision_lineage() -> list[Result]:
    path = ROOT / "artifacts" / "decision-lineage.json"
    csv_path = ROOT / "artifacts" / "decision-lineage.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        rows = payload.get("nodes", [])
        problems = []
        expected_summary = {"node_count": 11, "source_link_count": 32, "reported_supported_node_count": 4, "assumption_exposed_node_count": 10}
        if payload.get("summary") != expected_summary or len(rows) != 11 or len(csv_rows) != 11:
            problems.append("lineage summary or synchronized row count differs")
        if len({row.get("node_id") for row in rows}) != 11:
            problems.append("lineage node IDs are not unique")
        required = ("committee_claim", "current_value", "evidence_ids", "calculation_or_rule", "artifact_locator", "workbook_locator", "owner_role", "limitation")
        if any(any(not row.get(field) for field in required) for row in rows):
            problems.append("a lineage node lacks evidence, logic, location, ownership, or limitation")
        if any(not (ROOT / row.get("artifact_locator", "").split("#", 1)[0]).is_file() for row in rows):
            problems.append("a lineage artifact reference does not resolve")
        limit = payload.get("method_limit", "")
        if "does not convert assumptions into facts" not in limit or "independent review" not in limit:
            problems.append("lineage method limit omits evidence or review boundaries")
        actual = "; ".join(problems) if problems else "Eleven committee claims resolve through 32 evidence links to current values, rules, artifacts, workbook cells, owners, and limitations."
        return [result("X-14", "FAIL" if problems else "PASS", "Decision lineage is complete, resolvable, and evidence-bounded", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-14", "FAIL", "Decision lineage is complete, resolvable, and evidence-bounded", f"Cannot validate decision lineage: {exc}", path)]


def check_diligence_plan() -> list[Result]:
    path = ROOT / "artifacts" / "diligence-plan.json"
    csv_path = ROOT / "artifacts" / "diligence-plan.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        conditions = json.loads((ROOT / "artifacts" / "condition-register.json").read_text(encoding="utf-8"))["conditions"]
        lineage_ids = {row["node_id"] for row in json.loads((ROOT / "artifacts" / "decision-lineage.json").read_text(encoding="utf-8"))["nodes"]}
        rows = payload.get("tasks", [])
        problems = []
        expected_summary = {"task_count": 9, "critical_count": 4, "high_count": 5, "parallel_lane_count": 4, "wave_one_count": 8, "dependency_blocked_count": 1, "ready_to_start_count": 8}
        if payload.get("summary") != expected_summary or len(rows) != 9 or len(csv_rows) != 9:
            problems.append("diligence summary or synchronized row count differs")
        if {row.get("condition_id") for row in rows} != {row.get("condition_id") for row in conditions}:
            problems.append("diligence plan does not map one-to-one to conditions")
        if any(set(row.get("affected_lineage_nodes", [])) - lineage_ids for row in rows):
            problems.append("a diligence task references an unknown lineage node")
        control = next((row for row in rows if row.get("condition_id") == "CP-03"), {})
        if control.get("depends_on") != ["CP-01", "CP-02"] or control.get("wave") != 2 or not str(control.get("current_action", "")).startswith("waiting_on:"):
            problems.append("control-agreement dependency sequence differs")
        required = ("parallel_lane", "priority", "decision_impact", "failure_consequence", "completion_output", "owner_role", "verification_method")
        if any(any(not row.get(field) for field in required) for row in rows):
            problems.append("a diligence task lacks execution or decision-impact detail")
        if "not an executed closing checklist" not in payload.get("method_limit", ""):
            problems.append("diligence method limit omits execution boundary")
        actual = "; ".join(problems) if problems else "Nine blocking conditions form four parallel lanes, eight wave-one tasks, and one explicit ownership-and-lien dependency before control execution."
        return [result("X-15", "FAIL" if problems else "PASS", "Diligence plan is complete, acyclic, and decision-linked", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-15", "FAIL", "Diligence plan is complete, acyclic, and decision-linked", f"Cannot validate diligence plan: {exc}", path)]


def check_assumption_register() -> list[Result]:
    path = ROOT / "artifacts" / "assumption-register.json"
    csv_path = ROOT / "artifacts" / "assumption-register.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        rows = payload.get("assumptions", [])
        problems = []
        expected_summary = {"assumption_count": 7, "critical_count": 3, "high_count": 4, "unvalidated_count": 7, "downstream_lineage_link_count": 27}
        if payload.get("summary") != expected_summary or len(rows) != 7 or len(csv_rows) != 7:
            problems.append("assumption summary or synchronized row count differs")
        if {row.get("assumption_id") for row in rows} != {f"ASM-C00{index}" for index in range(1, 8)}:
            problems.append("assumption register does not cover ASM-C001 through ASM-C007")
        required = ("assumption", "materiality", "validation_status", "owner_role", "workbook_inputs", "validation_method", "challenge_trigger", "downstream_lineage_nodes")
        if any(any(not row.get(field) for field in required) for row in rows):
            problems.append("an assumption lacks governance detail")
        if any(row.get("validation_status") != "unvalidated" or row.get("evidence_class") not in {"assumed", "simulated"} for row in rows):
            problems.append("an assumption is mislabeled as validated or factual")
        if "does not validate an assumption" not in payload.get("method_limit", ""):
            problems.append("assumption method limit omits validation boundary")
        actual = "; ".join(problems) if problems else "All seven case assumptions retain assumed or simulated evidence status with materiality, ownership, workbook inputs, validation methods, challenge triggers, and 27 downstream links."
        return [result("X-16", "FAIL" if problems else "PASS", "Assumption register is complete, governed, and explicitly unvalidated", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, TypeError) as exc:
        return [result("X-16", "FAIL", "Assumption register is complete, governed, and explicitly unvalidated", f"Cannot validate assumption register: {exc}", path)]


def check_collateral_call_ladder() -> list[Result]:
    path = ROOT / "artifacts" / "collateral-call-ladder.json"
    try:
        payload = json.loads(path.read_text())
        rows = payload["rows"]
        stresses = [Decimal(row["price_stress_pct"]) for row in rows]
        proceeds = [Decimal(row["available_proceeds_usd"]) for row in rows]
        topups = [Decimal(row["top_up_required_usdc"]) for row in rows]
        commitments = [Decimal(row["rounded_coverage_compliant_commitment_usd"]) for row in rows]
        problems = []
        if len(rows) != 7 or stresses != sorted(stresses):
            problems.append("ladder must contain seven ordered stress rows")
        if not all(a >= b for a, b in zip(proceeds, proceeds[1:])):
            problems.append("available proceeds are not monotonic")
        if not all(a <= b for a, b in zip(topups, topups[1:])):
            problems.append("top-up requirement is not monotonic")
        if not all(a >= b for a, b in zip(commitments, commitments[1:])):
            problems.append("commitment step-down is not monotonic")
        if payload.get("first_grid_call_stress_pct") != "0.05" or rows[0].get("status") != "PASS":
            problems.append("base/pass or first-grid-call boundary changed")
        if "not an executed margin agreement" not in payload.get("method_limit", ""):
            problems.append("method boundary is missing")
        actual = "; ".join(problems) if problems else "7 ordered rows; base passes; first grid call is 5%; cure amounts and commitment step-downs are monotonic."
        return [result("X-17", "FAIL" if problems else "PASS", "Collateral-call ladder is reconciled, monotonic, and bounded", actual, path)]
    except (OSError, KeyError, ValueError, InvalidOperation, json.JSONDecodeError) as exc:
        return [result("X-17", "FAIL", "Collateral-call ladder is reconciled, monotonic, and bounded", f"Cannot validate collateral-call ladder: {exc}", path)]


def check_committee_packet_audit() -> list[Result]:
    path = ROOT / "artifacts" / "committee-packet-audit.json"
    packet = ROOT / "outputs" / "committee-packet.pdf"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected_titles = ["Executive cover", "Credit memorandum", "Downside and cure ladder", "Model-risk posture", "Opposing memorandum", "Reviewer brief"]
        problems = []
        if payload.get("page_count") != 7:
            problems.append(f"page count is {payload.get('page_count')}")
        if payload.get("bookmark_titles") != expected_titles:
            problems.append("bookmark order differs")
        if payload.get("failure_count") != 0:
            problems.append("packet self-audit records failures")
        if payload.get("sha256") != hashlib.sha256(packet.read_bytes()).hexdigest():
            problems.append("packet hash differs from audit")
        required = {"Downside and cure ladder", "Exact modeled breach", "64.7k USDC", "$48.8k", "$2.9m", "Committee question", "Model-risk posture", "MR-01", "MR-08", "Known limitations are decision inputs"}
        if set(payload.get("required_text", [])) != required:
            problems.append("required cure-page text contract differs")
        actual = "; ".join(problems) if problems else "Seven pages and six ordered bookmarks verified; cure analysis and all eight governed model risks are present."
        return [result("X-18", "FAIL" if problems else "PASS", "Committee packet is indexed, current, and contains cure and model-risk analysis", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
        return [result("X-18", "FAIL", "Committee packet is indexed, current, and contains cure and model-risk analysis", f"Cannot validate committee packet audit: {exc}", path)]


def check_control_matrix() -> list[Result]:
    path = ROOT / "artifacts" / "control-matrix.json"
    csv_path = ROOT / "artifacts" / "control-matrix.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_rows = read_csv(csv_path)
        rows = payload["controls"]
        problems = []
        if len(rows) != 8 or len(csv_rows) != 8:
            problems.append("expected eight synchronized control chains")
        for field in ("control_id", "monitor_id", "covenant_id", "playbook_id"):
            values = [row[field] for row in rows]
            if len(values) != len(set(values)):
                problems.append(f"{field} is not unique")
        covered = {condition for row in rows for condition in row["condition_ids"]}
        if covered != {"CP-01", "CP-02", "CP-03", "CP-04", "DD-01", "DD-02", "DD-03", "DD-04", "PF-01"}:
            problems.append("pre-funding condition coverage differs")
        if payload.get("activation_state") != "pre_funding_blocked" or payload.get("enforceability_status") != "draft_only":
            problems.append("activation or enforceability boundary changed")
        if any(row["condition_status"] != "outstanding" for row in rows):
            problems.append("a control chain implies a cleared condition")
        actual = "; ".join(problems) if problems else "Eight complete control chains cover all nine conditions and preserve blocked, draft-only governance boundaries."
        return [result("X-19", "FAIL" if problems else "PASS", "Control matrix joins every condition to monitoring, covenant, and escalation coverage", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error, KeyError, TypeError) as exc:
        return [result("X-19", "FAIL", "Control matrix joins every condition to monitoring, covenant, and escalation coverage", f"Cannot validate control matrix: {exc}", path)]


def check_reviewer_scorecard() -> list[Result]:
    path = ROOT / "artifacts" / "reviewer-scorecard.json"
    pdf_path = ROOT / "outputs" / "reviewer-scorecard.pdf"
    audit_path = ROOT / "artifacts" / "reviewer-scorecard-audit.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "data/review/reviewer-evidence.json").read_text(encoding="utf-8"))
        gates = payload["gates"]
        problems = []
        if [row.get("gate_id") for row in gates] != ["HG-01", "HG-02", "HG-03"]:
            problems.append("gate order differs")
        ledger_errors = validate_ledger(ledger)
        if ledger_errors:
            problems.append("reviewer evidence ledger is invalid")
        records = {row["gate_id"]: row for row in ledger.get("records", [])}
        expected_statuses = {gate_id: "PASS" if gate_passes(record) else "OUTSTANDING" for gate_id, record in records.items()}
        actual_statuses = {row.get("gate_id"): row.get("current_status") for row in gates}
        if actual_statuses != expected_statuses:
            problems.append("gate statuses differ from governed reviewer evidence")
        passed_count = sum(status == "PASS" for status in expected_statuses.values())
        expected_summary = {"gate_count": 3, "passed_count": passed_count, "outstanding_count": 3 - passed_count}
        if payload.get("summary") != expected_summary:
            problems.append("gate summary differs from governed reviewer evidence")
        if any(len(row.get("review_questions", [])) < 4 or len(row.get("pass_criteria", [])) < 3 for row in gates):
            problems.append("a gate lacks questions or pass criteria")
        if audit.get("page_count") != 4 or audit.get("failure_count") != 0:
            problems.append("PDF self-audit failed")
        if audit.get("passed_count") != passed_count or audit.get("outstanding_count") != 3 - passed_count:
            problems.append("PDF audit counts differ from governed reviewer evidence")
        if audit.get("sha256") != hashlib.sha256(pdf_path.read_bytes()).hexdigest():
            problems.append("scorecard PDF hash differs from audit")
        actual = "; ".join(problems) if problems else f"Three executable human-gate worksheets reflect governed evidence ({passed_count} passed, {3 - passed_count} outstanding); four-page PDF hash and text contract verified."
        return [result("X-20", "FAIL" if problems else "PASS", "Reviewer scorecard operationalizes human gates without fabricating completion", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return [result("X-20", "FAIL", "Reviewer scorecard operationalizes human gates without fabricating completion", f"Cannot validate reviewer scorecard: {exc}", path)]


def check_reviewer_brief_contract() -> list[Result]:
    narrative_path = ROOT / "artifacts" / "reviewer-brief.md"
    builder_path = ROOT / "work" / "build_pdfs.py"
    pdf_path = ROOT / "outputs" / "reviewer-brief.pdf"
    try:
        narrative = narrative_path.read_text(encoding="utf-8").lower()
        builder = builder_path.read_text(encoding="utf-8")
        required_narrative = {
            "decision": "## decision in one line",
            "unresolved assumption": "## one unresolved assumption",
            "precise question": "## review question",
            "external-validation disclaimer": "no external review",
        }
        problems = [name for name, token in required_narrative.items() if token not in narrative]
        if "def cap_chart()" not in builder or "Four-cap comparison" not in builder or "cap_chart()," not in builder:
            problems.append("rendered four-cap chart")
        if 'h("Unresolved assumption")' not in builder:
            problems.append("rendered unresolved-assumption section")
        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            problems.append("non-empty reviewer PDF")
        actual = "Missing: " + ", ".join(problems) if problems else "Decision, four-cap chart, unresolved assumption, precise question, and review-status disclaimer are declared and rendered."
        return [result("X-04", "FAIL" if problems else "PASS", "Reviewer brief satisfies CR-08 content contract", actual, pdf_path)]
    except (OSError, UnicodeError) as exc:
        return [result("X-04", "FAIL", "Reviewer brief satisfies CR-08 content contract", f"Cannot validate reviewer brief: {exc}", pdf_path)]


def check_readiness_report() -> list[Result]:
    path = ROOT / "artifacts" / "readiness-report.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        ledger = json.loads((ROOT / "data/review/reviewer-evidence.json").read_text(encoding="utf-8"))
        criteria = payload.get("criteria", [])
        gates = payload.get("human_gates", [])
        problems = []
        expected_ids = {f"CR-{index:02d}" for index in range(1, 11)}
        actual_ids = {row.get("id") for row in criteria}
        if actual_ids != expected_ids:
            problems.append(f"criterion IDs differ: {sorted(actual_ids)}")
        if not all(row.get("status") == "VERIFIED_LOCAL" and row.get("evidence") for row in criteria):
            problems.append("not every criterion is locally verified with evidence")
        if payload.get("local_acceptance_verified") is not True:
            problems.append("local acceptance is not verified")
        if {row.get("id") for row in gates} != {"HG-01", "HG-02", "HG-03"}:
            problems.append("human gate set is incomplete")
        ledger_errors = validate_ledger(ledger)
        if ledger_errors:
            problems.append("reviewer evidence ledger is invalid")
        expected_statuses = {row["gate_id"]: "PASS" if gate_passes(row) else "OUTSTANDING" for row in ledger.get("records", [])}
        actual_statuses = {row.get("id"): row.get("status") for row in gates}
        if actual_statuses != expected_statuses or not all(row.get("evidence") for row in gates):
            problems.append("human gates differ from governed reviewer evidence")
        expected_ready = payload.get("local_acceptance_verified") is True and all(status == "PASS" for status in expected_statuses.values())
        if payload.get("ready_to_share") is not expected_ready:
            problems.append("ready-to-share does not match local and human gate status")
        passed_count = sum(status == "PASS" for status in expected_statuses.values())
        actual = "; ".join(problems) if problems else f"CR-01 through CR-10 are locally verified; governed evidence records {passed_count} of 3 human gates passed."
        return [result("X-05", "FAIL" if problems else "PASS", "Readiness report separates local verification from human gates", actual, path)]
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
        return [result("X-05", "FAIL", "Readiness report separates local verification from human gates", f"Cannot validate readiness report: {exc}", path)]


def check_outputs() -> list[Result]:
    results: list[Result] = []
    artifacts = ROOT / "artifacts"
    for index, filename in enumerate(EXPECTED_OUTPUTS, start=1):
        if filename in {"credit-model.xlsx", "credit-memo.pdf", "committee-packet.pdf", "opposing-memo.pdf", "reviewer-brief.pdf", "reviewer-scorecard.pdf", "decision-view.html", "demo.mp4"}:
            path = ROOT / "outputs" / filename
        else:
            path = artifacts / filename
        status = "PASS" if path.is_file() and path.stat().st_size > 0 else "SKIP"
        actual = "Present and non-empty." if status == "PASS" else "Output is not yet available."
        if filename == "credit-model.xlsx" and status == "PASS":
            try:
                with zipfile.ZipFile(path) as workbook:
                    members = set(workbook.namelist())
                    corrupt_member = workbook.testzip()
                required_members = {"[Content_Types].xml", "xl/workbook.xml"}
                missing_members = sorted(required_members - members)
                if corrupt_member or missing_members:
                    status = "FAIL"
                    details = []
                    if corrupt_member:
                        details.append(f"corrupt ZIP member {corrupt_member}")
                    if missing_members:
                        details.append("missing XLSX members " + ", ".join(missing_members))
                    actual = "; ".join(details)
                else:
                    actual = f"Valid non-empty XLSX ZIP package with {len(members)} members."
            except (OSError, zipfile.BadZipFile) as exc:
                status = "FAIL"
                actual = f"Invalid XLSX ZIP package: {exc}"
        if filename.endswith(".pdf") and status == "PASS":
            try:
                data = path.read_bytes()
                if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
                    status = "FAIL"
                    actual = "File does not have a valid PDF header and terminal marker."
                else:
                    actual = f"Valid non-empty PDF container ({len(data):,} bytes)."
            except OSError as exc:
                status = "FAIL"
                actual = f"Cannot read PDF: {exc}"
        if filename == "decision-view.html" and status == "PASS":
            try:
                text = path.read_text(encoding="utf-8")
                required = (
                    "MARA-CR-001", "scenario-results", "Hypothetical", "<select",
                    "canonical_withdrawal_168h", "correlated_portfolio_stress", "thresholdStress",
                    "sourceCoverage", "Skip to decision content", "aria-live=\"polite\"",
                    "prefers-reduced-motion", "copySummary", "window.print()", "searchParams.set",
                    "scenarioMatrix", "downloadScenario", "Delta vs. base",
                    "conditionRegister", "fundingGate", "Pre-funding condition register",
                    "ratingBridge", "ratingScore", "Rating bridge",
                    "monitoringPlan", "Monitoring and early-warning design",
                    "liquidityBridge", "liquidityPrePut", "Public-data liquidity bridge",
                    "proFormaExposure", "proFormaSurplus", "exposureBasis",
                    "Requested-draw recovery exposure", "Recommended pro forma exposure",
                    "sensitivityTable", "sensitivityBody", "Collateral decision surface",
                    "covenantPlan", "covenantLimit", "Illustrative covenant package",
                    "escalationPlan", "escalationLimit", "Escalation and response playbook",
                    "whatIfLab", "evaluateWhatIf", "verifyWhatIfContract", "Live collateral what-if lab",
                    "attributionCount", "attributionLimit", "Primary driver", "Resolution evidence",
                    "lineageTable", "lineageLimit", "Decision lineage", "Committee claim",
                    "diligenceTable", "diligenceLimit", "Diligence execution plan", "Affected claims",
                    "assumptionTable", "assumptionLimit", "Assumption governance", "Challenge trigger",
                    "collateralCallSection", "collateralCallTable", "Coverage covenant call ladder", "Exact modeled breach stress",
                    "controlMatrixSection", "controlMatrixTable", "End-to-end control matrix", "Controls with outstanding conditions",
                    "readinessSection", "humanGateTable", "Review readiness and human gates", "reviewer-scorecard.pdf",
                )
                missing = [token for token in required if token not in text]
                if missing:
                    status = "FAIL"
                    actual = "Missing required decision-view content: " + ", ".join(missing)
                else:
                    actual = f"Self-contained HTML present ({len(text):,} characters)."
            except (OSError, UnicodeError) as exc:
                status = "FAIL"
                actual = f"Cannot read decision view: {exc}"
        if filename == "demo.mp4" and status == "PASS":
            try:
                data = path.read_bytes()
                if len(data) < 32 or b"ftyp" not in data[:64]:
                    status = "FAIL"
                    actual = "File does not have a recognizable ISO media container header."
                else:
                    actual = f"Valid non-empty ISO media container ({len(data):,} bytes)."
            except OSError as exc:
                status = "FAIL"
                actual = f"Cannot read demo video: {exc}"
        results.append(result(f"O-{index:02d}", status, f"Artifact available: {filename}", actual, path))
    return results


def check_labels() -> list[Result]:
    candidates = [
        ROOT / "artifacts/credit-memo.md",
        ROOT / "artifacts/opposing-memo.md",
        ROOT / "artifacts/reviewer-brief.md",
        ROOT / "artifacts/feedback-log.md",
        ROOT / "artifacts/reproducibility.md",
    ]
    present = [path for path in candidates if path.exists()]
    if not present:
        return [result("L-01", "SKIP", "Built narrative artifacts label the case hypothetical",
                       "No text narrative artifacts are available for inspection.", ROOT / "artifacts")]
    failures = []
    for path in present:
        text = path.read_text(encoding="utf-8").lower()
        if not re.search(r"\b(hypothetical|fictional|illustrative)\b", text):
            failures.append(str(path.relative_to(ROOT)))
    return [result("L-01", "FAIL" if failures else "PASS", "Built narrative artifacts label the case hypothetical",
                   "Missing explicit label: " + ", ".join(failures) if failures else f"Found an explicit label in {len(present)} text artifact(s).", ROOT / "artifacts")]


def check_scenarios() -> list[Result]:
    path = ROOT / "artifacts/scenario-results.csv"
    if not path.exists():
        return [result("C-01", "SKIP", "Scenario schema and arithmetic consistency", "Scenario results are not yet available.", path)]
    try:
        fields, rows = read_csv(path)
    except (OSError, csv.Error, UnicodeError, ValueError) as exc:
        return [result("C-01", "FAIL", "Scenario schema and arithmetic consistency", f"Cannot parse CSV: {exc}", path)]
    missing = sorted(SCENARIO_COLUMNS - set(fields))
    failures = []
    if missing:
        failures.append("missing columns " + ", ".join(missing))
    else:
        for line, row in enumerate(rows, start=2):
            try:
                requested = decimal(row["requested_amount_usd"])
                recommended = decimal(row["recommended_amount_usd"])
                available = decimal(row["available_proceeds_usd"])
                exposure = decimal(row["exposure_usd"])
                shortfall = decimal(row["shortfall_usd"])
                pro_forma = decimal(row["recommended_pro_forma_exposure_usd"])
                pro_forma_surplus = decimal(row["recommended_pro_forma_coverage_surplus_usd"])
            except (InvalidOperation, KeyError):
                failures.append(f"row {line}: nonnumeric amount")
                continue
            if min(requested, recommended, available, shortfall) < 0:
                failures.append(f"row {line}: negative amount")
            if recommended > requested:
                failures.append(f"row {line}: recommended exceeds requested")
            expected_shortfall = max(Decimal("0"), exposure - available)
            if abs(shortfall - expected_shortfall) > Decimal("1"):
                failures.append(f"row {line}: shortfall differs from max(0, exposure - available) by more than $1")
            expected_surplus = max(Decimal("0"), available - pro_forma)
            if abs(pro_forma_surplus - expected_surplus) > Decimal("1"):
                failures.append(f"row {line}: pro forma surplus differs from max(0, available - pro forma exposure) by more than $1")
    return [result("C-01", "FAIL" if failures else "PASS", "Scenario schema and arithmetic consistency",
                   "; ".join(failures) if failures else f"Validated {len(rows)} scenario row(s).", path)]


def check_package_metrics() -> list[Result]:
    path = ROOT / "artifacts/package-metrics.json"
    markdown = ROOT / "artifacts/package-metrics.md"
    if not path.is_file() or not markdown.is_file():
        return [result("X-21", "FAIL", "Generated package metrics match current artifacts",
                       "JSON or Markdown package metrics are missing.", path)]
    try:
        metrics = json.loads(path.read_text(encoding="utf-8"))
        workbook_rows = read_csv(ROOT / "artifacts/workbook-audit.csv")[1]
        scenarios = json.loads((ROOT / "artifacts/scenario-results.json").read_text(encoding="utf-8"))
        decision_audit = json.loads((ROOT / "artifacts/decision-view-audit.json").read_text(encoding="utf-8"))
        expected = {
            "workbook.audit_check_count": (metrics["workbook"]["audit_check_count"], len(workbook_rows)),
            "workbook.audit_pass_count": (metrics["workbook"]["audit_pass_count"], sum(row.get("status") == "PASS" for row in workbook_rows)),
            "decision_support.scenario_count": (metrics["decision_support"]["scenario_count"], len(scenarios)),
            "decision_view.required_id_count": (metrics["decision_view"]["required_id_count"], decision_audit["summary"]["required_id_count"]),
        }
        problems = [f"{name}: {actual} != {wanted}" for name, (actual, wanted) in expected.items() if actual != wanted]
        for name, recorded in metrics["artifact_sha256"].items():
            artifact = ROOT / name
            if not artifact.is_file():
                problems.append(f"missing hashed artifact {name}")
            elif hashlib.sha256(artifact.read_bytes()).hexdigest() != recorded:
                problems.append(f"stale hash for {name}")
        stale_guide = (ROOT / "artifacts/reproducibility.md").read_text(encoding="utf-8")
        if "67 checks" in stale_guide or "eight-sheet" in stale_guide:
            problems.append("reproducibility guide retains superseded hard-coded counts")
        actual = "; ".join(problems) if problems else "Generated metrics reconcile to current workbook audit, scenarios, decision-view audit, and primary-output hashes."
        return [result("X-21", "FAIL" if problems else "PASS", "Generated package metrics match current artifacts", actual, path)]
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [result("X-21", "FAIL", "Generated package metrics match current artifacts", f"Cannot validate package metrics: {exc}", path)]


def check_model_risk_register() -> list[Result]:
    path = ROOT / "artifacts/model-risk-register.json"
    csv_path = ROOT / "artifacts/model-risk-register.csv"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        _, csv_items = read_csv(csv_path)
        risks = payload["risks"]
        assumption_ids = {row["assumption_id"] for row in json.loads((ROOT / "artifacts/assumption-register.json").read_text())["assumptions"]}
        condition_ids = {row["condition_id"] for row in json.loads((ROOT / "artifacts/condition-register.json").read_text())["conditions"]}
        problems = []
        ids = [row.get("risk_id", "") for row in risks]
        if len(ids) != len(set(ids)) or not all(ids):
            problems.append("risk IDs are missing or duplicated")
        if ids != [row.get("risk_id") for row in csv_items]:
            problems.append("CSV and JSON risk order differs")
        for row in risks:
            missing_assumptions = set(row["linked_assumptions"]) - assumption_ids
            missing_conditions = set(row["linked_conditions"]) - condition_ids
            if missing_assumptions:
                problems.append(f"{row['risk_id']} unresolved assumptions {sorted(missing_assumptions)}")
            if missing_conditions:
                problems.append(f"{row['risk_id']} unresolved conditions {sorted(missing_conditions)}")
            if row["status"] == "open" and not all(row.get(key) for key in ("owner", "mitigation", "validation_evidence", "disposition_if_unresolved")):
                problems.append(f"{row['risk_id']} has incomplete open-risk governance")
        critical = sum(row["severity"] == "critical" for row in risks)
        actual = "; ".join(problems) if problems else f"{len(risks)} synchronized open risks; {critical} critical; all links resolve and every risk has mitigation, evidence, owner, and unresolved disposition."
        return [result("X-22", "FAIL" if problems else "PASS", "Model-risk register is synchronized, governed, and decision-linked", actual, path)]
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [result("X-22", "FAIL", "Model-risk register is synchronized, governed, and decision-linked", f"Cannot validate model-risk register: {exc}", path)]


def check_reviewer_evidence_ledger() -> list[Result]:
    path = ROOT / "data/review/reviewer-evidence.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        problems = validate_ledger(payload, ROOT)
        records = payload.get("records", [])
        passed = sum(gate_passes(row, ROOT) for row in records)
        readiness = json.loads((ROOT / "artifacts/readiness-report.json").read_text(encoding="utf-8"))
        readiness_passed = sum(row.get("status") == "PASS" for row in readiness["human_gates"])
        if passed != readiness_passed:
            problems.append(f"ledger passes {passed} differ from readiness passes {readiness_passed}")
        if any(row.get("outcome") == "PASS" and not gate_passes(row, ROOT) for row in records):
            problems.append("ledger contains an unsubstantiated PASS outcome")
        actual = "; ".join(problems) if problems else f"Three ordered reviewer records validated; {passed} evidence-backed gate(s) pass and readiness matches."
        return [result("X-23", "FAIL" if problems else "PASS", "Reviewer-evidence ledger rejects incomplete or unretained human-gate claims", actual, path)]
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return [result("X-23", "FAIL", "Reviewer-evidence ledger rejects incomplete or unretained human-gate claims", f"Cannot validate reviewer evidence: {exc}", path)]


def render(results: list[Result]) -> str:
    counts = {status: sum(item.status == status for item in results) for status in ("PASS", "FAIL", "SKIP")}
    lines = [
        "# Validation report",
        "",
        f"Executed: {date.today().isoformat()}",
        "Reviewer: automated local validator (`scripts/validate_package.py`)",
        "Method: deterministic Python standard-library checks; no network access",
        "",
        f"Summary: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['SKIP']} SKIP",
        "",
        "| ID | Status | Check | Actual result | Evidence |",
        "|---|---|---|---|---|",
    ]
    for item in results:
        values = [item.check_id, item.status, item.check, item.actual, item.evidence]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "PASS means the check executed and its tested condition held. FAIL means the check executed and found a concrete problem. SKIP means the required output or evidence was unavailable; it is not a pass.",
        "",
        "This validator checks frozen-source hashes, filing-fact reconciliation, PDF container markers, and XLSX archive structure. It does not independently recalculate workbook formulas in Excel, prove legal enforceability, or substitute for an independent human calculation. Those checks remain manual until suitable artifacts and reviewers exist.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true", help="write artifacts/validation-report.md")
    args = parser.parse_args()
    results = check_structure() + check_source_register() + check_fact_ledger() + check_workbook_audit() + check_integrity_manifest() + check_threshold_analysis() + check_machine_readable_files() + check_cross_artifact_consistency() + check_decision_record() + check_condition_register() + check_covenant_plan() + check_escalation_playbook() + check_what_if_contract() + check_scenario_attribution() + check_decision_lineage() + check_diligence_plan() + check_assumption_register() + check_model_risk_register() + check_reviewer_evidence_ledger() + check_collateral_call_ladder() + check_committee_packet_audit() + check_control_matrix() + check_reviewer_scorecard() + check_rating_analysis() + check_monitoring_plan() + check_liquidity_analysis() + check_reviewer_brief_contract() + check_readiness_report() + check_package_metrics() + check_outputs() + check_labels() + check_scenarios()
    report = render(results)
    if args.write_report:
        (ROOT / "artifacts/validation-report.md").write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return 1 if any(item.status == "FAIL" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
