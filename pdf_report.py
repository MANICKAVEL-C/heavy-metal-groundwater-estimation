# ============================================================
# pdf_report.py - Generates a downloadable field report PDF
# Project: AI-Driven Assessment of Heavy Metal Pollution Indices
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime
import os


def _generate_map_snapshot(latitude, longitude):
    """
    Generates a cropped snapshot of the Kadaladi region contamination
    map with a marker pin showing the report's sample location, for
    embedding directly into the PDF. Returns a BytesIO PNG buffer,
    or None if the base map image / matplotlib isn't available.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        import numpy as np

        base_map_path = os.path.join(os.path.dirname(__file__), "kriging_contamination_map.png")
        if not os.path.exists(base_map_path):
            return None
        img = mpimg.imread(base_map_path)

        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.imshow(img)
        ax.axis("off")

        # The base map's left panel (risk map) spans roughly the left
        # half of the source image; approximate the location's pixel
        # position within that panel using its known geographic bounds
        # (Kadaladi study region, matching the Kriging grid extent).
        if latitude is not None and longitude is not None:
            lon_min, lon_max = 78.30, 78.68
            lat_min, lat_max = 9.05, 9.42
            panel_w = img.shape[1] * 0.42   # left panel approx width fraction
            panel_h = img.shape[0] * 0.90
            x_off = img.shape[1] * 0.04
            y_off = img.shape[0] * 0.05

            frac_x = (longitude - lon_min) / (lon_max - lon_min)
            frac_y = 1 - (latitude - lat_min) / (lat_max - lat_min)
            px = x_off + frac_x * panel_w
            py = y_off + frac_y * panel_h

            if 0 <= px <= img.shape[1] and 0 <= py <= img.shape[0]:
                ax.plot(px, py, marker="v", markersize=16, color="#FF2D2D",
                        markeredgecolor="black", markeredgewidth=1.2, zorder=10)
                ax.annotate("Sample\nLocation", (px, py), xytext=(px + 40, py - 30),
                            fontsize=8, fontweight="bold", color="#111111",
                            arrowprops=dict(arrowstyle="->", color="#111111"))

        plt.tight_layout(pad=0.2)
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception:
        return None


def generate_field_report(location_name, season, hpi_value, safety_category,
                            input_mode, input_params, recommended_action,
                            hei_value=None, latitude=None, longitude=None):
    """
    Builds a one-page PDF field report summarizing a single prediction.
    Returns a BytesIO buffer ready for st.download_button.

    hei_value, latitude, longitude are optional - if not provided, those
    rows/sections are simply omitted rather than shown as blank/broken.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                              topMargin=18*mm, bottomMargin=18*mm,
                              leftMargin=20*mm, rightMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"],
                                   fontSize=16, alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
                                      fontSize=10, alignment=TA_CENTER,
                                      textColor=colors.grey, spaceAfter=14)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"],
                                     fontSize=12, spaceBefore=10, spaceAfter=6)
    body_style = styles["Normal"]

    elements = []
    elements.append(Paragraph("Groundwater Heavy Metal Pollution Field Report", title_style))
    elements.append(Paragraph("SIH25067 &mdash; Ministry of Jal Shakti | Tamil Nadu Groundwater Monitoring", subtitle_style))
    elements.append(HRFlowable(width="100%", color=colors.grey, thickness=1))
    elements.append(Spacer(1, 10))

    # Sample details table (now includes coordinates when provided)
    report_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    coord_text = f"{latitude:.5f}, {longitude:.5f}" if (latitude is not None and longitude is not None) else "Not specified"
    details_data = [
        ["Location / Village", location_name or "Not specified"],
        ["Geographic Coordinates", coord_text],
        ["Sampling Season", season],
        ["Report Generated", report_date],
        ["Input Mode", input_mode],
    ]
    details_table = Table(details_data, colWidths=[60*mm, 100*mm])
    details_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 14))

    # Prediction result (now includes HEI when provided)
    elements.append(Paragraph("Prediction Result", heading_style))
    color_map = {"Safe": colors.HexColor("#2e7d32"),
                 "Moderate": colors.HexColor("#e65100"),
                 "Highly Polluted": colors.HexColor("#c62828")}
    cat_color = color_map.get(safety_category, colors.black)

    result_data = [["Predicted HPI (Heavy Metal Pollution Index)", f"{hpi_value:.1f}"]]
    if hei_value is not None:
        result_data.append(["Predicted HEI (Heavy Metal Evaluation Index)", f"{hei_value:.2f}"])
    result_data.append(["Safety Category", safety_category])
    cat_row_idx = len(result_data) - 1

    result_table = Table(result_data, colWidths=[100*mm, 60*mm])
    style_cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TEXTCOLOR", (1, cat_row_idx), (1, cat_row_idx), cat_color),
        ("FONTNAME", (1, cat_row_idx), (1, cat_row_idx), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]
    result_table.setStyle(TableStyle(style_cmds))
    elements.append(result_table)
    elements.append(Spacer(1, 14))

    # Map snapshot (cropped Kriging map with a marker at the sample location)
    map_buf = _generate_map_snapshot(latitude, longitude)
    if map_buf is not None:
        elements.append(Paragraph("Location on Contamination Risk Map", heading_style))
        elements.append(RLImage(map_buf, width=150*mm, height=96*mm))
        elements.append(Spacer(1, 10))

    # Input parameters used
    elements.append(Paragraph("Input Parameters Used", heading_style))
    param_rows = [[k, f"{v:.4f}" if isinstance(v, float) else str(v)] for k, v in input_params.items()]
    param_table = Table([["Parameter", "Value"]] + param_rows, colWidths=[80*mm, 80*mm])
    param_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4262")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 14))

    # Recommended action
    elements.append(Paragraph("Recommended Action", heading_style))
    elements.append(Paragraph(recommended_action, body_style))
    elements.append(Spacer(1, 14))

    # Disclaimer
    disclaimer_style = ParagraphStyle("Disclaimer", parent=styles["Normal"],
                                        fontSize=8, textColor=colors.grey,
                                        spaceBefore=10)
    elements.append(HRFlowable(width="100%", color=colors.lightgrey, thickness=0.5))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Disclaimer: This is a decision-support estimate generated by a machine learning "
        "model trained on statistically-grounded reference data, not a certified laboratory "
        "measurement. Use this report to prioritize locations for physical lab confirmation, "
        "not as a substitute for it. Generated by the AI-Driven Heavy Metal Pollution "
        "Assessment System (Chennai Institute of Technology, ECE Department).",
        disclaimer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def get_recommended_action(safety_category):
    actions = {
        "Safe": "No immediate action required. Continue routine periodic monitoring "
                 "as per standard groundwater surveillance schedule.",
        "Moderate": "Retest recommended within 30 days. Monitor nearby industrial/agricultural "
                     "activity that may be contributing to elevated readings.",
        "Highly Polluted": "Immediate borewell shutdown advised pending laboratory confirmation. "
                             "Notify local health authorities and prioritize this location for "
                             "urgent physical lab testing.",
    }
    return actions.get(safety_category, "Consult a water quality specialist for further guidance.")
