# Architecture for an auditable local case

Status: implemented reference; independent review remains

## Design rule

The source snapshot and workbook are the system of record. A local interface may read derived outputs, but it must not contain separate credit logic.

```text
SEC filings        Coinbase market data       Fictional case CSVs
     |                       |                         |
     +----------- raw, dated, immutable snapshots ---+
                             |
                     normalized evidence
                             |
          +------------------+------------------+
          |                  |                  |
 obligor + liquidity  collateral waterfall   portfolio caps
          |                  |                  |
          +---------------- decision record ----+
                             |
              memo, opposing memo, scenarios
                             |
                  optional local decision view
```

## Components

### Snapshot layer

Store source files exactly as retrieved. Add a manifest with URL, request parameters, timestamps, and hashes. Never replace an old snapshot in place.

### Normalization layer

Create narrow tables for financial facts, debt maturities, market observations, and fictional case inputs. Preserve the source ID and evidence class on every row. Convert units in explicit columns rather than overwriting reported values.

### Decision layer

Use transparent formulas for:

- liquidity and cash-use measures;
- obligor rating factors and the illustrative obligor cap;
- collateral eligibility and stressed proceeds;
- facility exposure and shortfall;
- single-name, sector, asset, custodian, chain, and banking-route concentrations;
- hard blockers, conditions, and reversal triggers.

The Python engine and deterministic artifact builders own the implemented calculation contract. The workbook independently reproduces the decision, liquidity bridge, rating, scenarios, conditions, and monitoring states, and the audit reconciles those outputs to the source artifacts.

### Presentation layer

Generate fixed tables and charts for the memo. If time remains, add one local page with the recommendation, binding constraint, assumption switch, source link, and opposing view. The interface cannot edit source facts without creating a new case version.

## Control boundaries

- No network call runs during committee review. Review uses a frozen snapshot.
- No AI system calculates limits or changes source values.
- AI may draft prose only from approved tables. A human checks every figure and citation.
- Missing ownership or enforceability evidence produces a blocker, not a guessed haircut.
- The Base adapter, if later built, is read-only and cannot sign or submit a transaction.
- x402, wallet creation, lending execution, deployment, and customer data are outside scope.

## Likely implementation choices

Use Excel or Google Sheets for the required model because the role asks for spreadsheet analysis. A small Python standard-library script can later fetch public JSON, hash snapshots, and export normalized CSV files. Do not add a web framework until the memo and workbook pass validation.
