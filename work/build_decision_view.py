#!/usr/bin/env python3
"""Build a self-contained reviewer decision view from validated scenario JSON."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = json.loads((ROOT / "artifacts/scenario-results.json").read_text(encoding="utf-8"))
BASE = next(row for row in SCENARIOS if row["scenario_id"] == "base")
THRESHOLDS = json.loads((ROOT / "artifacts/threshold-analysis.json").read_text(encoding="utf-8"))
MONITORING = json.loads((ROOT / "artifacts/monitoring-plan.json").read_text(encoding="utf-8"))
LIQUIDITY = json.loads((ROOT / "artifacts/liquidity-analysis.json").read_text(encoding="utf-8"))
COVENANTS = json.loads((ROOT / "artifacts/covenant-plan.json").read_text(encoding="utf-8"))
ESCALATIONS = json.loads((ROOT / "artifacts/escalation-playbook.json").read_text(encoding="utf-8"))
WHAT_IF = json.loads((ROOT / "artifacts/what-if-contract.json").read_text(encoding="utf-8"))
ATTRIBUTION = json.loads((ROOT / "artifacts/scenario-attribution.json").read_text(encoding="utf-8"))
LINEAGE = json.loads((ROOT / "artifacts/decision-lineage.json").read_text(encoding="utf-8"))
DILIGENCE = json.loads((ROOT / "artifacts/diligence-plan.json").read_text(encoding="utf-8"))
ASSUMPTIONS = json.loads((ROOT / "artifacts/assumption-register.json").read_text(encoding="utf-8"))
MODEL_RISKS = json.loads((ROOT / "artifacts/model-risk-register.json").read_text(encoding="utf-8"))
COLLATERAL_CALLS = json.loads((ROOT / "artifacts/collateral-call-ladder.json").read_text(encoding="utf-8"))
CONTROL_MATRIX = json.loads((ROOT / "artifacts/control-matrix.json").read_text(encoding="utf-8"))
READINESS = json.loads((ROOT / "artifacts/readiness-report.json").read_text(encoding="utf-8"))
REVIEWER_SCORECARD = json.loads((ROOT / "artifacts/reviewer-scorecard.json").read_text(encoding="utf-8"))


def js(value) -> str:
    return json.dumps(value, separators=(",", ":")).replace("</", "<\\/")


template = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>MARA-CR-001 decision view</title>
  <style>
    :root { --navy:#16324f; --blue:#2f75b5; --ink:#17202a; --muted:#64707d; --line:#d8e0e8; --paper:#f4f7fa; --warn:#fff2cc; --bad:#a32121; --good:#1f6a44; }
    * { box-sizing:border-box; }
    body { margin:0; color:var(--ink); background:var(--paper); font:15px/1.45 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    .skip-link { position:absolute; left:12px; top:-60px; z-index:10; background:#fff; color:var(--navy); padding:10px 14px; border-radius:6px; font-weight:700; }
    .skip-link:focus { top:12px; }
    header { background:var(--navy); color:#fff; padding:22px max(24px,calc((100vw - 1160px)/2)); }
    header h1 { margin:0 0 4px; font-size:24px; letter-spacing:.1px; }
    header p { margin:0; opacity:.78; }
    main { max-width:1160px; margin:0 auto; padding:22px 24px 40px; }
    .boundary { background:var(--warn); border:1px solid #d6b656; padding:11px 14px; margin-bottom:18px; border-radius:7px; }
    .grid { display:grid; grid-template-columns:1.25fr .75fr; gap:18px; }
    .card { background:white; border:1px solid var(--line); border-radius:10px; padding:17px; box-shadow:0 2px 10px rgba(22,50,79,.05); }
    .card h2 { margin:0 0 12px; color:var(--navy); font-size:17px; }
    .decision { display:flex; justify-content:space-between; gap:20px; align-items:flex-start; }
    .decision strong { display:block; color:var(--navy); font-size:31px; line-height:1.1; margin-top:3px; }
    .status { padding:7px 10px; border-radius:999px; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; background:#e4f2ea; color:var(--good); }
    .status.decline { background:#fbe6e6; color:var(--bad); }
    .muted { color:var(--muted); font-size:13px; }
    select { width:100%; font:inherit; padding:9px 10px; border:1px solid #aebbc8; border-radius:6px; background:white; margin:4px 0 14px; }
    input { font:inherit; accent-color:var(--blue); }
    button { font:inherit; font-weight:650; color:var(--navy); background:#fff; border:1px solid #9aabba; border-radius:6px; padding:8px 11px; cursor:pointer; }
    button:hover { background:#edf4fa; }
    :is(a,button,select):focus-visible { outline:3px solid #f2b134; outline-offset:2px; }
    .toolbar { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 18px; align-items:center; }
    .toolbar .muted { margin-left:auto; }
    .review-nav { position:sticky; top:0; z-index:5; display:flex; gap:7px; overflow-x:auto; margin:0 0 18px; padding:9px; background:rgba(244,247,250,.96); border:1px solid var(--line); border-radius:8px; backdrop-filter:blur(8px); }
    .review-nav a { flex:0 0 auto; color:var(--navy); background:#fff; border:1px solid #b8c5d1; border-radius:999px; padding:6px 10px; font-size:12px; font-weight:700; text-decoration:none; }
    .review-nav a:hover { background:#edf4fa; }
    .metrics { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:10px; margin-top:15px; }
    .metric { border:1px solid var(--line); border-radius:7px; padding:10px; }
    .metric span { display:block; color:var(--muted); font-size:12px; }
    .metric b { font-size:18px; color:var(--navy); }
    table { width:100%; border-collapse:collapse; }
    th { text-align:left; color:white; background:var(--navy); padding:8px 10px; font-size:12px; }
    td { padding:8px 10px; border-bottom:1px solid var(--line); }
    td:last-child { text-align:right; font-variant-numeric:tabular-nums; }
    .scenario-table { display:block; overflow-x:auto; white-space:nowrap; }
    .scenario-table td:last-child { text-align:left; white-space:normal; min-width:190px; }
    .scenario-table tr.active { background:#fff7df; }
    .scenario-table button { border:0; padding:2px 0; background:transparent; color:#145a8d; text-decoration:underline; font-weight:700; }
    .delta-down { color:var(--bad); font-weight:700; }
    .delta-flat { color:var(--muted); }
    .call-pass { color:var(--good); font-weight:700; }
    .call-required { color:var(--bad); font-weight:700; }
    .action-link { display:inline-block; color:white; background:var(--blue); border-radius:6px; padding:9px 12px; font-weight:700; text-decoration:none; }
    .action-link:hover { background:var(--navy); }
    .gate { color:var(--bad)!important; font-size:14px!important; }
    .condition-table td:nth-child(1),.condition-table td:nth-child(4) { white-space:nowrap; }
    .condition-table td:last-child { text-align:left; }
    .bar-row { display:grid; grid-template-columns:105px 1fr 95px; align-items:center; gap:8px; margin:9px 0; }
    .track { height:14px; background:#edf1f5; border-radius:4px; overflow:hidden; }
    .bar { height:100%; background:var(--blue); transition:width .25s; }
    .bar.binding { background:#c26b2e; }
    .blockers { color:var(--bad); font-weight:650; }
    .question { font-size:18px; color:var(--navy); margin:4px 0 0; }
    .lab-grid { display:grid; grid-template-columns:repeat(2,minmax(220px,1fr)); gap:14px 22px; }
    .lab-control { display:grid; grid-template-columns:1fr auto; gap:4px 12px; align-items:center; }
    .lab-control input[type="range"] { grid-column:1/-1; width:100%; }
    .lab-value { color:var(--navy); font-weight:700; font-variant-numeric:tabular-nums; }
    .control-checks { display:flex; flex-wrap:wrap; gap:8px 18px; margin:16px 0; padding:12px; border:1px solid var(--line); border-radius:7px; }
    .control-checks label { display:flex; gap:7px; align-items:center; }
    .risk-filters { display:flex; flex-wrap:wrap; gap:10px 18px; align-items:end; margin:14px 0 10px; padding:11px 12px; border:1px solid var(--line); border-radius:7px; background:#f7fafc; }
    .risk-filters label { display:grid; gap:3px; color:var(--muted); font-size:12px; }
    .risk-filters label:has(input[type="checkbox"]) { display:flex; align-items:center; gap:7px; padding-bottom:9px; }
    .risk-filters select { width:auto; min-width:150px; margin:0; }
    .lab-result { border-left:4px solid var(--blue); background:#f7fafc; padding:13px 14px; margin-top:14px; }
    .lab-result.decline { border-color:var(--bad); background:#fff7f7; }
    .wide { grid-column:1/-1; }
    .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
    footer { color:var(--muted); margin-top:18px; font-size:12px; }
    @media (max-width:820px) { .grid,.lab-grid { grid-template-columns:1fr; } .metrics { grid-template-columns:1fr; } }
    @media (prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; } }
    @media print { body { background:#fff; font-size:11px; } header { padding:12px 0; color:var(--navy); background:#fff; border-bottom:2px solid var(--navy); } main { max-width:none; padding:12px 0; } .toolbar,.review-nav,.risk-filters,.skip-link { display:none!important; } .card { box-shadow:none; break-inside:avoid; padding:11px; } .grid { gap:10px; } footer { margin-top:10px; } }
  </style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to decision content</a>
<header><h1>MARA-CR-001 credit decision</h1><p>Hypothetical $5 million facility | public issuer facts + fictional transaction terms</p></header>
<main id="main-content" tabindex="-1">
  <div class="boundary">MARA is not represented as a Coinbase customer. The facility, collateral, Base route, policy caps, and portfolio are fictional. This view supports an independent case study, not a real credit decision.</div>
  <div class="toolbar" aria-label="Decision view actions">
    <button id="copySummary" type="button">Copy scenario summary</button>
    <button id="downloadScenario" type="button">Download scenario JSON</button>
    <button id="printView" type="button">Print view</button>
    <button id="resetScenario" type="button">Reset to base</button>
    <span id="actionStatus" class="muted" role="status" aria-live="polite"></span>
  </div>
  <nav class="review-nav" id="reviewNav" aria-label="Review sections"><a href="#decisionSummary">Decision</a><a href="#whatIfLab">What-if</a><a href="#scenarioMatrixSection">Scenarios</a><a href="#collateralCallSection">Cures</a><a href="#controlMatrixSection">Controls</a><a href="#modelRiskSection">Model risks</a><a href="#readinessSection">Readiness</a></nav>
  <div class="grid">
    <section class="card" id="decisionSummary" aria-live="polite" aria-atomic="true">
      <div class="decision"><div><span class="muted">Recommendation</span><strong id="amount"></strong><div id="decisionText" class="muted"></div></div><span id="status" class="status"></span></div>
      <div class="metrics"><div class="metric"><span>Available proceeds</span><b id="proceeds"></b></div><div class="metric"><span>Requested-draw recovery exposure</span><b id="exposure"></b></div><div class="metric"><span>Requested-draw recovery shortfall</span><b id="shortfall"></b></div><div class="metric"><span>Recommended pro forma exposure</span><b id="proFormaExposure"></b></div><div class="metric"><span>Recommended-limit coverage surplus</span><b id="proFormaSurplus"></b></div><div class="metric"><span>Funding gate</span><b id="fundingGate" class="gate"></b></div></div>
      <p class="muted" id="exposureBasis"></p>
    </section>
    <section class="card">
      <h2>Scenario</h2>
      <label class="muted" for="scenario">Change one declared case</label>
      <select id="scenario" aria-describedby="scenarioHelp"></select>
      <p id="scenarioHelp" class="sr-only">Selecting a scenario updates the recommendation, constraints, waterfall, and shareable URL.</p>
      <div><span class="muted">Binding constraint</span><div id="binding" style="font-size:21px;font-weight:700;color:var(--navy)"></div></div>
      <p id="blockers" class="blockers"></p>
    </section>
    <section class="card">
      <h2>Four-cap decision</h2>
      <div id="bars" role="img" aria-label="Four-cap comparison"></div>
    </section>
    <section class="card">
      <h2>Collateral waterfall</h2>
      <table><thead><tr><th>Measure</th><th>Amount</th></tr></thead><tbody id="waterfall"></tbody></table>
      <p class="muted">Base case: 4.0m fictional USDC, 2% stress, 50 bps execution cost, 25 bps delay cost, $20k fixed cost, and 1.25x coverage.</p>
    </section>
    <section class="card wide">
      <h2>Decision thresholds</h2>
      <div class="metrics"><div class="metric"><span>Max price decline preserving $3m</span><b id="thresholdStress"></b></div><div class="metric"><span>Minimum collateral for $3m</span><b id="thresholdQty"></b></div><div class="metric"><span>Maximum under non-collateral caps</span><b id="thresholdCap"></b></div></div>
      <p class="muted">Break-even sensitivities hold execution cost, delay, fixed cost, coverage, and all non-target drivers constant. They are not forecasts.</p>
    </section>
    <section class="card wide" id="collateralCallSection">
      <h2>Coverage covenant call ladder</h2>
      <p class="muted">Stress the recommended $3.0 million commitment plus accrued amount. A negative covenant headroom identifies the modeled cure needed to restore 1.25× coverage.</p>
      <div class="metrics"><div class="metric"><span>Exact modeled breach stress</span><b id="callExactStress"></b></div><div class="metric"><span>First tested call point</span><b id="callFirstGridStress"></b></div><div class="metric"><span>Required proceeds</span><b id="callRequiredProceeds"></b></div><div class="metric"><span>Exposure including accrued</span><b id="callExposure"></b></div></div>
      <div class="scenario-table"><table><caption class="sr-only">Collateral coverage stress, covenant status, cures, and compliant commitment</caption><thead><tr><th scope="col">Price stress</th><th scope="col">Available proceeds</th><th scope="col">Coverage</th><th scope="col">Status</th><th scope="col">Covenant headroom</th><th scope="col">Top-up required</th><th scope="col">Repayment required</th><th scope="col">Rounded compliant commitment</th></tr></thead><tbody id="collateralCallTable"></tbody></table></div>
      <p class="muted" id="collateralCallLimit"></p>
    </section>
    <section class="card wide" id="whatIfLab">
      <h2>Live collateral what-if lab</h2>
      <p class="muted">Change simulated collateral and execution assumptions. The obligor, single-name, concentration, coverage, and rounding rules remain locked to the case contract.</p>
      <div class="lab-grid">
        <label class="lab-control" for="labQuantity"><span>Accessible USDC quantity</span><output class="lab-value" id="labQuantityValue" for="labQuantity"></output><input id="labQuantity" type="range"></label>
        <label class="lab-control" for="labStress"><span>Price decline</span><output class="lab-value" id="labStressValue" for="labStress"></output><input id="labStress" type="range"></label>
        <label class="lab-control" for="labDelay"><span>Additional route delay</span><output class="lab-value" id="labDelayValue" for="labDelay"></output><input id="labDelay" type="range"></label>
        <label class="lab-control" for="labExecution"><span>Execution cost</span><output class="lab-value" id="labExecutionValue" for="labExecution"></output><input id="labExecution" type="range"></label>
      </div>
      <fieldset class="control-checks"><legend>Hard-blocker controls</legend><label><input id="labOwnership" type="checkbox"> Ownership verified</label><label><input id="labPriority" type="checkbox"> First priority verified</label><label><input id="labControl" type="checkbox"> Legal control enforceable</label><label><input id="labRoute" type="checkbox"> Repayment route available</label></fieldset>
      <div id="labResult" class="lab-result" role="status" aria-live="polite">
        <div class="metrics"><div class="metric"><span>Recommendation</span><b id="labRecommendation"></b></div><div class="metric"><span>Available proceeds</span><b id="labProceeds"></b></div><div class="metric"><span>Collateral cap</span><b id="labCollateralCap"></b></div><div class="metric"><span>Binding constraint</span><b id="labBinding"></b></div><div class="metric"><span>Pro forma exposure</span><b id="labProForma"></b></div><div class="metric"><span>Coverage surplus</span><b id="labSurplus"></b></div></div>
        <p id="labDecision"></p><p id="labBlockers" class="blockers"></p>
      </div>
      <div class="toolbar" style="margin-top:12px"><button id="resetLab" type="button">Reset lab</button><span id="labContractStatus" class="muted"></span></div>
      <p class="muted" id="whatIfLimit"></p>
    </section>
    <section class="card wide">
      <h2>Collateral decision surface</h2>
      <p class="muted">Rounded recommendation by fictional USDC quantity and price decline. All legal and operational conditions are assumed clear; an unresolved hard blocker still produces a decline.</p>
      <div class="scenario-table"><table id="sensitivityTable"><caption class="sr-only">Recommended amount by collateral quantity and price decline</caption><thead id="sensitivityHead"></thead><tbody id="sensitivityBody"></tbody></table></div>
    </section>
    <section class="card wide">
      <h2>Decision governance</h2>
      <div class="metrics"><div class="metric"><span>Illustrative rating</span><b id="rating"></b></div><div class="metric"><span>Weighted score</span><b id="ratingScore"></b></div><div class="metric"><span>Material public-fact coverage</span><b id="sourceCoverage"></b></div><div class="metric"><span>Review status</span><b id="reviewStatus" style="font-size:14px"></b></div></div>
      <p><b>Rationale:</b> <span id="ratingRationale"></span></p>
      <p><b>Reversal trigger:</b> <span id="reversalTrigger"></span></p>
      <p class="muted" id="coverageScope"></p>
    </section>
    <section class="card wide">
      <h2>Public-data liquidity bridge</h2>
      <p class="muted">This static screen tests the tension between reported cash and identified obligations. It is not a borrowing-entity forecast.</p>
      <div class="grid">
        <div><table><thead><tr><th scope="col">Line item</th><th scope="col">Amount</th></tr></thead><tbody id="liquidityBridge"></tbody></table></div>
        <div class="metrics"><div class="metric"><span>Residual before potential holder put</span><b id="liquidityPrePut"></b></div><div class="metric"><span>Residual after potential holder put</span><b id="liquidityPostPut"></b></div></div>
      </div>
      <p class="muted" id="liquidityLimit"></p>
    </section>
    <section class="card wide">
      <h2>Rating bridge</h2>
      <p class="muted">Declared ordinal factors show exactly what supports the illustrative obligor assessment and what evidence could change it.</p>
      <div class="scenario-table">
        <table>
          <thead><tr><th scope="col">Factor</th><th scope="col">Weight</th><th scope="col">Score</th><th scope="col">Contribution</th><th scope="col">Evidence</th><th scope="col">What improves it</th><th scope="col">Deterioration trigger</th></tr></thead>
          <tbody id="ratingBridge"></tbody>
        </table>
      </div>
      <p class="muted" id="ratingMethodLimit"></p>
    </section>
    <section class="card wide" id="scenarioMatrixSection">
      <h2>Scenario comparison</h2>
      <p class="muted">All declared cases use the same decision definitions. Each row identifies the binding driver and evidence needed to resolve or mitigate it.</p>
      <div class="metrics"><div class="metric"><span>Declared scenarios</span><b id="attributionCount"></b></div><div class="metric"><span>Reduced-limit cases</span><b id="attributionReduced"></b></div><div class="metric"><span>Declines</span><b id="attributionDeclines"></b></div><div class="metric"><span>Hard-blocker cases</span><b id="attributionBlockers"></b></div></div>
      <div class="scenario-table">
        <table>
          <thead><tr><th scope="col">Scenario</th><th scope="col">Decision</th><th scope="col">Recommended</th><th scope="col">Delta vs. base</th><th scope="col">Available proceeds</th><th scope="col">Binding constraint</th><th scope="col">Primary driver</th><th scope="col">Resolution evidence</th></tr></thead>
          <tbody id="scenarioMatrix"></tbody>
        </table>
      </div>
      <p class="muted" id="attributionLimit"></p>
    </section>
    <section class="card wide">
      <h2>Diligence execution plan</h2>
      <p class="muted">Eight tasks can begin in parallel. The control agreement moves to wave two after ownership and lien verification.</p>
      <div class="metrics"><div class="metric"><span>Blocking tasks</span><b id="diligenceTasks"></b></div><div class="metric"><span>Critical tasks</span><b id="diligenceCritical"></b></div><div class="metric"><span>Parallel lanes</span><b id="diligenceLanes"></b></div><div class="metric"><span>Ready to start</span><b id="diligenceReady"></b></div><div class="metric"><span>Waiting on dependencies</span><b id="diligenceWaiting"></b></div></div>
      <div class="scenario-table condition-table"><table><thead><tr><th scope="col">Wave</th><th scope="col">Condition</th><th scope="col">Priority</th><th scope="col">Lane</th><th scope="col">Current action</th><th scope="col">Requirement</th><th scope="col">Owner</th><th scope="col">Depends on</th><th scope="col">Decision impact</th><th scope="col">Affected claims</th><th scope="col">Completion output</th><th scope="col">Failure consequence</th></tr></thead><tbody id="diligenceTable"></tbody></table></div>
      <p class="muted" id="diligenceLimit"></p>
    </section>
    <section class="card wide">
      <h2>Pre-funding condition register</h2>
      <p class="muted">A conditional recommendation is not authority to fund. Every item below remains outstanding in the current evidence set.</p>
      <div class="scenario-table condition-table">
        <table>
          <thead><tr><th scope="col">ID</th><th scope="col">Requirement</th><th scope="col">Owner</th><th scope="col">Status</th><th scope="col">Verification evidence</th></tr></thead>
          <tbody id="conditionRegister"></tbody>
        </table>
      </div>
    </section>
    <section class="card wide">
      <h2>Monitoring and early-warning design</h2>
      <p class="muted">This framework is not active borrower monitoring. The facility remains blocked before funding, and five measures require private reporting or testing.</p>
      <div class="scenario-table condition-table">
        <table>
          <thead><tr><th scope="col">ID</th><th scope="col">Metric</th><th scope="col">Threshold</th><th scope="col">Current evidence</th><th scope="col">Frequency</th><th scope="col">Owner</th><th scope="col">Breach action</th></tr></thead>
          <tbody id="monitoringPlan"></tbody>
        </table>
      </div>
      <p class="muted" id="monitoringLimit"></p>
    </section>
    <section class="card wide" id="controlMatrixSection">
      <h2>End-to-end control matrix</h2>
      <p class="muted">Each row connects pre-funding evidence to the post-close metric, draft covenant, and response authority. It is a governance design, not evidence that any control is active or enforceable.</p>
      <div class="metrics"><div class="metric"><span>Control chains</span><b id="controlMatrixCount"></b></div><div class="metric"><span>Conditions covered</span><b id="controlMatrixConditions"></b></div><div class="metric"><span>Critical controls</span><b id="controlMatrixCritical"></b></div><div class="metric"><span>Controls with outstanding conditions</span><b id="controlMatrixOutstanding"></b></div></div>
      <div class="scenario-table condition-table"><table><thead><tr><th scope="col">Control</th><th scope="col">Objective</th><th scope="col">Pre-funding conditions</th><th scope="col">Monitor / threshold</th><th scope="col">Covenant</th><th scope="col">Cure</th><th scope="col">Escalation</th><th scope="col">Trigger severity / clock</th><th scope="col">Draw state</th><th scope="col">Decision owner</th><th scope="col">Exit criteria</th></tr></thead><tbody id="controlMatrixTable"></tbody></table></div>
      <p class="muted" id="controlMatrixLimit"></p>
    </section>
    <section class="card wide">
      <h2>Illustrative covenant package</h2>
      <p class="muted">Each draft term maps to one monitoring rule and states the test, cure, and consequence. These terms are not executed or legally reviewed.</p>
      <div class="scenario-table condition-table">
        <table>
          <thead><tr><th scope="col">ID</th><th scope="col">Type</th><th scope="col">Requirement</th><th scope="col">Threshold</th><th scope="col">Current evidence</th><th scope="col">Cure period</th><th scope="col">Breach consequence</th><th scope="col">Monitor</th></tr></thead>
          <tbody id="covenantPlan"></tbody>
        </table>
      </div>
      <p class="muted" id="covenantLimit"></p>
    </section>
    <section class="card wide">
      <h2>Escalation and response playbook</h2>
      <p class="muted">These are illustrative response paths. No incident or borrower breach is currently observed.</p>
      <div class="scenario-table condition-table">
        <table>
          <thead><tr><th scope="col">ID</th><th scope="col">Severity</th><th scope="col">Response clock</th><th scope="col">Draw state</th><th scope="col">Current state</th><th scope="col">Decision owner</th><th scope="col">Required evidence</th><th scope="col">Exit criteria</th></tr></thead>
          <tbody id="escalationPlan"></tbody>
        </table>
      </div>
      <p class="muted" id="escalationLimit"></p>
    </section>
    <section class="card wide">
      <h2>Committee disagreement</h2>
      <p><b>Conditional approval:</b> approve $3.0m only after ownership, first priority, enforceable control, and the Base-to-cash route are evidenced.</p>
      <p><b>Opposing view:</b> decline until private repayment-capacity diligence exists; the binding collateral cap is generated by synthetic terms.</p>
      <p class="question">Would you challenge the primary-repayment analysis, the collateral-access blocker, or the portfolio cap first, and what evidence would change your answer?</p>
    </section>
    <section class="card wide" id="readinessSection">
      <h2>Review readiness and human gates</h2>
      <p class="muted">Local model verification is complete. Sharing readiness remains separate and cannot be cleared by rebuilding the package or generating a blank review form.</p>
      <div class="metrics"><div class="metric"><span>Local acceptance</span><b id="readinessLocal"></b></div><div class="metric"><span>Ready to share</span><b id="readinessShare" class="gate"></b></div><div class="metric"><span>Human gates passed</span><b id="readinessPassed"></b></div><div class="metric"><span>Human gates outstanding</span><b id="readinessOutstanding"></b></div></div>
      <div class="scenario-table condition-table"><table><thead><tr><th scope="col">Gate</th><th scope="col">Required review</th><th scope="col">Reviewer role</th><th scope="col">Status</th><th scope="col">Evidence required</th></tr></thead><tbody id="humanGateTable"></tbody></table></div>
      <p><a class="action-link" id="reviewerScorecardLink" href="reviewer-scorecard.pdf">Open blank reviewer scorecard</a></p>
      <p class="muted" id="readinessInterpretation"></p>
    </section>
    <section class="card wide">
      <h2>Decision lineage</h2>
      <p class="muted">Trace each committee headline to its evidence, rule, generated artifact, workbook cell, owner, and limitation.</p>
      <div class="metrics"><div class="metric"><span>Committee claims</span><b id="lineageNodes"></b></div><div class="metric"><span>Evidence links</span><b id="lineageLinks"></b></div><div class="metric"><span>Reported-supported claims</span><b id="lineageReported"></b></div><div class="metric"><span>Assumption-exposed claims</span><b id="lineageAssumed"></b></div></div>
      <div class="scenario-table condition-table">
        <table><thead><tr><th scope="col">ID</th><th scope="col">Committee claim</th><th scope="col">Current value</th><th scope="col">Evidence</th><th scope="col">Calculation or rule</th><th scope="col">Artifact</th><th scope="col">Workbook</th><th scope="col">Owner</th><th scope="col">Limitation</th></tr></thead><tbody id="lineageTable"></tbody></table>
      </div>
      <p class="muted" id="lineageLimit"></p>
    </section>
    <section class="card wide">
      <h2>Assumption governance</h2>
      <p class="muted">Every registered case assumption remains explicitly unvalidated until its named evidence and review method are complete.</p>
      <div class="metrics"><div class="metric"><span>Registered assumptions</span><b id="assumptionCount"></b></div><div class="metric"><span>Critical</span><b id="assumptionCritical"></b></div><div class="metric"><span>High</span><b id="assumptionHigh"></b></div><div class="metric"><span>Unvalidated</span><b id="assumptionUnvalidated"></b></div></div>
      <div class="scenario-table condition-table"><table><thead><tr><th scope="col">ID</th><th scope="col">Assumption</th><th scope="col">Class</th><th scope="col">Materiality</th><th scope="col">Status</th><th scope="col">Owner</th><th scope="col">Workbook inputs</th><th scope="col">Validation method</th><th scope="col">Challenge trigger</th><th scope="col">Affected claims</th></tr></thead><tbody id="assumptionTable"></tbody></table></div>
      <p class="muted" id="assumptionLimit"></p>
    </section>
    <section class="card wide" id="modelRiskSection">
      <h2>Model-risk register</h2>
      <p class="muted">Known limitations are tied to the decision they can distort, the evidence needed to close them, and the required disposition while they remain open.</p>
      <div class="metrics"><div class="metric"><span>Open risks</span><b id="modelRiskOpen"></b></div><div class="metric"><span>Critical</span><b id="modelRiskCritical"></b></div><div class="metric"><span>High</span><b id="modelRiskHigh"></b></div><div class="metric"><span>Decision-blocking</span><b id="modelRiskBlocking"></b></div></div>
      <div class="risk-filters" aria-label="Model-risk filters"><label for="modelRiskSeverity">Severity<select id="modelRiskSeverity"><option value="all">All severities</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option></select></label><label><input id="modelRiskBlockingOnly" type="checkbox"> Decision-blocking only</label><span id="modelRiskVisible" class="muted" role="status" aria-live="polite"></span></div>
      <div class="scenario-table condition-table"><table><thead><tr><th scope="col">ID</th><th scope="col">Category</th><th scope="col">Risk</th><th scope="col">Severity</th><th scope="col">Affected decision</th><th scope="col">Linked assumptions / conditions</th><th scope="col">Mitigation</th><th scope="col">Validation evidence</th><th scope="col">Owner</th><th scope="col">Residual</th><th scope="col">If unresolved</th></tr></thead><tbody id="modelRiskTable"></tbody></table></div>
      <p class="muted" id="modelRiskLimit"></p>
    </section>
  </div>
  <footer>Sources: MARA June 30, 2026 Form 10-Q (SRC-001) and 2025 Form 10-K (SRC-002). All case calculations are illustrative. Built from artifacts/scenario-results.json.</footer>
</main>
<script>
const scenarios=__SCENARIOS__;
const base=__BASE__;
const thresholds=__THRESHOLDS__;
const monitoring=__MONITORING__;
const liquidity=__LIQUIDITY__;
const covenants=__COVENANTS__;
const escalations=__ESCALATIONS__;
const whatIf=__WHAT_IF__;
const attribution=__ATTRIBUTION__;
const lineage=__LINEAGE__;
const diligence=__DILIGENCE__;
const assumptionRegister=__ASSUMPTIONS__;
const modelRisks=__MODEL_RISKS__;
const controlMatrix=__CONTROL_MATRIX__;
const reviewerScorecard=__REVIEWER_SCORECARD__;
const readiness=__READINESS__;
const collateralCalls=__COLLATERAL_CALLS__;
const labels={
 base:"Base: simulated conditions verified",
 collateral_down_30:"30% collateral price decline",
 collateral_down_50:"50% collateral price decline",
 stale_price:"Stale collateral price",
 zero_collateral:"Zero accessible collateral",
 route_delay_24h:"24-hour additional route delay",
 canonical_withdrawal_168h:"One-week canonical withdrawal",
 route_failure:"Repayment route unavailable",
 missing_ownership_evidence:"Missing ownership evidence",
 borrower_cash_stress:"Borrower cash stress",
 correlated_portfolio_stress:"Correlated borrower and portfolio stress"
};
const money=v=>new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(Number(v));
const signedMoney=v=>(Number(v)>0?"+":"")+money(v);
const decisionLabel=value=>value==="decline"?"Decline":value==="approve_reduced"?"Conditional approval":value.replaceAll("_"," ");
const select=document.querySelector("#scenario");
document.querySelector("#thresholdStress").textContent=(100*Number(thresholds.max_price_decline_for_target["3000000"])).toFixed(2)+"%";
document.querySelector("#thresholdQty").textContent=(Number(thresholds.required_collateral_quantity_for_target["3000000"])/1e6).toFixed(3)+"m USDC";
document.querySelector("#thresholdCap").textContent=money(thresholds.maximum_non_collateral_limit_usd)+" ("+thresholds.maximum_non_collateral_limit_name+")";
document.querySelector("#callExactStress").textContent=(100*Number(collateralCalls.exact_modeled_breach_price_stress_pct)).toFixed(2)+"%";
document.querySelector("#callFirstGridStress").textContent=(100*Number(collateralCalls.first_grid_call_stress_pct)).toFixed(0)+"%";
document.querySelector("#callRequiredProceeds").textContent=money(collateralCalls.required_proceeds_usd);
document.querySelector("#callExposure").textContent=money(collateralCalls.pro_forma_exposure_usd);
document.querySelector("#collateralCallTable").innerHTML=collateralCalls.rows.map(row=>`<tr><td>${(100*Number(row.price_stress_pct)).toFixed(0)}%</td><td>${money(row.available_proceeds_usd)}</td><td>${Number(row.coverage_ratio).toFixed(3)}×</td><td class="${row.status==="PASS"?"call-pass":"call-required"}">${row.status.replaceAll("_"," ")}</td><td class="${Number(row.covenant_headroom_usd)<0?"call-required":"call-pass"}">${money(row.covenant_headroom_usd)}</td><td>${Number(row.top_up_required_usdc).toLocaleString("en-US",{maximumFractionDigits:0})} USDC</td><td>${money(row.repayment_required_usd)}</td><td>${money(row.rounded_coverage_compliant_commitment_usd)}</td></tr>`).join("");
document.querySelector("#collateralCallLimit").textContent=collateralCalls.method_limit;
document.querySelector("#rating").textContent=base.illustrative_rating;
document.querySelector("#ratingScore").textContent=Number(base.rating_score).toFixed(2)+" / 5.00";
document.querySelector("#sourceCoverage").textContent=(100*Number(base.source_coverage_rate)).toFixed(0)+"%";
document.querySelector("#reviewStatus").textContent=base.review_status;
document.querySelector("#ratingRationale").textContent=base.rating_rationale;
document.querySelector("#reversalTrigger").textContent=base.reversal_trigger;
document.querySelector("#coverageScope").textContent=base.source_coverage_scope;
document.querySelector("#ratingBridge").innerHTML=base.rating_factors.map(row=>`<tr><td>${row.factor}</td><td>${(100*Number(row.weight)).toFixed(0)}%</td><td>${row.score}</td><td>${Number(row.weighted_contribution).toFixed(2)}</td><td>${row.evidence_ids.join(", ")}</td><td>${row.improvement_evidence}</td><td>${row.deterioration_trigger}</td></tr>`).join("");
document.querySelector("#ratingMethodLimit").textContent=base.rating_method_limit;
document.querySelector("#conditionRegister").innerHTML=base.condition_register.map(row=>`<tr><td>${row.condition_id}</td><td>${row.requirement}</td><td>${row.owner_role}</td><td>${row.evidence_status}</td><td>${row.verification_method}</td></tr>`).join("");
document.querySelector("#monitoringPlan").innerHTML=monitoring.rules.map(row=>`<tr><td>${row.monitor_id}</td><td>${row.metric}</td><td>${row.threshold}</td><td>${row.current_value} (${row.status.replaceAll("_"," ")})</td><td>${row.frequency}</td><td>${row.owner_role}</td><td>${row.breach_action}</td></tr>`).join("");
document.querySelector("#monitoringLimit").textContent=monitoring.method_limit;
document.querySelector("#controlMatrixCount").textContent=controlMatrix.summary.control_count;
document.querySelector("#controlMatrixConditions").textContent=controlMatrix.summary.condition_count;
document.querySelector("#controlMatrixCritical").textContent=controlMatrix.summary.critical_control_count;
document.querySelector("#controlMatrixOutstanding").textContent=controlMatrix.summary.outstanding_condition_control_count;
document.querySelector("#controlMatrixTable").innerHTML=controlMatrix.controls.map(row=>`<tr><td>${row.control_id}</td><td>${row.control_objective}</td><td>${row.condition_ids.join(", ")} (${row.condition_status})</td><td>${row.monitor_id}: ${row.metric}<br>${row.threshold}</td><td>${row.covenant_id} (${row.covenant_type})</td><td>${row.cure_period}</td><td>${row.playbook_id}</td><td>${row.severity_on_trigger}; ${row.response_sla}</td><td>${row.draw_state_on_trigger.replaceAll("_"," ")}</td><td>${row.decision_owner}</td><td>${row.exit_criteria}</td></tr>`).join("");
document.querySelector("#controlMatrixLimit").textContent=controlMatrix.method_limit;
document.querySelector("#readinessLocal").textContent=readiness.local_acceptance_verified?"10 of 10 verified":"NOT VERIFIED";
document.querySelector("#readinessShare").textContent=readiness.ready_to_share?"YES":"NO";
document.querySelector("#readinessPassed").textContent=reviewerScorecard.summary.passed_count+" of "+reviewerScorecard.summary.gate_count;
document.querySelector("#readinessOutstanding").textContent=reviewerScorecard.summary.outstanding_count;
const readinessById=new Map(readiness.human_gates.map(row=>[row.id,row]));
document.querySelector("#humanGateTable").innerHTML=reviewerScorecard.gates.map(row=>`<tr><td>${row.gate_id}</td><td>${row.name}</td><td>${row.reviewer_role}</td><td class="call-required">${readinessById.get(row.gate_id).status}</td><td>${row.required_evidence}</td></tr>`).join("");
document.querySelector("#readinessInterpretation").textContent=readiness.interpretation+" "+reviewerScorecard.method_limit;
document.querySelector("#covenantPlan").innerHTML=covenants.covenants.map(row=>`<tr><td>${row.covenant_id}</td><td>${row.covenant_type}</td><td>${row.requirement}</td><td>${row.threshold}</td><td>${row.current_value} (${row.status.replaceAll("_"," ")})</td><td>${row.cure_period}</td><td>${row.breach_consequence}</td><td>${row.monitor_id}</td></tr>`).join("");
document.querySelector("#covenantLimit").textContent=covenants.method_limit;
document.querySelector("#escalationPlan").innerHTML=escalations.playbooks.map(row=>`<tr><td>${row.playbook_id}</td><td>${row.severity_on_trigger}</td><td>${row.response_sla}</td><td>${row.draw_state_on_trigger.replaceAll("_"," ")}</td><td>${row.current_response.replaceAll("_"," ")}</td><td>${row.decision_owner}</td><td>${row.required_evidence}</td><td>${row.exit_criteria}</td></tr>`).join("");
document.querySelector("#escalationLimit").textContent=escalations.method_limit;
document.querySelector("#whatIfLimit").textContent=whatIf.method_limit;
const attributionById=new Map(attribution.rows.map(row=>[row.scenario_id,row]));
document.querySelector("#attributionCount").textContent=attribution.summary.scenario_count;
document.querySelector("#attributionReduced").textContent=attribution.summary.reduced_limit_count;
document.querySelector("#attributionDeclines").textContent=attribution.summary.decline_count;
document.querySelector("#attributionBlockers").textContent=attribution.summary.hard_blocker_scenario_count;
document.querySelector("#attributionLimit").textContent=attribution.method_limit;
document.querySelector("#lineageNodes").textContent=lineage.summary.node_count;
document.querySelector("#lineageLinks").textContent=lineage.summary.source_link_count;
document.querySelector("#lineageReported").textContent=lineage.summary.reported_supported_node_count;
document.querySelector("#lineageAssumed").textContent=lineage.summary.assumption_exposed_node_count;
const lineageMoneyTypes=new Set(["input","decision_cap","calculation","decision","sensitivity"]);
const lineageValue=row=>lineageMoneyTypes.has(row.claim_type)&&Number.isFinite(Number(row.current_value))?money(row.current_value):row.current_value.replaceAll("_"," ");
document.querySelector("#lineageTable").innerHTML=lineage.nodes.map(row=>`<tr><td>${row.node_id}</td><td>${row.committee_claim}</td><td>${lineageValue(row)}</td><td>${row.evidence_ids.join(", ")} (${row.evidence_classes.join(", ")})</td><td>${row.calculation_or_rule}</td><td><code>${row.artifact_locator}</code></td><td><code>${row.workbook_locator}</code></td><td>${row.owner_role}</td><td>${row.limitation}</td></tr>`).join("");
document.querySelector("#lineageLimit").textContent=lineage.method_limit;
const lineageNameById=new Map(lineage.nodes.map(row=>[row.node_id,row.committee_claim]));
document.querySelector("#diligenceTasks").textContent=diligence.summary.task_count;
document.querySelector("#diligenceCritical").textContent=diligence.summary.critical_count;
document.querySelector("#diligenceLanes").textContent=diligence.summary.parallel_lane_count;
document.querySelector("#diligenceReady").textContent=diligence.summary.ready_to_start_count;
document.querySelector("#diligenceWaiting").textContent=diligence.summary.dependency_blocked_count;
document.querySelector("#diligenceTable").innerHTML=diligence.tasks.map(row=>`<tr><td>${row.wave}</td><td>${row.condition_id}</td><td>${row.priority}</td><td>${row.parallel_lane.replaceAll("_"," ")}</td><td>${row.current_action.replaceAll("_"," ").replace(":",": ")}</td><td>${row.requirement}</td><td>${row.owner_role}</td><td>${row.depends_on.length?row.depends_on.join(", "):"None"}</td><td>${row.decision_impact.replaceAll("_"," ")}</td><td>${row.affected_lineage_nodes.map(id=>lineageNameById.get(id)).join(", ")}</td><td>${row.completion_output}</td><td>${row.failure_consequence}</td></tr>`).join("");
document.querySelector("#diligenceLimit").textContent=diligence.method_limit;
document.querySelector("#assumptionCount").textContent=assumptionRegister.summary.assumption_count;
document.querySelector("#assumptionCritical").textContent=assumptionRegister.summary.critical_count;
document.querySelector("#assumptionHigh").textContent=assumptionRegister.summary.high_count;
document.querySelector("#assumptionUnvalidated").textContent=assumptionRegister.summary.unvalidated_count;
document.querySelector("#assumptionTable").innerHTML=assumptionRegister.assumptions.map(row=>`<tr><td>${row.assumption_id}</td><td>${row.assumption}</td><td>${row.evidence_class}</td><td>${row.materiality}</td><td>${row.validation_status}</td><td>${row.owner_role}</td><td><code>${row.workbook_inputs}</code></td><td>${row.validation_method}</td><td>${row.challenge_trigger}</td><td>${row.downstream_lineage_nodes.map(id=>lineageNameById.get(id)).join(", ")}</td></tr>`).join("");
document.querySelector("#assumptionLimit").textContent=assumptionRegister.method_limit;
document.querySelector("#modelRiskOpen").textContent=modelRisks.summary.open_count;
document.querySelector("#modelRiskCritical").textContent=modelRisks.summary.critical_count;
document.querySelector("#modelRiskHigh").textContent=modelRisks.summary.high_count;
document.querySelector("#modelRiskBlocking").textContent=modelRisks.summary.decision_blocking_count;
const isDecisionBlockingRisk=row=>/(block|decline|do not fund)/i.test(row.disposition_if_unresolved);
function renderModelRisks(){
 const severity=document.querySelector("#modelRiskSeverity").value;
 const blockingOnly=document.querySelector("#modelRiskBlockingOnly").checked;
 const rows=modelRisks.risks.filter(row=>(severity==="all"||row.severity===severity)&&(!blockingOnly||isDecisionBlockingRisk(row)));
 document.querySelector("#modelRiskTable").innerHTML=rows.map(row=>`<tr><td>${row.risk_id}</td><td>${row.category.replaceAll("_"," ")}</td><td>${row.risk}</td><td class="${row.severity==="critical"?"call-required":""}">${row.severity}</td><td>${row.affected_decision}</td><td>${row.linked_assumptions.join(", ")||"None"}<br>${row.linked_conditions.join(", ")||"None"}</td><td>${row.mitigation}</td><td>${row.validation_evidence}</td><td>${row.owner}</td><td>${row.residual_risk}</td><td>${row.disposition_if_unresolved}</td></tr>`).join("");
 document.querySelector("#modelRiskVisible").textContent=`Showing ${rows.length} of ${modelRisks.risks.length} risks`;
}
renderModelRisks();
document.querySelector("#modelRiskLimit").textContent=modelRisks.method_limit;
document.querySelector("#liquidityBridge").innerHTML=liquidity.rows.map(row=>`<tr><td>${row.line_item}</td><td>${money(row.amount_usd)}</td></tr>`).join("");
document.querySelector("#liquidityPrePut").textContent=money(liquidity.residual_before_potential_put_usd);
document.querySelector("#liquidityPostPut").textContent=money(liquidity.residual_after_potential_put_usd);
document.querySelector("#liquidityLimit").textContent=liquidity.method_limit;
function renderSensitivity(){
 const surface=thresholds.decision_surface;
 const cells=new Map(surface.cells.map(row=>[row.collateral_quantity_usdc+"|"+row.price_stress_pct,row]));
 document.querySelector("#sensitivityHead").innerHTML=`<tr><th scope="col">USDC quantity</th>${surface.price_stress_axis_pct.map(stress=>`<th scope="col">${(100*Number(stress)).toFixed(0)}%</th>`).join("")}</tr>`;
 document.querySelector("#sensitivityBody").innerHTML=surface.quantity_axis_usdc.map(quantity=>`<tr><th scope="row">${(Number(quantity)/1e6).toFixed(1)}m</th>${surface.price_stress_axis_pct.map(stress=>{const row=cells.get(quantity+"|"+stress);const amount=Number(row.recommended_amount_usd);const shade=amount>=4000000?"#d9ead3":amount>=3000000?"#fff2cc":amount>=2000000?"#fce5cd":"#f4cccc";return `<td style="background:${shade}">${money(amount)}</td>`}).join("")}</tr>`).join("");
}
const labFields={quantity_usdc:"labQuantity",price_stress_pct:"labStress",additional_route_delay_hours:"labDelay",execution_cost_bps:"labExecution"};
const controlFields={ownership:"labOwnership",first_priority:"labPriority",legal_control:"labControl",route_available:"labRoute"};
function labInputs(){return {quantity_usdc:document.querySelector("#labQuantity").value,price_stress_pct:document.querySelector("#labStress").value,additional_route_delay_hours:document.querySelector("#labDelay").value,execution_cost_bps:document.querySelector("#labExecution").value,controls:Object.fromEntries(Object.entries(controlFields).map(([key,id])=>[key,document.querySelector("#"+id).checked]))}}
function evaluateWhatIf(inputs){
 const blockers=Object.entries(inputs.controls).filter(([,verified])=>!verified).map(([name])=>name).sort();
 const quantity=Number(inputs.quantity_usdc),stress=Number(inputs.price_stress_pct),delay=Number(inputs.additional_route_delay_hours)+Number(whatIf.base_route_delay_hours),executionBps=Number(inputs.execution_cost_bps);
 const gross=quantity*Number(whatIf.quoted_price_usd)*Math.max(0,1-stress);
 const executionCost=gross*executionBps/10000,delayCost=gross*delay*Number(whatIf.delay_cost_bps_per_hour)/10000;
 const available=blockers.length?0:Math.max(0,gross-executionCost-delayCost-Number(whatIf.fixed_cost_usd));
 const caps={obligor:Number(whatIf.obligor_cap_usd),collateral:available/Number(whatIf.required_coverage_ratio),single_name:Number(whatIf.single_name_cap_usd),concentration:Number(whatIf.concentration_cap_usd)};
 const binding=blockers.length?"hard_blocker":Object.entries(caps).sort((a,b)=>a[1]-b[1]||a[0].localeCompare(b[0]))[0][0];
 const raw=blockers.length?0:Math.min(Number(whatIf.requested_commitment_usd),...Object.values(caps));
 const increment=Number(whatIf.recommendation_increment_usd),recommended=raw===0?0:Math.floor((raw+1e-7)/increment)*increment;
 const proForma=recommended>0?recommended+Number(whatIf.accrued_amount_usd):0;
 return {available_proceeds_usd:available,collateral_cap_usd:caps.collateral,recommended_amount_usd:recommended,recommended_pro_forma_exposure_usd:proForma,coverage_surplus_usd:Math.max(0,available-proForma),binding_cap:binding,hard_blockers:blockers,decision:blockers.length||recommended===0?"decline":recommended>=Number(whatIf.requested_commitment_usd)?"approve":"approve_reduced"};
}
function renderLab(){
 const inputs=labInputs(),result=evaluateWhatIf(inputs);
 document.querySelector("#labQuantityValue").textContent=(Number(inputs.quantity_usdc)/1e6).toFixed(1)+"m";
 document.querySelector("#labStressValue").textContent=(100*Number(inputs.price_stress_pct)).toFixed(0)+"%";
 document.querySelector("#labDelayValue").textContent=inputs.additional_route_delay_hours+" hours";
 document.querySelector("#labExecutionValue").textContent=inputs.execution_cost_bps+" bps";
 document.querySelector("#labRecommendation").textContent=money(result.recommended_amount_usd);document.querySelector("#labProceeds").textContent=money(result.available_proceeds_usd);document.querySelector("#labCollateralCap").textContent=money(result.collateral_cap_usd);document.querySelector("#labBinding").textContent=result.binding_cap.replaceAll("_"," ");document.querySelector("#labProForma").textContent=money(result.recommended_pro_forma_exposure_usd);document.querySelector("#labSurplus").textContent=money(result.coverage_surplus_usd);
 document.querySelector("#labDecision").textContent=result.decision==="decline"?"Decline under these simulated inputs.":"Conditional recommendation under these simulated inputs; the funding gate remains separate.";
 document.querySelector("#labBlockers").textContent=result.hard_blockers.length?"Hard blockers: "+result.hard_blockers.join(", "):"No simulated hard blocker.";
 document.querySelector("#labResult").classList.toggle("decline",result.decision==="decline");
}
function resetLab(){
 for(const [key,id] of Object.entries(labFields)){const input=document.querySelector("#"+id),bounds=whatIf.bounds[key];input.min=bounds.minimum;input.max=bounds.maximum;input.step=bounds.step;input.value=whatIf.defaults[key]}
 for(const [key,id] of Object.entries(controlFields))document.querySelector("#"+id).checked=whatIf.defaults.controls[key];
 renderLab();
}
function verifyWhatIfContract(){
 const moneyFields=["available_proceeds_usd","collateral_cap_usd","recommended_amount_usd","recommended_pro_forma_exposure_usd","coverage_surplus_usd"];
 const failures=[];for(const vector of whatIf.test_vectors){const actual=evaluateWhatIf(vector.inputs),expected=vector.expected;if(moneyFields.some(key=>Math.abs(actual[key]-Number(expected[key]))>.011)||actual.binding_cap!==expected.binding_cap||actual.decision!==expected.decision||actual.hard_blockers.join("|")!==expected.hard_blockers.join("|"))failures.push(vector.vector_id)}
 if(failures.length)throw new Error("What-if contract mismatch: "+failures.join(", "));document.querySelector("#labContractStatus").textContent="4 engine-derived boundary cases reconciled.";
}
for(const row of scenarios){const o=document.createElement("option");o.value=row.scenario_id;o.textContent=labels[row.scenario_id]||row.scenario_id;select.appendChild(o)}
function render(id){
 const r=scenarios.find(x=>x.scenario_id===id);
 if(!r)return;
 const approve=r.decision!=="decline";
 document.querySelector("#amount").textContent=money(r.recommended_amount_usd);
 document.querySelector("#decisionText").textContent=approve?"Conditional limit; simulated conditions precedent must be evidenced":"Decline under this scenario";
 const status=document.querySelector("#status");status.textContent=approve?"Conditional approval":"Decline";status.className="status"+(approve?"":" decline");
 document.querySelector("#proceeds").textContent=money(r.available_proceeds_usd);
 document.querySelector("#exposure").textContent=money(r.exposure_usd);
 document.querySelector("#shortfall").textContent=money(r.shortfall_usd);
 document.querySelector("#proFormaExposure").textContent=money(r.recommended_pro_forma_exposure_usd);
 document.querySelector("#proFormaSurplus").textContent=money(r.recommended_pro_forma_coverage_surplus_usd);
 document.querySelector("#exposureBasis").textContent="Recovery exposure basis: "+r.exposure_basis+".";
 document.querySelector("#fundingGate").textContent=r.funding_gate_status.replaceAll("_"," ");
 document.querySelector("#binding").textContent=r.binding_cap.replaceAll("_"," ");
 document.querySelector("#blockers").textContent=r.hard_blockers.length?"Blocker: "+r.hard_blockers.join(", "):"No simulated hard blocker in this scenario";
 const caps=r.caps_usd,max=Math.max(...Object.values(caps).map(Number));
 document.querySelector("#bars").setAttribute("aria-label","Four-cap comparison. "+Object.entries(caps).map(([k,v])=>k.replaceAll("_"," ")+" "+money(v)+(k===r.binding_cap?", binding":"")).join("; "));
 document.querySelector("#bars").innerHTML=Object.entries(caps).map(([k,v])=>`<div class="bar-row"><span>${k.replaceAll("_"," ")}</span><div class="track"><div class="bar ${k===r.binding_cap?"binding":""}" style="width:${100*Number(v)/max}%"></div></div><b>${money(v)}</b></div>`).join("");
 const lot=r.collateral_lots[0];
 const rows=[["Gross stressed value",lot.stressed_gross_value_usd],["Execution cost",-Number(lot.execution_cost_usd)],["Delay cost",-Number(lot.delay_cost_usd)],["Fixed cost",-Number(lot.fixed_cost_usd)],["Eligible proceeds",Number(r.available_proceeds_usd)],["Requested-draw recovery shortfall",Number(r.shortfall_usd)],["Recommended-limit coverage surplus",Number(r.recommended_pro_forma_coverage_surplus_usd)]];
 document.querySelector("#waterfall").innerHTML=rows.map(([k,v])=>`<tr><td>${k}</td><td>${money(v)}</td></tr>`).join("");
 document.querySelectorAll("#scenarioMatrix tr").forEach(row=>row.classList.toggle("active",row.dataset.scenario===id));
 try { const url=new URL(window.location.href);url.searchParams.set("scenario",id);history.replaceState(null,"",url); } catch(error) { /* Static file viewers may disallow URL mutation. */ }
}
function renderScenarioMatrix(){
 const baseAmount=Number(base.recommended_amount_usd);
 document.querySelector("#scenarioMatrix").innerHTML=scenarios.map(row=>{
 const delta=Number(row.recommended_amount_usd)-baseAmount;
  const driver=row.hard_blockers.length?row.hard_blockers.join(", "):row.binding_cap.replaceAll("_"," ");
  const why=attributionById.get(row.scenario_id);
  return `<tr data-scenario="${row.scenario_id}"><td><button type="button" data-select-scenario="${row.scenario_id}">${labels[row.scenario_id]||row.scenario_id}</button></td><td>${decisionLabel(row.decision)}</td><td>${money(row.recommended_amount_usd)}</td><td class="${delta<0?"delta-down":"delta-flat"}">${signedMoney(delta)}</td><td>${money(row.available_proceeds_usd)}</td><td>${driver}</td><td>${why.primary_driver.replaceAll("_"," ")}</td><td>${why.resolution_evidence}</td></tr>`;
 }).join("");
 document.querySelectorAll("[data-select-scenario]").forEach(button=>button.addEventListener("click",()=>{select.value=button.dataset.selectScenario;render(button.dataset.selectScenario);document.querySelector("#main-content").focus()}));
}
function summary(){
 const r=scenarios.find(x=>x.scenario_id===select.value);
 return [`MARA-CR-001 — ${labels[r.scenario_id]||r.scenario_id}`,`Decision: ${r.decision}; recommended ${money(r.recommended_amount_usd)}`,`Binding constraint: ${r.binding_cap.replaceAll("_"," ")}`,`Available proceeds: ${money(r.available_proceeds_usd)}`,`Requested-draw recovery shortfall: ${money(r.shortfall_usd)}`,`Recommended pro forma exposure: ${money(r.recommended_pro_forma_exposure_usd)}; coverage surplus ${money(r.recommended_pro_forma_coverage_surplus_usd)}`,`Hard blockers: ${r.hard_blockers.length?r.hard_blockers.join(", "):"none in simulated case"}`,`Review status: ${r.review_status}`].join("\n");
}
async function copySummary(){
 const status=document.querySelector("#actionStatus");
 try { await navigator.clipboard.writeText(summary()); status.textContent="Scenario summary copied."; }
 catch(error){ const area=document.createElement("textarea");area.value=summary();area.className="sr-only";document.body.appendChild(area);area.select();document.execCommand("copy");area.remove();status.textContent="Scenario summary copied."; }
}
function downloadScenario(){
 const row=scenarios.find(item=>item.scenario_id===select.value);
 const blob=new Blob([JSON.stringify(row,null,2)+"\n"],{type:"application/json"});
 const link=document.createElement("a");link.href=URL.createObjectURL(blob);link.download=`MARA-CR-001-${row.scenario_id}.json`;document.body.appendChild(link);link.click();link.remove();URL.revokeObjectURL(link.href);
 document.querySelector("#actionStatus").textContent=`${labels[row.scenario_id]||row.scenario_id} JSON downloaded.`;
}
select.addEventListener("change",e=>render(e.target.value));
document.querySelector("#copySummary").addEventListener("click",copySummary);
document.querySelector("#downloadScenario").addEventListener("click",downloadScenario);
document.querySelector("#printView").addEventListener("click",()=>window.print());
document.querySelector("#resetScenario").addEventListener("click",()=>{select.value="base";render("base");document.querySelector("#actionStatus").textContent="Base scenario restored.";select.focus()});
for(const id of [...Object.values(labFields),...Object.values(controlFields)])document.querySelector("#"+id).addEventListener("input",renderLab);
document.querySelector("#resetLab").addEventListener("click",resetLab);
document.querySelector("#modelRiskSeverity").addEventListener("change",renderModelRisks);
document.querySelector("#modelRiskBlockingOnly").addEventListener("change",renderModelRisks);
const requested=new URL(window.location.href).searchParams.get("scenario");
const initial=scenarios.some(row=>row.scenario_id===requested)?requested:"base";renderSensitivity();renderScenarioMatrix();resetLab();verifyWhatIfContract();select.value=initial;render(initial);
</script>
</body></html>"""

output = template.replace("__SCENARIOS__", js(SCENARIOS)).replace("__BASE__", js(BASE)).replace("__THRESHOLDS__", js(THRESHOLDS)).replace("__MONITORING__", js(MONITORING)).replace("__LIQUIDITY__", js(LIQUIDITY)).replace("__COVENANTS__", js(COVENANTS)).replace("__ESCALATIONS__", js(ESCALATIONS)).replace("__WHAT_IF__", js(WHAT_IF)).replace("__ATTRIBUTION__", js(ATTRIBUTION)).replace("__LINEAGE__", js(LINEAGE)).replace("__DILIGENCE__", js(DILIGENCE)).replace("__ASSUMPTIONS__", js(ASSUMPTIONS)).replace("__MODEL_RISKS__", js(MODEL_RISKS)).replace("__CONTROL_MATRIX__", js(CONTROL_MATRIX)).replace("__REVIEWER_SCORECARD__", js(REVIEWER_SCORECARD)).replace("__READINESS__", js(READINESS)).replace("__COLLATERAL_CALLS__", js(COLLATERAL_CALLS))
(ROOT / "outputs/decision-view.html").write_text(output, encoding="utf-8")
print(ROOT / "outputs/decision-view.html")
