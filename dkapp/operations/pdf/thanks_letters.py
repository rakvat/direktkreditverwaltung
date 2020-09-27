import io
import yaml

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

from django.contrib.staticfiles.storage import staticfiles_storage

from dkapp.operations.reports import InterestPerContract

class ThanksLettersGenerator:
    def __init__(self, contacts: List[InterestPerContract]):
        snippets = self._get_snippets()

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
            frame_floatables.append(Paragraph(snippets["thanks_what_happened"], styleN))
            frame_floatables.append(Paragraph(snippets["next_year"], styleN))
            frame_floatables.append(Paragraph(snippets["invitation"], styleN))
            frame_floatables.append(Paragraph(snippets["wish"], styleN))
            frame_floatables.append(Paragraph(snippets["greetings"], styleN))
            frame_floatables.append(Spacer(1, 8*cm))
            story.append(KeepTogether(frame_floatables))

        doc.build(story)
        self.buffer.seek(0)

    def _get_snippets(self):
        path = staticfiles_storage.path('custom/text_snippets.yml')
        snippets = {}
        with open(path, 'r') as stream:
            try:
                snippets = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return snippets

