import io
from typing import List

from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageTemplate,
    BaseDocTemplate,
    Paragraph,
    Spacer,
    Frame,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape

from dkapp.operations.reports import InterestPerContract

class ThanksLettersGenerator:
    def __init__(self, contacts: List[InterestPerContract]):
        self.buffer = io.BytesIO()

        story = []
        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading1']

        doc = BaseDocTemplate(self.buffer, pagesize=landscape(A4))

        frameWidth = doc.width/2
        frameHeight = doc.height-.05*cm

        frames = []
        for frame in range(2):
            leftMargin = doc.leftMargin + frame*frameWidth
            column = Frame(leftMargin, doc.bottomMargin, frameWidth, frameHeight)
            frames.append(column)

        template = PageTemplate(frames=frames)
        doc.addPageTemplates(template)

        for contact in contacts:
            frame_floatables = []
            frame_floatables.append(Paragraph(f"Hallo {contact.first_name},", styleN))
            frame_floatables.append(Spacer(1, 8*cm))
            story.append(KeepTogether(frame_floatables))

        doc.build(story)
        self.buffer.seek(0)
