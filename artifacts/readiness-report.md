# Package readiness report

Evaluated: 2026-09-23
Local acceptance verified: **YES**
Ready to share: **NO**

## Acceptance criteria

| ID | Status | Requirement | Evidence-backed result |
|---|---|---|---|
| CR-01 | VERIFIED_LOCAL | Two-page committee decision | Decision memo exists and its source narrative declares repayment, binding-cap, reversal, and source-linkage content. Evidence: `outputs/credit-memo.pdf`, `artifacts/credit-memo.md`, `artifacts/decision-record.json`, `artifacts/condition-register.json`. |
| CR-02 | VERIFIED_LOCAL | Best case against the recommendation | Opposing memo exists and names the alternative, disputed assumption, and resolving evidence. Evidence: `outputs/opposing-memo.pdf`, `artifacts/opposing-memo.md`. |
| CR-03 | VERIFIED_LOCAL | Auditable credit model | Workbook exists; 171/171 audit rows pass, including funding-gate and condition-register reconciliation. Evidence: `outputs/credit-model.xlsx`, `artifacts/workbook-audit.csv`. |
| CR-04 | VERIFIED_LOCAL | Evidence register | Source register contains 12 classified evidence rows. Evidence: `artifacts/source-register.csv`, `02-research/snapshots`. |
| CR-05 | VERIFIED_LOCAL | Comparable scenario results | Scenario suite contains 11 cases, including all required decision signals. Evidence: `artifacts/scenario-results.csv`, `data/case/scenarios.json`. |
| CR-06 | VERIFIED_LOCAL | Executed validation report | Validation report records method, reviewer, actual results, evidence, and explicit failure/skip semantics. Evidence: `artifacts/validation-report.md`, `scripts/validate_package.py`. |
| CR-07 | VERIFIED_LOCAL | Three-minute-or-less walkthrough | Narrated demo exists, its audit confirms audio and video streams within three minutes, and its deterministic source covers the required narrative beats and disclaimer. Evidence: `outputs/demo.mp4`, `artifacts/demo-audit.json`, `04-deliverables/demo-storyboard.md`, `work/build_demo.py`. |
| CR-08 | VERIFIED_LOCAL | One-page review request | Reviewer brief declares a decision, chart, unresolved assumption, precise question, and self-review status. Evidence: `outputs/reviewer-brief.pdf`, `artifacts/reviewer-brief.md`, `work/build_pdfs.py`. |
| CR-09 | VERIFIED_LOCAL | Review history | Feedback log separates self-review from external review and preserves responses, changes, and disagreements. Evidence: `artifacts/feedback-log.md`. |
| CR-10 | VERIFIED_LOCAL | Rebuild guide | Reproducibility guide identifies the case, snapshots, rebuild command, tolerances, and limitations. Evidence: `artifacts/reproducibility.md`, `scripts/build_package.py`. |

## Ready-to-share human gates

| ID | Status | Gate | Evidence |
|---|---|---|---|
| HG-01 | OUTSTANDING | Second reader reproduces a key number | Execution worksheet is available in outputs/reviewer-scorecard.pdf; governed ledger outcome is OUTSTANDING. Required evidence: Dated calculation steps, reviewer role, result, variance, conclusion, and permission to attribute the review role. |
| HG-02 | OUTSTANDING | Presenter explains both views without a script | Execution worksheet is available in outputs/reviewer-scorecard.pdf; governed ledger outcome is OUTSTANDING. Required evidence: Dated observer notes, reviewer role, question-level result, conclusion, and any corrective action. |
| HG-03 | OUTSTANDING | External feedback is attributed accurately | Execution worksheet is available in outputs/reviewer-scorecard.pdf; governed ledger outcome is OUTSTANDING. Required evidence: Dated attributed response or contemporaneous notes, permission status, resulting change, and unresolved disagreement. |

## Interpretation

Local verification is not external review, legal validation, production approval, or evidence of creditworthiness.
