#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import vm from "node:vm";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const htmlPath = path.join(root, "outputs", "decision-view.html");
const outputPath = path.join(root, "artifacts", "decision-view-audit.json");
const html = await fs.readFile(htmlPath, "utf8");

const contractMatch = html.match(/const whatIf=(.*);\nconst attribution=/s);
const collateralCallsMatch = html.match(/const collateralCalls=(.*);\nconst labels=/s);
const controlMatrixMatch = html.match(/const controlMatrix=(.*);\nconst reviewerScorecard=/s);
const modelRiskMatch = html.match(/const modelRisks=(.*);\nconst controlMatrix=/s);
const reviewerScorecardMatch = html.match(/const reviewerScorecard=(.*);\nconst readiness=/s);
const readinessMatch = html.match(/const readiness=(.*);\nconst collateralCalls=/s);
const evaluatorMatch = html.match(/function evaluateWhatIf\(inputs\)\{.*?\n\}\nfunction renderLab/s);
if (!contractMatch || !collateralCallsMatch || !controlMatrixMatch || !modelRiskMatch || !reviewerScorecardMatch || !readinessMatch || !evaluatorMatch) throw new Error("Unable to extract shipped what-if contract, collateral-call ladder, control matrix, model risks, readiness state, scorecard, or evaluator");
const contract = JSON.parse(contractMatch[1]);
const collateralCalls = JSON.parse(collateralCallsMatch[1]);
const controlMatrix = JSON.parse(controlMatrixMatch[1]);
const modelRisks = JSON.parse(modelRiskMatch[1]);
const reviewerScorecard = JSON.parse(reviewerScorecardMatch[1]);
const readiness = JSON.parse(readinessMatch[1]);
const evaluatorSource = evaluatorMatch[0].replace(/\nfunction renderLab$/, "");
const context = { whatIf: contract, result: null };
vm.createContext(context);
vm.runInContext(`${evaluatorSource}\nresult=whatIf.test_vectors.map(vector=>({vector_id:vector.vector_id,actual:evaluateWhatIf(vector.inputs),expected:vector.expected}));`, context);

const moneyFields = ["available_proceeds_usd", "collateral_cap_usd", "recommended_amount_usd", "recommended_pro_forma_exposure_usd", "coverage_surplus_usd"];
const vectorResults = context.result.map(({ vector_id, actual, expected }) => {
  const errors = [];
  for (const field of moneyFields) if (Math.abs(Number(actual[field]) - Number(expected[field])) > 0.011) errors.push(`${field}: ${actual[field]} != ${expected[field]}`);
  for (const field of ["binding_cap", "decision"]) if (actual[field] !== expected[field]) errors.push(`${field}: ${actual[field]} != ${expected[field]}`);
  if (actual.hard_blockers.join("|") !== expected.hard_blockers.join("|")) errors.push("hard_blockers differ");
  return { vector_id, status: errors.length ? "FAIL" : "PASS", errors };
});

const requiredIds = [
  "whatIfLab", "labQuantity", "labStress", "labDelay", "labExecution", "labOwnership",
  "labPriority", "labControl", "labRoute", "labRecommendation", "labProceeds",
  "labCollateralCap", "labBinding", "labProForma", "labSurplus", "labDecision",
  "labBlockers", "labContractStatus", "resetLab", "whatIfLimit",
  "attributionCount", "attributionReduced", "attributionDeclines", "attributionBlockers", "attributionLimit",
  "lineageNodes", "lineageLinks", "lineageReported", "lineageAssumed", "lineageTable", "lineageLimit",
  "diligenceTasks", "diligenceCritical", "diligenceLanes", "diligenceReady", "diligenceWaiting", "diligenceTable", "diligenceLimit",
  "assumptionCount", "assumptionCritical", "assumptionHigh", "assumptionUnvalidated", "assumptionTable", "assumptionLimit",
  "reviewNav", "decisionSummary", "scenarioMatrixSection",
  "modelRiskSection", "modelRiskOpen", "modelRiskCritical", "modelRiskHigh", "modelRiskBlocking", "modelRiskSeverity", "modelRiskBlockingOnly", "modelRiskVisible", "modelRiskTable", "modelRiskLimit",
  "collateralCallSection", "callExactStress", "callFirstGridStress", "callRequiredProceeds", "callExposure", "collateralCallTable", "collateralCallLimit",
  "controlMatrixSection", "controlMatrixCount", "controlMatrixConditions", "controlMatrixCritical", "controlMatrixOutstanding", "controlMatrixTable", "controlMatrixLimit",
  "readinessSection", "readinessLocal", "readinessShare", "readinessPassed", "readinessOutstanding", "humanGateTable", "reviewerScorecardLink", "readinessInterpretation",
];
const idResults = requiredIds.map(id => {
  const count = (html.match(new RegExp(`id=["']${id}["']`, "g")) || []).length;
  return { id, count, status: count === 1 ? "PASS" : "FAIL" };
});
const ladderErrors = [];
if (collateralCalls.rows.length !== 7) ladderErrors.push("expected seven ladder rows");
if (collateralCalls.first_grid_call_stress_pct !== "0.05") ladderErrors.push("first grid call is not 5%");
if (collateralCalls.rows[0].status !== "PASS" || collateralCalls.rows[1].status !== "CALL_REQUIRED") ladderErrors.push("pass/call boundary changed");
for (let index = 1; index < collateralCalls.rows.length; index++) {
  if (Number(collateralCalls.rows[index].repayment_required_usd) < Number(collateralCalls.rows[index - 1].repayment_required_usd)) ladderErrors.push(`repayment cure decreases at row ${index + 1}`);
  if (Number(collateralCalls.rows[index].rounded_coverage_compliant_commitment_usd) > Number(collateralCalls.rows[index - 1].rounded_coverage_compliant_commitment_usd)) ladderErrors.push(`commitment increases at row ${index + 1}`);
}
const ladderResult = { status: ladderErrors.length ? "FAIL" : "PASS", row_count: collateralCalls.rows.length, errors: ladderErrors };
const controlErrors = [];
if (controlMatrix.controls.length !== 8) controlErrors.push("expected eight control chains");
for (const field of ["control_id", "monitor_id", "covenant_id", "playbook_id"]) if (new Set(controlMatrix.controls.map(row => row[field])).size !== 8) controlErrors.push(`${field} is not unique`);
const coveredConditions = new Set(controlMatrix.controls.flatMap(row => row.condition_ids));
if (coveredConditions.size !== 9) controlErrors.push("expected nine covered conditions");
if (controlMatrix.activation_state !== "pre_funding_blocked" || controlMatrix.enforceability_status !== "draft_only") controlErrors.push("governance boundary changed");
const controlResult = { status: controlErrors.length ? "FAIL" : "PASS", row_count: controlMatrix.controls.length, condition_count: coveredConditions.size, errors: controlErrors };
const modelRiskErrors = [];
if (modelRisks.risks.length !== 8) modelRiskErrors.push("expected eight model risks");
if (modelRisks.risks.some(row => row.status !== "open" || !row.owner || !row.mitigation || !row.validation_evidence || !row.disposition_if_unresolved)) modelRiskErrors.push("model-risk governance is incomplete");
if (modelRisks.summary.critical_count !== 3) modelRiskErrors.push("expected three critical model risks");
const decisionBlockingRiskCount = modelRisks.risks.filter(row => /(block|decline|do not fund)/i.test(row.disposition_if_unresolved)).length;
const criticalBlockingRiskCount = modelRisks.risks.filter(row => row.severity === "critical" && /(block|decline|do not fund)/i.test(row.disposition_if_unresolved)).length;
if (decisionBlockingRiskCount !== 4 || criticalBlockingRiskCount !== 3 || !html.includes("function renderModelRisks()")) modelRiskErrors.push("model-risk filter contract is missing or changed");
const modelRiskResult = { status: modelRiskErrors.length ? "FAIL" : "PASS", row_count: modelRisks.risks.length, critical_count: modelRisks.summary.critical_count, decision_blocking_count: decisionBlockingRiskCount, critical_blocking_count: criticalBlockingRiskCount, errors: modelRiskErrors };
const navigationTargets = ["decisionSummary", "whatIfLab", "scenarioMatrixSection", "collateralCallSection", "controlMatrixSection", "modelRiskSection", "readinessSection"];
const navigationErrors = navigationTargets.filter(id => !html.includes(`href="#${id}"`) || !html.includes(`id="${id}"`)).map(id => `missing navigation target ${id}`);
const navigationResult = { status: navigationErrors.length ? "FAIL" : "PASS", target_count: navigationTargets.length, errors: navigationErrors };
const readinessErrors = [];
const passedHumanGates = readiness.human_gates.filter(row => row.status === "PASS").length;
const outstandingHumanGates = readiness.human_gates.filter(row => row.status === "OUTSTANDING").length;
if (!readiness.local_acceptance_verified) readinessErrors.push("local acceptance is not verified");
if (reviewerScorecard.summary.gate_count !== 3 || readiness.human_gates.length !== 3) readinessErrors.push("expected three human gates");
if (reviewerScorecard.summary.passed_count !== passedHumanGates || reviewerScorecard.summary.outstanding_count !== outstandingHumanGates) readinessErrors.push("scorecard and readiness gate counts differ");
if (passedHumanGates + outstandingHumanGates !== 3) readinessErrors.push("unsupported human gate status");
if (readiness.ready_to_share !== (readiness.local_acceptance_verified && passedHumanGates === 3)) readinessErrors.push("ready-to-share does not match local and human gate status");
if (!html.includes('id="reviewerScorecardLink" href="/mara-credit-case/reviewer-scorecard.pdf"')) readinessErrors.push("scorecard link is missing or changed");
const readinessResult = { status: readinessErrors.length ? "FAIL" : "PASS", gate_count: reviewerScorecard.summary.gate_count, outstanding_count: reviewerScorecard.summary.outstanding_count, errors: readinessErrors };
const failures = [...vectorResults.filter(row => row.status === "FAIL"), ...idResults.filter(row => row.status === "FAIL"), ...(ladderErrors.length ? [ladderResult] : []), ...(controlErrors.length ? [controlResult] : []), ...(modelRiskErrors.length ? [modelRiskResult] : []), ...(navigationErrors.length ? [navigationResult] : []), ...(readinessErrors.length ? [readinessResult] : [])];
const payload = {
  schema_version: "1.0",
  artifact: "outputs/decision-view.html",
  vector_results: vectorResults,
  required_id_results: idResults,
  collateral_call_result: ladderResult,
  control_matrix_result: controlResult,
  model_risk_result: modelRiskResult,
  navigation_result: navigationResult,
  readiness_result: readinessResult,
  summary: { vector_count: vectorResults.length, collateral_call_row_count: collateralCalls.rows.length, control_matrix_row_count: controlMatrix.controls.length, model_risk_row_count: modelRisks.risks.length, human_gate_count: reviewerScorecard.summary.gate_count, required_id_count: idResults.length, failure_count: failures.length },
};
await fs.writeFile(outputPath, JSON.stringify(payload, null, 2) + "\n");
if (failures.length) throw new Error(`Decision-view runtime audit failed with ${failures.length} issue(s)`);
console.log(`Decision-view audit: ${vectorResults.length} vectors, ${collateralCalls.rows.length} collateral-call rows, ${controlMatrix.controls.length} control chains, ${modelRisks.risks.length} model risks, ${reviewerScorecard.summary.gate_count} human gates, and ${idResults.length} unique IDs PASS`);
