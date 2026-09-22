# Reviewer brief: challenge the first decision

**Draft:** MARA-CR-001  
**Review status:** Self-review only; no external review or model validation completed

## Decision in one line

Would you support a **conditional $3.0 million limit** on a hypothetical $5.0 million, 12-month MARA working-capital facility when the binding constraint is a fictional collateral schedule and primary-repayment diligence remains incomplete?

All facility, collateral, Base, portfolio, policy, and rating terms are fictional. MARA is not represented as a Coinbase customer.

## Illustrative result

| Cap | Amount | What drives it |
|---|---:|---|
| Obligor | $7.5m | Assumed policy judgment |
| **Collateral** | **$3.096m** | 4.0m fictional USDC, 2% stress, explicit costs, 1.25x coverage |
| Single-name | $6.0m | Assumed limit |
| Concentration | $4.0m | Assumed shared-route limit |
| **Recommendation** | **$3.0m** | Rounded below collateral cap; conditions must be met before funding |

Public issuer context is mixed: MARA reported $421.3 million of cash and cash equivalents, $2.1 billion fair value across 35,577 bitcoin, and approximately $2.4 billion of debt at June 30, 2026 (SRC-001). Its 2025 filing reported $802.7 million of net operating cash use (SRC-002). Reported bitcoin is **not** treated as facility collateral.

## Decision logic

```text
$4.000m quoted fictional collateral
− $0.080m price/convertibility stress
− $0.0196m execution cost
− $0.0098m delay cost
− $0.020m fixed cost
= $3.8706m available proceeds
÷ 1.25x required coverage
= $3.09648m collateral cap → $3.0m rounded recommendation
```

Ownership, first priority, legal control, custody, and the repayment route remain unverified. Any unresolved item blocks collateral credit and therefore blocks funding under the recommendation.

## Strongest opposing view

The $3.0 million cap is an artifact of invented collateral. A cleaner decision is to decline pending private diligence, then underwrite the requested $5.0 million against actual repayment capacity instead of manufacturing precision from a synthetic schedule. Read the full [opposing memo](opposing-memo.md).

## One unresolved assumption

Can public information plus a current borrower cash forecast support the assumed $7.5 million obligor cap without relying on collateral (ASM-C004)?

## Review question

**Would you challenge the primary-repayment analysis, the collateral-access blocker, or the use of a fictional portfolio cap first—and what specific evidence would change your answer?**

Supporting materials: [credit memo](credit-memo.md), [source register](source-register.csv), and [reproducibility guide](reproducibility.md).
