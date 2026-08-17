# ==============================================================================
# pdf_report.py - Certified Field Inspection PDF Report Generator
# Standardized against BIS (IS 10500:2012) & Jal Jeevan Mission Specifications
# ==============================================================================

import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def _generate_map_snapshot(latitude, longitude):
    """
    Generates a cropped snapshot of the regional contamination map with a pin
    marking the exact sample location for PDF embedding.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        base_map_path = os.path.join(os.path.dirname(__file__), "kriging_contamination_map.png")
        if not os.path.exists(base_map_path):
            return None
        img = mpimg.imread(base_map_path)

        fig, ax = plt.subplots(figsize=(4.8, 2.8))
        ax.imshow(img)
        ax.axis("off")

        if latitude is not None and longitude is not None:
            lon_min, lon_max = 78.30, 78.68
            lat_min, lat_max = 9.05, 9.42
            panel_w = img.shape[1] * 0.42
            panel_h = img.shape[0] * 0.90
            x_off = img.shape[1] * 0.04
            y_off = img.shape[0] * 0.05

            frac_x = (longitude - lon_min) / (lon_max - lon_min)
            frac_y = 1 - (latitude - lat_min) / (lat_max - lat_min)
            px = x_off + frac_x * panel_w
            py = y_off + frac_y * panel_h

            if 0 <= px <= img.shape[1] and 0 <= py <= img.shape[0]:
                ax.plot(px, py, marker="v", markersize=14, color="#FF1A1A",
                        markeredgecolor="black", markeredgewidth=1.2, zorder=10)
                ax.annotate("Sample Point", (px, py), xytext=(px + 30, py - 20),
                            fontsize=8, fontweight="bold", color="#111111",
                            arrowprops=dict(arrowstyle="->", color="#111111"))

        plt.tight_layout(pad=0.1)
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception:
        return None


def generate_certified_report(
    location_name: str,
    season: str,
    hpi_value: float,
    hei_value: float,
    safety_category: str,
    input_mode: str,
    input_params: dict,
    remediation_plan: dict,
    latitude: float = None,
    longitude: float = None,
    compliance_list: list = None
) -> BytesIO:
    """
    Builds a high-impact certified field inspection PDF report.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=12*mm, bottomMargin=12*mm,
        leftMargin=15*mm, rightMargin=15*mm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"],
                                 fontSize=13, alignment=TA_CENTER, spaceAfter=2, fontName="Helvetica-Bold", textColor=colors.HexColor("#0A1418"))
    subtitle_style = ParagraphStyle("SubTitleStyle", parent=styles["Normal"],
                                    fontSize=8.5, alignment=TA_CENTER, textColor=colors.HexColor("#4A606E"), spaceAfter=8)
    section_heading = ParagraphStyle("SectionHeading", parent=styles["Heading2"],
                                     fontSize=10, spaceBefore=6, spaceAfter=4, fontName="Helvetica-Bold", textColor=colors.HexColor("#13242C"))
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#222222"))
    small_style = ParagraphStyle("SmallStyle", parent=styles["Normal"], fontSize=7.5, leading=9.5, textColor=colors.HexColor("#444444"))

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("MINISTRY OF JAL SHAKTI &middot; GOVT. OF INDIA", subtitle_style))
    elements.append(Paragraph("CERTIFIED GROUNDWATER QUALITY & HEAVY METAL FIELD REPORT", title_style))
    elements.append(Paragraph("Smart India Hackathon SIH25067 | Tamil Nadu Water Supply & Drainage Board (TWAD)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2A9D8F"), spaceAfter=8))

    # 2. Metadata Grid
    report_time = datetime.now().strftime("%d-%m-%Y %H:%M IST")
    coord_text = f"{latitude:.5f} N, {longitude:.5f} E" if (latitude and longitude) else "Not Specified"
    
    meta_data = [
        [Paragraph("<b>Borewell / Location:</b>", small_style), Paragraph(location_name or "Kadaladi Station", small_style),
         Paragraph("<b>Date & Time:</b>", small_style), Paragraph(report_time, small_style)],
        [Paragraph("<b>GPS Coordinates:</b>", small_style), Paragraph(coord_text, small_style),
         Paragraph("<b>Hydrological Season:</b>", small_style), Paragraph(season, small_style)],
        [Paragraph("<b>Evaluation Mode:</b>", small_style), Paragraph(f"<b>{input_mode}</b>", small_style),
         Paragraph("<b>Inspection Authority:</b>", small_style), Paragraph("CIT ECE Water Intelligence Group", small_style)]
    ]
    meta_table = Table(meta_data, colWidths=[38*mm, 52*mm, 40*mm, 50*mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F2F7F8")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1DFE4")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6))

    # 3. Primary Risk Readout Box
    if safety_category == "Safe":
        badge_bg = colors.HexColor("#5C9271")
        badge_text = "POTABLE / SAFE QUALITY"
    elif safety_category == "Moderate":
        badge_bg = colors.HexColor("#C99A44")
        badge_text = "MODERATE CONTAMINATION (FILTRATION ADVISED)"
    else:
        badge_bg = colors.HexColor("#C4602F")
        badge_text = "CRITICAL HAZARD - NON-POTABLE"

    readout_data = [
        [
            Paragraph(f"<b>PREDICTED HPI SCORE:</b> <font size='12'><b>{hpi_value:.1f}</b></font>", body_style),
            Paragraph(f"<b>EVALUATION INDEX (HEI):</b> <font size='10'><b>{hei_value:.2f}</b></font>", body_style),
            Paragraph(f"<font color='white'><b>{badge_text}</b></font>", ParagraphStyle("BadgeP", parent=small_style, alignment=TA_CENTER))
        ]
    ]
    readout_table = Table(readout_data, colWidths=[65*mm, 55*mm, 60*mm])
    readout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#EAEFF2")),
        ('BACKGROUND', (2,0), (2,0), badge_bg),
        ('ALIGN', (2,0), (2,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor("#BDCCD4")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(readout_table)
    elements.append(Spacer(1, 6))

    # 4. Parameter Breakdown Table
    elements.append(Paragraph("1. Hydrochemical Parameters & Standard Compliance (BIS IS 10500:2012)", section_heading))
    
    table_rows = [
        [Paragraph("<b>Parameter</b>", small_style),
         Paragraph("<b>Measured / Est.</b>", small_style),
         Paragraph("<b>Permissible Limit (Si)</b>", small_style),
         Paragraph("<b>Status / Excess</b>", small_style)]
    ]

    # Physicochemical
    for p in ["pH", "TDS", "EC"]:
        if p in input_params:
            val = input_params[p]
            limit_str = "6.5 - 8.5" if p == "pH" else ("500 mg/L" if p == "TDS" else "750 uS/cm")
            status_p = "Compliant" if (p == "pH" and 6.5 <= val <= 8.5) or (p == "TDS" and val <= 1000) or (p == "EC" and val <= 1500) else "Elevated"
            table_rows.append([Paragraph(p, small_style), Paragraph(f"{val:.1f}", small_style), Paragraph(limit_str, small_style), Paragraph(status_p, small_style)])

    # Heavy Metals
    if compliance_list:
        for item in compliance_list:
            excess = f"+{item['excess_percentage']:.1f}%" if item['excess_percentage'] > 0 else "Compliant"
            table_rows.append([
                Paragraph(f"{item['name']} ({item['symbol']})", small_style),
                Paragraph(f"{item['concentration']:.4f} mg/L", small_style),
                Paragraph(f"{item['Si']:.4f} mg/L", small_style),
                Paragraph(f"{item['status']} ({excess})", small_style)
            ])
    elif "Cd" in input_params:
        for m in ["Cd", "Pb", "Fe", "Mn", "Cu", "Zn", "Ni"]:
            if m in input_params:
                table_rows.append([
                    Paragraph(m, small_style),
                    Paragraph(f"{input_params[m]:.4f} mg/L", small_style),
                    Paragraph("Standard", small_style),
                    Paragraph("Tested", small_style)
                ])

    param_table = Table(table_rows, colWidths=[48*mm, 38*mm, 44*mm, 50*mm])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#13242C")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1DFE4")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FBFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 6))

    # 5. Actionable Remediation Plan
    elements.append(Paragraph("2. Actionable Engineering Remediation & Community Treatment Plan", section_heading))
    
    rem_text = f"<b>Primary Verdict:</b> {remediation_plan.get('verdict', '')}<br/>"
    rem_text += f"<b>Estimated Treatment Cost:</b> Rs. {remediation_plan.get('estimated_cost_per_kl', 0.0):.2f} / kL (1000 Liters)<br/>"
    rem_text += "<b>Recommended Engineering Process Flow:</b><br/>"
    
    for step in remediation_plan.get("treatment_steps", []):
        rem_text += f"&bull; <b>{step['stage']}:</b> {step['technology']} &mdash; <i>{step['purpose']}</i> (Est: Rs. {step['cost_inr_kl']:.2f}/kL)<br/>"
        
    elements.append(Paragraph(rem_text, small_style))
    elements.append(Spacer(1, 6))

    # 6. Map Snapshot
    map_buf = _generate_map_snapshot(latitude, longitude)
    if map_buf:
        elements.append(Paragraph("3. Regional Spatial Location Verification", section_heading))
        elements.append(RLImage(map_buf, width=170*mm, height=50*mm))
        elements.append(Spacer(1, 6))

    # 7. Official Footer
    elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#A0B4BC"), spaceAfter=4))
    footer_text = "System Output &middot; AI-Driven Assessment of Heavy Metal Pollution Indices &middot; Verified via BIS IS 10500 Guidelines"
    elements.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=small_style, alignment=TA_CENTER, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    return buffer
