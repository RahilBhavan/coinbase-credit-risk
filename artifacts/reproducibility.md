# Reproducibility guide

**Status:** Locally verified method record for MARA-CR-001  
**Current implementation:** Deterministic Python engine, Excel workbook, scenario outputs, written artifacts, captioned demo video, and local validation  
**Not available:** Private diligence, narrated demo mux, second-reader reproduction, or external review

## Exact inputs used

Public issuer facts are listed as SRC-001 and SRC-002 in [source-register.csv](source-register.csv). The Base timing statement is SRC-005. All deal and policy inputs are ASM-C001 through ASM-C007. Do not replace an assumption with a fact in place; create a new case version.

The current hand-worked collateral case uses:

- quantity: 4,000,000 fictional USDC;
- quoted price: $1.00 per USDC;
- price/convertibility stress: 2%;
- execution cost: 50 basis points of stressed gross value;
- delay cost: $9,800;
- fixed cost: $20,000;
- required coverage: 1.25x;
- approved amount: rounded down to $3,000,000.

## Rebuild the illustrative result

1. Calculate quoted value: `4,000,000 × $1.00 = $4,000,000`.
2. Apply the 2% stress: `$4,000,000 × 0.98 = $3,920,000`.
3. Calculate execution cost: `$3,920,000 × 0.005 = $19,600`.
4. Calculate available proceeds: `$3,920,000 − $19,600 − $9,800 − $20,000 = $3,870,600`.
5. Calculate the collateral cap: `$3,870,600 ÷ 1.25 = $3,096,480`.
6. Take the minimum of the $7.5 million obligor cap, $3.09648 million collateral cap, $6.0 million single-name cap, and $4.0 million concentration cap.
7. Round down to the stated $3.0 million commitment.
8. Apply hard blockers. If ownership, priority, legal control, or the repayment route is unknown, no collateral credit is permitted and funding is declined.

The Python engine reproduces the arithmetic exactly using decimal calculations. The workbook reproduces the available proceeds and collateral cap within the declared $1 tolerance.

## Rebuild the implemented outputs

The canonical full build is:

```bash
python3 scripts/build_package.py
```

This executes evidence extraction, public-data liquidity analysis, condition-register and rating-bridge generation, the base decision, monitoring-plan generation, all scenarios, PDF and workbook generation, the interactive view, workbook audit, regression tests, readiness reporting, integrity-manifest creation, package validation, and portable review-bundle creation in dependency order. Use `--with-demo` on macOS when the captioned video also needs regeneration.

The final step creates `../outputs/review-package.zip`. It contains `START-HERE.md`, the principal reviewer outputs, supporting audit artifacts, and `BUNDLE-MANIFEST.json`. The builder reopens the ZIP, checks its central directory, and recomputes every embedded SHA-256 digest before reporting success.

The same build creates `threshold-analysis.json` and `threshold-analysis.csv`. These solve for break-even price declines and minimum collateral quantities at $2 million, $3 million, $4 million, and $5 million target limits while holding every other driver constant.

It also creates `rating-analysis.json` and `rating-analysis.csv`. The five declared factor weights sum to 1.00, their weighted contributions sum to 3.10, and the score maps to `3 / Watchful`. This is an assumed ordinal bridge only; it is not statistically calibrated and does not represent Coinbase policy.

`monitoring-plan.json` and `monitoring-plan.csv` define eight post-close rules. Calculated projections, the pre-funding blocked state, and unavailable private observations remain separate. The plan is not evidence that monitoring occurred or that a borrower complied.

`liquidity-analysis.json` and `liquidity-analysis.csv` reproduce a nine-row public-data bridge from the reconciled fact ledger. The $96.81 million pre-put residual and negative $194.79 million post-put sensitivity are static screens, not forecasts; the method limitation lists the excluded cash flows and entity-level evidence.

Extract and reconcile the cited SEC facts from the frozen filings:

```bash
python3 scripts/extract_filing_facts.py
```

This produces `issuer-fact-ledger.csv` with the XBRL or narrative locator, exact filing value, presented model or memo value, difference, declared rounding tolerance, and pass/fail result. The extractor prefers the highest-precision tagged value when a filing repeats a fact at multiple display precisions.

Run the behavioral tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Rebuild the scenario files:

```bash
PYTHONPATH=src python3 -m credit_risk --case-dir data/case --all-scenarios \
  --json-out artifacts/scenario-results.json \
  --csv-out artifacts/scenario-results.csv
```

Run the package validator:

```bash
python3 scripts/validate_package.py --write-report
```

The workbook is `../outputs/credit-model.xlsx`. Its reproducible builder is `../work/build_workbook.mjs`; it uses the bundled workspace artifact runtime rather than repository dependencies.

Audit its OOXML formulas, cached values, engine agreement, case inputs, and filing-fact inputs:

```bash
python3 scripts/audit_workbook.py
```

The resulting `workbook-audit.csv` records one row per check and the SHA-256 of the exact workbook inspected. The generated `package-metrics.json` and `package-metrics.md` record the current workbook sheet, formula, audit-check, and regression-test counts so this guide does not drift as the package expands. Package validation rejects a stale audit whose hash does not match the current XLSX. This is an independent Python comparison of the workbook package against the decision engine; it is not an Excel-native recalculation.

The three PDFs in `../outputs/` are built by `../work/build_pdfs.py`. The build uses ReportLab. The verification pass extracts text from every page, renders each page with Poppler, and visually checks the PNG output.

The captioned walkthrough is `../outputs/demo.mp4`. Rebuild its slides, local narration assets, and video container with the bundled Python runtime:

```bash
<local-path> work/build_demo.py
```

The builder compiles a small local AVFoundation writer, creates a Motion JPEG intermediate, and transcodes it to MP4 with macOS `avconvert`. The distributed MP4 is silent and fully captioned. AIFF narration assets are retained under `../work/demo/`; the host Swift compiler/SDK mismatch prevented the planned narration mux.

## Evidence controls for the next version

Five cited public sources are frozen under `../02-research/snapshots/2026-09-20/`. Their project-relative paths and SHA-256 hashes are registered in both copies of `source-register.csv`; the validator recomputes every declared hash and requires the two registers to match byte-for-byte. Keep issuer facts in separate rows from fictional terms and create a new dated snapshot rather than overwriting an existing source.

If market data is added, fetch BTC-USD candles in explicit non-overlapping windows of at most 300 records, record missing buckets, and retain the raw responses. A level-2 book is one point-in-time observation and must not be represented as historical executable depth. Neither market dataset is needed to reproduce the current USDC illustration.

## Known limits

- No private borrower information, actual facility documentation, lien search, legal opinion, wallet evidence, or portfolio data was reviewed.
- The public sources are frozen and hash-verified, but the reported issuer facts have not yet received an independent second-reader extraction.
- The facility and all limit-setting inputs are invented for demonstration.
- The model and workbook use illustrative policy and deal inputs. They are not calibrated credit policy.
- No second-reader reproduction or external review has been completed.
- The demo is captioned but silent; narration assets exist but are not muxed into the MP4.
- No Base transaction, RPC call, wallet action, account, paid service, or deployment is required or permitted for this draft.

## Version rule

Any change to a material fact, assumption, formula, or decision creates a new case version and a dated entry in [feedback-log.md](feedback-log.md). Preserve the prior version or record a content hash once versioned artifacts exist.
