#!/usr/bin/env python3
"""Create demo slides, local narration, and the final MP4 walkthrough."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work" / "demo"
OUTPUT = ROOT / "outputs" / "demo.mp4"
WORK.mkdir(parents=True, exist_ok=True)

NAVY = "#16324f"
BLUE = "#2f75b5"
INK = "#17202a"
MUTED = "#64707d"
PAPER = "#f4f7fa"
WHITE = "#ffffff"
AMBER = "#fff2cc"
RED = "#a32121"
GREEN = "#1f6a44"

FONT = "/System/Library/Fonts/Helvetica.ttc"
FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size=size, index=1 if bold else 0)


def wrap(draw, text, width, fnt):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def slide(number, title, kicker, body, callouts=(), alert=None):
    image = Image.new("RGB", (1920, 1080), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1920, 145), fill=NAVY)
    draw.text((95, 42), "MARA-CR-001", font=font(25, True), fill=WHITE)
    draw.text((1680, 45), f"{number}/6", font=font(23), fill="#c8d5e2")
    draw.text((95, 200), title, font=font(52, True), fill=NAVY)
    draw.text((98, 272), kicker, font=font(27), fill=MUTED)
    y = 350
    body_font = font(32)
    for paragraph in body:
        for line in wrap(draw, paragraph, 1260, body_font):
            draw.text((100, y), line, font=body_font, fill=INK)
            y += 45
        y += 18
    if callouts:
        x, box_y = 100, 780
        width = int(1660 / len(callouts)) - 20
        for label, value, color in callouts:
            draw.rounded_rectangle((x, box_y, x + width, 970), radius=18, fill=WHITE, outline="#d8e0e8", width=3)
            draw.text((x + 26, box_y + 25), label, font=font(24), fill=MUTED)
            draw.text((x + 26, box_y + 78), value, font=font(42, True), fill=color)
            x += width + 20
    if alert:
        draw.rounded_rectangle((1380, 330, 1810, 680), radius=20, fill=AMBER, outline="#d6b656", width=3)
        ay = 370
        for line in wrap(draw, alert, 360, font(29, True)):
            draw.text((1420, ay), line, font=font(29, True), fill=NAVY)
            ay += 43
    draw.text((100, 1030), "Hypothetical facility. Public issuer facts remain separate from fictional lending terms.", font=font(20), fill=MUTED)
    path = WORK / f"slide-{number}.png"
    image.save(path)
    return path


scenarios = json.loads((ROOT / "artifacts/scenario-results.json").read_text())
base = next(row for row in scenarios if row["scenario_id"] == "base")
route_failure = next(row for row in scenarios if row["scenario_id"] == "route_failure")

slides = [
    (
        slide(1, "A disputed $5 million credit decision", "Approve, reduce, condition, or decline?", [
            "The case uses MARA Holdings public filings, but it does not claim a Coinbase relationship.",
            "The facility, collateral, Base route, portfolio, and policy limits are fictional by design.",
        ], [("Requested", "$5.0m", NAVY), ("Conditional limit", "$3.0m", GREEN), ("Information date", "Jun 30, 2026", BLUE)]),
        "This project asks a narrow credit committee question. Would you approve a hypothetical five million dollar, twelve month facility? MARA Holdings supplies the public financial facts, but every lending term is fictional. The current answer is a three million dollar conditional limit, subject to evidence that does not exist in public filings.",
    ),
    (
        slide(2, "Underwrite the obligor first", "Headline liquidity is not the same as repayment capacity", [
            "MARA reported $421.3 million of cash and $2.1 billion of bitcoin fair value.",
            "It also reported about $2.4 billion of debt and $802.7 million of 2025 operating cash use.",
            "Reported bitcoin is never treated as collateral for this fictional facility.",
        ], [("Cash", "$421.3m", NAVY), ("Debt", "~$2.4bn", RED), ("2025 operating cash use", "$802.7m", RED)]),
        "The analysis starts with the borrower, not the collateral. MARA reported four hundred twenty one point three million dollars of cash and about two point one billion dollars of bitcoin fair value. But debt was roughly two point four billion dollars, and the prior year used more than eight hundred million dollars of operating cash. Public statements cannot establish which cash belongs to the borrowing entity or which assets a lender can control.",
    ),
    (
        slide(3, "Make collateral availability explicit", "The same quoted value can produce a different credit result", [
            "The fictional lot is four million USDC on Base.",
            "Price stress, execution cost, delay cost, and fixed cost remain separate.",
            "Unknown ownership, lien priority, control, or route means zero eligible value.",
        ], [("Quoted", "$4.000m", NAVY), ("Available proceeds", "$3.8706m", BLUE), ("Coverage", "1.25x", NAVY)]),
        "The fictional collateral schedule starts with four million USDC on Base. I do not hide every risk inside one haircut. A two percent price stress, fifty basis points of execution cost, twenty five basis points of delay cost, and twenty thousand dollars of fixed cost produce three million eight hundred seventy thousand six hundred dollars of available proceeds. Ownership, priority, legal control, and the repayment route remain separate gates.",
    ),
    (
        slide(4, "The lowest cap controls", "Transparent policy arithmetic beats a black-box score", [
            "The recommended limit is the minimum of obligor, collateral, single-name, and concentration caps.",
            "The collateral cap binds at $3.09648 million and rounds down to $3.0 million.",
        ], [("Obligor", "$7.500m", NAVY), ("Collateral", "$3.096m", RED), ("Single-name", "$6.000m", NAVY), ("Concentration", "$4.000m", NAVY)]),
        "The decision rule is deliberately simple. The final limit is the lowest of four caps, after hard blockers. The illustrative obligor cap is seven point five million. The collateral cap is three point zero nine six million. Single name capacity is six million, and concentration capacity is four million. Collateral binds, so the recommendation rounds down to three million dollars.",
    ),
    (
        slide(5, "Adverse cases must change the answer", "A route failure is not another small haircut", [
            "A thirty percent collateral decline reduces the rounded limit to $2.2 million.",
            "A twenty four hour delay reduces proceeds while preserving the decision structure.",
            "An unavailable route produces zero eligible proceeds and a decline.",
        ], [("Base", "$3.0m", GREEN), ("30% decline", "$2.2m", RED), ("Route failure", "$0 / decline", RED)], alert="Chain confirmation does not equal repayment availability."),
        "The scenario engine tests economic direction and hard boundaries. A thirty percent collateral decline lowers the rounded limit to two point two million dollars. A twenty four hour delay reduces available proceeds. If the Base to bank route becomes unavailable, the model does not apply a slightly larger haircut. It grants zero collateral credit and declines the facility.",
    ),
    (
        slide(6, "The disagreement is the deliverable", "Conditional approval versus decline pending private diligence", [
            "The approval case says a smaller, controlled limit can proceed after named conditions are satisfied.",
            "The opposing memo says synthetic collateral cannot substitute for primary repayment diligence.",
            "The best review question is which assumption should be challenged first.",
        ], [("Regression tests", "PASS", GREEN), ("Package checks", "PASS", GREEN), ("External review", "Outstanding", RED)]),
        "The strongest version of this project does not pretend the recommendation is obviously right. The opposing memo argues for decline until the actual repayment source and legal structure can be reviewed. That disagreement is useful. My question for a practitioner is this: would you challenge the primary repayment analysis, the collateral access blocker, or the portfolio cap first, and what evidence would change your answer?",
    ),
]

audio_files = []
for index, (_, narration) in enumerate(slides, 1):
    text_path = WORK / f"narration-{index}.txt"
    audio_path = WORK / f"narration-{index}.aiff"
    text_path.write_text(narration, encoding="utf-8")
    subprocess.run(["/usr/bin/say", "-r", "165", "-o", str(audio_path), "-f", str(text_path)], check=True)
    audio_files.append(audio_path)

# The host's Swift compiler can lag its SDK, so the reproducible default uses
# a tiny Objective-C AVFoundation writer. Narration assets remain beside the
# slides for a later voice-mux pass; the exported walkthrough is captioned.
binary = WORK / "build_demo"
intermediate = WORK / "captioned-demo.mov"
subprocess.run(
    [
        "/usr/bin/clang", "-fobjc-arc", "-fblocks",
        "-framework", "Foundation", "-framework", "AVFoundation",
        "-framework", "CoreGraphics", "-framework", "CoreMedia", "-framework", "CoreVideo",
        "-framework", "ImageIO", str(ROOT / "work" / "build_demo.m"),
        "-o", str(binary),
    ],
    check=True,
)
subprocess.run(
    [str(binary), str(intermediate), "14", *[str(slide_path) for slide_path, _ in slides]],
    check=True,
)
subprocess.run(
    [
        "/usr/bin/avconvert", "--source", str(intermediate),
        "--preset", "Preset1920x1080", "--output", str(OUTPUT),
        "--replace", "--disableMetadataFilter",
    ],
    check=True,
)
print(OUTPUT)
