# First build in 25 to 35 focused hours

Status: execution plan, not started

## Milestone 1: a defensible paper decision

Target: 12 to 16 hours.

1. Freeze the June 2026 10-Q and 2025 10-K source snapshots. Build the source manifest.
2. Extract the income statement, balance sheet, cash flow, debt maturities, cash designations, and bitcoin availability facts.
3. Draft the fictional facility and a collateral schedule with no real address or claimed issuer ownership.
4. Build the obligor and collateral tabs in the workbook.
5. Reconcile one waterfall by hand.
6. Write the first two-page memo and one-page opposing memo.

Exit gate: the memo reaches a conditional decision, every material number has a source or assumption ID, and legal-access gaps can block collateral credit. This is the first useful artifact. Do not wait for an interface.

## Milestone 2: challenge the limit

Target: 8 to 10 hours.

1. Add two fictional portfolio exposures and four narrow caps.
2. Run the base, price, access, enforceability, borrower, and concentration cases.
3. Acquire BTC-USD daily candles only if the endpoint is available. Freeze requests in windows of at most 300 candles.
4. Add one timestamped book snapshot only if it helps explain the difference between displayed and executable liquidity.
5. Complete the validation report and correct defects.

Exit gate: adverse changes move results in the expected direction, the binding cap is visible, and one scenario changes a decision or condition for a defensible reason.

## Milestone 3: present and review

Target: 5 to 9 hours.

1. Produce the waterfall and four-cap chart.
2. Build the one-page reviewer brief.
3. Record the three-minute demo.
4. Ask a reviewer only after separate authorization to contact them.
5. Record self-review now and external feedback only if it occurs.

Build a local one-screen view only if CR-01 through CR-06 already meet their draft gates. A spreadsheet screen share is acceptable.

## Dependencies

The required build uses a spreadsheet editor, a PDF exporter, SEC filing snapshots, and standard CSV files. Public Coinbase Exchange data is optional. A Python standard-library fetch script is optional and should require no new package. A Base RPC client, JavaScript framework, database, cloud service, wallet, and x402 library are not required.

## Practical schedule

| Session | Work | Hours |
|---|---|---:|
| 1 | Source snapshot and extraction | 4-5 |
| 2 | Facility, collateral, and manual case | 4-5 |
| 3 | Obligor analysis and first memo | 4-6 |
| 4 | Portfolio and stress scenarios | 4-5 |
| 5 | Validation and corrections | 4-5 |
| 6 | Reviewer packet and demo | 5-9 |

The schedule is an estimate, not a deadline. If source reconciliation takes longer, remove the interface and live data before reducing analytical checks.

