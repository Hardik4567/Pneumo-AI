"""
PneumoAI — PDF Report Generator  v2.0
======================================
Produces a styled, dark-themed clinical report containing:
  • Patient information table
  • AI prediction result (condition / confidence / severity)
  • Original chest X-ray image  (history.image_path)
  • Grad-CAM heatmap image       (history.heatmap_path)
  • AI interpretation paragraph
  • Medical disclaimer & footer

Drop-in replacement for the original generate_prediction_report().
All other files (report_service.py, router) stay unchanged.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

REPORT_DIRECTORY = Path("static/reports")
REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Page dimensions
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = A4
MARGIN = 15 * mm

# ---------------------------------------------------------------------------
# Colour palette  (matches the PneumoAI dark UI)
# ---------------------------------------------------------------------------

C_DARK_BG   = colors.HexColor("#c0c9f4")
C_PANEL     = colors.HexColor("#141929")
C_LABEL_COL = colors.HexColor("#1a2540")
C_BORDER    = colors.HexColor("#1e2d4a")
C_BLUE      = colors.HexColor("#4f8ef7")
C_TEAL      = colors.HexColor("#00d4aa")
C_RED       = colors.HexColor("#ff4757")
C_ORANGE    = colors.HexColor("#f0a060")
C_WHITE     = colors.HexColor("#ffffff")
C_GREY      = colors.HexColor("#8899bb")
C_PURPLE    = colors.HexColor("#7c5cbf")

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

def _style(name: str, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, **kw)


S_TITLE    = _style("title",   fontName="Helvetica-Bold",   fontSize=20, textColor=C_WHITE,  alignment=TA_CENTER, spaceAfter=5)
S_SUBTITLE = _style("sub",     fontName="Helvetica",        fontSize=9,  textColor=C_GREY,   alignment=TA_CENTER, spaceAfter=2)
S_SECTION  = _style("sec",     fontName="Helvetica-Bold",   fontSize=10, textColor=C_BLUE,   spaceBefore=6, spaceAfter=5)
S_LABEL    = _style("lbl",     fontName="Helvetica-Bold",   fontSize=8,  textColor=C_GREY)
S_VALUE    = _style("val",     fontName="Helvetica",        fontSize=9,  textColor=C_WHITE)
S_BODY     = _style("body",    fontName="Helvetica",        fontSize=8,  textColor=C_GREY,   leading=13, spaceAfter=4)
S_CAPTION  = _style("cap",     fontName="Helvetica-Oblique",fontSize=7,  textColor=C_GREY,   alignment=TA_CENTER, spaceBefore=3)
S_FOOTER   = _style("footer",  fontName="Helvetica",        fontSize=7,  textColor=C_GREY,   alignment=TA_CENTER)
S_DISCLAIM = _style("discl",   fontName="Helvetica-Oblique",fontSize=7,  textColor=C_ORANGE, leading=11)

def _result_style(color: colors.Color) -> ParagraphStyle:
    return _style(f"rc_{id(color)}", fontName="Helvetica-Bold", fontSize=13,
                  textColor=color, alignment=TA_CENTER)


# ---------------------------------------------------------------------------
# Reusable element builders
# ---------------------------------------------------------------------------

def _hr() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=C_BORDER,
                      spaceBefore=4, spaceAfter=8)


def _key_val_table(rows: list[tuple[str, str]],
                   col_widths: list | None = None) -> Table:
    """Two-column label / value table with dark theme."""
    cw = col_widths or [55 * mm, 107 * mm]
    data = [[Paragraph(k, S_LABEL), Paragraph(v, S_VALUE)] for k, v in rows]
    t = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), C_LABEL_COL),
        ("BACKGROUND",    (1, 0), (1, -1), C_PANEL),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _image_cell(image_path: str | None,
                label: str,
                img_w: float,
                img_h: float) -> list:
    """
    Return a list of flowables for one image panel cell.
    Falls back to a placeholder paragraph if the file is missing.
    """
    cell: list = []
    if image_path:
        p = Path(image_path)
        if p.exists():
            cell.append(RLImage(str(p), width=img_w, height=img_h))
        else:
            cell.append(Paragraph(f"[File not found:<br/>{image_path}]", S_BODY))
    else:
        cell.append(Paragraph("[Image not available]", S_BODY))
    cell.append(Paragraph(label, S_CAPTION))
    return cell


# ---------------------------------------------------------------------------
# Page background / accent bars
# ---------------------------------------------------------------------------

def _draw_background(canvas, doc) -> None:  # noqa: ANN001
    canvas.saveState()
    # Dark background
    canvas.setFillColor(C_DARK_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Top gradient bar  (blue → purple → teal)
    bar_h = 5
    canvas.setFillColor(C_BLUE)
    canvas.rect(0, PAGE_H - bar_h, PAGE_W / 3, bar_h, fill=1, stroke=0)
    canvas.setFillColor(C_PURPLE)
    canvas.rect(PAGE_W / 3, PAGE_H - bar_h, PAGE_W / 3, bar_h, fill=1, stroke=0)
    canvas.setFillColor(C_TEAL)
    canvas.rect(2 * PAGE_W / 3, PAGE_H - bar_h, PAGE_W / 3, bar_h, fill=1, stroke=0)
    # Bottom accent line
    canvas.setFillColor(C_TEAL)
    canvas.rect(0, 0, PAGE_W, 3, fill=1, stroke=0)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Severity helper
# ---------------------------------------------------------------------------

def _severity(disease: str, confidence: float) -> tuple[str, colors.Color]:
    if disease.upper() == "PNEUMONIA":
        if confidence >= 85:
            return "High Risk", C_RED
        return "Moderate", C_ORANGE
    return "Low Risk", C_TEAL


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

async def generate_prediction_report(history, user) -> str:
    """
    Generate a styled PDF prediction report.

    Parameters
    ----------
    history : ORM model instance
        Expected fields: history_id, patient_name, patient_age, patient_gender,
        prediction_date, detected_disease, confidence,
        image_path, heatmap_path
    user : ORM model instance
        Expected fields: full_name, email_id

    Returns
    -------
    str
        Relative path to the generated PDF file.
    """
    report_name = (
        f"prediction_report_{history.history_id}"
        f"_{int(datetime.now().timestamp())}.pdf"
    )
    report_path = REPORT_DIRECTORY / report_name

    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    # Convenience aliases
    disease    = (history.detected_disease or "Unknown").upper()
    confidence = float(history.confidence or 0.0)
    sev_label, sev_color = _severity(disease, confidence)
    result_color = C_RED if disease == "PNEUMONIA" else C_TEAL

    elements = []

    # ── Header ─────────────────────────────────────────────────────────
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph("PneumoAI", S_TITLE))
    elements.append(Paragraph("AI-Powered Pneumonia Detection Report", S_SUBTITLE))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y  –  %H:%M')}",
        S_SUBTITLE,
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(_hr())

    # ── Patient information ────────────────────────────────────────────
    elements.append(Paragraph("Patient Information", S_SECTION))
    elements.append(_key_val_table([
        ("Patient Name",    history.patient_name   or "—"),
        ("Age",             str(history.patient_age) if history.patient_age else "—"),
        ("Gender",          history.patient_gender or "—"),
        ("Physician",       user.full_name  if user else "—"),
        ("Email",           user.email_id   if user else "—"),
        ("Prediction Date", str(history.prediction_date) if history.prediction_date else "—"),
    ]))
    elements.append(Spacer(1, 5 * mm))

    # ── AI result banner (3-column) ───────────────────────────────────
    elements.append(Paragraph("AI Prediction Result", S_SECTION))

    result_table = Table(
        [
            # Header row
            [
                Paragraph("Detected Condition", S_LABEL),
                Paragraph("Confidence Score",   S_LABEL),
                Paragraph("Severity Level",     S_LABEL),
            ],
            # Value row
            [
                Paragraph(f"<b>{disease}</b>",           _result_style(result_color)),
                Paragraph(f"<b>{confidence:.2f}%</b>",   _result_style(C_TEAL)),
                Paragraph(f"<b>{sev_label}</b>",          _result_style(sev_color)),
            ],
        ],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )
    result_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("BACKGROUND",    (0, 1), (-1, 1), C_PANEL),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 5 * mm))

    # ── Images: X-ray + Heatmap side by side ─────────────────────────
    elements.append(Paragraph("Imaging", S_SECTION))

    img_w = 83 * mm
    img_h = 83 * mm

    xray_cell    = _image_cell(history.image_path,   "Original Chest X-Ray",          img_w, img_h)
    heatmap_cell = _image_cell(history.heatmap_path, "AI Attention Heatmap (Grad-CAM)", img_w, img_h)

    img_table = Table(
        [[xray_cell, heatmap_cell]],
        colWidths=[img_w + 4 * mm, img_w + 4 * mm],
    )
    img_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_PANEL),
        ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    elements.append(img_table)
    elements.append(Spacer(1, 5 * mm))

    # ── AI Interpretation ─────────────────────────────────────────────
    elements.append(Paragraph("AI Interpretation", S_SECTION))

    if disease == "PNEUMONIA":
        clinical = (
            "Signs consistent with pneumonia were detected. "
            "Immediate consultation with a qualified radiologist is strongly recommended."
        )
    else:
        clinical = (
            "No significant pneumonia indicators were detected. "
            "Regular health checkups are recommended."
        )

    elements.append(Paragraph(
        f"The uploaded chest X-ray image was analyzed using a <b>DenseNet-121</b> deep "
        f"learning model. The AI model predicted <b>{disease}</b> with a confidence score "
        f"of <b>{confidence:.2f}%</b>. {clinical}",
        S_BODY,
    ))
    elements.append(Spacer(1, 5 * mm))

    # ── Disclaimer & footer ───────────────────────────────────────────
    elements.append(_hr())
    elements.append(Paragraph(
        "⚠  Medical Disclaimer: This report is generated automatically using Artificial "
        "Intelligence and is intended for informational purposes only. It must not replace "
        "professional medical diagnosis. Please consult a qualified radiologist or physician "
        "before making any clinical decisions.",
        S_DISCLAIM,
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "PneumoAI  |  AI Assisted Medical Imaging Platform  |  Confidential",
        S_FOOTER,
    ))

    # ── Build ─────────────────────────────────────────────────────────
    doc.build(
        elements,
        onFirstPage=_draw_background,
        onLaterPages=_draw_background,
    )

    return str(report_path)