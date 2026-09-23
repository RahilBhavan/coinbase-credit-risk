# Coinbase Credit Risk case

Status: complete local reviewer package; illustrative case, independent human gates outstanding  
Prepared: September 20, 2026  

## The decision

Should a lender approve a hypothetical $5 million, 12-month secured revolving facility to MARA Holdings, Inc.?

MARA is the public-information case. The facility, collateral package, Base location, covenants, and two portfolio exposures are fictional. Nothing in this package claims that MARA is a Coinbase customer or that Coinbase is considering this transaction.

The recommended design is a **credit committee case with an availability-aware collateral waterfall**. It starts with the obligor's financial capacity, then applies collateral access, liquidation, concentration, and enforceability constraints. The planned output may recommend approval, a smaller conditional limit, or decline. The analysis must earn the answer.

## Why this design

The June 30, 2026 MARA filing gives the case real tension. MARA reported $421.3 million of cash and cash equivalents, 35,577 bitcoin with a $2.1 billion fair value, and about $2.4 billion of debt. Of the bitcoin, 4,742 were loaned, 4,528 were pledged, and 26,307 were reported as unrestricted. About 30% of cash was held by a majority-owned subsidiary and designated for its operations for the next year. These are public issuer facts, not claims about collateral available to this facility.

The fictional collateral schedule forces the committee to distinguish quoted value from assets that the lender can control and turn into repayment cash on time. A separate Base scenario asks whether collateral on Base is available for an obligation due on Base, Ethereum, or a bank rail. It does not treat chain confirmation as legal ownership or perfected security.

## Package map

- [Decision brief](01-brief/decision-brief.md): the committee question, boundaries, and decision rule.
- [Data feasibility](02-research/data-feasibility.md): candidate evidence, source limits, and fallbacks.
- [Source register](02-research/source-register.csv): dated evidence and assumption classes.
- [Design comparison](03-design/options.md): three designs and the selection.
- [Architecture](03-design/architecture.md) and [data model](03-design/data-model.md): planned calculation flow and records.
- [Deliverables](04-deliverables/deliverables.md): exact outputs and acceptance criteria.
- [Demo storyboard](04-deliverables/demo-storyboard.md) and [reviewer packet](04-deliverables/reviewer-packet.md): how the work is presented.
- [Validation plan](05-validation/validation-plan.md) and [adversarial review](05-validation/adversarial-review.md): checks, weaknesses, and scope cuts.
- [First build](06-execution/first-build.md): a 25-to-35-hour sequence with stop gates.
- [Open decisions](06-execution/open-decisions.md): unresolved facts and fallback paths.
- [Artifact manifest](artifacts/manifest.md): planned files and honest status labels.
- [Prior plans](02-research/prior-plans/): preserved copies of the source package.

## Scope and status

The first build now includes a deterministic Python decision engine, a reconciled public-data liquidity bridge, a transparent five-factor illustrative rating bridge, an auditable Excel workbook, eleven scenarios, a structured nine-item pre-funding condition register, an eight-rule monitoring and early-warning design, an eight-path escalation playbook, an eight-item model-risk register, a live collateral what-if lab, automated checks, a two-page credit memo, an opposing memo, a reviewer brief, a self-contained decision view, a captioned demo video, and a portable review bundle with its own checksums. The Base layer remains a fictional availability scenario. No live RPC adapter exists. x402 is deferred.

The monitoring design keeps projections separate from observed compliance: two measures are calculable projections, one remains blocked before funding, and five require private borrower reporting or route testing.

The escalation playbook turns every monitoring trigger into a response clock, draw state, named decision owner, evidence package, and exit criterion. It remains inactive design: no incident or borrower breach is represented as observed.

The decision view includes a browser-local what-if lab for collateral quantity, price decline, route delay, execution cost, and hard blockers. Four engine-derived boundary cases execute in the page at load time so the interactive implementation fails visibly if it diverges from the generated contract.

Scenario attribution quantifies each case against the base recommendation and proceeds, identifies the binding driver, ranks severity deterministically, and states the evidence needed to resolve or mitigate the result. It explains the declared engine outputs without adding probabilities or a separate decision rule.

Decision lineage connects eleven committee headlines to 32 registered evidence links, their exact calculation or judgment rule, generated artifact, workbook cell, accountable owner, and limitation. The interface exposes the same trace so a reviewer can move from decision to evidence without reverse-engineering the package.

The diligence execution plan converts all nine blocking conditions into four parallel work lanes. Eight tasks can start immediately; the control agreement is sequenced after ownership and lien verification. Every task states its decision impact, affected lineage claims, completion output, and failure consequence.

The assumption register governs all seven `ASM-C` records with materiality, ownership, exact workbook inputs, validation methods, challenge triggers, and 27 downstream decision-lineage links. Every record remains explicitly unvalidated and retains its assumed or simulated evidence class.

The public-data liquidity bridge leaves $96.81 million after designated cash and two identified near-term obligations, but negative $194.79 million after adding the June 2027 holder-put sensitivity. It is intentionally labeled as a static screen rather than a borrowing-entity forecast.

## Run the first build

Rebuild and verify the full reviewer package in dependency order:

```bash
python3 scripts/build_package.py
```

On macOS, add `--with-demo` to regenerate the captioned AVFoundation video. The default preserves the already-built demo so the core package remains rebuildable in environments without macOS media frameworks.

Run the engine tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Rebuild all scenario outputs:

```bash
PYTHONPATH=src python3 -m credit_risk --case-dir data/case --all-scenarios \
  --json-out artifacts/scenario-results.json \
  --csv-out artifacts/scenario-results.csv
```

Re-extract and reconcile the issuer facts from the frozen SEC filings:

```bash
python3 scripts/extract_filing_facts.py
```

Validate the package:

```bash
python3 scripts/validate_package.py --write-report
```

When an actual independent review occurs, retain its evidence inside the project and record the gate through the guarded command rather than editing readiness status manually:

```bash
python3 scripts/record_reviewer_gate.py HG-01 \
  --outcome PASS \
  --reviewer-identifier "Reviewer identifier" \
  --reviewer-role "Independent model reviewer" \
  --reviewed-on YYYY-MM-DD \
  --attribution-permission ROLE_ONLY \
  --criterion PASS --criterion PASS --criterion PASS \
  --evidence-path path/to/retained-evidence.md \
  --notes "Independent reproduction result and any remaining disagreement"
```

The command rejects incomplete records, future review dates, paths outside the project, missing or empty evidence, and any `PASS` with a failed criterion. Rebuild the package afterward; readiness is derived from the validated ledger and cannot be cleared by generating a form or changing a display field.

The current base case produces $3,870,600 of available proceeds, a $3,096,480 collateral cap, and a $3,000,000 rounded conditional limit. The fully drawn $5.0 million request plus accrued amount has a $1,179,400 recovery shortfall, while the recommended $3.0 million limit plus accrued amount has an $820,600 coverage surplus. A 40-cell collateral quantity and price-stress surface shows the rounded recommendation between the named scenarios. Eight draft-only covenants map each monitoring control to a test, cure period, owner, and breach consequence. Unknown enforceability or an unavailable repayment route produces a decline and zero recommended pro forma exposure.

The recommendation is not authority to fund. The current evidence set leaves all nine pre-funding conditions outstanding, so the engine reports `blocked_pending_conditions` even in the base conditional-approval case.

The `3 / Watchful` obligor rating is an assumed ordinal bridge, not a Coinbase rating or a calibrated probability of default. Its five weighted factors reconcile to 3.10 and state the evidence that would improve or weaken each judgment.


No application, outreach, account creation, dependency installation, wallet action, transaction, deployment, or production change occurred. Major, coursework, spreadsheet skill, available time, New York hybrid feasibility, and complete eligibility remain unknown.
