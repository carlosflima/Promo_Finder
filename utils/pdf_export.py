# -*- coding: utf-8 -*-
"""Exportação simples de resultados para PDF."""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from config import HISTORY_DIR


def export_products_to_pdf(products: list, filename: str = None) -> str:
    os.makedirs(HISTORY_DIR, exist_ok=True)
    filename = filename or f"promocoes_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    path = os.path.join(HISTORY_DIR, filename)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    rows = [["Produto", "Preço", "Desconto", "Loja", "Fonte"]]
    for p in products:
        rows.append([p.get("title", ""), f"R$ {float(p.get('price', 0)):.2f}", f"{p.get('discount_percent', 0):.0f}%", p.get("store", "-"), p.get("site", "-")])
    table = Table(rows, repeatRows=1, colWidths=[8*cm, 3*cm, 2.5*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#14213D")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .3, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    doc.build([Paragraph("Relatório de Promoções", styles["Title"]), Spacer(1, .3*cm), table])
    return path
