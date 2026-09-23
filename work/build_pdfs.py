#!/usr/bin/env python3
"""Build the three reviewer PDFs from the standardized MARA-CR-001 case."""

from __future__ import annotations

from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#2F75B5")
PALE_BLUE = colors.HexColor("#DCE6F1")
PALE_AMBER = colors.HexColor("#FFF2CC")
PALE_RED = colors.HexColor("#FCE4D6")
MID_GRAY = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#E7E6E6")

STYLES = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "Title",
    parent=STYLES["Title"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=20,
    textColor=NAVY,
    alignment=TA_LEFT,
    spaceAfter=5,
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=STYLES["Normal"],
    fontName="Helvetica",
    fontSize=8.5,
    leading=11,
    textColor=MID_GRAY,
    spaceAfter=9,
)
H2 = ParagraphStyle(
    "H2",
    parent=STYLES["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    textColor=NAVY,
    spaceBefore=7,
    spaceAfter=4,
)
BODY = ParagraphStyle(
    "Body",
    parent=STYLES["BodyText"],
    fontName="Helvetica",
    fontSize=8.6,
    leading=11.2,
    textColor=colors.HexColor("#1F1F1F"),
    spaceAfter=4,
)
SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=7.6,
    leading=9.5,
)
TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=SMALL,
    fontName="Helvetica-Bold",
    textColor=colors.white,
)
CALLOUT = ParagraphStyle(
    "Callout",
    parent=BODY,
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    textColor=NAVY,
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LIGHT_GRAY)
    canvas.line(0.55 * inch, 0.47 * inch, 7.95 * inch, 0.47 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(0.55 * inch, 0.30 * inch, "MARA-CR-001 | Hypothetical case | September 20, 2026")
    canvas.drawRightString(7.95 * inch, 0.30 * inch, f"Page {doc.page}")
    canvas.restoreState()


def document(path: Path) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.48 * inch,
        bottomMargin=0.58 * inch,
        title="MARA-CR-001 hypothetical credit case",
        author="Credit Risk project",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    return doc


def p(text: str, style=BODY) -> Paragraph:
    return Paragraph(text, style)


def h(text: str) -> Paragraph:
    return Paragraph(text, H2)


def label(text: str) -> Table:
    table = Table([[p(text, SMALL)]], colWidths=[7.3 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_AMBER),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6B656")),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def data_table(rows, widths, number_cols=()):
    cooked = [
        [p(str(cell), TABLE_HEADER if row_index == 0 else SMALL) for cell in row]
        for row_index, row in enumerate(rows)
    ]
    table = Table(cooked, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LIGHT_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for column in number_cols:
        style.append(("ALIGN", (column, 1), (column, -1), "RIGHT"))
    table.setStyle(TableStyle(style))
    return table


def bullets(items):
    return [p(f"<b>{index}.</b> {item}", BODY) for index, item in enumerate(items, 1)]


def cap_chart() -> Drawing:
    """Compact four-cap comparison for the one-page reviewer brief."""
    values = [
        ("Obligor", 7.500, NAVY),
        ("Collateral", 3.046, colors.HexColor("#C00000")),
        ("Single-name", 6.000, BLUE),
        ("Concentration", 4.000, colors.HexColor("#7F8C8D")),
    ]
    drawing = Drawing(7.3 * inch, 1.35 * inch)
    drawing.add(String(0, 88, "Four-cap comparison ($ millions)", fontName="Helvetica-Bold", fontSize=8, fillColor=NAVY))
    label_width = 76
    bar_width = 365
    scale = bar_width / 8.0
    for index, (name, value, color) in enumerate(values):
        y = 67 - index * 18
        drawing.add(String(0, y + 2, name, fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#1F1F1F")))
        drawing.add(Rect(label_width, y, bar_width, 9, fillColor=colors.HexColor("#EEF2F6"), strokeColor=None))
        drawing.add(Rect(label_width, y, value * scale, 9, fillColor=color, strokeColor=None))
        drawing.add(String(label_width + value * scale + 5, y + 1, f"${value:.3f}m", fontName="Helvetica-Bold", fontSize=7, fillColor=color))
    drawing.add(String(label_width, 1, "Binding cap", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor("#C00000")))
    drawing.add(String(label_width + 45, 1, "= collateral", fontName="Helvetica", fontSize=6.5, fillColor=MID_GRAY))
    return drawing


def build_credit_memo():
    path = OUTPUTS / "credit-memo.pdf"
    monitoring = json.loads((ROOT / "artifacts" / "monitoring-plan.json").read_text(encoding="utf-8"))
    liquidity = json.loads((ROOT / "artifacts" / "liquidity-analysis.json").read_text(encoding="utf-8"))
    monitoring_rows = [["Metric", "Threshold / state", "Breach action"]] + [
        [row["metric"], f"{row['threshold']}; {row['current_value']}", row["breach_action"]]
        for row in monitoring["rules"]
    ]
    story = [
        p("Illustrative credit memorandum", TITLE),
        p("MARA Holdings, Inc. | Case MARA-CR-001 | Information date: June 30, 2026", SUBTITLE),
        label("Hypothetical exercise. MARA is not represented as a Coinbase customer. The facility, collateral, Base location, policy limits, rating, and portfolio are fictional."),
        h("Recommendation"),
        p("<b>Conditionally approve a maximum $3.0 million commitment</b> on the fictional $5.0 million, 12-month request. Do not fund until ownership, first-priority lien, enforceable control, and the Base-to-cash route are evidenced. If any item remains unresolved, decline."),
        data_table(
            [
                ["Cap", "Amount", "Basis"],
                ["Obligor", "$7.500m", "Illustrative public-information judgment"],
                ["Collateral", "$3.046m", "$3.8706m proceeds / 1.25x coverage - $0.05m accrued"],
                ["Single-name", "$6.000m", "Illustrative policy"],
                ["Concentration", "$4.000m", "Illustrative shared-risk capacity"],
                ["Recommended", "$3.000m", "Rounded below the binding collateral cap"],
            ],
            [1.25 * inch, 1.15 * inch, 4.9 * inch],
            number_cols=(1,),
        ),
        h("Credit view"),
        p("MARA reported $421.3 million of cash and cash equivalents at June 30, 2026. About 30% was held by majority-owned Exaion and designated for its operations over the following year. MARA also reported 35,577 bitcoin with a $2.1 billion fair value: 4,742 loaned, 4,528 pledged, and 26,307 described as unrestricted (SRC-001). None is assumed to secure this facility."),
        p("MARA reported about $2.4 billion of debt after note repurchases. Identified near-term items included a $150 million line of credit, $48.1 million of December 2026 notes, and $291.6 million classified current because holders can require repurchase in June 2027 (SRC-001). The 2025 Form 10-K reported $802.7 million of net operating cash use (SRC-002)."),
        p(f"A static public-data bridge leaves <b>${float(liquidity['residual_before_potential_put_usd']) / 1_000_000:.2f} million</b> after designated cash, the line of credit, and December 2026 notes. Adding the June 2027 holder-put sensitivity produces <b>negative ${abs(float(liquidity['residual_after_potential_put_usd'])) / 1_000_000:.2f} million</b>. This is not a borrowing-entity forecast and does not assert that the put will be exercised."),
        p("The primary repayment source remains unproven. The draft assumes unrestricted operating liquidity and working-capital cash generation, not collateral liquidation. Funding requires a current cash forecast, facility purpose, legal-entity cash map, and debt-service schedule."),
        p("The recovery view and approval view use different exposure bases. If the full $5.0 million request were drawn, the $5.05 million exposure including accrued amount would exceed base eligible proceeds by <b>$1,179,400</b>. The recommended $3.0 million limit implies $3.05 million of pro forma exposure and an <b>$820,600 coverage surplus</b>. This distinction prevents the full-request shortfall from being read as the exposure created by the smaller recommendation."),
        h("Illustrative collateral waterfall"),
        data_table(
            [
                ["Step", "Calculation", "Amount"],
                ["Quoted value", "4.0m fictional USDC x $1.00", "$4,000,000"],
                ["Stressed gross", "$4.0m x 98%", "$3,920,000"],
                ["Execution cost", "$3.920m x 0.50%", "($19,600)"],
                ["Delay cost", "$3.920m x 25 bps", "($9,800)"],
                ["Fixed cost", "Assumed", "($20,000)"],
                ["Available proceeds", "Stressed value less costs", "$3,870,600"],
                ["Collateral cap", "$3.8706m / 1.25x - $0.05m accrued", "$3,046,480"],
            ],
            [1.45 * inch, 3.8 * inch, 2.05 * inch],
            number_cols=(2,),
        ),
        PageBreak(),
        p("Conditions, monitoring, and reversal", TITLE),
        p("Illustrative credit memorandum | MARA-CR-001", SUBTITLE),
        h("Conditions precedent"),
        *bullets(
            [
                "Verify beneficial ownership, no prior lien, first-priority security, and enforceable lender control over the fictional collateral lot.",
                "Test the read-only custody-to-liquidation-to-bank route. Chain confirmation alone does not establish repayment availability.",
                "Receive a 13-week cash forecast, use-of-proceeds schedule, legal-entity cash map, and complete debt-service schedule.",
                "Maintain at least 1.25x stressed coverage and prohibit collateral substitution without a new case version.",
                "Confirm the fictional single-name and shared-risk limits before funding.",
            ]
        ),
        h("Principal risks and monitoring"),
        p("Eight post-close rules distinguish calculated projections from unavailable private evidence. The design is not active monitoring or evidence of compliance.", SMALL),
        data_table(monitoring_rows, [2.05 * inch, 2.25 * inch, 3.0 * inch]),
        h("Reversal evidence"),
        p("Increase toward $5.0 million only if a refreshed cash forecast supports repayment without collateral, or if more eligible collateral raises the binding cap without breaching another limit. Decline if ownership, priority, control, or route evidence cannot be obtained, or if combined stress makes the conditional limit inconsistent with portfolio capacity."),
        h("Strongest objection"),
        p("The $3.0 million result is generated by fictional collateral. A cleaner committee action is to decline pending real repayment-capacity diligence, then assess the full request without manufacturing precision from a synthetic structure. See the opposing memorandum."),
        h("Evidence and limits"),
        p("SRC-001 is MARA's June 30, 2026 Form 10-Q. SRC-002 is MARA's 2025 Form 10-K. All lending inputs are ASM-C assumptions. The model is a portfolio exercise, not Coinbase policy, legal advice, a calibrated default model, or a real credit recommendation."),
    ]
    document(path).build(story)


def build_opposing_memo():
    path = OUTPUTS / "opposing-memo.pdf"
    story = [
        p("Opposing memorandum", TITLE),
        p("MARA-CR-001 | Alternative recommendation: decline pending private diligence", SUBTITLE),
        label("Hypothetical exercise. The $3.0 million recommendation is an illustrative model result, not evidence that a real facility is safe."),
        h("Do not manufacture a collateral constraint"),
        p("The conditional recommendation is precise but not yet persuasive. Its binding cap comes from an invented 4.0 million USDC lot and invented costs. The waterfall demonstrates a method; it does not establish an economically appropriate limit for MARA."),
        h("Scale points toward a different question"),
        p("MARA reported $421.3 million of cash and cash equivalents and 26,307 unrestricted bitcoin at June 30, 2026 (SRC-001). A $5.0 million request is about 1.2% of reported cash. Reducing the request by $2.0 million because synthetic collateral supports only $3.046 million creates false precision."),
        p("The same filings report about $2.4 billion of debt, meaningful near-term obligations, designated cash, and $802.7 million of operating cash use in 2025 (SRC-001, SRC-002). Those facts justify private diligence. They do not justify letting fictional collateral replace primary repayment analysis."),
        h("Alternative decision"),
        p("<b>Decline on the present record.</b> Obtain the facility purpose, borrowing-entity financials, 13-week cash forecast, legal-entity cash map, complete debt-service schedule, and actual collateral terms. If the evidence supports repayment, assess the full $5.0 million request directly. If it does not, a smaller secured exposure is not automatically safe."),
        h("Why this alternative is stronger"),
        *bullets(
            [
                "It does not treat a lower number as conservative merely because a model produced it.",
                "It keeps collateral recovery subordinate to operating repayment capacity.",
                "It refuses to turn onchain visibility into ownership, priority, or enforceability.",
                "It identifies the exact evidence needed to resolve the disagreement.",
            ]
        ),
        h("Disputed assumption"),
        p("The disputed assumption is the $7.5 million obligor cap. A reconciled cash forecast and debt-service schedule at the borrowing entity, including downside liquidity and covenant headroom, would resolve the dispute. Until then, the collateral waterfall belongs in sensitivity analysis, not as the sole basis for approval."),
        h("Committee question"),
        p("Would the committee rather approve a smaller number supported by synthetic collateral, or decline until it can underwrite actual repayment capacity? The opposing view chooses the latter."),
    ]
    document(path).build(story)


def build_reviewer_brief():
    path = OUTPUTS / "reviewer-brief.pdf"
    story = [
        p("Reviewer brief", TITLE),
        p("MARA-CR-001 | One disputed decision | Self-review only", SUBTITLE),
        label("All lending terms are fictional. MARA is not represented as a Coinbase customer."),
        Spacer(1, 4),
        Table(
            [[p("Conditional recommendation", SMALL), p("$3.0m", CALLOUT), p("Requested", SMALL), p("$5.0m", CALLOUT)]],
            colWidths=[1.7 * inch, 1.2 * inch, 1.0 * inch, 1.2 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.6, BLUE),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        ),
        h("Decision logic"),
        cap_chart(),
        h("Waterfall"),
        p("$4.000m quoted value - $0.080m price stress - $0.0196m execution cost - $0.0098m delay cost - $0.020m fixed cost = <b>$3.8706m available proceeds</b>. Dividing by 1.25x coverage and subtracting the $0.05m accrued amount gives a <b>$3.04648m collateral cap</b>, rounded down to $3.0m."),
        h("Public issuer context"),
        p("MARA reported $421.3 million of cash, $2.1 billion fair value across 35,577 bitcoin, and about $2.4 billion of debt at June 30, 2026 (SRC-001). Its 2025 filing reported $802.7 million of net operating cash use (SRC-002). Reported bitcoin is not treated as facility collateral."),
        h("Strongest opposing view"),
        p("The $3.0 million cap is an artifact of invented collateral. Decline pending private diligence, then underwrite actual repayment capacity rather than manufacturing precision from a synthetic schedule."),
        h("Unresolved assumption"),
        p("Can public information plus a current borrower cash forecast support the assumed $7.5 million obligor cap without relying on collateral (ASM-C004)?"),
        h("Review question"),
        Table(
            [[p("Would you challenge the primary-repayment analysis, the collateral-access blocker, or the fictional portfolio cap first, and what specific evidence would change your answer?", CALLOUT)]],
            colWidths=[7.3 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), PALE_RED),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#C00000")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        ),
    ]
    document(path).build(story)


if __name__ == "__main__":
    build_credit_memo()
    build_opposing_memo()
    build_reviewer_brief()
    print("built", *(str(OUTPUTS / name) for name in ("credit-memo.pdf", "opposing-memo.pdf", "reviewer-brief.pdf")), sep="\n")
