# Credit Decision Context

This context defines the project’s credit-decision language. It keeps analytical recommendations, evidence gates, and real funding authority separate.

## Language

**Illustrative rating**:
An ordinal obligor-risk judgment produced from declared factors and assumed weights. It is not a calibrated probability of default or a Coinbase rating.
_Avoid_: Credit score, default grade, Coinbase rating

**Rating factor**:
A separately evidenced dimension that contributes to the illustrative rating through a declared score and weight.
_Avoid_: Signal, feature

**Obligor cap**:
The maximum exposure supported by the illustrative standalone borrower assessment before collateral and portfolio constraints.
_Avoid_: Credit limit, approved amount

**Decision cap**:
One of the obligor, collateral, single-name, or concentration constraints used to determine the recommendation.
_Avoid_: Limit when the specific cap is known

**Conditional recommendation**:
An analytical recommendation that becomes actionable only after every blocking pre-funding condition is verified.
_Avoid_: Approval, cleared facility

**Funding gate**:
The separate state that records whether blocking conditions permit funding. A positive recommendation does not clear this gate.
_Avoid_: Approval status

**Hard blocker**:
A failed or unknown scenario state that forces zero eligible collateral credit and a decline in that scenario.
_Avoid_: Haircut, warning

**Pre-funding condition**:
A named evidence requirement with an owner, status, and verification method that must be satisfied before funding.
_Avoid_: Checklist item, note

**Evidence class**:
The declared origin of a value: reported, observed, calculated, assumed, or simulated.
_Avoid_: Confidence level
