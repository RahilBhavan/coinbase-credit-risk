# Validation plan

Status: automated evidence, calculation, scenario, and package checks executed; independent human review remains

Each executed check must record the case version, expected result, actual result, method, exit status when applicable, evidence path, date, reviewer, and status.

## Evidence checks

| ID | Check | Expected result |
|---|---|---|
| E-01 | Trace every material memo number | 100% maps to a source ID or assumption ID |
| E-02 | Compare workbook filing inputs with SEC facts | Period, unit, sign, and value agree |
| E-03 | Search for mixed issuer and fictional deal claims | No row or sentence implies actual MARA facility terms or Coinbase relationship |
| E-04 | Verify snapshot manifest and hashes | Every acquired file has retrieval metadata and a stable hash |

## Calculation checks

| ID | Change | Expected result |
|---|---|---|
| C-01 | Lower collateral price | Available proceeds do not increase |
| C-02 | Increase execution cost or delay cost | Available proceeds do not increase |
| C-03 | Move a lot from accessible to inaccessible | Eligible quantity and collateral cap do not increase |
| C-04 | Increase funded exposure | Shortfall does not decrease |
| C-05 | Compare recovery and approval exposure bases | Full-request shortfall remains separate from recommended pro forma exposure and surplus |
| C-05 | Breach a concentration threshold | Recommended limit does not increase |
| C-06 | Set enforceability to unknown | Hard blocker appears and no collateral credit is granted |
| C-07 | Recalculate one base case by hand | Difference is no more than $1 after declared rounding |

## Scenario checks

Run base, 30% USDC decline, 50% USDC decline, stale price, zero collateral, route failure, 24-hour access delay, one-week canonical-withdrawal case, missing ownership evidence, borrower cash stress, and correlated portfolio stress. Do not assume that each scenario produces a different recommendation.

## Base checks

- Keep chain confirmation, custody control, legal control, liquidation, transfer, and bank settlement as separate fields.
- Apply a canonical-withdrawal delay only to the route that uses it.
- Confirm that a Base-to-Base obligation does not inherit an Ethereum withdrawal delay.
- Remove the Base module if no availability field changes the decision or a condition.

## Data-quality checks

- Deduplicate candles by product and bucket start.
- Detect missing daily buckets and nonnumeric fields.
- Record the candles request windows because each request allows at most 300 points.
- Treat the order book as one timestamped observation.
- Never infer historical depth from the current snapshot.

## Human review

The builder reviews every generated sentence against the approved tables. The opposing memo receives a separate self-review. A second person, if available, reproduces one calculation without coaching.

The automated results are recorded in `../artifacts/validation-report.md`. The filing fact ledger in `../artifacts/issuer-fact-ledger.csv` records exact values, presentation values, differences, and rounding tolerances. Independent human reproduction and legal review remain outside the automated pass.
