"""
SmartCOD AI - Professional Business Memo PDF Generator
Generates a publication-grade, 2-page executive memo for the D2C Haircare Founder.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_memo_pdf(output_path="docs/BUSINESS_MEMO.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom palette
    primary_color = colors.HexColor("#0f172a")    # Slate 900
    brand_emerald = colors.HexColor("#059669")    # Emerald 600
    text_dark = colors.HexColor("#1e293b")        # Slate 800
    text_muted = colors.HexColor("#64748b")       # Slate 500
    bg_light = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#cbd5e1")     # Slate 300
    danger_color = colors.HexColor("#dc2626")     # Red 600

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=brand_emerald,
        fontStyle='BOLD',
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    stat_label_style = ParagraphStyle(
        'StatLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=text_muted,
        alignment=1
    )

    stat_val_style = ParagraphStyle(
        'StatVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=primary_color,
        alignment=1
    )

    story = []

    # Memo Header Table
    header_data = [
        [Paragraph("<strong>EXECUTIVE STRATEGY MEMORANDUM</strong>", title_style), 
         Paragraph("<strong>CONFIDENTIAL</strong><br/>October 2026", ParagraphStyle('RightMeta', parent=body_style, alignment=2, textColor=text_muted))],
        [Paragraph("<strong>TO:</strong> Founder & CEO, D2C Haircare Brand<br/>"
                   "<strong>FROM:</strong> Lead AI Automation & Systems Engineer<br/>"
                   "<strong>SUBJECT:</strong> SmartCOD AI — Intelligent COD Risk & RTO Prevention Architecture", subtitle_style),
         Paragraph("<strong>STATUS:</strong> Production Implementation<br/>"
                   "<strong>DATASET:</strong> 1,988 Deduplicated Orders<br/>"
                   "<strong>ENGINE:</strong> Calibrated 4-Tier Triage", ParagraphStyle('RightMeta2', parent=body_style, alignment=2))]
    ]
    t_header = Table(header_data, colWidths=[4.2 * inch, 3.0 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8, spaceBefore=2))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "At our current monthly scale of <strong>3,000 orders</strong> with <strong>55% COD penetration</strong>, our "
        "<strong>28.4% COD Return-to-Origin (RTO) rate</strong> creates approximately <strong>469 failed deliveries monthly</strong>. "
        "With a verified direct cash loss of <strong>Rs 169.40 per RTO</strong> (Rs 65 forward shipping + Rs 65 return shipping + "
        "Rs 25 packaging + 8% product damage on Rs 180 unit cost = Rs 14.40), the brand leaks over <strong>Rs 79,500 in pure cash every month</strong>. "
        "More critically, blunt order cancellations destroy company value: cancelling a genuine customer sacrifices Rs 402.38 in delivered gross "
        "profit (62% on Rs 649 AOV) plus Rs 300+ in sunk Meta Customer Acquisition Cost (CAC), totaling a catastrophic <strong>Rs 702.38 loss per false cancellation</strong>. "
        "SmartCOD AI eliminates this tension by deploying a 4-tier decision triage: <strong>SHIP_AS_IS</strong> for high-trust repeat customers, "
        "<strong>SHIP_AFTER_CONFIRMATION</strong> via 2-way WhatsApp for moderate risk, <strong>NUDGE_TO_PREPAID</strong> with an 8% discount to convert impulse buyers, "
        "and reserving <strong>HOLD_OR_CANCEL</strong> strictly for verified fake names, defective addresses, and chronic return abusers.",
        body_style
    ))

    # Key Statistics Box
    stat_boxes = [
        [
            Paragraph("MONTHLY COD ORDERS", stat_label_style),
            Paragraph("CURRENT COD RTO", stat_label_style),
            Paragraph("DIRECT LOSS / RTO", stat_label_style),
            Paragraph("FALSE POSITIVE COST", stat_label_style),
            Paragraph("PROJECTED NET SAVING", stat_label_style)
        ],
        [
            Paragraph("1,650", stat_val_style),
            Paragraph("28.4%", ParagraphStyle('RtoVal', parent=stat_val_style, textColor=danger_color)),
            Paragraph("Rs 169.40", stat_val_style),
            Paragraph("Rs 702.38", ParagraphStyle('FpVal', parent=stat_val_style, textColor=danger_color)),
            Paragraph("+Rs 48,200/mo", ParagraphStyle('SavVal', parent=stat_val_style, textColor=brand_emerald))
        ]
    ]
    t_stats = Table(stat_boxes, colWidths=[1.44 * inch] * 5)
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 8))

    # Key Findings from Dataset
    story.append(Paragraph("2. Empirical Ground Truths (from 1,988 Deduplicated Orders)", h1_style))
    story.append(Paragraph(
        "Analysis of our historical dataset identified 30 exact duplicate pairs (60 rows) that were deduplicated to 1,988 unique orders (1,422 Delivered, 565 RTO, 1 In-Transit). "
        "Four statistical findings form the mathematical backbone of our decision engine:",
        body_style
    ))
    story.append(Paragraph("• <strong>Finding 1 — Prior RTO History is the #1 Predictor (3.22x Risk Escalation):</strong> "
                           "Repeat customers with 0 prior RTOs deliver at an outstanding <strong>86.00% success rate (14.00% RTO across 350 orders)</strong>. "
                           "However, repeat customers with past RTOs spike to <strong>45.07% RTO (142 orders)</strong>. Prior RTO history is our strongest negative feature.", bullet_style))
    story.append(Paragraph("• <strong>Finding 2 — Address Defectiveness Generates 61.75% Failure:</strong> "
                           "Orders with truncated or placeholder addresses ('xyz', 'home', '.', or &lt;20 chars) fail at <strong>61.75% RTO (183 orders)</strong>. "
                           "Conversely, structured addresses with flat/house numbers and street names deliver at <strong>76.06% (1,412 orders)</strong>.", bullet_style))
    story.append(Paragraph("• <strong>Finding 3 — Synthetic Names & Rapid Duplicate Bursts:</strong> "
                           "Test names ('Test Order', 'asdf', 'qwerty') exhibited a <strong>63.64% RTO rate (44 orders)</strong>. "
                           "Additionally, 28 orders were placed within 15 minutes of each other by identical phone numbers, clustering heavily in the KT15xxxx series.", bullet_style))
    story.append(Paragraph("• <strong>Finding 4 — Channel and Courier Disparities:</strong> "
                           "Meta Ads represents 38.6% of volume with <strong>31.24% RTO</strong>, while Direct traffic achieves <strong>22.92% RTO</strong>. "
                           "Among couriers, Delhivery achieved the lowest RTO (26.04%), whereas Xpressbees suffered the highest (30.95%).", bullet_style))

    story.append(Spacer(1, 6))

    # Operations vs Marketing Trade-Off
    story.append(Paragraph("3. The Economic Core: Operations vs. Marketing Alignment", h1_style))
    story.append(Paragraph(
        "The Head of Operations wants zero RTOs; the Head of Marketing wants maximum customer acquisition. "
        "A naive cancellation policy destroys equity: because Rs 702.38 (profit + CAC) / Rs 169.40 (direct RTO saving) = <strong>4.14</strong>, "
        "an automated system must be at least <strong>80.5% confident</strong> before cancelling an order outright. "
        "Instead of cancelling, SmartCOD AI solves this through intermediate economic instruments:",
        body_style
    ))

    tradeoff_table = [
        [
            Paragraph("<strong>Assigned Action</strong>", ParagraphStyle('ThStyle', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("<strong>Risk Threshold</strong>", ParagraphStyle('ThStyle', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("<strong>Operational Mechanism</strong>", ParagraphStyle('ThStyle', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("<strong>Financial Trade-Off Justification</strong>", ParagraphStyle('ThStyle', parent=body_style, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph("<strong>SHIP_AS_IS</strong>", ParagraphStyle('Act1', parent=body_style, textColor=brand_emerald)),
            Paragraph("&lt; 20% Score", body_style),
            Paragraph("Instant label generation; fast fulfillment SLA.", body_style),
            Paragraph("Expected margin (Rs 362+) dwarfs RTO risk (Rs 25). Zero friction for trusted buyers.", body_style)
        ],
        [
            Paragraph("<strong>SHIP_AFTER_CONFIRMATION</strong>", ParagraphStyle('Act2', parent=body_style, textColor=colors.HexColor("#2563eb"))),
            Paragraph("20% – 45% Score", body_style),
            Paragraph("Interactive WhatsApp YES/NO prompt before packing.", body_style),
            Paragraph("Filters out impulse buyers without cancelling. Preserves 100% of CAC on genuine buyers.", body_style)
        ],
        [
            Paragraph("<strong>NUDGE_TO_PREPAID</strong>", ParagraphStyle('Act3', parent=body_style, textColor=colors.HexColor("#7c3aed"))),
            Paragraph("45% – 68% (or &gt;Rs 1k)", body_style),
            Paragraph("WhatsApp 8% discount link (Rs 52 off) to pay via UPI.", body_style),
            Paragraph("Prepaid RTO is only 4%. Risk drop saves Rs 67 in RTO cost for a Rs 52 discount = +Rs 15 net cash gain.", body_style)
        ],
        [
            Paragraph("<strong>HOLD_OR_CANCEL</strong>", ParagraphStyle('Act4', parent=body_style, textColor=danger_color)),
            Paragraph("&ge; 68% Score", body_style),
            Paragraph("Dispatch hold; route to CS agent for address fix.", body_style),
            Paragraph("Restricted strictly to defective addresses, fake names, and chronic abusers (&gt;60% return rate).", body_style)
        ]
    ]
    t_tradeoff = Table(tradeoff_table, colWidths=[1.8 * inch, 1.1 * inch, 2.0 * inch, 2.3 * inch])
    t_tradeoff.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_tradeoff)

    story.append(Spacer(1, 6))

    # Edge Cases & Failure Modes
    story.append(Paragraph("4. Known Edge Cases & Defensive Safeguards", h1_style))
    story.append(Paragraph("• <strong>Hinglish Local Landmarks:</strong> Addresses containing authentic local cues (e.g., 'peepal ke ped ke samne', 'doodh dairy ke pass', 'gali no 3') "
                           "might appear long or unstructured to standard western address validators. Our NLP parser detects Indian landmark cues and assigns a positive trust bonus.", bullet_style))
    story.append(Paragraph("• <strong>Low Sample Size Pincodes:</strong> With 461 pincodes in 1,988 orders, many pincodes have only 1–2 historical orders. "
                           "We apply Empirical Bayes / Laplace smoothing (m=10) toward the 28.4% prior, preventing unfair penalization of newly opened territories.", bullet_style))
    story.append(Paragraph("• <strong>WhatsApp 24-Hour Timeout:</strong> Unresponsive customers are neither cancelled nor dispatched blindly; after 24 hours, "
                           "the order transitions to 'TIMEOUT' state with a hold flag for manual review, eliminating unneeded stock tie-ups.", bullet_style))

    story.append(Spacer(1, 6))

    # 2-Week Actionable Rollout Plan
    story.append(Paragraph("5. Actionable 2-Week Rollout & Experimentation Plan", h1_style))
    rollout_data = [
        [
            Paragraph("<strong>Phase / Days</strong>", ParagraphStyle('RollTh', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("<strong>Target Milestone</strong>", ParagraphStyle('RollTh', parent=body_style, fontName='Helvetica-Bold')),
            Paragraph("<strong>Operational Focus & Success Metrics</strong>", ParagraphStyle('RollTh', parent=body_style, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph("<strong>Days 1 – 3</strong><br/>Shadow Mode", body_style),
            Paragraph("Zero-Risk Baseline", body_style),
            Paragraph("Deploy decision engine in read-only shadow mode behind Shopify webhooks. Score 100% of incoming COD orders without altering courier dispatch. Verify prediction calibration against actual delivery runs.", body_style)
        ],
        [
            Paragraph("<strong>Days 4 – 7</strong><br/>Confirmation Trial", body_style),
            Paragraph("Workflow A Rollout (50% A/B Split)", body_style),
            Paragraph("Activate WhatsApp confirmation on medium-risk cohort. Control group receives standard COD; variant receives automated confirmation prompt. Benchmark confirmation response rate (target &gt;70%) and RTO delta.", body_style)
        ],
        [
            Paragraph("<strong>Days 8 – 11</strong><br/>Prepaid Nudge Trial", body_style),
            Paragraph("Workflow B Rollout (&gt;Rs 1,000 orders)", body_style),
            Paragraph("Trigger 8% UPI discount nudge on high-value COD orders. Measure conversion rate from COD to prepaid (target 12–18%) and calculate net margin savings vs discount cost.", body_style)
        ],
        [
            Paragraph("<strong>Days 12 – 14</strong><br/>Full Autonomous Triage", body_style),
            Paragraph("Operational Sign-Off & Automation", body_style),
            Paragraph("Enable automated label generation for SHIP_AS_IS bucket, automated hold on defective addresses, and live Founder Dashboard monitoring. Conduct weekly threshold review with Operations & Growth heads.", body_style)
        ]
    ]
    t_rollout = Table(rollout_data, colWidths=[1.4 * inch, 1.8 * inch, 4.0 * inch])
    t_rollout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_rollout)

    doc.build(story)
    print(f"Business Memo successfully generated at {output_path}")

if __name__ == "__main__":
    generate_memo_pdf()
