# Data model and calculation contract

Status: implemented reference; independent review remains

## Evidence records

`source`

| Field | Type | Rule |
|---|---|---|
| `source_id` | text | Stable identifier |
| `evidence_class` | enum | `reported`, `observed`, `calculated`, `assumed`, or `simulated` |
| `url_or_assumption` | text | Exact source URL or case assumption ID |
| `published_at` | date | Source publication date, when present |
| `retrieved_at_utc` | timestamp | Retrieval time |
| `content_hash` | text | Hash of the raw snapshot |
| `limitations` | text | What the source cannot establish |

`financial_fact`

| Field | Type | Rule |
|---|---|---|
| `fact_id` | text | Stable identifier |
| `issuer_id` | text | `MARA` for the selected case |
| `metric` | text | One canonical name per metric |
| `value_reported` | decimal | Never overwrite |
| `unit_reported` | text | Preserve filing units |
| `value_normalized` | decimal | USD or base unit |
| `period_start`, `period_end` | date | No mixed periods in one ratio |
| `source_id` | text | Required |

`market_observation`

| Field | Type | Rule |
|---|---|---|
| `observation_id` | text | Stable identifier |
| `product_id` | text | Expected `BTC-USD` |
| `kind` | enum | `candle` or `book_snapshot` |
| `observed_at_utc` | timestamp | Required |
| `price`, `quantity` | decimal | String input parsed without binary rounding |
| `book_side`, `book_level` | text or integer | Null for candles |
| `source_id` | text | Required |

## Fictional case records

`facility` contains `case_id`, requested commitment, funded exposure, accrued amount, tenor, use of proceeds, repayment rail, maturity, and required coverage ratio.

`collateral_lot` contains asset, quantity, quoted price source, chain, custodian class, ownership evidence state, lien state, control state, confirmation state, earliest usable timestamp, route to repayment rail, execution-cost schedule, and fixed costs.

`portfolio_exposure` contains fictional name, funded and potential exposure, sector, collateral asset, custodian, chain, bank route, and shared risk tags.

`policy_limit` contains limit type, threshold, measurement basis, hard or soft status, effective date, and assumption ID. Every limit is illustrative.

`scenario` contains price shock, execution-cost basis points, availability delay, route availability, borrower stress, and portfolio changes. Change one driver at a time before combining stresses.

`condition` contains a stable ID, category, requirement, evidence class and status, blocking flag, accountable owner role, timing, verification method, and assumption source ID. Conditional approval and authority to fund are separate states.

`monitoring_rule` contains a stable ID, metric, threshold, frequency, owner role, source IDs, measurement method, breach action, and escalation path. Projected values and observed borrower reporting use different statuses.

`covenant` contains a stable ID, type, draft requirement, threshold, test frequency, cure period, breach consequence, accountable owner, and exactly one linked monitoring rule. Every covenant remains `draft_only` until executed and legally reviewed.

`escalation_playbook` contains a stable ID, exactly one linked monitoring rule and covenant, trigger severity, response clock, draw state, decision owner, required evidence, exit criteria, and the current non-incident response state.

`scenario_attribution` contains one row per declared engine scenario with recommendation and proceeds deltas against base, a deterministic severity rank, binding constraint, primary driver classification, hard blockers, and resolution evidence. It does not own or alter decision logic.

`decision_lineage` contains one node per committee-relevant claim with its current resolved value, registered evidence IDs and classes, calculation or judgment rule, artifact anchor, workbook cell, accountable owner, and explicit limitation.

`diligence_task` extends exactly one pre-funding condition with priority, parallel lane, acyclic dependencies, decision impact, affected lineage nodes, failure consequence, completion output, execution wave, and current action.

`assumption_governance` extends exactly one registered `ASM-C` evidence record with materiality, validation status, accountable owner, workbook inputs, validation method, challenge trigger, and downstream lineage nodes.

## Decision output

`decision_record` contains:

- case and scenario version;
- requested and recommended amount;
- obligor, collateral, single-name, and concentration caps;
- binding cap;
- hard blockers and conditions;
- structured condition register, outstanding blocking-condition IDs, and funding-gate status;
- available proceeds, requested-draw recovery exposure and shortfall;
- recommended pro forma exposure and its coverage surplus;
- illustrative rating with written rationale;
- reversal trigger;
- source coverage rate;
- preparer and review status.

## Invariants

- A reported issuer fact cannot share a row with a fictional facility input.
- A collateral lot with unknown ownership, prior lien, or legal control receives no eligible value until the policy explicitly permits a conservative treatment.
- Lower price or accessibility cannot increase available proceeds when other inputs stay fixed.
- On the decision surface, increasing price stress cannot increase the recommendation and increasing eligible collateral quantity cannot reduce it.
- Higher funded exposure cannot reduce shortfall when other inputs stay fixed.
- A decline has zero recommended pro forma exposure; otherwise it equals the recommended limit plus accrued amount.
- The collateral cap equals available proceeds divided by the required coverage ratio, less the accrued amount, so the recommended pro forma exposure keeps the required coverage.
- Recommended-limit coverage surplus equals available proceeds less recommended pro forma exposure. It is not floored, so a shortfall shows as a negative value.
- A limit breach cannot increase the recommended amount.
- A book snapshot cannot be reused as a historical observation for another time.
- A chain state cannot stand in for custody, legal control, or settlement on a bank rail.
- A projected monitoring pass cannot be represented as observed compliance.
- An illustrative response path cannot be represented as an open incident or observed borrower breach.
- Scenario attribution cannot be represented as a probability, forecast, causal estimate, or independent decision rule.
- Decision lineage cannot convert an assumed or simulated input into a reported fact merely because it is traceable.
- A diligence task cannot clear the funding gate until its underlying condition is verified; plan sequencing is not evidence completion.
- An assumption stays assumed or simulated and unvalidated until its named evidence and review method are completed.
