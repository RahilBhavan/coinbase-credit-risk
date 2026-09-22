# MARA case evidence is feasible with strict limits

Status: cited public sources acquired and hash-frozen; market-data acquisition not run  
Evidence review date: September 20, 2026

## Selected public issuer

MARA Holdings, Inc. is the selected case because its current SEC filings expose liquidity, debt, operating cash use, and several states of bitcoin availability. The June 30, 2026 Form 10-Q reports:

- $421.3 million of cash and cash equivalents, excluding restricted cash;
- about 30% of cash and cash equivalents held by majority-owned Exaion and designated for its operations for the next year;
- 35,577 bitcoin with a reported fair value of $2.1 billion at $58,524 per bitcoin;
- 4,742 bitcoin loaned to third parties, 4,528 pledged as collateral, and 26,307 reported as unrestricted;
- about $2.4 billion of debt after note repurchases;
- a $150 million line of credit due within twelve months, $48.1 million of December 2026 notes, and $291.6 million classified current because holders can require repurchase in June 2027.

These facts are enough to study financial capacity and asset availability. They are not enough to approve a real loan. The filing does not establish which assets a new lender could take, where the assets are held, whether liens exist beyond disclosed pledges, or whether a security interest would be enforceable.

The December 31, 2025 Form 10-K adds an audited annual baseline. It reports $802.7 million of net cash used in operating activities and $3.6 billion of debt at year end. The June 2026 filing must control for current balances, while the annual filing supports trend and accounting analysis.

## Concrete data package

The first build needs five small inputs:

| Dataset | Source | Planned rows | Use | Feasibility |
|---|---|---:|---|---|
| Annual financials | MARA 2025 Form 10-K | 2 fiscal years plus footnotes | earnings quality, cash use, debt baseline | High |
| Interim financials | MARA June 2026 Form 10-Q | current and prior interim periods | current liquidity and maturities | High |
| BTC-USD daily candles | Coinbase Exchange public candles endpoint | 365 to 730 daily observations | transparent price-stress anchors | Medium-high |
| One timestamped BTC-USD level-2 book snapshot | Coinbase Exchange public book endpoint | one raw response plus metadata | illustrate point-in-time executable depth | Medium |
| Fictional case inputs | versioned CSV created by the builder | fewer than 50 rows | facility, collateral location, portfolio, policy | High |

The official candles documentation says a request returns at most 300 candles and can omit intervals without ticks. Acquisition must therefore use explicit, non-overlapping time windows, retain raw responses, deduplicate by bucket timestamp, and report missing buckets. The endpoint is useful for price history, not historical order-book reconstruction.

The official book endpoint can return an aggregated level-2 book. It is a point-in-time observation, not proof that the displayed liquidity was executable for the whole unwind, available historically, or representative of stress. The first build should use it as a labeled observation and use declared execution-cost sensitivities for adverse cases.

## Base evidence boundary

The first build uses synthetic Base records only. Each record states asset, quantity, chain, custody state, legal-control state, confirmation state, earliest usable time, exit route, and destination rail. The scenario can compare:

- USDC on Base for an obligation due on Base;
- an asset on Base that must reach Ethereum through a canonical withdrawal;
- proceeds that must reach a bank account after transfer and sale.

Base documentation distinguishes unsafe, safe, and finalized L2 states. It also describes a one-week challenge window for optimistic-rollup withdrawals finalized on L1. Do not apply that delay to ordinary Base transfers or every off-ramp. A later read-only adapter may inspect public blocks and receipts, but it still cannot prove ownership, lien priority, or lender control.

## Acquisition and reproducibility rules

1. Save every raw response or filing extract unchanged under a dated snapshot directory.
2. Record source URL, publication date, retrieval time in UTC, request parameters, response hash, unit, and period.
3. Normalize with a deterministic script or workbook import. Do not hand-copy material figures without a second check.
4. Tag every value as `reported`, `observed`, `calculated`, `assumed`, or `simulated`.
5. Keep issuer facts in separate tables from fictional deal terms.
6. Freeze a case version before memo drafting.

## Frozen evidence package

The five cited public pages were retrieved on September 20, 2026 and preserved under `snapshots/2026-09-20/`. The canonical source register records each local path and SHA-256 digest. Package validation recomputes those hashes and rejects missing or modified snapshots. Live URLs remain in the register for provenance, but reproduction no longer depends on those pages remaining unchanged.

## Fallbacks

- If the Coinbase candles endpoint is unavailable, use dated BTC fair values from the SEC filings for the minimum case and label all stress prices as assumed.
- If a full level-2 snapshot is unavailable, remove observed depth. Keep a sensitivity table for execution cost and state that no market-depth evidence was acquired.
- If MARA reporting definitions or periods cannot be reconciled, stop issuer-specific underwriting and switch to a fully fictional borrower. Do not mix unreconciled public figures into a conclusion.
- If Base does not change a timing or access constraint, keep Base out of the demo.

## Sources reviewed

- [MARA June 30, 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1507605/000150760526000022/mara-20260630.htm)
- [MARA 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1507605/000150760526000007/mara-20251231.htm)
- [Coinbase Exchange product candles](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles)
- [Coinbase Exchange product book](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-book)
- [Base transaction derivation and finality](https://docs.base.org/base-chain/specs/protocol/consensus/derivation)
