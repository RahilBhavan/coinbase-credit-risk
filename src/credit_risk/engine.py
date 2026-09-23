"""Transparent, standard-library-only credit decision engine.

Reported issuer facts are loaded independently from fictional deal inputs. Money
and rates use Decimal throughout so identical inputs produce identical outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from pathlib import Path
from typing import Any


ZERO = Decimal("0")
ONE = Decimal("1")
CENT = Decimal("0.01")
SCENARIO_KEYS = {
    "scenario_id",
    "unavailable_routes",
    "delayed_route",
    "additional_route_delay_hours",
    "price_shock_pct",
    "extra_execution_cost_bps",
    "accessible_quantity_pct",
    "forced_exclusion_reasons",
    "obligor_cap_usd_override",
    "concentration_cap_usd_override",
}


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_case(case_dir: Path) -> dict[str, Any]:
    return {
        "issuer": _load(case_dir / "issuer_facts.json"),
        "facility": _load(case_dir / "facility.json"),
        "collateral": _load(case_dir / "collateral.json"),
        "portfolio": _load(case_dir / "portfolio.json"),
        "policy": _load(case_dir / "policy.json"),
        "scenarios": _load(case_dir / "scenarios.json"),
        "governance": _load(case_dir / "governance.json"),
        "conditions": _load(case_dir / "conditions.json"),
        "rating": _load(case_dir / "rating.json"),
    }


def _rating_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    factors = payload["factors"]
    total_weight = sum((_decimal(row["weight"]) for row in factors), ZERO)
    if total_weight != ONE:
        raise ValueError(f"rating weights sum to {total_weight}, expected 1")
    ids = [row["factor_id"] for row in factors]
    if len(ids) != len(set(ids)):
        raise ValueError("rating factor IDs must be unique")
    if any(not ONE <= _decimal(row["score"]) <= Decimal("5") for row in factors):
        raise ValueError("rating factor scores must be between 1 and 5")
    score = sum((_decimal(row["weight"]) * _decimal(row["score"]) for row in factors), ZERO)
    matches = [band for band in payload["scale"] if _decimal(band["minimum"]) <= score <= _decimal(band["maximum"])]
    if len(matches) != 1:
        raise ValueError(f"weighted rating score {score} maps to {len(matches)} bands")
    return {
        "score": str(score.quantize(CENT)),
        "grade": matches[0]["grade"],
        "factors": [
            {**row, "weighted_contribution": str((_decimal(row["weight"]) * _decimal(row["score"])).quantize(CENT))}
            for row in factors
        ],
        "scale": payload["scale"],
        "method_limit": payload["method_limit"],
    }


def _concentration_cap(
    portfolio: dict[str, Any], policy: dict[str, Any], proposed_asset: str
) -> Decimal:
    exposures = portfolio["exposures"]
    total = sum((_decimal(row["funded_usd"]) for row in exposures), ZERO)
    same_asset = sum(
        (
            _decimal(row["funded_usd"])
            for row in exposures
            if row["collateral_asset"] == proposed_asset
        ),
        ZERO,
    )
    limit = _decimal(policy["collateral_asset_concentration_limit"])
    if limit >= ONE:
        return _decimal(policy["maximum_commitment_usd"])
    return max(ZERO, (limit * total - same_asset) / (ONE - limit))


def _collateral_proceeds(
    lots: list[dict[str, Any]], scenario: dict[str, Any], policy: dict[str, Any]
) -> tuple[Decimal, list[dict[str, Any]], list[str]]:
    total = ZERO
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    unavailable_routes = set(scenario.get("unavailable_routes", []))
    scenario_delay = _decimal(scenario.get("additional_route_delay_hours", "0"))
    price_shock = _decimal(scenario.get("price_shock_pct", "0"))
    extra_execution_bps = _decimal(scenario.get("extra_execution_cost_bps", "0"))
    accessible_quantity_pct = _decimal(scenario.get("accessible_quantity_pct", "1"))
    forced_exclusions = scenario.get("forced_exclusion_reasons", {})
    delay_bps_per_hour = _decimal(policy["delay_cost_bps_per_hour"])

    for lot in lots:
        reasons: list[str] = []
        if lot["ownership_evidence"] != "verified":
            reasons.append("ownership_not_verified")
        if lot["lien_state"] != "first_priority":
            reasons.append("first_priority_lien_not_verified")
        if lot["legal_control"] != "enforceable":
            reasons.append("legal_control_not_enforceable")
        if lot["route"] in unavailable_routes:
            reasons.append("repayment_route_unavailable")
        reasons.extend(forced_exclusions.get(lot["lot_id"], []))

        accessible_quantity = _decimal(lot["quantity"]) * accessible_quantity_pct
        gross = accessible_quantity * _decimal(lot["quoted_price_usd"])
        effective_delay = _decimal(lot["earliest_usable_hours"])
        if lot["route"] == scenario.get("delayed_route"):
            effective_delay += scenario_delay
        total_cost_bps = _decimal(lot["execution_cost_bps"]) + extra_execution_bps
        stressed_gross = gross * max(ZERO, ONE - price_shock)
        execution_cost = stressed_gross * total_cost_bps / Decimal("10000")
        delay_cost = stressed_gross * effective_delay * delay_bps_per_hour / Decimal("10000")
        fixed_cost = _decimal(lot["fixed_cost_usd"])
        proceeds = ZERO if reasons else max(ZERO, stressed_gross - execution_cost - delay_cost - fixed_cost)
        total += proceeds
        blockers.extend(f"{lot['lot_id']}:{reason}" for reason in reasons)
        rows.append(
            {
                "lot_id": lot["lot_id"],
                "route": lot["route"],
                "eligible": not reasons,
                "accessible_quantity": str(accessible_quantity),
                "effective_delay_hours": str(effective_delay),
                "stressed_gross_value_usd": str(_money(stressed_gross)),
                "execution_cost_usd": str(_money(execution_cost)),
                "delay_cost_usd": str(_money(delay_cost)),
                "fixed_cost_usd": str(_money(fixed_cost)),
                "available_proceeds_usd": str(_money(proceeds)),
                "exclusion_reasons": reasons,
            }
        )
    return _money(total), rows, sorted(blockers)


def evaluate_case(case_dir: str | Path, scenario_id: str = "base") -> dict[str, Any]:
    """Evaluate one scenario and return a stable, JSON-compatible decision record."""
    case = _read_case(Path(case_dir))
    scenario = next(
        (row for row in case["scenarios"] if row["scenario_id"] == scenario_id), None
    )
    if scenario is None:
        raise ValueError(f"unknown scenario_id: {scenario_id}")
    unknown_keys = sorted(set(scenario) - SCENARIO_KEYS)
    if unknown_keys:
        raise ValueError(f"unknown scenario key(s) in {scenario_id}: {', '.join(unknown_keys)}")

    issuer = case["issuer"]
    facility = case["facility"]
    policy = case["policy"]
    governance = case["governance"]
    rating = _rating_analysis(case["rating"])
    if rating["grade"] != governance["illustrative_rating"]:
        raise ValueError("computed illustrative rating differs from governance record")
    condition_register = case["conditions"]
    available, lot_results, blockers = _collateral_proceeds(
        case["collateral"], scenario, policy
    )
    coverage = _decimal(facility["required_coverage_ratio"])
    accrued = _decimal(facility["accrued_amount_usd"])
    caps = {
        "obligor": _decimal(scenario.get("obligor_cap_usd_override", policy["obligor_cap_usd"])),
        # Size on the same basis as the pro forma exposure: commitment plus accrued amount.
        "collateral": available / coverage - accrued,
        "single_name": _decimal(policy["single_name_cap_usd"]),
        "concentration": _concentration_cap(
            case["portfolio"], policy, case["collateral"][0]["asset"]
        ),
    }
    if "concentration_cap_usd_override" in scenario:
        caps["concentration"] = _decimal(scenario["concentration_cap_usd_override"])
    caps = {name: _money(max(ZERO, value)) for name, value in caps.items()}
    requested = _decimal(facility["requested_commitment_usd"])
    binding_cap = min(caps, key=lambda name: (caps[name], name))
    if requested < caps[binding_cap]:
        binding_cap = "requested"
    raw_recommended = ZERO if blockers else min(requested, *caps.values())
    increment = _decimal(policy["recommendation_increment_usd"])
    recommended = (
        ZERO
        if raw_recommended == ZERO
        else (raw_recommended / increment).quantize(ZERO, rounding=ROUND_DOWN) * increment
    )
    exposure = _decimal(facility["funded_exposure_usd"]) + _decimal(
        facility["accrued_amount_usd"]
    )
    shortfall = max(ZERO, exposure - available)
    decision = "decline" if blockers or recommended == ZERO else (
        "approve" if recommended >= requested else "approve_reduced"
    )
    outstanding_conditions = sorted(
        row["condition_id"]
        for row in condition_register
        if row["blocking"] and row["evidence_status"] != "verified"
    )
    funding_gate_status = (
        "declined" if decision == "decline"
        else "blocked_pending_conditions" if outstanding_conditions
        else "cleared_to_fund"
    )
    pro_forma_exposure = recommended + accrued if recommended > ZERO else ZERO
    pro_forma_surplus = available - pro_forma_exposure

    return {
        "case_id": facility["case_id"],
        "case_version": facility["case_version"],
        "scenario_id": scenario_id,
        "decision": decision,
        "requested_amount_usd": str(_money(requested)),
        "recommended_amount_usd": str(_money(recommended)),
        "caps_usd": {name: str(value) for name, value in sorted(caps.items())},
        "binding_cap": "hard_blocker" if blockers else binding_cap,
        "available_proceeds_usd": str(available),
        "exposure_usd": str(_money(exposure)),
        "shortfall_usd": str(_money(shortfall)),
        "exposure_basis": "requested fully drawn recovery case plus accrued amount; not the recommended pro forma exposure",
        "recommended_pro_forma_exposure_usd": str(_money(pro_forma_exposure)),
        "recommended_pro_forma_coverage_surplus_usd": str(_money(pro_forma_surplus)),
        "hard_blockers": blockers,
        "conditions": list(facility.get("conditions", [])),
        "condition_register": condition_register,
        "outstanding_blocking_conditions": outstanding_conditions,
        "funding_gate_status": funding_gate_status,
        "illustrative_rating": rating["grade"],
        "rating_score": rating["score"],
        "rating_factors": rating["factors"],
        "rating_scale": rating["scale"],
        "rating_method_limit": rating["method_limit"],
        "rating_rationale": governance["rating_rationale"],
        "reversal_trigger": governance["reversal_trigger"],
        "source_coverage_rate": governance["source_coverage_rate"],
        "source_coverage_scope": governance["source_coverage_scope"],
        "preparer": governance["preparer"],
        "review_status": governance["review_status"],
        "collateral_lots": lot_results,
        "calculation_trace": {
            "available_proceeds_formula": "sum(max(0, stressed_gross - execution_cost - delay_cost - fixed_cost)) for eligible lots; blocked lots receive zero",
            "collateral_cap_formula": "available_proceeds / required_coverage_ratio - accrued_amount",
            "decision_formula": "min(requested, obligor_cap, collateral_cap, single_name_cap, concentration_cap), or zero on hard blocker",
            "rounding_formula": "round down to recommendation_increment_usd",
            "required_coverage_ratio": str(coverage),
            "raw_recommended_amount_usd": str(_money(raw_recommended)),
            "recommendation_increment_usd": str(_money(increment)),
            "rounded_recommended_amount_usd": str(_money(recommended)),
        },
        "scenario_drivers": {
            key: scenario[key]
            for key in sorted(scenario)
            if key != "scenario_id"
        },
        "evidence_boundary": {
            "issuer_facts_class": issuer["evidence_class"],
            "facility_inputs_class": facility["evidence_class"],
            "collateral_inputs_class": "simulated",
            "portfolio_inputs_class": case["portfolio"]["evidence_class"],
        },
    }


def write_csv(result: dict[str, Any], path: str | Path) -> None:
    rows = [
        ("decision", result["decision"]),
        ("requested_amount_usd", result["requested_amount_usd"]),
        ("recommended_amount_usd", result["recommended_amount_usd"]),
        ("available_proceeds_usd", result["available_proceeds_usd"]),
        ("shortfall_usd", result["shortfall_usd"]),
        ("binding_cap", result["binding_cap"]),
    ]
    rows.extend((f"cap_{name}_usd", value) for name, value in result["caps_usd"].items())
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def evaluate_all(case_dir: str | Path) -> list[dict[str, Any]]:
    """Evaluate every declared scenario in fixture order."""
    root = Path(case_dir)
    scenarios = _load(root / "scenarios.json")
    return [evaluate_case(root, row["scenario_id"]) for row in scenarios]


def write_scenario_csv(results: list[dict[str, Any]], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "scenario_id",
        "decision",
        "requested_amount_usd",
        "recommended_amount_usd",
        "available_proceeds_usd",
        "exposure_usd",
        "shortfall_usd",
        "recommended_pro_forma_exposure_usd",
        "recommended_pro_forma_coverage_surplus_usd",
        "binding_cap",
        "hard_blockers",
    ]
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    field: "|".join(result[field]) if field == "hard_blockers" else result[field]
                    for field in fields
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", default="data/case")
    parser.add_argument("--scenario", default="base")
    parser.add_argument("--json-out")
    parser.add_argument("--csv-out")
    parser.add_argument("--all-scenarios", action="store_true")
    args = parser.parse_args(argv)
    result = evaluate_all(args.case_dir) if args.all_scenarios else evaluate_case(
        args.case_dir, args.scenario
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.csv_out:
        if args.all_scenarios:
            write_scenario_csv(result, args.csv_out)
        else:
            write_csv(result, args.csv_out)
    return 0
