# Illustrative credit memorandum: MARA Holdings, Inc.

**Status:** Draft for self-review; not externally reviewed  
**Case version:** MARA-CR-001  
**Information date:** June 30, 2026  
**Decision:** Conditionally approve a maximum **$3.0 million** commitment, subject to the pre-funding conditions below; otherwise decline.

> This is a hypothetical exercise using public issuer information. MARA is not represented as a Coinbase customer. The facility, collateral, Base location, covenants, portfolio, policy limits, and internal rating are fictional. The results below are illustrative calculations, not outputs of a completed or tested model.

## Request and recommendation

The fictional request is a $5.0 million, 12-month revolving working-capital facility with a bullet maturity (ASM-C001). I would not approve it as proposed. I would permit a rounded $3.0 million commitment only after the lender obtains satisfactory evidence of collateral ownership, first priority, and legal control and validates the repayment route (ASM-C002, ASM-C007).

The $3.0 million limit is below the illustrative collateral cap of $3.096 million and is the lowest of the four assumed caps. It is not supported by MARA's reported bitcoin holdings. The collateral schedule instead assumes 4.0 million USDC on Base in a lender-controlled structure that has not been evidenced (ASM-C002).

| Cap | Illustrative amount | Basis |
|---|---:|---|
| Obligor | $7.5m | Fictional policy judgment; no calibrated probability of default (ASM-C004) |
| Collateral | $3.096m | Fictional waterfall shown below (ASM-C002, ASM-C003) |
| Single-name | $6.0m | Fictional policy limit (ASM-C005) |
| Concentration | $4.0m | Fictional shared-route limit (ASM-C006) |
| **Recommended commitment** | **$3.0m** | Rounded below the binding collateral cap |

## Credit view

MARA reported $421.3 million of cash and cash equivalents at June 30, 2026, but approximately 30% was held by majority-owned Exaion and designated for its operations over the following year (SRC-001). MARA also reported 35,577 bitcoin with a $2.1 billion fair value: 4,742 loaned, 4,528 pledged, and 26,307 described as unrestricted (SRC-001). None is assumed to secure this facility.

Liquidity must be read beside leverage and cash use. MARA reported approximately $2.4 billion of debt after note repurchases, including a $150 million line of credit due within twelve months, $48.1 million of December 2026 notes, and $291.6 million classified current because holders can require repurchase in June 2027 (SRC-001). The 2025 Form 10-K reported $802.7 million of net cash used in operating activities and $3.6 billion of year-end debt (SRC-002). These facts support capacity at the requested scale but also argue against treating headline liquidity as an uncomplicated repayment source.

A static public-data bridge sharpens that tension. Reported cash less the approximate Exaion designation, the $150 million line, and the $48.1 million December 2026 notes leaves **$96.81 million**. Adding the $291.6 million holder-put sensitivity produces **negative $194.79 million**. This is not a liquidity forecast: it excludes inflows, operating needs, capex, taxes, other restrictions, and unlisted obligations, and it does not assert that holders will exercise the put.

The **primary repayment source is not yet established**. For this draft, it is assumed to be unrestricted operating liquidity and working-capital cash generation, not collateral liquidation (ASM-C001). That assumption requires a current cash forecast, facility purpose, legal-entity cash map, and debt-service schedule before funding. The illustrative internal grade is **3 / Watchful**, produced by five declared factors with a weighted score of **3.10**: ample reported asset liquidity relative to the request, offset by material leverage, historical operating cash use, bitcoin price exposure, and incomplete private diligence (ASM-C004). It is an ordinal judgment, not a calibrated probability of default or Coinbase rating.

## Illustrative collateral waterfall

The schedule assumes 4.0 million USDC on Base at $1.00, a 2% price/convertibility stress, 50 basis points of execution cost on stressed gross value, $9,800 of delay cost, $20,000 of fixed cost, and 1.25x required coverage (ASM-C002, ASM-C003).

| Step | Calculation | Amount |
|---|---|---:|
| Quoted value | 4,000,000 × $1.00 | $4,000,000 |
| Stressed gross value | $4,000,000 × 98% | $3,920,000 |
| Execution cost | $3,920,000 × 0.50% | ($19,600) |
| Delay cost | Assumed | ($9,800) |
| Fixed cost | Assumed | ($20,000) |
| Available proceeds | Stressed value less costs | $3,870,600 |
| **Collateral cap** | $3,870,600 ÷ 1.25 | **$3,096,480** |

The waterfall applies only if ownership, lien priority, legal control, custody, and the route to the repayment rail are evidenced. A Base transaction state does not prove any of those facts. If a canonical Base-to-Ethereum withdrawal is required, the route may face a roughly one-week challenge window; that delay should not be imposed on a Base-to-Base transfer (SRC-005). Unknown enforceability means zero collateral credit, not a larger haircut.

## Conditions precedent

1. Obtain satisfactory evidence of beneficial ownership, no prior lien, first-priority security, and enforceable lender control over the fictional collateral lot.
2. Test a read-only route from custody through liquidation and settlement to the contractual repayment rail; do not require a wallet transaction for this project.
3. Receive a 13-week cash forecast, use-of-proceeds schedule, legal-entity cash map, and complete debt-service schedule supporting primary repayment.
4. Cap commitment at $3.0 million, require collateral coverage of at least 1.25x under the stated waterfall, and prohibit substitution without a new case version.
5. Confirm the fictional single-name and shared-route limits before funding; any hard-limit breach reduces the commitment.

## Principal risks and monitoring

The post-close design contains eight owned rules with stated thresholds, frequency, breach actions, and escalation. It is not active monitoring or evidence of compliance. At the current base projection, collateral coverage at the recommended limit is **1.269x** and concentration headroom is **$1.0 million**. Ownership, priority, and control remain blocked before funding. Five borrower-reporting and route-test measures remain unmeasured.

- **Repayment risk:** require at least $25 million of borrowing-entity unrestricted cash, no adverse operating-cash variance greater than 20% to the approved forecast, and monthly reporting within 15 business days. A breach freezes new availability or refreshes the rating and repayment analysis.
- **Collateral-access risk:** maintain at least 1.25x coverage, continuous verified ownership/priority/control, and a monthly Base-to-cash route test completed within four hours. Failure blocks draws or assigns zero collateral credit.
- **Wrong-way and concentration risk:** require nonnegative USDC concentration headroom before each draw and lender consent for any additional secured debt or lien. A breach rejects the draw and triggers portfolio, credit, and legal review.

## Reversal evidence

Increase toward the $5.0 million request only if a refreshed cash forecast and debt schedule support repayment without collateral, or if additional eligible collateral raises the binding cap without breaching another policy limit. Decline if ownership, priority, control, or repayment-route evidence cannot be obtained; if the cash forecast does not support debt service; or if correlated stress makes the $3.0 million limit inconsistent with the fictional portfolio limits.

## Sources

See [source-register.csv](source-register.csv). Rebuild instructions and limitations are in [reproducibility.md](reproducibility.md). The strongest case against this recommendation is in [opposing-memo.md](opposing-memo.md).
