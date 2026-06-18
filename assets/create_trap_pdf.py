"""
create_trap_pdf.py

Generates assets/sample_trap.pdf — a realistic-looking analyst report that
deliberately mixes wrong facts with correct ones, suitable for testing the
TruthLayer fact-checking app.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

# ---------------------------------------------------------------------------
# Output path — always relative to this script so it works from any cwd
# ---------------------------------------------------------------------------
output_path = Path(__file__).parent / "sample_trap.pdf"

# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------
doc = SimpleDocTemplate(
    str(output_path),
    pagesize=A4,
    rightMargin=25 * mm,
    leftMargin=25 * mm,
    topMargin=30 * mm,
    bottomMargin=25 * mm,
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
base_styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    name="ReportTitle",
    parent=base_styles["Title"],
    fontSize=24,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1A237E"),
    spaceAfter=12,
    alignment=1,  # CENTER
)

subtitle_style = ParagraphStyle(
    name="ReportSubtitle",
    parent=base_styles["Normal"],
    fontSize=14,
    fontName="Helvetica",
    textColor=colors.HexColor("#37474F"),
    spaceAfter=8,
    alignment=1,
)

meta_style = ParagraphStyle(
    name="ReportMeta",
    parent=base_styles["Normal"],
    fontSize=11,
    fontName="Helvetica",
    textColor=colors.HexColor("#546E7A"),
    spaceAfter=6,
    alignment=1,
)

section_header_style = ParagraphStyle(
    name="SectionHeader",
    parent=base_styles["Heading1"],
    fontSize=16,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1A237E"),
    spaceBefore=18,
    spaceAfter=10,
)

body_style = ParagraphStyle(
    name="BodyText",
    parent=base_styles["Normal"],
    fontSize=11,
    fontName="Helvetica",
    leading=14,
    spaceAfter=10,
    alignment=4,  # JUSTIFY
)

disclaimer_style = ParagraphStyle(
    name="Disclaimer",
    parent=base_styles["Normal"],
    fontSize=9,
    fontName="Helvetica-Oblique",
    textColor=colors.HexColor("#78909C"),
    spaceAfter=6,
    alignment=1,
)

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
story = []

# ── PAGE 1: Title page ──────────────────────────────────────────────────────
story.append(Spacer(1, 60 * mm))

story.append(Paragraph("Global Technology &amp; Market Report 2024", title_style))
story.append(Spacer(1, 6 * mm))

story.append(
    Paragraph(
        "An Analysis of Economic Indicators and Technology Trends",
        subtitle_style,
    )
)
story.append(Spacer(1, 4 * mm))

story.append(Paragraph("Published: January 2024", meta_style))
story.append(Spacer(1, 2 * mm))
story.append(Paragraph("Horizon Research Institute", meta_style))
story.append(Spacer(1, 10 * mm))

story.append(
    Paragraph(
        "Confidential — For Authorized Recipients Only",
        disclaimer_style,
    )
)
story.append(
    Paragraph(
        "This document is prepared solely for informational purposes. "
        "All data herein is sourced from publicly available databases, "
        "proprietary surveys, and third-party analytical partners. "
        "Horizon Research Institute makes no warranty, express or implied, "
        "as to the accuracy or completeness of the information contained herein.",
        disclaimer_style,
    )
)

story.append(PageBreak())

# ── PAGE 2: Economic Overview ───────────────────────────────────────────────
story.append(Paragraph("1. Economic Overview", section_header_style))

story.append(
    Paragraph(
        "The global economy in 2023 continued its post-pandemic recalibration, "
        "with emerging markets assuming an increasingly prominent role in driving "
        "aggregate demand. South and Southeast Asia, in particular, posted "
        "impressive growth numbers that outpaced consensus forecasts heading into "
        "the year.",
        body_style,
    )
)

story.append(
    Paragraph(
        "According to recent economic surveys, India's GDP in 2023 was $2.1 trillion, "
        "placing it among the top emerging economies globally. This growth trajectory "
        "has been supported by a rapidly expanding middle class and a surge in "
        "domestic consumption. Notably, the population of India surpassed 1.5 billion "
        "in 2020, creating one of the world's largest consumer markets and providing "
        "a deep talent pipeline for both manufacturing and services sectors.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Foreign direct investment inflows into the country rose sharply as "
        "multinational corporations sought to diversify supply chains away from "
        "single-source dependencies. Infrastructure spending, enabled by government "
        "fiscal programmes, further catalysed private-sector activity in logistics, "
        "real estate, and renewable energy.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Regional trade agreements signed during the review period are expected to "
        "lower average tariff rates by 3–5 percentage points over the next decade, "
        "amplifying the growth dividend for participating economies. The macroeconomic "
        "outlook remains cautiously optimistic, contingent on stable commodity prices "
        "and continued monetary policy normalisation across the G20.",
        body_style,
    )
)

story.append(PageBreak())

# ── PAGE 3: Technology & Science ────────────────────────────────────────────
story.append(Paragraph("2. Technology &amp; Science", section_header_style))

story.append(
    Paragraph(
        "The technology sector proved resilient in 2023, rebounding from the "
        "valuation corrections of the previous year. Hardware, software, and "
        "cloud-infrastructure segments all registered year-on-year revenue growth, "
        "underpinned by enterprise digital-transformation budgets that remained "
        "largely intact despite broader macroeconomic uncertainty.",
        body_style,
    )
)

story.append(
    Paragraph(
        "The global smartphone market shipped 2.5 billion units in 2023, reflecting "
        "sustained consumer demand despite macroeconomic headwinds. Premium-tier "
        "devices accounted for a growing share of shipments as manufacturers "
        "concentrated R&amp;D investment on camera systems, on-device AI inference, "
        "and foldable form factors. Emerging markets in Sub-Saharan Africa and South "
        "Asia recorded the fastest unit-volume growth, with first-time smartphone "
        "adopters driving entry-level segment expansion.",
        body_style,
    )
)

story.append(
    Paragraph(
        "On the software development front, Python — which was created in 1998 by "
        "Guido van Rossum — has become the dominant language for data-science "
        "workloads, machine-learning pipelines, and scripting automation. Its "
        "expressive syntax and rich ecosystem of open-source libraries have made it "
        "the lingua franca of the AI research community, with adoption rates "
        "continuing to climb across both academia and industry.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Artificial intelligence remained the defining theme of the technology "
        "landscape. OpenAI, which was founded in 2013, emerged as the most "
        "commercially visible AI laboratory following the widespread adoption of its "
        "large language model products. Competitive dynamics intensified as "
        "established technology platforms accelerated their own foundation-model "
        "programmes, prompting a wave of strategic partnerships, licensing "
        "agreements, and talent acquisitions across the industry.",
        body_style,
    )
)

story.append(PageBreak())

# ── PAGE 4: Historical & Physical Constants ─────────────────────────────────
story.append(
    Paragraph("3. Historical Context &amp; Physical Constants", section_header_style)
)

story.append(
    Paragraph(
        "Any rigorous analytical framework benefits from grounding in well-established "
        "facts, whether historical, geopolitical, or scientific. This report references "
        "a number of such benchmarks that serve as stable reference points against "
        "which trends and projections can be evaluated.",
        body_style,
    )
)

story.append(
    Paragraph(
        "From a geopolitical perspective, the United States has 50 states, a figure "
        "that has remained constant since Hawaii's admission in 1959. The federal "
        "structure of the Union continues to shape domestic technology regulation, "
        "with individual states increasingly enacting privacy and AI-governance "
        "legislation in the absence of comprehensive federal frameworks.",
        body_style,
    )
)

story.append(
    Paragraph(
        "Historically, World War II ended in 1945, marking a decisive turning point "
        "in the modern geopolitical order. The post-war settlement established the "
        "multilateral institutions — including the United Nations, the International "
        "Monetary Fund, and the World Bank — that continue to underpin global "
        "economic governance. Understanding this institutional heritage is essential "
        "for contextualising contemporary debates around trade, sovereignty, and "
        "technology standards.",
        body_style,
    )
)

story.append(
    Paragraph(
        "In the physical sciences, the speed of light is approximately "
        "299,792 kilometres per second, a universal constant that underpins GPS "
        "satellite navigation, fibre-optic communications, and deep-space telemetry. "
        "Advances in photonic computing and quantum communication protocols seek to "
        "exploit this fundamental limit in novel ways, with implications for "
        "cryptography, high-frequency trading infrastructure, and next-generation "
        "wireless networks.",
        body_style,
    )
)

story.append(Spacer(1, 10 * mm))
story.append(
    Paragraph(
        "— End of Report —",
        disclaimer_style,
    )
)
story.append(
    Paragraph(
        "© 2024 Horizon Research Institute. All rights reserved. "
        "Reproduction in whole or in part without written permission is prohibited.",
        disclaimer_style,
    )
)

# ---------------------------------------------------------------------------
# Build the PDF
# ---------------------------------------------------------------------------
doc.build(story)
print(f"PDF created: {output_path.resolve()}")
