# Open decisions and fallback paths

Status: unresolved at the end of planning

| Decision or gap | Why it matters | Resolve before | Fallback |
|---|---|---|---|
| Facility use of proceeds and repayment source | Shapes obligor analysis | Case version 1 | Use working-capital liquidity with bullet maturity and label it assumed |
| Fictional collateral asset and quantity | Drives Base relevance and recovery | Case version 1 | Use two alternate schedules, BTC offchain custody and USDC on Base, without claiming either is MARA property |
| Legal-control policy | Determines whether unknown enforceability blocks approval | Workbook design | Use a hard blocker and zero eligible value |
| Illustrative rating scale | Needed for written substantiation | Memo draft | Use five ordinal grades without default probabilities |
| Portfolio limit thresholds | Determines concentration cap | Scenario build | Use simple declared limits and sensitivity ranges, all marked assumed |
| Market-stress calibration | Avoids arbitrary shocks | Scenario build | Use fixed 30% and 50% shocks and disclose that they are sensitivities, not estimates |
| Order-book access | Affects execution-cost evidence | Milestone 2 | Remove observed-depth language and keep assumed cost ranges |
| Base decision value | Determines whether the module belongs | Demo lock | Remove Base if it changes no decision or condition |
| External practitioner review | Affects evidence of feedback | Ready-to-share gate | Record the opposing memo as self-review and make no external-validation claim |

## Recheck policy

Record a date and source whenever an open item closes. Do not silently replace an assumption with a fact. Create a new case version when a resolved item changes a material result.

