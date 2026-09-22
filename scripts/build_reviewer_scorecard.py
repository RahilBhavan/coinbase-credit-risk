#!/usr/bin/env python3
"""Build a printable, auditable scorecard for the three outstanding human gates."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from reviewer_evidence import gate_passes, load as load_reviewer_evidence, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "case" / "reviewer_gates.json"
JSON_OUT = ROOT / "artifacts" / "reviewer-scorecard.json"
CSV_OUT = ROOT / "artifacts" / "reviewer-scorecard.csv"
MD_OUT = ROOT / "artifacts" / "reviewer-scorecard.md"
PDF_OUT = ROOT / "outputs" / "reviewer-scorecard.pdf"
AUDIT_OUT = ROOT / "artifacts" / "reviewer-scorecard-audit.json"
NAVY, BLUE, MUTED, LINE, AMBER = (colors.HexColor(value) for value in ("#16324F", "#2F75B5", "#64707D", "#D8E0E8", "#FFF2CC"))


def build(ledger: dict[str, object] = None, evidence_root: Path = ROOT) -> dict[str, object]:
    config = json.loads(CONFIG.read_text())
    configured_gates = config["gates"]
    gates = [dict(row) for row in configured_gates]
    ids = [row["gate_id"] for row in gates]
    if ids != ["HG-01", "HG-02", "HG-03"]:
        raise ValueError("reviewer gates must be the three ordered readiness gates")
    if any(row["current_status"] != "OUTSTANDING" for row in configured_gates):
        raise ValueError("gate configuration must not pre-declare a human gate passed")
    ledger = load_reviewer_evidence() if ledger is None else ledger
    ledger_errors = validate_ledger(ledger, evidence_root)
    if ledger_errors:
        raise ValueError("Invalid reviewer evidence ledger: " + "; ".join(ledger_errors))
    records = {row["gate_id"]: row for row in ledger["records"]}
    for gate in gates:
        record = records[gate["gate_id"]]
        gate["current_status"] = "PASS" if gate_passes(record, evidence_root) else "OUTSTANDING"
        gate["review_outcome"] = record["outcome"]
        gate["reviewed_on"] = record.get("reviewed_on", "")
        gate["reviewer_role_recorded"] = record.get("reviewer_role", "")
        gate["evidence_paths"] = record.get("evidence_paths", [])
    passed_count = sum(row["current_status"] == "PASS" for row in gates)
    return {
        "schema_version": "1.0", "case_id": "MARA-CR-001", "evidence_class": config["evidence_class"],
        "summary": {"gate_count": len(gates), "passed_count": passed_count, "outstanding_count": len(gates) - passed_count},
        "gates": gates, "method_limit": config["method_limit"],
    }


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    lines = ["# Independent reviewer gate scorecard", "", f"**Status:** {summary['outstanding_count']} outstanding / {summary['passed_count']} passed", "", payload["method_limit"], ""]
    for gate in payload["gates"]:
        lines.extend([
            f"## {gate['gate_id']} - {gate['name']}", "", f"**Governed status:** {gate['current_status']} ({gate['review_outcome']})", "", f"**Reviewer role:** {gate['reviewer_role']}", "",
            f"**Objective:** {gate['objective']}", "", "### Questions", "",
            *[f"- {item}" for item in gate["review_questions"]], "", "### Pass criteria", "",
            *[f"- [ ] {item}" for item in gate["pass_criteria"]], "",
            "**Reviewer name or identifier:** ____________________", "", "**Review date:** ____________________", "",
            "**Conclusion (PASS / FAIL / NEEDS WORK):** ____________________", "", "**Evidence or notes:**", "", "", "",
        ])
    return "\n".join(lines)


def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(LINE); canvas.line(0.55 * inch, 0.47 * inch, 7.95 * inch, 0.47 * inch)
    canvas.setFont("Helvetica", 7); canvas.setFillColor(MUTED)
    canvas.drawString(0.55 * inch, 0.30 * inch, "MARA-CR-001 | Governed evidence status and execution worksheet")
    canvas.drawRightString(7.95 * inch, 0.30 * inch, f"Page {doc.page}"); canvas.restoreState()


def render_pdf(payload: dict[str, object]) -> None:
    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, spaceAfter=5)
    subtitle = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=10)
    heading = ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=NAVY, spaceBefore=7, spaceAfter=4)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=8.4, leading=11, textColor=colors.HexColor("#1F1F1F"), spaceAfter=4)
    small = ParagraphStyle("small", parent=body, fontSize=7.4, leading=9.4, textColor=MUTED)
    doc = SimpleDocTemplate(str(PDF_OUT), pagesize=letter, leftMargin=0.58 * inch, rightMargin=0.58 * inch, topMargin=0.5 * inch, bottomMargin=0.62 * inch, title="MARA-CR-001 independent reviewer scorecard", author="Credit Risk project")
    summary = payload["summary"]
    ready = summary["passed_count"] == summary["gate_count"]
    story = [Paragraph("Independent reviewer gate scorecard", title), Paragraph("MARA-CR-001 | Governed evidence status and execution worksheets", subtitle)]
    status = Table([["Current state", "Local acceptance", "Human gates", "Ready to share"], ["Ledger synchronized", "10 of 10 verified", f"{summary['passed_count']} of {summary['gate_count']} passed", "YES" if ready else "NO"]], colWidths=[1.8 * inch] * 4)
    status.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"), ("TEXTCOLOR", (0, 1), (-1, 1), BLUE), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.extend([status, Spacer(1, 9), Paragraph(payload["method_limit"], body), Paragraph("Instructions", heading), Paragraph("Assign each page to a reviewer who meets the stated role. The reviewer completes the questions, records evidence, marks each criterion, and signs or identifies themselves. Record the governed result with scripts/record_reviewer_gate.py and transfer the response into artifacts/feedback-log.md. Rebuilding this scorecard never changes reviewer evidence or readiness status.", body), PageBreak()])
    for index, gate in enumerate(payload["gates"]):
        story.extend([Paragraph(f"{gate['gate_id']} - {gate['name']}", title), Paragraph(f"Reviewer role: {gate['reviewer_role']}", subtitle), Paragraph("Objective", heading), Paragraph(gate["objective"], body)])
        inputs = [["Required review inputs"]] + [[item] for item in gate["required_inputs"]]
        input_table = Table([[Paragraph(str(cell), body) for cell in row] for row in inputs], colWidths=[7.25 * inch])
        input_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.extend([input_table, Paragraph("Review questions", heading)])
        for number, question in enumerate(gate["review_questions"], 1):
            story.extend([Paragraph(f"<b>{number}.</b> {question}", body), Paragraph("Response: __________________________________________________________________________________", small), Spacer(1, 3)])
        story.append(Paragraph("Pass criteria", heading))
        criteria = [["Result", "Criterion"]] + [["[  ] Pass   [  ] Fail", item] for item in gate["pass_criteria"]]
        criteria_table = Table([[Paragraph(str(cell), small) for cell in row] for row in criteria], colWidths=[1.35 * inch, 5.9 * inch])
        criteria_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.extend([criteria_table, Paragraph("Required retained evidence", heading), Paragraph(gate["required_evidence"], body), Paragraph("Reviewer record", heading)])
        record = [["Reviewer name / identifier", ""], ["Reviewer role", ""], ["Review date", ""], ["Attribution permission", "[  ] Yes   [  ] No   [  ] Role only"], ["Conclusion", "[  ] PASS   [  ] FAIL   [  ] NEEDS WORK"], ["Evidence location", ""], ["Required follow-up", ""]]
        record_table = Table([[Paragraph(str(cell), small) for cell in row] for row in record], colWidths=[1.65 * inch, 5.6 * inch], rowHeights=[0.31 * inch] * len(record))
        record_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), AMBER), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
        story.append(record_table)
        if index < len(payload["gates"]) - 1: story.append(PageBreak())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    payload = build()
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    MD_OUT.write_text(render_markdown(payload) + "\n")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        fields = ["gate_id", "name", "reviewer_role", "objective", "required_inputs", "review_questions", "pass_criteria", "required_evidence", "current_status", "review_outcome", "reviewed_on", "reviewer_role_recorded", "evidence_paths"]
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for gate in payload["gates"]: writer.writerow({**gate, "required_inputs": " | ".join(gate["required_inputs"]), "review_questions": " | ".join(gate["review_questions"]), "pass_criteria": " | ".join(gate["pass_criteria"]), "evidence_paths": " | ".join(gate["evidence_paths"])})
    render_pdf(payload)
    reader = PdfReader(PDF_OUT); text = " ".join("\n".join(page.extract_text() or "" for page in reader.pages).split())
    summary = payload["summary"]
    required = ["Independent reviewer gate scorecard", "HG-01", "HG-02", "HG-03", f"{summary['passed_count']} of {summary['gate_count']} passed", "Ledger synchronized", "Rebuilding this scorecard never changes reviewer evidence or readiness status"]
    if len(reader.pages) != 4 or any(token not in text for token in required):
        raise RuntimeError("reviewer scorecard PDF verification failed")
    AUDIT_OUT.write_text(json.dumps({"schema_version": "1.0", "artifact": "outputs/reviewer-scorecard.pdf", "sha256": hashlib.sha256(PDF_OUT.read_bytes()).hexdigest(), "page_count": 4, "passed_count": summary["passed_count"], "outstanding_count": summary["outstanding_count"], "required_text": required, "failure_count": 0}, indent=2, sort_keys=True) + "\n")
    print(f"Reviewer scorecard: {summary['passed_count']} passed, {summary['outstanding_count']} outstanding -> outputs/reviewer-scorecard.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
