# External review execution kit

This kit prepares the three human gates. It does not count as review evidence. Only a real reviewer response with retained evidence can change a gate status.

## HG-01: independent calculation reproduction

### Reviewer

Use an independent second reader with financial-model review experience. Do not give the reviewer the workbook result before the calculation.

### Inputs to provide

- 4,000,000 fictional USDC
- $1.00 reference price
- 2% price or convertibility stress
- 50 basis points of execution cost on stressed gross value
- 25 basis points of delay cost on stressed gross value
- $20,000 fixed cost
- 1.25x required coverage

### Ask the reviewer to return

- Dated calculation steps
- Available proceeds and unrounded collateral cap
- Variance from the project result, if known after completion
- The assumption that most affects the result
- Any ambiguous instruction
- Reviewer role and attribution permission
- PASS, FAIL, or NEEDS WORK conclusion

### Pass standard

Available proceeds must equal $3,870,600 within $1. The collateral cap must equal $3,096,480 within $1. The reviewer must document independent steps and any ambiguity.

## HG-02: unscripted presentation assessment

### Reviewer

Use an observer who did not build the case.

### Materials

- `outputs/committee-packet.pdf`
- `outputs/reviewer-brief.pdf`
- `outputs/decision-view.html`

### Procedure

1. Give the presenter five minutes to explain the case without reading a script.
2. Ask why the recommendation is $3.0 million rather than $5.0 million.
3. Ask why a conditional recommendation remains blocked from funding.
4. Ask for the strongest case for decline.
5. Ask what evidence would reverse the decision.
6. Record inaccuracies, misunderstandings, corrections, and follow-up actions.

### Pass standard

The presenter answers all four questions accurately, keeps public facts separate from fictional inputs, and does not claim Coinbase policy, legal validation, or authority to fund.

## HG-03: attributed practitioner feedback

### Reviewer

Use an external credit, legal, collateral, or portfolio practitioner who is authorized to respond in their personal or professional capacity.

### Request

> I built a hypothetical secured-credit case using public MARA filings and fictional lending terms. Would you review the attached one-page brief and tell me which decision assumption you would challenge first, what evidence would change your conclusion, and which proposed control seems operationally unrealistic? May I attribute your role and summarize your response in the project log?

### Evidence to retain

- Dated response or contemporaneous notes
- Reviewer role
- Attribution permission: YES, NO, or ROLE_ONLY
- Actual feedback without embellishment
- Resulting project change
- Remaining disagreement
- PASS, FAIL, or NEEDS WORK conclusion

## Record completed evidence

Store evidence inside the project. Then run the guarded command shown in `README.md`. Rebuild with:

```bash
python3 scripts/build_package.py
```

Confirm that the readiness report reflects the evidence. Never edit readiness status directly.
