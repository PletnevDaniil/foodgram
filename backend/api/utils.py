from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)


def generate_shopping_list_pdf(recipes_in_shopping_list):
    buffer = BytesIO()

    pdfmetrics.registerFont(TTFont(
        'DejaVuLGCSans',
        './api/fonts/DejaVuLGCSans.ttf'
    ))

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
        fontName='DejaVuLGCSans',
        textColor=colors.darkgreen
    ))

    story = []

    story.append(Paragraph("Список покупок", styles['TitleStyle']))
    story.append(Spacer(1, 0.2 * inch))

    data = [["Ингредиент", "Количество"]]
    for item in recipes_in_shopping_list:
        name = item['ingredient__name']
        unit = item['ingredient__measurement_unit']
        amount = item['sum']
        data.append([name, f"{amount} {unit}"])

    table = Table(data, colWidths=[4 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuLGCSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))

    story.append(table)

    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.lightblue)
        canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)

        canvas.setFillColor(colors.white)
        canvas.rect(
            0.5 * inch, 0.5 * inch,
            letter[0] - inch, letter[1] - inch,
            fill=1, stroke=0
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=add_background, onLaterPages=add_background)

    buffer.seek(0)
    return buffer
