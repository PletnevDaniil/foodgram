from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph,
    Spacer, Table, TableStyle,
)
from io import BytesIO


def generate_shopping_list_pdf(recipes_in_shopping_list):
    buffer = BytesIO()

    pdfmetrics.registerFont(TTFont(
        'DejaVuLGCSans',
        './api/fonts/DejaVuLGCSans.ttf'
    ))

    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFillColor(colors.lightblue)
    c.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    c.setFillColor(colors.white, alpha=0.85)
    c.rect(50, 50, letter[0] - 100, letter[1] - 100, fill=1, stroke=0)
    c.showPage()
    c.save()

    buffer.seek(0)
    background_buffer = buffer
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleStyle',
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=20,
        fontName='DejaVuLGCSans',
        textColor=colors.darkblue
    ))

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
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuLGCSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ]))

    story.append(table)

    doc.build(
        story,
        canvasmaker=lambda *args,
        **kw: canvas.Canvas(background_buffer, *args, **kw)
    )

    buffer = background_buffer
    buffer.seek(0)
    return buffer
