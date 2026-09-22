# Compare three project designs

Status: design selection

| Design | Decision | Evidence strength | Practitioner value | Main failure | Verdict |
|---|---|---|---|---|---|
| A. Credit committee case with availability-aware collateral | Approve, condition, reduce, or decline the $5 million facility | High for public obligor facts; explicit assumptions for deal terms | Tests underwriting, written substantiation, liquidity, concentration, and monitoring | Can imply false precision or a real relationship if labels fail | Select |
| B. Collateral liquidation simulator | Set a haircut or eligible collateral amount | Medium; price history is available but historical executable depth is weak | Strong asset-liquidity component | Becomes a market-risk tool with little financial-statement analysis | Keep as one module in A |
| C. Portfolio concentration monitor | Decide whether a new exposure breaches limits | Low-to-medium because the portfolio is fictional | Shows portfolio review and shared dependencies | The obligor can become a token row in a dashboard | Keep as one cap in A |

## Why A wins

Design A supports a disputed credit decision. It requires the builder to form a view on repayment capacity before giving collateral credit. It also gives the Base scenario a precise job: determine when collateral is usable for the obligation, not decorate the project with chain data.

The design uses B and C without letting either dominate. The liquidation module produces stressed proceeds. The concentration module determines whether an otherwise supportable limit fits the fictional portfolio. The memo explains which cap binds and why.

## Designs rejected from core scope

- A borrower default model is rejected. Public observations do not support a calibrated probability of default for this case.
- A live lending app is rejected. Execution, wallet custody, and automated approval add risk without improving the committee decision.
- A Base wallet balance viewer is rejected. A balance does not establish ownership, availability, priority, or repayment capacity.
- An x402 evidence purchase is deferred. The first version does not need a paid information state machine.
- A broad market dashboard is rejected. It adds screens while hiding the decision.

## Selection test

Keep a component only if removing it changes at least one of these outputs:

- the recommended limit;
- an approval condition;
- the hard-blocker state;
- the monitoring or decision-reversal trigger;
- the strength of the opposing memo.

If a Base scenario, API call, chart, or interface does not change one of those outputs, remove it from the core package.

