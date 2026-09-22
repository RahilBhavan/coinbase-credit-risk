#!/usr/bin/env python3
"""Assemble an indexed credit-committee packet from the verified PDFs."""

from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "committee-packet.pdf"
NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#2F75B5")
MUTED = colors.HexColor("#64707D")
LINE = colors.HexColor("#D8E0E8")
AMBER = colors.HexColor("#FFF2CC")
PALE_RED = colors.HexColor("#FCE4D6")
AUDIT = ROOT / "artifacts" / "committee-packet-audit.json"


def cover_pdf() -> bytes:
    thresholds = json.loads((ROOT / "artifacts" / "threshold-analysis.json").read_text(encoding="utf-8"))
    monitoring = json.loads((ROOT / "artifacts" / "monitoring-plan.json").read_text(encoding="utf-8"))
    liquidity = json.loads((ROOT / "artifacts" / "liquidity-analysis.json").read_text(encoding="utf-8"))
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.62 * inch,
        rightMargin=0.62 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="MARA-CR-001 credit committee packet",
        author="Credit Risk project",
    )
    title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20, leading=23, textColor=NAVY, spaceAfter=5)
    subtitle = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=9, leading=12, textColor=MUTED, spaceAfter=15)
    heading = ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#1F1F1F"), spaceAfter=5)
    small = ParagraphStyle("small", parent=body, fontSize=7.7, leading=10, textColor=MUTED)
    story = [
        Paragraph("MARA-CR-001", title),
        Paragraph("Hypothetical credit committee packet | September 20, 2026", subtitle),
    ]
    decision = Table(
        [
            [Paragraph("Recommendation", heading), Paragraph("$3.0 million conditional limit", ParagraphStyle("decision", parent=heading, fontSize=15, textColor=BLUE))],
            [Paragraph("Requested", body), Paragraph("$5.0 million / 12 months", body)],
            [Paragraph("Binding constraint", body), Paragraph("Collateral cap: $3,096,480 before rounding", body)],
            [Paragraph("Exposure views", body), Paragraph("Full-request recovery: $5.05m exposure / $1.1794m shortfall. Recommended limit: $3.05m pro forma exposure / $0.8206m coverage surplus.", body)],
            [Paragraph("Hard-stop rule", body), Paragraph("Decline if ownership, priority, enforceable control, price freshness, or the repayment route is unavailable.", body)],
            [Paragraph("Monitoring state", body), Paragraph(f"{monitoring['summary']['pass_projection_count']} projected passes; {monitoring['summary']['pre_funding_blocked_count']} pre-funding blocker; {monitoring['summary']['not_measured_count']} private-evidence measures not measured", body)],
            [Paragraph("Liquidity screen", body), Paragraph(f"${float(liquidity['residual_before_potential_put_usd']) / 1_000_000:.2f}m before and negative ${abs(float(liquidity['residual_after_potential_put_usd'])) / 1_000_000:.2f}m after the potential holder put; not a forecast", body)],
        ],
        colWidths=[1.65 * inch, 5.05 * inch],
    )
    decision.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
        ("INNERGRID", (0, 1), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([decision, Spacer(1, 10), Paragraph("Committee framing", heading)])
    callout = Table([[Paragraph(
        "The approval case and the decline case are both included. Public issuer facts establish scale and reported liquidity; they do not establish private repayment capacity or control of the fictional collateral.", body
    )]], colWidths=[6.7 * inch])
    callout.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D6B656")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([callout, Paragraph("Packet contents", heading)])
    contents = [
        ["Section", "Purpose", "Starts"],
        ["Credit memorandum", "Conditional approval case, structure, risks, conditions, and reversal evidence", "Page 2"],
        ["Downside and cure ladder", "Coverage breach point, collateral top-up, repayment, and commitment step-down", "Page 4"],
        ["Model-risk posture", "Known limitations, mitigations, evidence requirements, and unresolved dispositions", "Page 5"],
        ["Opposing memorandum", "Strongest defensible case for declining on the present record", "Page 6"],
        ["Reviewer brief", "Three-minute orientation and targeted practitioner questions", "Page 7"],
    ]
    table = Table(contents, colWidths=[1.35 * inch, 4.55 * inch, 0.8 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    threshold_rows = [
        ["Threshold", "Result", "Meaning"],
        ["Preserve $3.0m limit", f"{100 * float(thresholds['max_price_decline_for_target']['3000000']):.2f}% max decline", "Beyond this, the collateral cap rounds below $3.0m"],
        ["Support $3.0m limit", f"{float(thresholds['required_collateral_quantity_for_target']['3000000']) / 1_000_000:.3f}m USDC", "Minimum quantity under base cost and coverage assumptions"],
        ["Non-collateral ceiling", "$4.0m", "Current concentration cap prevents the full $5.0m request"],
    ]
    threshold_table = Table(threshold_rows, colWidths=[1.65 * inch, 1.45 * inch, 3.6 * inch], repeatRows=1)
    threshold_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.7), ("LEADING", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Paragraph("Decision thresholds", heading), threshold_table, Paragraph("Evidence boundary", heading), Paragraph(
        "MARA is not represented as a Coinbase customer. The facility, collateral, Base route, covenants, portfolio, limits, and internal grade are fictional. The package contains hash-frozen public sources, machine-reconciled filing facts, an audited workbook, eleven illustrative scenarios, and a separately stated opposing view. It is not legal advice or a real credit approval.", body
    ), Paragraph(
        "Review control: use artifacts/validation-report.md for executed checks and artifacts/package-integrity.json for file verification. The monitoring plan is inactive; private diligence, legal enforceability, and independent practitioner review remain outstanding.", small
    )])
    doc.build(story)
    return buffer.getvalue()


def cure_pdf() -> bytes:
    ladder = json.loads((ROOT / "artifacts" / "collateral-call-ladder.json").read_text(encoding="utf-8"))
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.48 * inch, bottomMargin=0.5 * inch,
        title="MARA-CR-001 downside and cure ladder", author="Credit Risk project",
    )
    title = ParagraphStyle("cure-title", fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, spaceAfter=4)
    subtitle = ParagraphStyle("cure-subtitle", fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=10)
    heading = ParagraphStyle("cure-heading", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=NAVY, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("cure-body", fontName="Helvetica", fontSize=8.3, leading=10.5, textColor=colors.HexColor("#1F1F1F"), spaceAfter=4)
    small = ParagraphStyle("cure-small", parent=body, fontSize=7.2, leading=9, textColor=MUTED)
    metric = Table([
        ["Recommended commitment", "Exposure incl. accrued", "Required proceeds", "Exact modeled breach"],
        [f"${float(ladder['recommended_commitment_usd']) / 1_000_000:.2f}m", f"${float(ladder['pro_forma_exposure_usd']) / 1_000_000:.2f}m", f"${float(ladder['required_proceeds_usd']) / 1_000_000:.4f}m", f"{100 * float(ladder['exact_modeled_breach_price_stress_pct']):.2f}%"],
    ], colWidths=[1.85 * inch] * 4)
    metric.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7.2), ("FONTSIZE", (0, 1), (-1, 1), 12),
        ("TEXTCOLOR", (0, 1), (-1, 1), BLUE), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    rows = [["Stress", "Proceeds", "Coverage", "State", "Headroom", "Top-up", "Repayment", "Rounded limit"]]
    for row in ladder["rows"]:
        rows.append([
            f"{100 * float(row['price_stress_pct']):.0f}%",
            f"${float(row['available_proceeds_usd']) / 1_000_000:.3f}m",
            f"{float(row['coverage_ratio']):.3f}x",
            row["status"].replace("_", " "),
            f"${float(row['covenant_headroom_usd']) / 1_000:.1f}k",
            f"{float(row['top_up_required_usdc']) / 1_000:.1f}k USDC",
            f"${float(row['repayment_required_usd']) / 1_000:.1f}k",
            f"${float(row['rounded_coverage_compliant_commitment_usd']) / 1_000_000:.1f}m",
        ])
    table = Table(rows, colWidths=[0.48 * inch, 0.78 * inch, 0.63 * inch, 0.88 * inch, 0.74 * inch, 1.02 * inch, 0.9 * inch, 0.94 * inch], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.8), ("LEADING", (0, 0), (-1, -1), 8.3),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("ALIGN", (3, 0), (3, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#E2F0D9")),
        ("BACKGROUND", (0, 2), (-1, -1), PALE_RED), ("TEXTCOLOR", (3, 2), (4, -1), colors.HexColor("#A32121")),
    ]
    table.setStyle(TableStyle(style))
    story = [
        Paragraph("Downside and cure ladder", title),
        Paragraph("MARA-CR-001 | Illustrative coverage mechanics at the $3.0 million recommended commitment", subtitle),
        metric, Paragraph("Coverage sensitivity", heading), table,
        Paragraph("How to read the remedies", heading),
        Paragraph("At 5% stress, available proceeds fall to $3.7515 million and modeled coverage falls to 1.230x. Restoring 1.25x requires either approximately 64.7 thousand additional USDC, a $48.8 thousand repayment, or a rounded commitment reduction to $2.9 million. The alternatives are mathematical equivalents under the declared assumptions; they are not an instruction to select or execute a remedy.", body),
        Paragraph("Control boundary", heading),
        Paragraph(ladder["method_limit"], body),
        Paragraph("The ladder assumes ownership, first priority, enforceable control, and route availability remain satisfied. Failure or uncertainty in any of those conditions is a hard blocker that assigns zero collateral credit; a cure calculation does not override the funding gate.", body),
        Paragraph("Committee question", heading),
        Paragraph("Should the draft control package require automatic collateral top-up, cash repayment, commitment step-down, or a credit-and-legal election among those remedies—and what cure period is operationally supportable?", ParagraphStyle("question", parent=body, fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=NAVY)),
        Spacer(1, 5), Paragraph("Evidence source: artifacts/collateral-call-ladder.json, generated from the declared facility, collateral, cost, coverage, accrued-amount, and rounding assumptions.", small),
    ]
    doc.build(story)
    return buffer.getvalue()


def model_risk_pdf() -> bytes:
    register = json.loads((ROOT / "artifacts" / "model-risk-register.json").read_text(encoding="utf-8"))
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, leftMargin=0.46 * inch, rightMargin=0.46 * inch,
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
        title="MARA-CR-001 model-risk posture", author="Credit Risk project",
    )
    title = ParagraphStyle("risk-title", fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, spaceAfter=4)
    subtitle = ParagraphStyle("risk-subtitle", fontName="Helvetica", fontSize=8.3, leading=10.5, textColor=MUTED, spaceAfter=9)
    body = ParagraphStyle("risk-body", fontName="Helvetica", fontSize=7.4, leading=9.2, textColor=colors.HexColor("#1F1F1F"))
    small = ParagraphStyle("risk-small", parent=body, fontSize=6.8, leading=8.5, textColor=MUTED, spaceBefore=6)
    summary = register["summary"]
    metrics = Table([
        ["Open risks", "Critical", "High", "Decision-blocking"],
        [str(summary["open_count"]), str(summary["critical_count"]), str(summary["high_count"]), str(summary["decision_blocking_count"])],
    ], colWidths=[1.82 * inch] * 4)
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#DCE6F1")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 7.5),
        ("FONTSIZE", (0, 1), (-1, 1), 14), ("TEXTCOLOR", (0, 1), (-1, 1), BLUE),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    rows = [["ID / severity", "Known limitation", "Mitigation and required evidence", "Disposition while unresolved"]]
    for risk in register["risks"]:
        rows.append([
            Paragraph(f"<b>{risk['risk_id']}</b><br/>{risk['severity']}<br/>{risk['category'].replace('_', ' ')}", body),
            Paragraph(risk["risk"], body),
            Paragraph(f"{risk['mitigation']}<br/><font color='#64707D'>Evidence: {risk['validation_evidence']}</font>", body),
            Paragraph(risk["disposition_if_unresolved"], body),
        ])
    table = Table(rows, colWidths=[0.82 * inch, 1.76 * inch, 2.88 * inch, 1.82 * inch], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for index, risk in enumerate(register["risks"], start=1):
        if risk["severity"] == "critical":
            style.append(("BACKGROUND", (0, index), (-1, index), PALE_RED))
    table.setStyle(TableStyle(style))
    story = [
        Paragraph("Model-risk posture", title),
        Paragraph("MARA-CR-001 | Known limitations are decision inputs, not footnotes", subtitle),
        metrics, Spacer(1, 8), table,
        Paragraph("The three critical risks concern synthetic collateral terms, absent borrowing-entity repayment proof, and unverified legal enforceability. None can be cleared by model precision. Four risks require a decline, zero collateral credit, or no funding while unresolved.", small),
        Paragraph(register["method_limit"], small),
    ]
    doc.build(story)
    return buffer.getvalue()


def main() -> int:
    components = [
        ("Executive cover", PdfReader(BytesIO(cover_pdf()))),
        ("Credit memorandum", PdfReader(ROOT / "outputs" / "credit-memo.pdf")),
        ("Downside and cure ladder", PdfReader(BytesIO(cure_pdf()))),
        ("Model-risk posture", PdfReader(BytesIO(model_risk_pdf()))),
        ("Opposing memorandum", PdfReader(ROOT / "outputs" / "opposing-memo.pdf")),
        ("Reviewer brief", PdfReader(ROOT / "outputs" / "reviewer-brief.pdf")),
    ]
    writer = PdfWriter()
    starts: list[tuple[str, int]] = []
    for title, reader in components:
        starts.append((title, len(writer.pages)))
        for page in reader.pages:
            writer.add_page(page)
    for title, page_index in starts:
        writer.add_outline_item(title, page_index)
    writer.add_metadata({
        "/Title": "MARA-CR-001 hypothetical credit committee packet",
        "/Author": "Credit Risk project",
        "/Subject": "Conditional approval and opposing credit case",
        "/Keywords": "credit risk, collateral, Base, scenario analysis, hypothetical",
    })
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    verified = PdfReader(OUTPUT)
    outline_titles = [item.title for item in verified.outline if hasattr(item, "title")]
    extracted = "\n".join(page.extract_text() or "" for page in verified.pages)
    required_text = ["Downside and cure ladder", "Exact modeled breach", "64.7k USDC", "$48.8k", "$2.9m", "Committee question", "Model-risk posture", "MR-01", "MR-08", "Known limitations are decision inputs"]
    if len(verified.pages) != 7 or outline_titles != [title for title, _ in components] or any(token not in extracted for token in required_text):
        raise RuntimeError("Committee packet verification failed")
    AUDIT.write_text(json.dumps({
        "schema_version": "1.0", "artifact": "outputs/committee-packet.pdf",
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), "page_count": len(verified.pages),
        "bookmark_titles": outline_titles, "required_text": required_text, "failure_count": 0,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{OUTPUT} ({len(writer.pages)} pages, {len(starts)} bookmarks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
