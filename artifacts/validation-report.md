# Validation report

Executed: 2026-09-23
Reviewer: automated local validator (`scripts/validate_package.py`)
Method: deterministic Python standard-library checks; no network access

Summary: 49 PASS, 0 FAIL, 0 SKIP

| ID | Status | Check | Actual result | Evidence |
|---|---|---|---|---|
| S-01 | PASS | Required project directories exist | All required directories exist. | . |
| S-02 | PASS | Core planning documents exist | All core planning documents exist. | . |
| E-01 | PASS | Source register schema and evidence separation | Parsed 12 rows with unique IDs and separated fact/fiction locators. | 02-research/source-register.csv |
| E-02 | PASS | Frozen source snapshots match registered hashes | Verified 5 immutable source snapshot(s). | 02-research/snapshots |
| E-03 | PASS | Design and artifact source registers are identical | Registers match byte-for-byte. | artifacts/source-register.csv |
| E-04 | PASS | Frozen filing facts reconcile to model and memo values | Reconciled 13 extracted filing facts; all model differences are within declared tolerances. | artifacts/issuer-fact-ledger.csv |
| E-05 | PASS | Workbook audit matches the current workbook | Verified 171 passing checks against workbook SHA-256 25b254e85e6d29daf0fbdad5002b7c6bcedf46a1d4868f14bce45f2c40080c00. | artifacts/workbook-audit.csv |
| E-06 | PASS | Package integrity manifest matches review files | Verified SHA-256 and byte length for 78 package file(s). | artifacts/package-integrity.json |
| E-07 | PASS | Threshold analysis is internally consistent | Verified four break-even targets, the $4m concentration ceiling, and a monotonic 40-cell decision surface. | artifacts/threshold-analysis.json |
| D-01 | PASS | Project CSV files parse with unique headers | Parsed 20 CSV file(s). | . |
| D-02 | PASS | Project JSON files parse | Parsed 45 JSON file(s). | . |
| X-01 | PASS | Case inputs agree with registered evidence and project decision | Issuer source is registered, facility is fictional, and requested commitment is $5,000,000. | data/case |
| X-02 | PASS | Executable collateral case agrees with reproducibility guide | Case ID and collateral asset agree. | artifacts/reproducibility.md |
| X-03 | PASS | Decision record satisfies the declared output contract | Decision record includes governance fields and a reconciled calculation trace. | artifacts/decision-record.json |
| X-06 | PASS | Condition register preserves the pre-funding evidence gate | Nine uniquely identified pre-funding conditions remain blocking and outstanding in synchronized CSV and JSON artifacts. | artifacts/condition-register.json |
| X-10 | PASS | Covenant package is complete, synchronized, and bounded | Eight draft-only covenants map one-to-one to monitoring rules with explicit cure and breach consequences. | artifacts/covenant-plan.json |
| X-11 | PASS | Escalation playbook is synchronized, actionable, and bounded | Eight response playbooks map one-to-one across monitoring and covenants with explicit timing, authority, evidence, and exit criteria. | artifacts/escalation-playbook.json |
| X-12 | PASS | Interactive what-if contract is bounded and reconciled | Four engine-derived boundary vectors, seven collateral-call rows, eight control chains, eight filterable model risks, and three governed human gates (3 outstanding) reconcile in the shipped JavaScript; all 79 interactive IDs are unique. | artifacts/what-if-contract.json |
| X-13 | PASS | Scenario attribution is complete, quantified, and bounded | All eleven scenarios carry quantified base deltas, unique severity ranks, binding drivers, and resolution evidence without adding a new decision rule. | artifacts/scenario-attribution.json |
| X-14 | PASS | Decision lineage is complete, resolvable, and evidence-bounded | Eleven committee claims resolve through 32 evidence links to current values, rules, artifacts, workbook cells, owners, and limitations. | artifacts/decision-lineage.json |
| X-15 | PASS | Diligence plan is complete, acyclic, and decision-linked | Nine blocking conditions form four parallel lanes, eight wave-one tasks, and one explicit ownership-and-lien dependency before control execution. | artifacts/diligence-plan.json |
| X-16 | PASS | Assumption register is complete, governed, and explicitly unvalidated | All seven case assumptions retain assumed or simulated evidence status with materiality, ownership, workbook inputs, validation methods, challenge triggers, and 27 downstream links. | artifacts/assumption-register.json |
| X-22 | PASS | Model-risk register is synchronized, governed, and decision-linked | 8 synchronized open risks; 3 critical; all links resolve and every risk has mitigation, evidence, owner, and unresolved disposition. | artifacts/model-risk-register.json |
| X-23 | PASS | Reviewer-evidence ledger rejects incomplete or unretained human-gate claims | Three ordered reviewer records validated; 0 evidence-backed gate(s) pass and readiness matches. | data/review/reviewer-evidence.json |
| X-17 | PASS | Collateral-call ladder is reconciled, monotonic, and bounded | 7 ordered rows; base passes; first grid call is 5%; cure amounts and commitment step-downs are monotonic. | artifacts/collateral-call-ladder.json |
| X-18 | PASS | Committee packet is indexed, current, and contains cure and model-risk analysis | Seven pages and six ordered bookmarks verified; cure analysis and all eight governed model risks are present. | artifacts/committee-packet-audit.json |
| X-19 | PASS | Control matrix joins every condition to monitoring, covenant, and escalation coverage | Eight complete control chains cover all nine conditions and preserve blocked, draft-only governance boundaries. | artifacts/control-matrix.json |
| X-20 | PASS | Reviewer scorecard operationalizes human gates without fabricating completion | Three executable human-gate worksheets reflect governed evidence (0 passed, 3 outstanding); four-page PDF hash and text contract verified. | artifacts/reviewer-scorecard.json |
| X-07 | PASS | Illustrative rating bridge is transparent and reconciled | Five weighted factors reconcile to 3.10 / Watchful with explicit evidence and method limits. | artifacts/rating-analysis.json |
| X-08 | PASS | Monitoring design is actionable without implying observed compliance | Eight owned monitoring rules separate projected passes, the pre-funding blocker, and five unmeasured private-evidence metrics. | artifacts/monitoring-plan.json |
| X-09 | PASS | Public-data liquidity bridge is reconciled and bounded | Nine-row public-data bridge reconciles to $96.81m before and negative $194.79m after the potential holder put, with forecast limitations explicit. | artifacts/liquidity-analysis.json |
| X-04 | PASS | Reviewer brief satisfies CR-08 content contract | Decision, four-cap chart, unresolved assumption, precise question, and review-status disclaimer are declared and rendered. | outputs/reviewer-brief.pdf |
| X-24 | PASS | Narrated demo audit matches the distributed MP4 | Six-slide narrated demo is 147.646s with audio and video streams; SHA-256 matches. | artifacts/demo-audit.json |
| X-05 | PASS | Readiness report separates local verification from human gates | CR-01 through CR-10 are locally verified; governed evidence records 0 of 3 human gates passed. | artifacts/readiness-report.json |
| X-21 | PASS | Generated package metrics match current artifacts | Generated metrics reconcile to current workbook audit, scenarios, decision-view audit, and primary-output hashes. | artifacts/package-metrics.json |
| O-01 | PASS | Artifact available: credit-memo.pdf | Valid non-empty PDF container (8,025 bytes). | outputs/credit-memo.pdf |
| O-02 | PASS | Artifact available: committee-packet.pdf | Valid non-empty PDF container (26,084 bytes). | outputs/committee-packet.pdf |
| O-03 | PASS | Artifact available: opposing-memo.pdf | Valid non-empty PDF container (3,689 bytes). | outputs/opposing-memo.pdf |
| O-04 | PASS | Artifact available: credit-model.xlsx | Valid non-empty XLSX ZIP package with 27 members. | outputs/credit-model.xlsx |
| O-05 | PASS | Artifact available: source-register.csv | Present and non-empty. | artifacts/source-register.csv |
| O-06 | PASS | Artifact available: scenario-results.csv | Present and non-empty. | artifacts/scenario-results.csv |
| O-07 | PASS | Artifact available: demo.mp4 | Valid non-empty ISO media container (3,517,709 bytes). | outputs/demo.mp4 |
| O-08 | PASS | Artifact available: reviewer-brief.pdf | Valid non-empty PDF container (3,923 bytes). | outputs/reviewer-brief.pdf |
| O-09 | PASS | Artifact available: reviewer-scorecard.pdf | Valid non-empty PDF container (9,534 bytes). | outputs/reviewer-scorecard.pdf |
| O-10 | PASS | Artifact available: feedback-log.md | Present and non-empty. | artifacts/feedback-log.md |
| O-11 | PASS | Artifact available: reproducibility.md | Present and non-empty. | artifacts/reproducibility.md |
| O-12 | PASS | Artifact available: decision-view.html | Self-contained HTML present (248,597 characters). | outputs/decision-view.html |
| L-01 | PASS | Built narrative artifacts label the case hypothetical | Found an explicit label in 5 text artifact(s). | artifacts |
| C-01 | PASS | Scenario schema and arithmetic consistency | Validated 11 scenario row(s). | artifacts/scenario-results.csv |

## Interpretation

PASS means the check executed and its tested condition held. FAIL means the check executed and found a concrete problem. SKIP means the required output or evidence was unavailable; it is not a pass.

This validator checks frozen-source hashes, filing-fact reconciliation, PDF container markers, and XLSX archive structure. It does not independently recalculate workbook formulas in Excel, prove legal enforceability, or substitute for an independent human calculation. Those checks remain manual until suitable artifacts and reviewers exist.
