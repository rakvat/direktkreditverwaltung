import io
from typing import List

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape

from dkapp.operations.reports import InterestPerContract


class InterestLettersGenerator:
    def __init__(self, contacts: List[InterestPerContract]):
        self.buffer = io.BytesIO()

        story = []
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading1']

        for contact in contacts:
            story.append(Paragraph(f"Hallo {contact.full_name},", styleN))
            story.append(PageBreak())

        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.build(story)
        self.buffer.seek(0)
