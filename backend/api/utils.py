from PyPDF2 import PdfFileReader, PdfFileWriter
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
    background_buffer = BytesIO()

    c = canvas.Canvas(background_buffer, pagesize=letter)
    c.setFillColor(colors.lightblue)
    c.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    c.setFillColor(colors.white, alpha=0.85)
    c.rect(50, 50, letter[0] - 100, letter[1] - 100, fill=1, stroke=0)
    c.showPage()
    c.save()
    background_buffer.seek(0)

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
        fontName='DejaVuLGCSans',
        textColor=colors.darkblue
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuLGCSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(
            '#FFFFFF',
            alpha=0.7
        )),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))

    story.append(table)

    doc.build(story)

    background = PdfFileReader(background_buffer)
    content = PdfFileReader(buffer)

    output = PdfFileWriter()
    page = content.getPage(0)
    page.mergePage(background.getPage(0))
    output.addPage(page)

    result_buffer = BytesIO()
    output.write(result_buffer)
    result_buffer.seek(0)

    return result_buffer
