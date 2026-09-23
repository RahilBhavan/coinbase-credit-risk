# Artifact manifest

Status: locally verified package manifest; human review gates remain governed separately  
Updated: September 20, 2026

| Artifact | Status | Current file | Build dependency |
|---|---|---|---|
| Credit memo | Verified locally | `../outputs/credit-memo.pdf` | Practitioner review remains |
| Committee packet | Verified locally | `../outputs/committee-packet.pdf` | Indexed seven-page consolidated review package with dedicated downside-and-cure and model-risk pages |
| Committee packet audit | Verified locally | `committee-packet-audit.json` | Seven pages, six ordered bookmarks, required cure and model-risk content, and current PDF hash verified |
| Opposing memo | Verified locally | `../outputs/opposing-memo.pdf` | Independent review remains |
| Credit model | Verified locally | `../outputs/credit-model.xlsx` | External spreadsheet-engine review remains |
| Workbook audit | Verified locally | `workbook-audit.csv` | Formula, input, engine-output, collateral-call, control-matrix, model-risk, liquidity, rating, condition-gate, monitoring, and source-value checks tied to workbook hash; current count is generated in `package-metrics.json` |
| Source register | Verified locally | `source-register.csv` | Five public-source snapshots frozen with registered SHA-256 hashes |
| Issuer fact ledger | Verified locally | `issuer-fact-ledger.csv` | Thirteen filing facts extracted and reconciled within explicit tolerances |
| Liquidity analysis | Verified locally | `liquidity-analysis.csv` / `liquidity-analysis.json` | Nine-row public-data bridge with pre-put and post-put residuals and explicit forecast limitations |
| Scenario results | Verified locally | `scenario-results.csv` | Eleven declared cases; stress inputs remain illustrative |
| Threshold analysis | Verified locally | `threshold-analysis.csv` / `threshold-analysis.json` | Break-even price and collateral requirements hold other drivers constant |
| Collateral-call ladder | Verified locally | `collateral-call-ladder.csv` / `collateral-call-ladder.json` | Seven stress points reconcile covenant headroom, top-up, repayment, and rounded commitment cures; not an executed margin agreement |
| Control matrix | Verified locally | `control-matrix.csv` / `control-matrix.json` | Eight chains connect all nine conditions to monitoring, draft covenants, escalation ownership, and exit criteria |
| Decision record | Verified locally | `decision-record.json` | Uses illustrative inputs |
| Condition register | Verified locally | `condition-register.csv` / `condition-register.json` | Nine blocking items with owners, status, and verification method; none cleared by public evidence |
| Rating analysis | Verified locally | `rating-analysis.csv` / `rating-analysis.json` | Five assumed ordinal factors reconcile to 3.10 / Watchful; not a calibrated default model or Coinbase policy |
| Monitoring plan | Verified locally | `monitoring-plan.csv` / `monitoring-plan.json` | Eight owned rules with thresholds, frequency, breach action, escalation, and explicit unmeasured states |
| Model-risk register | Verified locally | `model-risk-register.csv` / `model-risk-register.json` | Eight open limitations with severity, decision effect, linked assumptions and conditions, mitigation, required evidence, owner, residual risk, and unresolved disposition |
| Validation report | Verified locally | `validation-report.md` | Records pass, fail, and skip states |
| Package integrity | Verified locally | `package-integrity.json` | SHA-256 and byte length for the review files inventoried in `package-metrics.json` |
| Package metrics | Verified locally | `package-metrics.md` / `package-metrics.json` | Generated counts and primary-output hashes; source of truth for package scale |
| Readiness report | Verified locally | `readiness-report.md` / `readiness-report.json` | Maps CR-01 through CR-10 separately from outstanding human gates |
| Decision view | Verified locally | `../outputs/decision-view.html` | Runtime-audited sticky review navigation, filterable model-risk triage, deep links, accessible control names, live decision state, call-ladder cures, print layout, copy-summary action, and embedded-data checks |
| Demo | Verified locally | `../outputs/demo.mp4` | Narrated 1080p walkthrough; audio/video streams, duration, slide count, and file hash recorded in `demo-audit.json` |
| External review kit | Ready for execution | `external-review-kit.md` | Reviewer instructions and evidence requirements for HG-01 through HG-03; does not itself clear a gate |
| Reviewer brief | Verified locally | `../outputs/reviewer-brief.pdf` | Authorized outreach remains |
| Reviewer gate scorecard | Verified locally | `../outputs/reviewer-scorecard.pdf` | Four-page governed status summary and execution worksheet for HG-01 through HG-03; pass states derive only from the validated evidence ledger |
| Reviewer evidence ledger | Verified locally | `../data/review/reviewer-evidence.json` | Three ordered gate records; incomplete, future-dated, path-escaping, missing-file, or partially failed PASS claims are rejected |
| Portable review bundle | Verified locally | `../outputs/review-package.zip` | Deterministic ZIP with start guide, generated artifact count, and independently checked embedded hashes |
| Feedback log | Draft | `feedback-log.md` | No external review recorded |
| Reproducibility guide | Verified locally | `reproducibility.md` | External second-reader reproduction remains |

`Verified locally` means the artifact passed the checks recorded in `validation-report.md`. It does not mean externally reviewed, legally validated, or ready for a real credit decision.
