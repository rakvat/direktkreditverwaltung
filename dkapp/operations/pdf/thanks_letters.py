import io
import yaml

from typing import List

from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageTemplate,
    PageBreak,
    BaseDocTemplate,
    Paragraph,
    Spacer,
    Frame,
    KeepTogether,
    Table,
    TableStyle,
)
from reportlab.lib import utils, colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape

from django.contrib.staticfiles.storage import staticfiles_storage

from dkapp.operations.reports import InterestPerContract


def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def print_fonts():
    c = canvas.Canvas('tmp.pdf')
    print(c.getAvailableFonts())

class ThanksLettersGenerator:
    LOGO_WIDTH=5.4*cm
    IMG_WIDTH=5.0*cm

    def __init__(self, contacts: List[InterestPerContract]):
        # print_fonts()
        snippets = self._get_snippets()

        self.buffer = io.BytesIO()

        story = [] # floatables
        styles = getSampleStyleSheet()
        styleH = styles['Heading3']
        styleH.fontName = 'Times-BoldItalic'
        styleH.fontSize = 14
        styleN = styles['Normal']
        styleN.spaceAfter = 0.3*cm
        styleN.fontName = 'Times-Italic'
        styleN.leading = 14
        styleN.fontSize = 12
        # styleN.backColor = colors.Color(0,1,0)

        # canvas = canvas.Canvas('myfile.pdf', pagesize=A4)
        # canvas.setFont('Helvetica', 12)
        doc = BaseDocTemplate(self.buffer, pagesize=landscape(A4))
        doc.leftMargin = 1*cm
        doc.rightMargin = 1*cm
        doc.topMargin = 1*cm
        doc.bottomMargin = 1*cm

        # doc.canvs.getAvailableFonts()
        # doc.canv.setFont('Helvetica', 12)

        frameWidth = doc.width/2
        leftRightSpace = 3*cm
        frameHeight = doc.height + 3*cm

        frames = []
        for frame in range(2):
            leftMargin = doc.leftMargin + frame*(frameWidth+leftRightSpace)
            column = Frame(leftMargin, doc.bottomMargin, frameWidth, frameHeight)
            frames.append(column)

        template = PageTemplate(frames=frames)
        doc.addPageTemplates(template)

        for contact in contacts:
            frame_floatables = []
            img = get_image(staticfiles_storage.path('custom/logo.png'), width=self.LOGO_WIDTH)
            table_style = TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('VALIGN', (0, 0), (0, 0), 'BOTTOM'),
                ('ALIGN', (0, 1), (0, 1), 'RIGHT'),
                ('VALIGN', (0, 1), (0, 1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
            frame_floatables.append(Table([[
                Paragraph(f"Hallo {contact.first_name},", styleH),
                img,
            ]], style=table_style, colWidths='*'))
            frame_floatables.append(Spacer(1, 0.4*cm))
            frame_floatables.append(Paragraph(snippets["thanks_what_happened"], styleN))
            frame_floatables.append(Paragraph(snippets["next_year"], styleN))
            frame_floatables.append(Paragraph(snippets["invitation"], styleN))
            frame_floatables.append(Paragraph(snippets["wish"], styleN))
            frame_floatables.append(Spacer(1, 0.5*cm))
            img = get_image(staticfiles_storage.path('custom/image.png'), width=self.IMG_WIDTH)
            table_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                # ('BACKGROUND', (0, 0), (-1, -1), colors.Color(1,0,0)),
            ])
            frame_floatables.append(Table([[
                img,
                Paragraph(snippets["greetings"], styleN),
            ]], style=table_style, colWidths='*'))
            story.append(KeepTogether(frame_floatables))
            # story.append(PageBreak()) # needed?

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

