# Adversarial review and scope cuts

Status: design self-review

## The strongest criticism

The project can look more rigorous than it is. A precise spreadsheet cannot replace private diligence, legal review, collateral control evidence, or an actual portfolio. A reviewer may conclude that the public-company case says little about institutional counterparty underwriting because the deal terms and portfolio are invented.

That criticism is fair. The project earns credibility only by making the boundary central to the decision. Missing ownership, priority, custody, or remedy evidence must block collateral credit. The memo must explain what can and cannot be concluded from the filing.

## Material weaknesses

### The requested amount is too small to stress MARA's reported scale

A $5 million request is small relative to reported cash and bitcoin. This can make approval seem trivial. The model must avoid solving the case with a simple cash-to-loan ratio. The decision should test availability, primary repayment, structure, and policy discipline. If no constraint becomes meaningful without implausible assumptions, switch to a fully fictional mid-sized counterparty while preserving MARA as a financial-analysis exercise.

### Public bitcoin holdings are not facility collateral

The issuer's holdings cannot be copied into the fictional collateral schedule. Create a separate, small collateral package with explicit fictional labels. Cite MARA holdings only in the obligor analysis.

### Base may feel attached after the fact

MARA's reported holdings are Bitcoin, not Base assets. The Base case must be an explicitly fictional alternate collateral schedule or portfolio exposure. If a reviewer cannot see why the repayment rail changes availability, remove Base from the core demo.

### Market liquidity evidence is thin

Daily candles support price history, not execution capacity. One order-book snapshot is not stress evidence. Use it only to explain the data shape. Base the adverse unwind on labeled sensitivity ranges and state that historical stressed depth was not acquired.

### Illustrative ratings can imply false calibration

Use ordinal grades with written criteria. Do not attach default probabilities, loss rates, or claims of Coinbase policy. Show which evidence moves the grade.

### Concentration is fictional

Two invented exposures demonstrate mechanics, not empirical portfolio risk. Keep the shared-risk story narrow and deterministic. Do not claim portfolio optimization.

## Required cuts when time runs short

Cut in this order:

1. Live Base RPC adapter.
2. Local web interface.
3. Order-book snapshot ingestion.
4. More than two fictional portfolio exposures.
5. More than seven stress scenarios in the reviewer-facing package.

Never cut the source register, opposing memo, hard blockers, manual reconciliation, or public-versus-fictional labels.

## Conditions that should stop the project

- Filing values cannot be reconciled across periods.
- The final recommendation depends on an unstated legal conclusion.
- The builder cannot explain the limit without the interface.
- Base or concentration exists only for visual interest.
- The memo treats a reported balance as controlled collateral.
- A reviewer cannot reproduce the waterfall.

The right result can be a well-supported conditional decline. The project fails only if it hides uncertainty or forces a preferred answer.

