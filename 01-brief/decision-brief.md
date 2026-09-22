# Decide the facility, not the dashboard

Status: design decision  
Case date: June 30, 2026 financial information  
Decision date: hypothetical

## Committee question

Should the committee approve a hypothetical $5 million, 12-month revolving facility to MARA Holdings, Inc., and if so, what funded limit and conditions are defensible?

The committee must choose one outcome:

1. Approve up to $5 million.
2. Approve a lower amount or add conditions.
3. Decline until a named diligence gap is resolved.
4. Decline because repayment capacity or collateral support remains inadequate under the stated policy.

## What the analysis must answer

- What is the primary repayment source without collateral liquidation?
- How much liquidity is available after separating restricted, pledged, loaned, designated, or otherwise unavailable assets?
- What collateral does the fictional agreement cover, where is it held, and when can the lender control it?
- What are proceeds after price stress, execution cost, delay cost, fixed cost, and enforceability constraints?
- Which obligor, recovery, single-name, sector, and shared-dependency cap binds?
- What evidence would reverse the decision?

## Case boundary

MARA's filings supply reported financial facts. The following items are fictional assumptions until the builder replaces them with a versioned case file:

- the $5 million request, tenor, pricing, use of proceeds, and amortization;
- every covenant, representation, default, remedy, and security interest;
- the collateral quantity, asset, address, custodian, chain, and control agreement;
- Base availability and withdrawal routes;
- the two portfolio exposures and every concentration limit;
- internal rating grades and policy caps.

Do not infer an actual commercial relationship from this exercise. Do not connect a public address to MARA. Do not use MARA's reported bitcoin holdings as if they were pledged to this facility.

## Planned recommendation method

The model calculates four independent caps:

`final limit = min(obligor cap, collateral cap, single-name cap, concentration cap)`

Approval also requires all hard blockers to be false. Hard blockers include missing evidence of ownership, unavailable legal control, double-pledged collateral, an unapproved custody route, and a repayment route that cannot meet the obligation date.

The collateral calculation keeps each loss source visible:

`available proceeds = accessible quantity × stressed price − execution cost − delay cost − fixed cost`

`collateral cap = max(0, available proceeds ÷ required coverage ratio)`

`requested-draw recovery shortfall = max(0, requested fully drawn exposure + accrued amounts − available proceeds)`

`recommended pro forma exposure = recommended limit + accrued amounts` when the decision is not a decline; otherwise zero.

`recommended-limit coverage surplus = max(0, available proceeds − recommended pro forma exposure)`

The requested-draw shortfall tests recovery if the full request were outstanding. It is not the exposure created by the smaller recommended limit.

Accessibility is a scenario field, not a haircut. If enforceability is unknown, the collateral cap is blocked rather than quietly reduced by an arbitrary percentage.

## Required alternatives

The committee compares the requested facility with at least two alternatives:

- a smaller facility that relies on operating liquidity and excludes disputed collateral;
- a facility with lender-controlled eligible collateral and a tested route to the repayment rail;
- decline until ownership, priority, custody, and remedy evidence is complete.

The opposing memo must state the strongest case against the chosen recommendation. A useful opposing case could argue that a $5 million exposure is immaterial relative to reported liquidity, or that reported liquidity overstates resources available when operating cash use, asset volatility, existing pledges, and legal access are considered together.

## Success standard

A credit practitioner should be able to identify the decision, binding constraint, three material assumptions, strongest objection, and reversal evidence in three minutes. A second reader should reproduce one scenario from source rows and formulas without using the interface.
