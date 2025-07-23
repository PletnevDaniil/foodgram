from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from io import BytesIO


def generate_shopping_list_pdf(recipes_in_shopping_list):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    ))

    story = []

    story.append(Paragraph("Список покупок", styles['TitleStyle']))
    story.append(Spacer(1, 0.2 * inch))

    data = []
    data.append(["Ингредиент", "Количество"])

    for item in recipes_in_shopping_list:
        name = item['ingredient__name']
        measurement_unit = item['ingredient__measurement_unit']
        total_amount = item['sum']

        amount = f"{total_amount} {measurement_unit}"
        data.append([name, amount])

    table = Table(data, colWidths=[4 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))

    story.append(table)

    doc.build(story)

    buffer.seek(0)
    return buffer
