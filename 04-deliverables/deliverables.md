# Deliverables and acceptance criteria

Status: built and locally verified; ready-to-share human gates remain

| ID | Output | Purpose | Acceptance criteria |
|---|---|---|---|
| CR-01 | `outputs/credit-memo.pdf` | Two-page committee decision | States amount, rating rationale, primary repayment, binding cap, conditions, three risks, unknowns, and reversal trigger. Every material figure cites a source ID. |
| CR-02 | `outputs/opposing-memo.pdf` | Best case against CR-01 | Argues a credible alternative. Names the disputed assumption and evidence that resolves it. Fits one page. |
| CR-03 | `outputs/credit-model.xlsx` | Auditable model | Has Summary, Assumptions, Financials, Liquidity, Rating, Collateral, Portfolio, Scenarios, Sensitivity, Conditions, Control Matrix, Model Risks, Covenants, Monitoring, Escalations, and Sources tabs. No hidden credit logic. The base case, 40-cell decision surface, seven-row collateral-call cure ladder, end-to-end control chains, public-data liquidity bridge, rating, funding gate, governed assumption and model-risk registers, covenant package, monitoring states, and response playbook reconcile to generated artifacts and automated audit. |
| CR-04 | `artifacts/source-register.csv` | Evidence register | Covers every material memo input. Separates publication and retrieval dates. Labels facts and assumptions. |
| CR-05 | `artifacts/scenario-results.csv` | Comparable results | Includes base, borrower stress, price stress, access delay, route failure, enforceability block, and concentration cases on fixed definitions. |
| CR-06 | `artifacts/validation-report.md` | Executed checks | Records expected and actual results, method, status, evidence path, date, and reviewer. Failed and not-run checks remain visible. |
| CR-07 | `outputs/demo.mp4` | Three-minute case walkthrough | Shows the decision, one source, one assumption change, the binding cap change, and the opposing view. Labels the case hypothetical on screen. |
| CR-08 | `outputs/reviewer-brief.pdf` | One-page review request | Contains one decision, one chart, one unresolved assumption, and one precise question. Makes no claim of external validation. |
| CR-09 | `artifacts/feedback-log.md` | Review history | Records reviewer role, question, actual response, change, and remaining disagreement. Self-review and external review are distinct. |
| CR-10 | `artifacts/reproducibility.md` | Rebuild guide | Names source snapshot, case version, workbook version, calculation steps, tolerance, and known limits. Uses no account, wallet, or paid service. |

The consolidated `outputs/committee-packet.pdf` presents the executive cover, two-page credit memorandum, downside-and-cure ladder, model-risk posture, opposing memorandum, and reviewer brief in seven indexed pages. Its generated audit verifies page count, bookmark order, cure metrics, model-risk coverage, committee question, and file hash.

`outputs/reviewer-scorecard.pdf` converts the three outstanding human gates into four printable pages with reviewer-role requirements, questions, pass criteria, retained-evidence requirements, attribution permission, conclusion, and follow-up fields. Generation never marks a gate complete; actual attributed evidence must be added to the feedback log.

## Required before any interface work

CR-01 through CR-06 must exist in draft form. The source register must cover all material inputs. The workbook must reconcile one manual case. Hard blockers must work. If these gates fail, use the remaining time on the model and memo.

## Ready-to-share gate

The package is ready to share only when:

- CR-01 through CR-10 exist;
- material validation checks pass or the affected claim is removed;
- limitations and fictional terms are visible without opening this README;
- a second reader reproduces a key number;
- the author can explain the recommendation and opposing view without reading a script;
- any external feedback is attributed accurately.

Ready to share does not mean production-ready, legally reviewed, or endorsed by Coinbase.
