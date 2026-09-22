import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const outputPath = path.join(root, "outputs", "credit-model.xlsx");
const previewDir = path.join(root, "work", "workbook-previews");
const covenantPlan = JSON.parse(await fs.readFile(path.join(root, "artifacts", "covenant-plan.json"), "utf8"));
const escalationPlaybook = JSON.parse(await fs.readFile(path.join(root, "artifacts", "escalation-playbook.json"), "utf8"));
const assumptionRegister = JSON.parse(await fs.readFile(path.join(root, "artifacts", "assumption-register.json"), "utf8"));
const collateralCallLadder = JSON.parse(await fs.readFile(path.join(root, "artifacts", "collateral-call-ladder.json"), "utf8"));
const controlMatrix = JSON.parse(await fs.readFile(path.join(root, "artifacts", "control-matrix.json"), "utf8"));
const modelRiskRegister = JSON.parse(await fs.readFile(path.join(root, "artifacts", "model-risk-register.json"), "utf8"));
await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const wb = Workbook.create();
const sheetNames = ["Summary", "Assumptions", "Financials", "Liquidity", "Rating", "Collateral", "Portfolio", "Scenarios", "Sensitivity", "Conditions", "Control Matrix", "Model Risks", "Covenants", "Monitoring", "Escalations", "Sources"];
for (const name of sheetNames) wb.worksheets.add(name);

const navy = "#16324F";
const blue = "#2F75B5";
const paleBlue = "#DCE6F1";
const paleGreen = "#E2F0D9";
const paleAmber = "#FFF2CC";
const paleRed = "#FCE4D6";
const gray = "#E7E6E6";
const dark = "#1F1F1F";
const green = "#008000";
const inputBlue = "#0000FF";
const money = '$#,##0;[Red]($#,##0);-';
const money1 = '$0.0,,"M";[Red]($0.0,,"M");-';
const pct = '0.0%;[Red](0.0%);-';
const qty = '#,##0.00;[Red](#,##0.00);-';

function baseSheet(sheet, tabColor) {
  sheet.showGridLines = false;
  sheet.tabColor = tabColor;
  const used = sheet.getRange("A1:N80");
  used.format.font = { name: "Arial", size: 10, color: dark };
  used.format.verticalAlignment = "center";
}

function title(sheet, text, subtitle) {
  sheet.getRange("C2").values = [[text]];
  sheet.getRange("C2").format.font = { name: "Arial", size: 16, bold: true, color: navy };
  sheet.getRange("C3:J3").format.borders = { bottom: { style: "thin", color: navy } };
  if (subtitle) {
    sheet.getRange("C4").values = [[subtitle]];
    sheet.getRange("C4").format.font = { name: "Arial", size: 10, italic: true, color: "#666666" };
  }
}

function section(sheet, range, text) {
  const r = sheet.getRange(range);
  r.values = [[text, ...Array(r.columnCount - 1).fill("")]];
  r.format.fill = navy;
  r.format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
  r.format.borders = { preset: "outside", style: "thin", color: navy };
}

function header(sheet, range) {
  const r = sheet.getRange(range);
  r.format.fill = navy;
  r.format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
  r.format.horizontalAlignment = "center";
  r.format.borders = { preset: "inside", style: "thin", color: "#FFFFFF" };
}

function formatInputs(sheet, range) {
  const r = sheet.getRange(range);
  r.format.fill = paleAmber;
  r.format.font = { name: "Arial", size: 10, color: inputBlue };
}

function formatCrossLinks(sheet, range) {
  sheet.getRange(range).format.font = { name: "Arial", size: 10, color: green };
}

// Assumptions: all values are fictional case or policy inputs.
{
  const s = wb.worksheets.getItem("Assumptions"); baseSheet(s, "#5B9BD5");
  title(s, "Fictional case assumptions", "Editable inputs only — not MARA or Coinbase terms or policy");
  section(s, "C6:H6", "Facility terms");
  s.getRange("C7:F14").values = [
    ["Input", "Value", "Unit", "Evidence class"],
    ["Requested commitment", 5000000, "USD", "Assumed"],
    ["Funded exposure", 5000000, "USD", "Assumed"],
    ["Accrued amount", 50000, "USD", "Assumed"],
    ["Tenor", 12, "months", "Assumed"],
    ["Required collateral coverage", 1.25, "x", "Assumed"],
    ["Obligor cap", 7500000, "USD", "Illustrative policy"],
    ["Recommendation increment", 100000, "USD", "Illustrative policy"],
  ];
  header(s, "C7:F7"); formatInputs(s, "D8:D14");
  s.getRange("D8:D10").format.numberFormat = money;
  s.getRange("D12").format.numberFormat = "0";
  s.getRange("D13:D14").format.numberFormat = money;
  section(s, "C16:H16", "Collateral and liquidation assumptions");
  s.getRange("C17:F28").values = [
    ["Input", "Value", "Unit", "Evidence class"],
    ["Fictional USDC quantity", 4000000, "USDC", "Simulated"],
    ["Reference USDC price", 1, "USD/USDC", "Assumed"],
    ["Price stress", 0.02, "% decline", "Assumed"],
    ["Execution cost", 0.005, "% of gross", "Assumed"],
    ["Earliest usable", 2, "hours", "Assumed"],
    ["Delay cost per hour", 0.00125, "% per hour", "Assumed"],
    ["Fixed cost", 20000, "USD", "Assumed"],
    ["Ownership evidence", "Yes", "status", "Simulated condition precedent"],
    ["Legal control", "Yes", "status", "Simulated condition precedent"],
    ["Prior lien search", "Yes", "status", "Simulated condition precedent"],
    ["Approved Base-to-cash route", "Yes", "status", "Simulated condition precedent"],
  ];
  header(s, "C17:F17"); formatInputs(s, "D18:D28");
  s.getRange("D18").format.numberFormat = qty;
  s.getRange("D19").format.numberFormat = money;
  s.getRange("D20:D21").format.numberFormat = pct;
  s.getRange("D23").format.numberFormat = pct;
  s.getRange("D24").format.numberFormat = money;
  s.getRange("D25:D28").dataValidation = { rule: { type: "list", values: ["Yes", "No", "Unknown"] } };
  section(s, "C30:H30", "Illustrative portfolio policy");
  s.getRange("C31:F35").values = [
    ["Input", "Value", "Unit", "Evidence class"],
    ["Single-name limit", 6000000, "USD", "Illustrative policy"],
    ["Digital-mining sector limit", 8500000, "USD", "Illustrative policy"],
    ["USDC collateral concentration limit", 15000000, "USD", "Illustrative policy"],
    ["Shared custody-route limit", 10000000, "USD", "Illustrative policy"],
  ];
  header(s, "C31:F31"); formatInputs(s, "D32:D35"); s.getRange("D32:D35").format.numberFormat = money;
  s.getRange("C38:H40").values = [["Use", "Yellow cells are editable fictional assumptions. Blue font marks inputs."],["Boundary", "Public MARA facts appear only on Financials and are never treated as pledged collateral."],["Decision rule", "Approval requires the lowest of four caps and no hard blocker."]];
  s.getRange("C38:C40").format.font = { bold: true, color: navy };
  s.getRange("D38:H40").format.wrapText = true;
  section(s, "C43:L43", "Assumption governance");
  const governanceRows = [["ID", "Materiality", "Status", "Assumption", "Class", "Owner", "Workbook inputs", "Validation method", "Challenge trigger", "Affected lineage"]];
  for (const row of assumptionRegister.assumptions) governanceRows.push([row.assumption_id, row.materiality, row.validation_status, row.assumption, row.evidence_class, row.owner_role, row.workbook_inputs, row.validation_method, row.challenge_trigger, row.downstream_lineage_nodes.join(", ")]);
  s.getRange("C44:L51").values = governanceRows;
  header(s, "C44:L44");
  s.getRange("C44:L51").format.wrapText = true;
  s.getRange("D45:D51").conditionalFormats.add("containsText", { text: "CRITICAL", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("E45:E51").conditionalFormats.add("containsText", { text: "UNVALIDATED", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  s.getRange("C53:D53").values = [["Method limit", assumptionRegister.method_limit]];
  s.getRange("C53").format.font = { bold: true, color: navy };
  s.getRange("D53:L53").format.wrapText = false;
  s.freezePanes.freezeRows(7);
}

// Financials: selected public facts from filed reports.
{
  const s = wb.worksheets.getItem("Financials"); baseSheet(s, "#F4B183");
  title(s, "MARA public financial facts", "Reported figures only; facility and collateral terms are excluded");
  s.getRange("C6:I13").values = [
    ["Fact ID", "Metric", "Value", "Unit", "Period end", "Source ID", "Availability note"],
    ["FIN-001", "Cash and cash equivalents", 421300000, "USD", new Date("2026-06-30"), "SRC-001", "Excludes restricted cash"],
    ["FIN-002", "Cash designated for Exaion operations", 0.30, "% of cash", new Date("2026-06-30"), "SRC-001", "Approximate share; not assumed available"],
    ["FIN-003", "Bitcoin holdings", 35577, "BTC", new Date("2026-06-30"), "SRC-001", "Reported holdings; not facility collateral"],
    ["FIN-004", "Bitcoin fair value", 2100000000, "USD", new Date("2026-06-30"), "SRC-001", "At reported $58,524/BTC reference"],
    ["FIN-005", "Bitcoin loaned to third parties", 4742, "BTC", new Date("2026-06-30"), "SRC-001", "Not treated as unrestricted"],
    ["FIN-006", "Bitcoin pledged as collateral", 4528, "BTC", new Date("2026-06-30"), "SRC-001", "Not available to this fictional facility"],
    ["FIN-007", "Bitcoin reported unrestricted", 26307, "BTC", new Date("2026-06-30"), "SRC-001", "Does not prove ownership/control for this facility"],
  ];
  header(s, "C6:I6");
  s.getRange("E7:E13").format.numberFormat = money;
  s.getRange("E8").format.numberFormat = pct;
  s.getRange("E9:E13").format.numberFormat = '#,##0';
  s.getRange("G7:G13").format.numberFormat = "yyyy-mm-dd";
  s.getRange("C16:I22").values = [
    ["Fact ID", "Metric", "Value", "Unit", "Period end", "Source ID", "Availability note"],
    ["FIN-008", "Debt after note repurchases", 2400000000, "USD", new Date("2026-06-30"), "SRC-001", "Approximate"],
    ["FIN-009", "Line of credit due within 12 months", 150000000, "USD", new Date("2026-06-30"), "SRC-001", "Current obligation"],
    ["FIN-010", "December 2026 notes", 48100000, "USD", new Date("2026-06-30"), "SRC-001", "Current maturity"],
    ["FIN-011", "2025 operating cash used", -802700000, "USD", new Date("2025-12-31"), "SRC-002", "Annual audited baseline"],
    ["FIN-012", "June 2031 notes classified current", 291600000, "USD", new Date("2026-06-30"), "SRC-001", "Holders can require repurchase in June 2027"],
    ["FIN-013", "2025 year-end debt", 3600000000, "USD", new Date("2025-12-31"), "SRC-002", "Approximate annual baseline"],
  ];
  header(s, "C16:I16"); s.getRange("E17:E22").format.numberFormat = money; s.getRange("G17:G22").format.numberFormat = "yyyy-mm-dd";
  s.getRange("C25:G29").values = [
    ["Calculated view", "Formula", "Result", "Unit", "Interpretation"],
    ["Cash after Exaion designation", "Cash × (1 − designation)", "", "USD", "Illustrative availability screen, not unrestricted cash conclusion"],
    ["Near-term debt identified", "LOC + Dec-26 notes", "", "USD", "Excludes other current debt and operating needs"],
    ["Requested facility / cash", "Request ÷ reported cash", "", "%", "Small size does not cure legal-control gaps"],
    ["Requested facility / debt", "Request ÷ reported debt", "", "%", "Scale context only"],
  ];
  header(s, "C25:G25");
  s.getRange("E26:E29").formulas = [["=E7*(1-E8)"],["=SUM(E18:E19)"],["='Assumptions'!D8/E7"],["='Assumptions'!D8/E17"]];
  s.getRange("E26:E27").format.numberFormat = money; s.getRange("E28:E29").format.numberFormat = pct; formatCrossLinks(s, "E28:E29");
  s.getRange("C31:I33").values = [["Boundary", "These values are selected filing facts, not a complete underwriting file."],["Collateral boundary", "MARA's reported bitcoin is not pledged to this hypothetical facility."],["Source boundary", "See Sources for URLs, dates, and limitations."]];
  s.getRange("C31:C33").format.font = { bold: true, color: navy }; s.getRange("D31:I33").format.wrapText = true;
  s.freezePanes.freezeRows(6);
}

// Liquidity: static public-data screen, not a borrowing-entity forecast.
{
  const s = wb.worksheets.getItem("Liquidity"); baseSheet(s, "#C55A11");
  title(s, "Public-data liquidity bridge", "Static filing screen; not a borrowing-entity cash forecast");
  s.getRange("C6:G15").values = [
    ["Line ID", "Line item", "Amount", "Source ID", "Evidence class"],
    ["LIQ-01", "Reported cash and cash equivalents", "", "SRC-001", "Reported"],
    ["LIQ-02", "Less: cash designated for Exaion operations", "", "SRC-001", "Calculated from reported approximate share"],
    ["LIQ-03", "Cash after designation screen", "", "SRC-001", "Calculated"],
    ["LIQ-04", "Less: line of credit due within 12 months", "", "SRC-001", "Reported"],
    ["LIQ-05", "Less: December 2026 notes", "", "SRC-001", "Reported"],
    ["LIQ-06", "Residual before potential holder put", "", "SRC-001", "Calculated"],
    ["LIQ-07", "Less: June 2031 notes classified current for June 2027 put", "", "SRC-001", "Reported potential obligation"],
    ["LIQ-08", "Residual after potential holder put", "", "SRC-001", "Calculated sensitivity"],
    ["LIQ-09", "2025 operating cash used", "", "SRC-002", "Reported historical reference"],
  ];
  header(s, "C6:G6");
  s.getRange("E7:E15").formulas = [["='Financials'!E7"],["=-'Financials'!E7*'Financials'!E8"],["=SUM(E7:E8)"],["=-'Financials'!E18"],["=-'Financials'!E19"],["=SUM(E9:E11)"],["=-'Financials'!E21"],["=SUM(E12:E13)"],["='Financials'!E20"]];
  s.getRange("E7:E15").format.numberFormat = money;
  formatCrossLinks(s, "E7:E8"); formatCrossLinks(s, "E10:E11"); formatCrossLinks(s, "E13:E15");
  s.getRange("C9:G9").format.font = { bold: true, color: navy };
  s.getRange("C12:G12").format.font = { bold: true, color: navy };
  s.getRange("C14:G14").format.font = { bold: true, color: "#C00000" };
  s.getRange("E14").conditionalFormats.add("cellIs", { operator: "lessThan", formula: 0, format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C18:D20").values = [["Interpretation", "The screen leaves $96.81 million before the potential holder put and negative $194.79 million after it."],["Holder-put boundary", "The June 2027 put is a sensitivity, not an assertion that holders will exercise it."],["Method limit", "Excludes cash inflows, operating needs, capex, taxes, entity restrictions beyond the stated designation, and unlisted obligations."]];
  s.getRange("C18:C20").format.font = { bold: true, color: navy }; s.getRange("D18:G20").format.wrapText = true;
  s.getRange("C6:G15").format.wrapText = true;
  s.freezePanes.freezeRows(6);
}

// Rating: transparent assumed ordinal bridge, not a calibrated PD or Coinbase policy.
{
  const s = wb.worksheets.getItem("Rating"); baseSheet(s, "#8064A2");
  title(s, "Illustrative obligor rating bridge", "Assumed ordinal judgment — not statistically calibrated and not Coinbase policy");
  s.getRange("C6:K11").values = [
    ["Factor ID", "Factor", "Weight", "Score", "Contribution", "Evidence", "Rationale", "What improves it", "Deterioration trigger"],
    ["RAT-01", "Liquidity scale", 0.25, 1, "", "SRC-001", "Cash is large relative to the request, subject to availability limits.", "Entity cash map confirms unrestricted repayment liquidity.", "Available entity liquidity is materially below headline cash."],
    ["RAT-02", "Leverage and maturities", 0.25, 4, "", "SRC-001; SRC-002", "Debt is substantial with identified near-term obligations.", "Debt schedule shows durable maturity headroom.", "Near-term maturities or refinancing needs increase materially."],
    ["RAT-03", "Operating cash generation", 0.20, 4, "", "SRC-002", "The 2025 filing reported significant operating cash use.", "Forecast and actuals show sustained positive cash generation.", "Operating cash use persists or worsens."],
    ["RAT-04", "Asset volatility and concentration", 0.15, 3, "", "SRC-001", "Headline liquidity includes material bitcoin exposure.", "Repayment no longer depends on bitcoin value.", "Bitcoin stress and issuer liquidity weaken together."],
    ["RAT-05", "Private diligence completeness", 0.15, 4, "", "ASM-C001; ASM-C004", "Forecast, entity cash map, and complete debt schedule are unavailable.", "All repayment diligence reconciles without material exception.", "Private diligence contradicts assumptions or remains unavailable."],
  ];
  header(s, "C6:K6");
  formatInputs(s, "E7:F11");
  s.getRange("E7:E11").format.numberFormat = "0%";
  s.getRange("F7:F11").dataValidation = { rule: { type: "list", values: [1, 2, 3, 4, 5] } };
  s.getRange("G7:G11").formulas = [["=E7*F7"],["=E8*F8"],["=E9*F9"],["=E10*F10"],["=E11*F11"]];
  s.getRange("G7:G11").format.numberFormat = "0.00";
  s.getRange("C14:D16").values = [["Rating result", "Value"],["Weighted score", ""],["Illustrative rating", ""]];
  header(s, "C14:D14");
  s.getRange("D15").formulas = [["=SUM(G7:G11)"]]; s.getRange("D15").format.numberFormat = "0.00";
  s.getRange("D16").formulas = [["=IF(D15<1.5,\"1 / Strong\",IF(D15<2.5,\"2 / Satisfactory\",IF(D15<3.5,\"3 / Watchful\",IF(D15<4.5,\"4 / Weak\",\"5 / Critical\"))))"]];
  s.getRange("C19:D21").values = [["Boundary", "The bridge is ordinal and judgmental; it does not imply PD, expected loss, or Coinbase policy."],["Interpretation", "Higher scores indicate weaker credit quality."],["Evidence rule", "Change a score only when the cited evidence or declared private diligence supports the change."]];
  s.getRange("C19:C21").format.font = { bold: true, color: navy }; s.getRange("D19:K21").format.wrapText = true;
  s.getRange("C6:K11").format.wrapText = true;
  s.freezePanes.freezeRows(6);
}

// Collateral waterfall.
{
  const s = wb.worksheets.getItem("Collateral"); baseSheet(s, "#70AD47");
  title(s, "Collateral proceeds and eligibility", "Case MARA-CR-001 | fictional USDC on Base; simulated conditions precedent are not real-world evidence");
  section(s, "C6:H6", "Base waterfall");
  s.getRange("C7:F21").values = [
    ["Step", "Value", "Unit", "Status"],
    ["Fictional USDC quantity", "", "USDC", "Input link"],
    ["Reference USDC price", "", "USD/USDC", "Input link"],
    ["Stressed USDC price", "", "USD/USDC", "Calculated"],
    ["Gross stressed value", "", "USD", "Calculated"],
    ["Execution cost", "", "USD", "Calculated"],
    ["Delay cost (2 hours × 12.5 bps)", "", "USD", "Calculated"],
    ["Fixed cost", "", "USD", "Input link"],
    ["Available proceeds before legal gate", "", "USD", "Calculated"],
    ["Ownership evidence complete?", "", "status", "Input link"],
    ["Legal control available?", "", "status", "Input link"],
    ["Prior lien cleared?", "", "status", "Input link"],
    ["Approved custody route?", "", "status", "Input link"],
    ["Hard blocker", "", "status", "Calculated"],
    ["Eligible proceeds", "", "USD", "Calculated"],
  ];
  header(s, "C7:F7");
  s.getRange("D8:D21").formulas = [
    ["='Assumptions'!D18"],["='Assumptions'!D19"],["=D9*(1-'Assumptions'!D20)"],["=D8*D10"],["=D11*'Assumptions'!D21"],["=D11*'Assumptions'!D22*'Assumptions'!D23"],["='Assumptions'!D24"],["=MAX(0,D11-D12-D13-D14)"],["='Assumptions'!D25"],["='Assumptions'!D26"],["='Assumptions'!D27"],["='Assumptions'!D28"],["=IF(OR(D16<>\"Yes\",D17<>\"Yes\",D18<>\"Yes\",D19<>\"Yes\"),\"YES\",\"NO\")"],["=IF(D20=\"YES\",0,D15)"],
  ];
  formatCrossLinks(s, "D8:D9"); formatCrossLinks(s, "D14"); formatCrossLinks(s, "D16:D19");
  s.getRange("D8").format.numberFormat = qty; s.getRange("D9:D10").format.numberFormat = money; s.getRange("D11:D15").format.numberFormat = money; s.getRange("D21").format.numberFormat = money;
  s.getRange("C24:F28").values = [
    ["Decision measure", "Value", "Unit", "Formula note"],
    ["Required coverage ratio", "", "x", "Assumption link"],
    ["Collateral cap", "", "USD", "Eligible proceeds ÷ coverage"],
    ["Exposure incl. accrued", "", "USD", "Funded + accrued"],
    ["Shortfall", "", "USD", "Max(0, exposure − eligible proceeds)"],
  ];
  header(s, "C24:F24"); s.getRange("D25:D28").formulas = [["='Assumptions'!D12"],["=MAX(0,D21/D25)"],["='Assumptions'!D9+'Assumptions'!D10"],["=MAX(0,D27-D21)"]];
  formatCrossLinks(s, "D25"); formatCrossLinks(s, "D27"); s.getRange("D26:D28").format.numberFormat = money;
  s.getRange("C31:H33").values = [["Interpretation", "Base-case ownership, priority, legal control, and route approval are simulated conditions precedent—not evidenced facts. Unknown or failed status sets proceeds to zero."],["Base note", "Chain state and protocol finality do not establish custody, enforceability, liquidation, withdrawal, or bank settlement."],["Reversal evidence", "Verified ownership, first-priority lien, enforceable control agreement, and approved tested repayment route."]];
  s.getRange("C31:C33").format.font = { bold: true, color: navy }; s.getRange("D31:H33").format.wrapText = true;
  section(s, "C36:L36", "Coverage covenant call ladder");
  s.getRange("C37:L44").values = [["Price stress", "Available proceeds", "Coverage", "Status", "Required proceeds", "Covenant headroom", "Top-up required", "Repayment required", "Max compliant commitment", "Rounded commitment"], ...collateralCallLadder.rows.map(row => [Number(row.price_stress_pct), "", "", "", "", "", "", "", "", ""])];
  header(s, "C37:L37");
  for (let row = 38; row <= 44; row++) {
    s.getRange(`D${row}:L${row}`).formulas = [[
      `=MAX(0,'Assumptions'!$D$18*'Assumptions'!$D$19*(1-C${row})*(1-'Assumptions'!$D$21-'Assumptions'!$D$22*'Assumptions'!$D$23)-'Assumptions'!$D$24)`,
      `=D${row}/('Summary'!$D$14+'Assumptions'!$D$10)`,
      `=IF(E${row}>='Assumptions'!$D$12,"PASS","CALL REQUIRED")`,
      `=('Summary'!$D$14+'Assumptions'!$D$10)*'Assumptions'!$D$12`,
      `=D${row}-G${row}`,
      `=MAX(0,(G${row}+'Assumptions'!$D$24)/('Assumptions'!$D$19*(1-C${row})*(1-'Assumptions'!$D$21-'Assumptions'!$D$22*'Assumptions'!$D$23))-'Assumptions'!$D$18)`,
      `=MAX(0,'Summary'!$D$14+'Assumptions'!$D$10-D${row}/'Assumptions'!$D$12)`,
      `=MAX(0,D${row}/'Assumptions'!$D$12-'Assumptions'!$D$10)`,
      `=FLOOR(K${row},'Assumptions'!$D$14)`,
    ]];
  }
  s.getRange("C38:C44").format.numberFormat = pct;
  s.getRange("D38:D44").format.numberFormat = money;
  s.getRange("E38:E44").format.numberFormat = "0.000x";
  s.getRange("G38:L44").format.numberFormat = money;
  s.getRange("F38:F44").conditionalFormats.add("containsText", { text: "CALL", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C46:L47").values = [["Exact modeled breach stress", Number(collateralCallLadder.exact_modeled_breach_price_stress_pct), "First grid call", Number(collateralCallLadder.first_grid_call_stress_pct), "", "", "", "", "", ""], ["Method limit", collateralCallLadder.method_limit, "", "", "", "", "", "", "", ""]];
  s.getRange("C46").format.font = { bold: true, color: navy }; s.getRange("E46").format.font = { bold: true, color: navy };
  s.getRange("D46:F46").format.numberFormat = pct; s.getRange("D47:L47").format.wrapText = true;
}

// Portfolio limit build.
{
  const s = wb.worksheets.getItem("Portfolio"); baseSheet(s, "#A5A5A5");
  title(s, "Illustrative portfolio concentration", "All exposures and policy limits are fictional");
  s.getRange("C6:J9").values = [
    ["Exposure", "Current funded", "Potential", "Sector", "Collateral", "Custody route", "Bank route", "Evidence class"],
    ["Fictional Miner A", 3500000, 1000000, "Digital mining", "USDC", "Route A", "Bank X", "Simulated"],
    ["Fictional Exchange B", 2000000, 1500000, "Digital assets", "USDC", "Route B", "Bank Y", "Simulated"],
    ["Proposed MARA case", "", "", "Digital mining", "USDC", "Route A", "Bank X", "Hypothetical"],
  ];
  header(s, "C6:J6"); formatInputs(s, "D7:E8");
  s.getRange("D9").formulas = [["='Assumptions'!D9"]]; s.getRange("E9").formulas = [["='Assumptions'!D8-'Assumptions'!D9"]]; formatCrossLinks(s, "D9:E9");
  s.getRange("D7:E9").format.numberFormat = money;
  section(s, "C12:H12", "Four-cap inputs");
  s.getRange("C13:F18").values = [
    ["Cap", "Limit", "Existing use", "Remaining capacity"],
    ["Obligor", "", 0, ""],
    ["Collateral", "", 0, ""],
    ["Single-name", "", 0, ""],
    ["Digital-mining sector", "", 4500000, ""],
    ["Shared custody route", "", 3500000, ""],
  ];
  header(s, "C13:F13");
  s.getRange("D14:D18").formulas = [["='Assumptions'!D13"],["='Collateral'!D26"],["='Assumptions'!D32"],["='Assumptions'!D33"],["='Assumptions'!D35"]];
  s.getRange("F14:F18").formulas = [["=MAX(0,D14-E14)"],["=MAX(0,D15-E15)"],["=MAX(0,D16-E16)"],["=MAX(0,D17-E17)"],["=MAX(0,D18-E18)"]];
  formatCrossLinks(s, "D14:D18"); s.getRange("D14:F18").format.numberFormat = money;
  s.getRange("C21:F25").values = [
    ["Decision cap", "Value", "Unit", "Explanation"],
    ["Obligor cap", "", "USD", "Illustrative standalone obligor capacity"],
    ["Collateral cap", "", "USD", "Eligibility-gated recovery support"],
    ["Single-name cap", "", "USD", "Policy capacity for the name"],
    ["Concentration cap", "", "USD", "Lower of sector and shared-route capacity"],
  ];
  header(s, "C21:F21"); s.getRange("D22:D25").formulas = [["=F14"],["=F15"],["=F16"],["=MIN(F17,F18)"]]; s.getRange("D22:D25").format.numberFormat = money;
}

// Scenarios: explicit one-driver and combined cases.
{
  const s = wb.worksheets.getItem("Scenarios"); baseSheet(s, "#8064A2");
  title(s, "Scenario comparison", "Each row recalculates the same collateral logic; all drivers are hypothetical");
  s.getRange("C6:O11").values = [
    ["Scenario", "Price decline", "Execution cost", "Effective hours", "Delay bps/hr", "Accessible qty", "Legal gate", "Gross value", "Available proceeds", "Collateral cap", "Exposure + accrued", "Shortfall", "Decision effect"],
    ["Base: simulated CPs verified", 0.02, 0.005, 2, 0.00125, 4000000, "Clear", "", "", "", "", "", "$3.0m rounded conditional limit"],
    ["30% USDC price decline", 0.30, 0.005, 2, 0.00125, 4000000, "Clear", "", "", "", "", "", "$2.2m rounded conditional limit"],
    ["24-hour additional route delay", 0, 0.005, 26, 0.00125, 4000000, "Clear", "", "", "", "", "", "$3.0m rounded conditional limit"],
    ["Route unavailable", 0, 0.005, 2, 0.00125, 0, "Blocked", "", "", "", "", "", "Decline; no eligible proceeds"],
    ["Unknown enforceability", 0.02, 0.005, 2, 0.00125, 4000000, "Blocked", "", "", "", "", "", "Decline pending diligence"],
  ];
  header(s, "C6:O6"); formatInputs(s, "D7:I11");
  s.getRange("D7:E11").format.numberFormat = pct; s.getRange("G7:G11").format.numberFormat = pct; s.getRange("H7:H11").format.numberFormat = qty;
  for (let row = 7; row <= 11; row++) {
    s.getRange(`J${row}:N${row}`).formulas = [[
      `=H${row}*'Assumptions'!D19*(1-D${row})`,
      `=IF(I${row}=\"Blocked\",0,MAX(0,J${row}*(1-E${row}-F${row}*G${row})-'Assumptions'!D24))`,
      `=MAX(0,K${row}/'Assumptions'!D12)`,
      `='Assumptions'!D9+'Assumptions'!D10`,
      `=MAX(0,M${row}-K${row})`,
    ]];
  }
  s.getRange("J7:N11").format.numberFormat = money; formatCrossLinks(s, "J7:N11");
  s.getRange("C14:H19").values = [
    ["Invariant", "Test result", "Formula / test"],
    ["Lower price cannot increase proceeds", "", "30% price proceeds ≤ base proceeds"],
    ["Higher delay cost cannot increase proceeds", "", "24-hour delay proceeds ≤ base proceeds"],
    ["Zero accessible quantity yields zero proceeds", "", "Route unavailable proceeds = 0"],
    ["Blocked legal gate yields zero eligible proceeds", "", "Blocked-base proceeds = 0"],
    ["Higher eligible proceeds cannot increase shortfall", "", "Clear-base shortfall ≤ blocked-base shortfall"],
  ];
  header(s, "C14:H14"); s.getRange("D15:D19").formulas = [["=IF(K8<=K7,\"PASS\",\"FAIL\")"],["=IF(K9<=K7,\"PASS\",\"FAIL\")"],["=IF(K10=0,\"PASS\",\"FAIL\")"],["=IF(K11=0,\"PASS\",\"FAIL\")"],["=IF(N7<=N11,\"PASS\",\"FAIL\")"]];
  s.getRange("D15:D19").conditionalFormats.add("containsText", { text: "FAIL", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
}

// Two-dimensional collateral quantity and price-stress sensitivity.
{
  const s = wb.worksheets.getItem("Sensitivity"); baseSheet(s, "#8064A2");
  title(s, "Collateral decision surface", "Recommended limit by fictional USDC quantity and price decline; all other assumptions held constant");
  section(s, "C6:K6", "Recommended amount");
  s.getRange("C7:K12").values = [
    ["USDC quantity / price decline", 0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50],
    [2000000, "", "", "", "", "", "", "", ""],
    [3000000, "", "", "", "", "", "", "", ""],
    [4000000, "", "", "", "", "", "", "", ""],
    [5000000, "", "", "", "", "", "", "", ""],
    [6000000, "", "", "", "", "", "", "", ""],
  ];
  header(s, "C7:K7"); s.getRange("D7:K7").format.numberFormat = pct;
  s.getRange("C8:C12").format.numberFormat = '#,##0,,"m"';
  for (let row = 8; row <= 12; row++) {
    for (let col = 4; col <= 11; col++) {
      const letter = String.fromCharCode(64 + col);
      s.getRange(`${letter}${row}`).formulas = [[`=FLOOR(MIN('Assumptions'!$D$8,MAX(0,($C${row}*'Assumptions'!$D$19*(1-${letter}$7))*(1-'Assumptions'!$D$21-'Assumptions'!$D$22*'Assumptions'!$D$23)-'Assumptions'!$D$24)/'Assumptions'!$D$12,'Portfolio'!$D$22,'Portfolio'!$D$24,'Portfolio'!$D$25),'Assumptions'!$D$14)`]];
    }
  }
  s.getRange("D8:K12").format.numberFormat = money1;
  s.getRange("D8:K12").conditionalFormats.add("colorScale", { colors: ["#F4CCCC", "#FFF2CC", "#D9EAD3"], thresholds: ["min", { type: "percentile", value: 50 }, "max"] });
  s.getRange("C15:K18").values = [
    ["Interpretation", "Each cell is the rounded recommendation after the collateral, obligor, single-name, concentration, and requested-amount caps."],
    ["Base location", "4.0m USDC and 2% price decline reproduces the $3.0m conditional recommendation."],
    ["Boundary", "The grid assumes every simulated legal and operational condition is clear. An unresolved hard blocker still produces a decline."],
    ["Method", "Execution cost, delay cost, fixed cost, coverage, and non-collateral caps remain at the declared base assumptions."],
  ];
  s.getRange("C15:C18").format.font = { bold: true, color: navy };
  s.getRange("D15:K18").format.wrapText = false;
}

// Summary decision and chart.
{
  const s = wb.worksheets.getItem("Summary"); baseSheet(s, navy);
  title(s, "MARA hypothetical facility decision", "Case MARA-CR-001 | $5 million request | public issuer facts + fictional case terms");
  section(s, "C6:H6", "Committee decision");
  s.getRange("C7:F16").values = [
    ["Measure", "Result", "Unit", "Interpretation"],
    ["Requested commitment", "", "USD", "Hypothetical"],
    ["Hard blocker", "", "status", "Ownership, lien, legal control, and approved route must all be clear"],
    ["Obligor cap", "", "USD", "Illustrative"],
    ["Collateral cap", "", "USD", "Eligibility-gated"],
    ["Single-name cap", "", "USD", "Illustrative"],
    ["Concentration cap", "", "USD", "Illustrative"],
    ["Recommended amount", "", "USD", "Lowest cap rounded down to the declared $100k increment, subject to no hard blocker"],
    ["Recommendation", "", "decision", "Reassess after named diligence evidence is complete"],
    ["Funding gate", "", "status", "Conditional approval is not authority to fund"],
  ];
  header(s, "C7:F7");
  s.getRange("D8:D16").formulas = [["='Assumptions'!D8"],["='Collateral'!D20"],["='Portfolio'!D22"],["='Portfolio'!D23"],["='Portfolio'!D24"],["='Portfolio'!D25"],["=IF(D9=\"YES\",0,FLOOR(MIN(D8,D10:D13),'Assumptions'!D14))"],["=IF(D9=\"YES\",\"DECLINE PENDING DILIGENCE\",IF(D14>=D8,\"APPROVE REQUESTED AMOUNT\",IF(D14>0,\"APPROVE $3.0M SUBJECT TO SIMULATED CONDITIONS PRECEDENT\",\"DECLINE\")))"],["='Conditions'!D10"]];
  s.getRange("D8").format.numberFormat = money; s.getRange("D10:D14").format.numberFormat = money1;
  formatCrossLinks(s, "D16");
  s.getRange("D16").conditionalFormats.add("containsText", { text: "BLOCKED", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C17:F23").values = [
    ["Supporting measure", "Value", "Unit", "Why it matters"],
    ["Available proceeds before legal gate", "", "USD", "Economic value before enforceability constraints"],
    ["Eligible proceeds", "", "USD", "Equals available proceeds only when every simulated condition precedent is clear"],
    ["Requested-draw recovery exposure", "", "USD", "Requested fully drawn amount plus accrued; used only for recovery testing"],
    ["Requested-draw recovery shortfall", "", "USD", "Requested-draw recovery exposure less eligible proceeds, floored at zero"],
    ["Recommended pro forma exposure", "", "USD", "Recommended limit plus accrued amount"],
    ["Recommended-limit coverage surplus", "", "USD", "Eligible proceeds less recommended pro forma exposure, floored at zero"],
  ];
  header(s, "C17:F17"); s.getRange("D18:D23").formulas = [["='Collateral'!D15"],["='Collateral'!D21"],["='Collateral'!D27"],["='Collateral'!D28"],["=IF(D14>0,D14+'Assumptions'!D10,0)"],["=MAX(0,D19-D22)"]]; s.getRange("D18:D23").format.numberFormat = money1;
  s.getRange("C26:H30").values = [
    ["Action", "Requirement"],
    ["Decision", "Approve a $3.0 million conditional limit only if the simulated ownership, first-priority lien, enforceable control, and Base-to-cash route conditions are evidenced before funding."],
    ["Alternative 1", "Consider a smaller unsecured limit only after primary-repayment analysis and full policy review."],
    ["Alternative 2", "Decline if any simulated condition precedent remains unknown or the Base-to-cash route fails."],
    ["Strongest objection", "The request is small relative to reported cash and bitcoin, but those balances do not establish availability to this facility."],
  ];
  s.getRange("C26:D26").format.fill = navy; s.getRange("C26:D26").format.font = { bold: true, color: "#FFFFFF" };
  s.getRange("D27:H30").format.wrapText = true;
  s.getRange("J7:K11").values = [["Cap", "Amount"],["Obligor", ""],["Collateral", ""],["Single-name", ""],["Concentration", ""]];
  s.getRange("K8:K11").formulas = [["=D10"],["=D11"],["=D12"],["=D13"]]; s.getRange("K8:K11").format.numberFormat = money1; header(s, "J7:K7");
  const chart = s.charts.add("bar", s.getRange("J7:K11"));
  chart.titleText = "Four-cap comparison ($M)";
  chart.hasLegend = false;
  chart.setPosition("J13", "N30");
}

// Conditions: operational closing tracker linked to the decision gate.
{
  const s = wb.worksheets.getItem("Conditions"); baseSheet(s, "#C55A11");
  title(s, "Pre-funding conditions", "Current project evidence status; conditional approval is not authority to fund");
  section(s, "C6:H6", "Funding gate summary");
  s.getRange("C7:D10").values = [
    ["Measure", "Result"],
    ["Total blocking conditions", ""],
    ["Outstanding conditions", ""],
    ["Funding gate", ""],
  ];
  header(s, "C7:D7");
  s.getRange("D8:D10").formulas = [["=COUNTA(C14:C22)"],["=COUNTIF(G14:G22,\"Outstanding\")"],["=IF(D9>0,\"BLOCKED PENDING CONDITIONS\",\"CLEARED TO FUND\")"]];
  s.getRange("D8:D9").format.numberFormat = "0";
  s.getRange("D10").conditionalFormats.add("containsText", { text: "BLOCKED", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C13:K22").values = [
    ["Condition ID", "Category", "Requirement", "Owner", "Status", "Timing", "Verification evidence", "Source ID", "Blocking"],
    ["CP-01", "Collateral", "Verify beneficial ownership of the proposed collateral lot.", "Credit / borrower", "Outstanding", "Before funding", "Ownership documents and independently corroborated custody records", "ASM-C007", "Yes"],
    ["CP-02", "Legal", "Confirm no prior lien and first-priority perfected security.", "Legal", "Outstanding", "Before funding", "Lien search, executed security documents, and legal confirmation", "ASM-C007", "Yes"],
    ["CP-03", "Control", "Establish enforceable lender control over the collateral and custody account.", "Legal / operations", "Outstanding", "Before funding", "Executed control agreement and operating-procedure test", "ASM-C007", "Yes"],
    ["CP-04", "Operations", "Test the Base-to-liquidation-to-bank repayment route end to end.", "Operations / treasury", "Outstanding", "Before funding", "Read-only route test with timestamps, fees, and destination confirmation", "ASM-C007", "Yes"],
    ["DD-01", "Repayment", "Obtain and reconcile a current 13-week borrowing-entity cash forecast.", "Credit / borrower", "Outstanding", "Before funding", "Forecast-to-bank and forecast-to-historical reconciliation", "ASM-C001", "Yes"],
    ["DD-02", "Purpose", "Document facility purpose and a controlled use-of-proceeds schedule.", "Credit / borrower", "Outstanding", "Before funding", "Approved sources-and-uses schedule tied to facility documents", "ASM-C001", "Yes"],
    ["DD-03", "Entity", "Map legal-entity cash ownership and transfer restrictions.", "Credit / legal", "Outstanding", "Before funding", "Entity chart, account map, and restriction review", "ASM-C001", "Yes"],
    ["DD-04", "Repayment", "Reconcile the complete debt-service and maturity schedule.", "Credit / borrower", "Outstanding", "Before funding", "Debt schedule tied to agreements, filings, and forecast cash flows", "ASM-C001", "Yes"],
    ["PF-01", "Portfolio", "Confirm current single-name and shared-risk concentration capacity.", "Portfolio risk", "Outstanding", "Before funding", "Current portfolio report and limit-owner sign-off", "ASM-C005", "Yes"],
  ];
  header(s, "C13:K13");
  formatInputs(s, "G14:G22");
  s.getRange("G14:G22").dataValidation = { rule: { type: "list", values: ["Outstanding", "Verified"] } };
  s.getRange("G14:G22").conditionalFormats.add("containsText", { text: "Outstanding", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C13:K22").format.wrapText = true;
  s.getRange("E14:E22").format.verticalAlignment = "top";
  s.getRange("I14:I22").format.verticalAlignment = "top";
  s.freezePanes.freezeRows(13);
}

// Model risks: known limitations with evidence requirements and explicit unresolved dispositions.
{
  const s = wb.worksheets.getItem("Model Risks"); baseSheet(s, "#7030A0");
  title(s, "Model-risk register", "Known limitations remain open until their required evidence is independently reviewed");
  section(s, "C6:F6", "Risk posture summary");
  s.getRange("C7:C10").values = [["Open risks"], ["Critical risks"], ["High risks"], ["Decision-blocking risks"]];
  s.getRange("D7:D10").formulas = [["=COUNTIF(G15:G22,\"open\")"], ["=COUNTIF(F15:F22,\"critical\")"], ["=COUNTIF(F15:F22,\"high\")"], ["=COUNTIF(C15:C22,\"MR-01\")+COUNTIF(C15:C22,\"MR-02\")+COUNTIF(C15:C22,\"MR-03\")+COUNTIF(C15:C22,\"MR-07\")"]];
  s.getRange("C7:C10").format.font = { bold: true, color: navy };
  const rows = [["Risk ID", "Category", "Risk", "Severity", "Status", "Affected decision", "Linked assumptions", "Linked conditions", "Mitigation", "Validation evidence", "Residual risk", "Owner", "Disposition if unresolved"]];
  for (const risk of modelRiskRegister.risks) rows.push([
    risk.risk_id, risk.category, risk.risk, risk.severity, risk.status, risk.affected_decision,
    risk.linked_assumptions.join(", ") || "None", risk.linked_conditions.join(", ") || "None",
    risk.mitigation, risk.validation_evidence, risk.residual_risk, risk.owner, risk.disposition_if_unresolved,
  ]);
  s.getRange("C14:O22").values = rows;
  header(s, "C14:O14");
  s.getRange("C14:O22").format.wrapText = true;
  s.getRange("E15:E22").conditionalFormats.add("containsText", { text: "critical", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("F15:F22").conditionalFormats.add("containsText", { text: "open", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  s.getRange("C25:O25").values = [["Method limit", modelRiskRegister.method_limit, "", "", "", "", "", "", "", "", "", "", ""]];
  s.getRange("C25").format.font = { bold: true, color: navy }; s.getRange("D25:O25").format.wrapText = false;
  s.freezePanes.freezeRows(14);
}

// Covenant package: draft contractual control design linked to monitoring evidence.
{
  const s = wb.worksheets.getItem("Control Matrix"); baseSheet(s, "#4472C4");
  title(s, "End-to-end control matrix", "Pre-funding evidence through monitoring, draft covenant, response authority, and closure");
  section(s, "C6:G6", "Control architecture summary");
  s.getRange("C7:D11").values = [
    ["Control chains", controlMatrix.summary.control_count],
    ["Conditions covered", controlMatrix.summary.condition_count],
    ["Critical controls", controlMatrix.summary.critical_control_count],
    ["High controls", controlMatrix.summary.high_control_count],
    ["Controls with outstanding conditions", controlMatrix.summary.outstanding_condition_control_count],
  ];
  s.getRange("C7:C11").format.font = { bold: true, color: navy };
  const rows = [["Control", "Objective", "Conditions", "Condition state", "Monitor", "Metric / threshold", "Covenant", "Cure period", "Playbook", "Severity / response clock", "Draw state", "Decision owner", "Exit criteria"]];
  for (const row of controlMatrix.controls) rows.push([
    row.control_id, row.control_objective, row.condition_ids.join(", "), row.condition_status, row.monitor_id,
    `${row.metric} | ${row.threshold}`, row.covenant_id, row.cure_period, row.playbook_id,
    `${row.severity_on_trigger} | ${row.response_sla}`, row.draw_state_on_trigger.replaceAll("_", " "), row.decision_owner, row.exit_criteria,
  ]);
  s.getRange("C14:O22").values = rows;
  header(s, "C14:O14");
  s.getRange("C14:O22").format.wrapText = true;
  s.getRange("F15:F22").conditionalFormats.add("containsText", { text: "outstanding", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  s.getRange("M15:M22").conditionalFormats.add("containsText", { text: "blocked", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("C25:O25").values = [["Method limit", controlMatrix.method_limit, "", "", "", "", "", "", "", "", "", "", ""]];
  s.getRange("C25").format.font = { bold: true, color: navy }; s.getRange("D25:O25").format.wrapText = true;
  s.freezePanes.freezeRows(14);
}

// Covenant package: draft contractual control design linked to monitoring evidence.
{
  const s = wb.worksheets.getItem("Covenants"); baseSheet(s, "#C55A11");
  title(s, "Illustrative covenant package", "Draft control terms only; not executed, legally reviewed, or Coinbase policy");
  const rows = [["ID", "Type", "Requirement", "Threshold", "Current evidence", "Status", "Frequency", "Cure period", "Breach consequence", "Owner", "Monitor"]];
  for (const covenant of covenantPlan.covenants) {
    rows.push([covenant.covenant_id, covenant.covenant_type, covenant.requirement, covenant.threshold, "", "", covenant.test_frequency, covenant.cure_period, covenant.breach_consequence, covenant.owner_role, covenant.monitor_id]);
  }
  s.getRange("C6:M14").values = rows;
  header(s, "C6:M6");
  for (let row = 7; row <= 14; row++) {
    const monitoringRow = row;
    s.getRange(`G${row}:H${row}`).formulas = [[`='Monitoring'!F${monitoringRow}`, `='Monitoring'!G${monitoringRow}`]];
  }
  formatCrossLinks(s, "G7:H14");
  s.getRange("G7").format.numberFormat = "0.000x";
  s.getRange("G8").format.numberFormat = "0";
  s.getRange("G13").format.numberFormat = money;
  s.getRange("H7:H14").conditionalFormats.add("containsText", { text: "BLOCKED", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("H7:H14").conditionalFormats.add("containsText", { text: "NOT MEASURED", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  s.getRange("C6:M14").format.wrapText = true;
  section(s, "C17:F17", "Covenant state summary");
  s.getRange("C18:D21").values = [["Covenant count", ""],["Projected passes", ""],["Pre-funding blockers", ""],["Not measured", ""]];
  s.getRange("D18:D21").formulas = [["=COUNTA(C7:C14)"],["=COUNTIF(H7:H14,\"PASS PROJECTION\")"],["=COUNTIF(H7:H14,\"PRE-FUNDING BLOCKED\")"],["=COUNTIF(H7:H14,\"NOT MEASURED\")"]];
  s.getRange("C23:D23").values = [["Method limit", covenantPlan.method_limit]];
  s.getRange("C18:C23").format.font = { bold: true, color: navy };
  s.getRange("D23:M23").format.wrapText = false;
  s.freezePanes.freezeRows(6);
}

// Monitoring: illustrative post-close controls; private observations remain explicitly unavailable.
{
  const s = wb.worksheets.getItem("Monitoring"); baseSheet(s, "#A5A5A5");
  title(s, "Monitoring and early-warning design", "Not active borrower monitoring; funding remains blocked pending conditions");
  s.getRange("C6:K14").values = [
    ["ID", "Metric", "Threshold", "Current evidence", "Status", "Frequency", "Owner", "Breach action", "Escalation"],
    ["MON-01", "Collateral coverage at recommended limit", ">= 1.25x", "", "", "Continuous", "Credit risk", "Block new draws; require cure or collateral top-up.", "Immediate credit and legal review"],
    ["MON-02", "Collateral ownership, priority, and control", "All verified", "", "", "Continuous and on custody change", "Legal and collateral operations", "Assign zero collateral credit and block funding.", "Immediate credit, legal, and operations review"],
    ["MON-03", "Base-to-cash route test", "<= 4 hours end to end", "Private test required", "NOT MEASURED", "Monthly and after route change", "Collateral operations", "Suspend availability until a successful route test.", "Same-day operations and credit review"],
    ["MON-04", "Borrowing-entity unrestricted cash", ">= $25 million", "Private reporting required", "NOT MEASURED", "Monthly", "Borrower reporting and credit risk", "Freeze incremental availability and reassess obligor cap.", "Five-business-day credit review"],
    ["MON-05", "Operating cash generation variance", "No >20% adverse variance", "Private reporting required", "NOT MEASURED", "Monthly and quarterly", "Credit risk", "Refresh rating factors and repayment analysis.", "Next review; immediate if liquidity runway is affected"],
    ["MON-06", "Additional secured debt or lien creation", "$0 without lender consent", "Private reporting required", "NOT MEASURED", "Event-driven with monthly certification", "Legal and credit risk", "Block new draws and assess default or waiver path.", "Immediate legal and credit review"],
    ["MON-07", "USDC collateral concentration headroom", ">= $0", "", "", "Continuous before each draw", "Portfolio risk", "Reject the draw or reduce the facility limit.", "Pre-draw portfolio-risk review"],
    ["MON-08", "Financial and collateral reporting delivery", "Within 15 business days", "Private reporting required", "NOT MEASURED", "Monthly", "Credit administration", "Block new draws until reporting is complete.", "Five-business-day credit-administration review"],
  ];
  header(s, "C6:K6");
  s.getRange("F7").formulas = [["='Collateral'!D15/('Summary'!D14+'Assumptions'!D10)"]];
  s.getRange("G7").formulas = [["=IF(F7>=1.25,\"PASS PROJECTION\",\"BREACH PROJECTION\")"]];
  s.getRange("F8").formulas = [["='Conditions'!D9"]];
  s.getRange("G8").formulas = [["=IF(F8>0,\"PRE-FUNDING BLOCKED\",\"READY FOR ACTIVATION\")"]];
  s.getRange("F13").formulas = [["='Portfolio'!D25-'Summary'!D14"]];
  s.getRange("G13").formulas = [["=IF(F13>=0,\"PASS PROJECTION\",\"BREACH PROJECTION\")"]];
  s.getRange("F7").format.numberFormat = "0.000x";
  s.getRange("F8").format.numberFormat = "0";
  s.getRange("F13").format.numberFormat = money;
  s.getRange("G7:G14").conditionalFormats.add("containsText", { text: "BLOCKED", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("G7:G14").conditionalFormats.add("containsText", { text: "NOT MEASURED", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  section(s, "C17:F17", "Monitoring state summary");
  s.getRange("C18:D21").values = [["Rule count", ""],["Projected passes", ""],["Pre-funding blockers", ""],["Not measured", ""]];
  s.getRange("D18:D21").formulas = [["=COUNTA(C7:C14)"],["=COUNTIF(G7:G14,\"PASS PROJECTION\")"],["=COUNTIF(G7:G14,\"PRE-FUNDING BLOCKED\")"],["=COUNTIF(G7:G14,\"NOT MEASURED\")"]];
  s.getRange("C23:D23").values = [["Method limit", "Illustrative monitoring design only. It is not executed borrower reporting, an executed or legally reviewed covenant package, or Coinbase policy."]];
  s.getRange("C18:C23").format.font = { bold: true, color: navy };
  s.getRange("C6:K14").format.wrapText = true; s.getRange("D23:K23").format.wrapText = true;
  s.freezePanes.freezeRows(6);
}

// Escalation response paths linked to monitoring and covenant controls.
{
  const s = wb.worksheets.getItem("Escalations"); baseSheet(s, "#C00000");
  title(s, "Escalation and response playbook", "Illustrative response paths; no incident or borrower breach is currently observed");
  const rows = [["ID", "Severity", "Response clock", "Draw state", "Current evidence", "Current status", "Current response", "Decision owner", "Required evidence", "Exit criteria", "Monitor", "Covenant"]];
  for (const row of escalationPlaybook.playbooks) {
    rows.push([row.playbook_id, row.severity_on_trigger, row.response_sla, row.draw_state_on_trigger, "", "", row.current_response.replaceAll("_", " "), row.decision_owner, row.required_evidence, row.exit_criteria, row.monitor_id, row.covenant_id]);
  }
  s.getRange("C6:N14").values = rows;
  header(s, "C6:N6");
  for (let row = 7; row <= 14; row++) {
    s.getRange(`G${row}:H${row}`).formulas = [[`='Monitoring'!F${row}`, `='Monitoring'!G${row}`]];
  }
  formatCrossLinks(s, "G7:H14");
  s.getRange("G7").format.numberFormat = "0.000x";
  s.getRange("G8").format.numberFormat = "0";
  s.getRange("G13").format.numberFormat = money;
  s.getRange("D7:D14").conditionalFormats.add("containsText", { text: "CRITICAL", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("H7:H14").conditionalFormats.add("containsText", { text: "BLOCKED", format: { fill: paleRed, font: { bold: true, color: "#C00000" } } });
  s.getRange("H7:H14").conditionalFormats.add("containsText", { text: "NOT MEASURED", format: { fill: paleAmber, font: { bold: true, color: dark } } });
  s.getRange("C6:N14").format.wrapText = true;
  section(s, "C18:F18", "Response design summary");
  s.getRange("C19:D24").values = [["Playbook count", ""], ["Critical", ""], ["High", ""], ["Moderate", ""], ["Current pre-funding blocker", ""], ["Private evidence required", ""]];
  s.getRange("D19:D24").formulas = [["=COUNTA(C7:C14)"], ["=COUNTIF(D7:D14,\"CRITICAL\")"], ["=COUNTIF(D7:D14,\"HIGH\")"], ["=COUNTIF(D7:D14,\"MODERATE\")"], ["=COUNTIF(H7:H14,\"PRE-FUNDING BLOCKED\")"], ["=COUNTIF(H7:H14,\"NOT MEASURED\")"]];
  s.getRange("C26:D26").values = [["Method limit", escalationPlaybook.method_limit]];
  s.getRange("C19:C26").format.font = { bold: true, color: navy };
  s.getRange("D26:N26").format.wrapText = false;
  s.freezePanes.freezeRows(6);
}

// Source register and limitations.
{
  const s = wb.worksheets.getItem("Sources"); baseSheet(s, "#7F7F7F");
  title(s, "Source register", "Primary public sources and explicit assumption records");
  s.getRange("C6:J14").values = [
    ["Source ID", "Input or claim", "Class", "URL or assumption", "Period end", "Published", "Retrieved", "Limitation"],
    ["SRC-001", "MARA June 2026 financial and liquidity facts", "Reported", "https://www.sec.gov/Archives/edgar/data/1507605/000150760526000022/mara-20260630.htm", new Date("2026-06-30"), new Date("2026-08-07"), new Date("2026-09-20"), "Does not establish facility collateral, ownership, lien priority, or Coinbase relationship"],
    ["SRC-002", "MARA 2025 annual financial and cash-flow facts", "Reported", "https://www.sec.gov/Archives/edgar/data/1507605/000150760526000007/mara-20251231.htm", new Date("2025-12-31"), new Date("2026-03-02"), new Date("2026-09-20"), "Annual baseline predates interim filing"],
    ["SRC-003", "Coinbase Exchange candles endpoint behavior", "Reported", "https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles", "", new Date("2026-09-20"), new Date("2026-09-20"), "Historical intervals can be missing; not order-book history"],
    ["SRC-004", "Coinbase Exchange product book", "Reported", "https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-book", "", new Date("2026-09-20"), new Date("2026-09-20"), "Point-in-time displayed depth does not prove execution"],
    ["SRC-005", "Base finality and derivation", "Reported", "https://docs.base.org/base-chain/specs/protocol/consensus/derivation", "", new Date("2026-09-20"), new Date("2026-09-20"), "Does not establish custody, control, withdrawal, or off-ramp timing"],
    ["ASM-001", "Facility amount and terms", "Assumed", "Fictional case", "", new Date("2026-09-20"), new Date("2026-09-20"), "Not MARA or Coinbase terms"],
    ["ASM-002", "Collateral and availability", "Simulated", "Fictional case", "", new Date("2026-09-20"), new Date("2026-09-20"), "Cannot establish ownership or enforceability"],
    ["ASM-003", "Portfolio exposures and limits", "Simulated", "Fictional policy", "", new Date("2026-09-20"), new Date("2026-09-20"), "Not Coinbase policy"],
  ];
  header(s, "C6:J6"); s.getRange("G7:I14").format.numberFormat = "yyyy-mm-dd"; s.getRange("F7:F14").format.wrapText = false; s.getRange("J7:J14").format.wrapText = true;
  s.getRange("C17:J22").values = [
    ["Model limitation", "Treatment"],
    ["No verified collateral ownership", "Hard blocker; eligible proceeds are zero"],
    ["No legal opinion or lien search", "Hard blocker; no arbitrary enforceability haircut"],
    ["No executable market-depth history", "Execution and delay costs remain labeled assumptions"],
    ["No private borrower forecast", "Obligor cap is illustrative, not a calibrated rating or PD"],
    ["No Coinbase policy or confidential portfolio", "Limits and exposures are fictional"],
  ];
  s.getRange("C17:D17").format.fill = navy; s.getRange("C17:D17").format.font = { bold: true, color: "#FFFFFF" }; s.getRange("D18:J22").format.wrapText = true;
}

// Consistent dimensions and compact layout.
for (const name of sheetNames) {
  const s = wb.worksheets.getItem(name);
  s.getRange("A:A").format.columnWidth = 2;
  s.getRange("B:B").format.columnWidth = 2;
  s.getRange("C:C").format.columnWidth = 24;
  s.getRange("D:D").format.columnWidth = 22;
  s.getRange("E:E").format.columnWidth = 16;
  s.getRange("F:F").format.columnWidth = 20;
  s.getRange("G:N").format.columnWidth = 16;
  s.getRange("2:2").format.rowHeight = 24;
  s.getUsedRange().format.autofitRows();
}
wb.worksheets.getItem("Summary").getRange("F:F").format.columnWidth = 42;
wb.worksheets.getItem("Summary").getRange("D:D").format.columnWidth = 28;
wb.worksheets.getItem("Financials").getRange("D:D").format.columnWidth = 34;
wb.worksheets.getItem("Financials").getRange("I:I").format.columnWidth = 42;
wb.worksheets.getItem("Assumptions").getRange("C:C").format.columnWidth = 14;
wb.worksheets.getItem("Assumptions").getRange("D:D").format.columnWidth = 22;
wb.worksheets.getItem("Assumptions").getRange("E:E").format.columnWidth = 15;
wb.worksheets.getItem("Assumptions").getRange("F:F").format.columnWidth = 38;
wb.worksheets.getItem("Assumptions").getRange("G:G").format.columnWidth = 14;
wb.worksheets.getItem("Assumptions").getRange("H:H").format.columnWidth = 28;
wb.worksheets.getItem("Assumptions").getRange("I:I").format.columnWidth = 28;
wb.worksheets.getItem("Assumptions").getRange("J:K").format.columnWidth = 46;
wb.worksheets.getItem("Assumptions").getRange("L:L").format.columnWidth = 26;
wb.worksheets.getItem("Assumptions").getRange("45:51").format.rowHeight = 58;
wb.worksheets.getItem("Liquidity").getRange("C:C").format.columnWidth = 20;
wb.worksheets.getItem("Liquidity").getRange("D:D").format.columnWidth = 48;
wb.worksheets.getItem("Liquidity").getRange("E:E").format.columnWidth = 20;
wb.worksheets.getItem("Liquidity").getRange("F:F").format.columnWidth = 16;
wb.worksheets.getItem("Liquidity").getRange("G:G").format.columnWidth = 42;
wb.worksheets.getItem("Liquidity").getRange("7:15").format.rowHeight = 30;
wb.worksheets.getItem("Rating").getRange("C:C").format.columnWidth = 14;
wb.worksheets.getItem("Rating").getRange("D:D").format.columnWidth = 28;
wb.worksheets.getItem("Rating").getRange("E:G").format.columnWidth = 14;
wb.worksheets.getItem("Rating").getRange("H:H").format.columnWidth = 20;
wb.worksheets.getItem("Rating").getRange("I:K").format.columnWidth = 44;
wb.worksheets.getItem("Rating").getRange("7:11").format.rowHeight = 58;
wb.worksheets.getItem("Collateral").getRange("C:C").format.columnWidth = 24;
wb.worksheets.getItem("Collateral").getRange("D:D").format.columnWidth = 22;
wb.worksheets.getItem("Collateral").getRange("E:E").format.columnWidth = 16;
wb.worksheets.getItem("Collateral").getRange("F:F").format.columnWidth = 20;
wb.worksheets.getItem("Collateral").getRange("G:I").format.columnWidth = 22;
wb.worksheets.getItem("Collateral").getRange("J:L").format.columnWidth = 24;
wb.worksheets.getItem("Collateral").getRange("37:37").format.rowHeight = 30;
wb.worksheets.getItem("Collateral").getRange("C37:L44").format.wrapText = true;
wb.worksheets.getItem("Collateral").getRange("47:47").format.rowHeight = 72;
wb.worksheets.getItem("Sources").getRange("D:D").format.columnWidth = 36;
wb.worksheets.getItem("Sources").getRange("F:F").format.columnWidth = 64;
wb.worksheets.getItem("Sources").getRange("J:J").format.columnWidth = 48;
wb.worksheets.getItem("Scenarios").getRange("C:C").format.columnWidth = 36;
wb.worksheets.getItem("Scenarios").getRange("D:D").format.columnWidth = 18;
wb.worksheets.getItem("Scenarios").getRange("E:E").format.columnWidth = 26;
wb.worksheets.getItem("Scenarios").getRange("F:N").format.columnWidth = 18;
wb.worksheets.getItem("Scenarios").getRange("O:O").format.columnWidth = 38;
wb.worksheets.getItem("Scenarios").getRange("C6:O11").format.wrapText = true;
wb.worksheets.getItem("Scenarios").getRange("C14:E19").format.wrapText = true;
wb.worksheets.getItem("Scenarios").getRange("15:19").format.rowHeight = 30;
wb.worksheets.getItem("Sensitivity").getRange("C:C").format.columnWidth = 30;
wb.worksheets.getItem("Sensitivity").getRange("D:K").format.columnWidth = 15;
wb.worksheets.getItem("Sensitivity").getRange("15:18").format.rowHeight = 20;
wb.worksheets.getItem("Conditions").getRange("C:C").format.columnWidth = 24;
wb.worksheets.getItem("Conditions").getRange("D:D").format.columnWidth = 18;
wb.worksheets.getItem("Conditions").getRange("E:E").format.columnWidth = 46;
wb.worksheets.getItem("Conditions").getRange("F:F").format.columnWidth = 24;
wb.worksheets.getItem("Conditions").getRange("G:H").format.columnWidth = 18;
wb.worksheets.getItem("Conditions").getRange("I:I").format.columnWidth = 48;
wb.worksheets.getItem("Conditions").getRange("J:K").format.columnWidth = 14;
wb.worksheets.getItem("Conditions").getRange("14:22").format.rowHeight = 40;
wb.worksheets.getItem("Control Matrix").getRange("C:C").format.columnWidth = 13;
wb.worksheets.getItem("Control Matrix").getRange("D:D").format.columnWidth = 38;
wb.worksheets.getItem("Control Matrix").getRange("E:G").format.columnWidth = 19;
wb.worksheets.getItem("Control Matrix").getRange("H:H").format.columnWidth = 35;
wb.worksheets.getItem("Control Matrix").getRange("I:I").format.columnWidth = 14;
wb.worksheets.getItem("Control Matrix").getRange("J:J").format.columnWidth = 34;
wb.worksheets.getItem("Control Matrix").getRange("K:K").format.columnWidth = 14;
wb.worksheets.getItem("Control Matrix").getRange("L:L").format.columnWidth = 31;
wb.worksheets.getItem("Control Matrix").getRange("M:M").format.columnWidth = 18;
wb.worksheets.getItem("Control Matrix").getRange("N:N").format.columnWidth = 25;
wb.worksheets.getItem("Control Matrix").getRange("O:O").format.columnWidth = 42;
wb.worksheets.getItem("Control Matrix").getRange("15:22").format.rowHeight = 64;
wb.worksheets.getItem("Control Matrix").getRange("25:25").format.rowHeight = 54;
wb.worksheets.getItem("Model Risks").getRange("C:C").format.columnWidth = 13;
wb.worksheets.getItem("Model Risks").getRange("D:D").format.columnWidth = 18;
wb.worksheets.getItem("Model Risks").getRange("E:E").format.columnWidth = 44;
wb.worksheets.getItem("Model Risks").getRange("F:G").format.columnWidth = 15;
wb.worksheets.getItem("Model Risks").getRange("H:H").format.columnWidth = 28;
wb.worksheets.getItem("Model Risks").getRange("I:J").format.columnWidth = 23;
wb.worksheets.getItem("Model Risks").getRange("K:L").format.columnWidth = 46;
wb.worksheets.getItem("Model Risks").getRange("M:M").format.columnWidth = 15;
wb.worksheets.getItem("Model Risks").getRange("N:N").format.columnWidth = 26;
wb.worksheets.getItem("Model Risks").getRange("O:O").format.columnWidth = 42;
wb.worksheets.getItem("Model Risks").getRange("15:22").format.rowHeight = 62;
wb.worksheets.getItem("Model Risks").getRange("25:25").format.rowHeight = 24;
wb.worksheets.getItem("Covenants").getRange("C:C").format.columnWidth = 13;
wb.worksheets.getItem("Covenants").getRange("D:D").format.columnWidth = 15;
wb.worksheets.getItem("Covenants").getRange("E:E").format.columnWidth = 44;
wb.worksheets.getItem("Covenants").getRange("F:H").format.columnWidth = 22;
wb.worksheets.getItem("Covenants").getRange("I:I").format.columnWidth = 28;
wb.worksheets.getItem("Covenants").getRange("J:K").format.columnWidth = 42;
wb.worksheets.getItem("Covenants").getRange("L:L").format.columnWidth = 28;
wb.worksheets.getItem("Covenants").getRange("M:M").format.columnWidth = 13;
wb.worksheets.getItem("Covenants").getRange("7:14").format.rowHeight = 54;
wb.worksheets.getItem("Covenants").getRange("23:23").format.rowHeight = 20;
wb.worksheets.getItem("Monitoring").getRange("C:C").format.columnWidth = 20;
wb.worksheets.getItem("Monitoring").getRange("D:D").format.columnWidth = 34;
wb.worksheets.getItem("Monitoring").getRange("E:E").format.columnWidth = 24;
wb.worksheets.getItem("Monitoring").getRange("F:G").format.columnWidth = 22;
wb.worksheets.getItem("Monitoring").getRange("H:H").format.columnWidth = 30;
wb.worksheets.getItem("Monitoring").getRange("I:I").format.columnWidth = 32;
wb.worksheets.getItem("Monitoring").getRange("J:K").format.columnWidth = 44;
wb.worksheets.getItem("Monitoring").getRange("7:14").format.rowHeight = 48;
wb.worksheets.getItem("Escalations").getRange("C:C").format.columnWidth = 30;
wb.worksheets.getItem("Escalations").getRange("D:D").format.columnWidth = 14;
wb.worksheets.getItem("Escalations").getRange("E:F").format.columnWidth = 25;
wb.worksheets.getItem("Escalations").getRange("G:G").format.columnWidth = 28;
wb.worksheets.getItem("Escalations").getRange("H:H").format.columnWidth = 24;
wb.worksheets.getItem("Escalations").getRange("I:I").format.columnWidth = 31;
wb.worksheets.getItem("Escalations").getRange("J:J").format.columnWidth = 24;
wb.worksheets.getItem("Escalations").getRange("K:L").format.columnWidth = 46;
wb.worksheets.getItem("Escalations").getRange("M:N").format.columnWidth = 13;
wb.worksheets.getItem("Escalations").getRange("7:14").format.rowHeight = 58;
wb.worksheets.getItem("Escalations").getRange("26:26").format.rowHeight = 20;

const conditionSheet = wb.worksheets.getItem("Conditions");
conditionSheet.getRange("G14").values = [["Verified"]];
wb.recalculate();
const partialOutstanding = Number(conditionSheet.getRange("D9").values[0][0]);
const partialGate = String(conditionSheet.getRange("D10").values[0][0]);
if (partialOutstanding !== 8 || partialGate !== "BLOCKED PENDING CONDITIONS") {
  throw new Error(`Condition workflow check failed after one verification: count=${partialOutstanding}, gate=${partialGate}`);
}
conditionSheet.getRange("G14:G22").values = Array.from({ length: 9 }, () => ["Verified"]);
wb.recalculate();
const clearedGate = String(conditionSheet.getRange("D10").values[0][0]);
if (clearedGate !== "CLEARED TO FUND") throw new Error(`Condition workflow clear-state check failed: ${clearedGate}`);
conditionSheet.getRange("G14:G22").values = Array.from({ length: 9 }, () => ["Outstanding"]);
wb.recalculate();
const restoredGate = String(conditionSheet.getRange("D10").values[0][0]);
if (restoredGate !== "BLOCKED PENDING CONDITIONS") throw new Error(`Condition workflow restore check failed: ${restoredGate}`);
const ratingSheet = wb.worksheets.getItem("Rating");
const baseRatingScore = Number(ratingSheet.getRange("D15").values[0][0]);
const baseRatingGrade = String(ratingSheet.getRange("D16").values[0][0]);
ratingSheet.getRange("F7").values = [[2]];
wb.recalculate();
const worsenedRatingScore = Number(ratingSheet.getRange("D15").values[0][0]);
if (baseRatingScore !== 3.1 || baseRatingGrade !== "3 / Watchful" || worsenedRatingScore < baseRatingScore) {
  throw new Error(`Rating workflow check failed: base=${baseRatingScore}/${baseRatingGrade}, worsened=${worsenedRatingScore}`);
}
ratingSheet.getRange("F7").values = [[1]];
wb.recalculate();
const monitoringSheet = wb.worksheets.getItem("Monitoring");
const monitoringSummary = monitoringSheet.getRange("D18:D21").values.flat().map(Number);
if (monitoringSummary.join(",") !== "8,2,1,5") {
  throw new Error(`Monitoring workflow summary failed: ${monitoringSummary.join(",")}`);
}
const escalationSheet = wb.worksheets.getItem("Escalations");
const escalationSummary = escalationSheet.getRange("D19:D24").values.flat().map(Number);
if (escalationSummary.join(",") !== "8,3,4,1,1,5") {
  throw new Error(`Escalation workflow summary failed: ${escalationSummary.join(",")}`);
}
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(outputPath);

for (const name of sheetNames) {
  const preview = await wb.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, `${name.toLowerCase()}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const formulaScan = await wb.inspect({ kind: "formula", maxChars: 20000, options: { maxResults: 500 } });
const errorScan = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, maxChars: 12000 });
const summary = await wb.inspect({ kind: "region", sheetId: "Summary", range: "C6:N30", maxChars: 12000 });
await fs.rename(`${outputPath}.inspect.ndjson`, path.join(previewDir, "credit-model.inspect.ndjson")).catch(() => {});
const formulaCount = formulaScan.ndjson.split("\n").filter(Boolean).length;
const errorMatches = errorScan.ndjson.includes("matched 0 entries") ? 0 : errorScan.ndjson.split("\n").filter(Boolean).length;
console.log(JSON.stringify({ outputPath, previews: sheetNames.length, formulaCount, errorMatches, conditionWorkflowChecks: 3, ratingWorkflowChecks: 1, monitoringWorkflowChecks: 1, summaryRegions: summary.ndjson.split("\n").filter(Boolean).length }, null, 2));
