# Executed validation checks

Status: executable local validation and artifact audits implemented; independent human and legal review remain

Run from the project root:

```sh
python3 scripts/validate_package.py --write-report
```

The command uses only the Python standard library and exits with status 1 when any executed check fails. It writes the full result table to `artifacts/validation-report.md`.

The validator currently checks:

- required project directories and core planning documents;
- source-register schema, unique IDs, evidence classes, public-versus-fictional separation, frozen snapshots, and SHA-256 integrity;
- reconciliation of 13 filing facts against model and memo presentation values with declared rounding tolerances;
- the generated workbook-audit suite covering formulas, case inputs, filing inputs, cached results, engine agreement, sensitivity-grid reconciliation, assumption governance, covenant-to-monitoring linkage, escalation-playbook linkage, model-risk governance, and workbook-hash freshness;
- parseability and unique headers for project CSV files;
- parseability of JSON files when any exist;
- availability and container structure of each planned artifact;
- explicit hypothetical, fictional, or illustrative labeling in built Markdown narratives;
- eleven-scenario schema, nonnegative amounts, recommendation bounds, and shortfall arithmetic within $1.
- live what-if reconciliation across four engine-derived boundary vectors and uniqueness of every required interactive control/output ID;
- complete scenario attribution across eleven engine outputs, including base deltas, severity ranks, binding drivers, and resolution evidence.
- decision lineage across eleven committee claims, 32 registered evidence links, resolvable artifacts, workbook locators, owners, and limitations.
- diligence sequencing across nine blocking conditions, four parallel lanes, two execution waves, acyclic dependencies, affected claims, and completion outputs.
- governance of all seven case assumptions, including materiality, owners, workbook inputs, validation methods, challenge triggers, and 27 downstream lineage links.

An unavailable output is `SKIP`, never `PASS`. Excel-native recalculation, legal enforceability, and independent human reproduction remain outside the automated evidence boundary and must stay visible as manual work.

The generated report records the execution date, method, status, actual result, and evidence location for every automated check.

Current counts are generated in `artifacts/package-metrics.json` and `artifacts/package-metrics.md`; this document intentionally does not duplicate values that change as checks and interface controls are added.
# Exposure-basis reconciliation

The executable decision record now carries an explicit requested fully drawn recovery basis, recommended pro forma exposure, and recommended-limit coverage surplus. Unit tests verify the base reconciliation and verify that a decline produces zero recommended pro forma exposure. Package validation independently recomputes pro forma exposure from the recommendation plus the facility's accrued amount and recomputes the related surplus from available proceeds.

## Decision-surface reconciliation

The threshold artifact includes 40 combinations of collateral quantity and price stress. Automated tests require recommendations to be non-increasing as stress rises and non-decreasing as eligible quantity rises. Five nonadjacent workbook cells reconcile to the machine-readable surface, including the base location and a severe-stress boundary. The workbook now reads the declared $100k recommendation increment from Assumptions; it no longer embeds a different increment in formulas.

## Covenant-control reconciliation

Eight draft-only covenants map one-to-one to the eight monitoring rules. Each record specifies the test frequency, cure period, breach consequence, owner, current evidence state, and linked monitoring ID. The workbook links covenant evidence and status directly to Monitoring, while package validation checks synchronization, unique IDs, status counts, and the explicit non-enforceability boundary.

## Escalation-response reconciliation

Eight response playbooks map one-to-one to both monitoring rules and covenants. Each path declares trigger severity, response timing, draw state, decision ownership, required evidence, and exit criteria. The workbook links current evidence and status directly to Monitoring, while package validation checks both mappings, current-state counts, and the explicit no-open-incident boundary.
