import io
import copy

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    HRFlowable,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4

from dkapp.operations.reports import InterestTransferListReport

from django.contrib.staticfiles.storage import staticfiles_storage

from dkapp.templatetags.my_filters import euro, fraction
from .util import get_image, interest_year_table


class InterestLettersGenerator:
    LOGO_WIDTH=5.4*cm

    def __init__(self, report: InterestTransferListReport, year: int, today: str):
        self.buffer = io.BytesIO()

        story = []
        styles = getSampleStyleSheet()
        styleN = copy.deepcopy(styles['Normal'])
        styleN.fontName = 'Helvetica'
        styleB = copy.deepcopy(styles['Normal'])
        styleB.fontName = 'Helvetica-Bold'

        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.leftMargin = 1*cm
        doc.rightMargin = 1*cm
        doc.topMargin = 1*cm
        doc.bottomMargin = 1*cm

        for data in report.per_contract_data:
            img = get_image(staticfiles_storage.path('custom/logo.png'), width=self.LOGO_WIDTH)
            table_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
            story.append(Table([[
                img,
            ]], style=table_style, colWidths='*'))

            table_style = TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('VALIGN', (0, 0), (0, 0), 'TOP'),
                ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                ('VALIGN', (0, 1), (0, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ])
            story.append(Table([
                [
                    Paragraph("Projekt im Mietshäuser Syndikat"),
                ], [
                    Paragraph("Straße\nStadt"),
                ], [
                    Paragraph("Absender"),
                    Paragraph("Email\nWebpage"),
                ]
            ], style=table_style, colWidths='*'))

            story.append(Paragraph(data.contract.contact.full_name, styleN))
            story.append(Paragraph(data.contract.contact.address, styleN))

            story.append(Paragraph(f"Kontostand Direktkreditvertrag Nr. {data.contract.number}", styleB))

            story.append(Paragraph(f"Guten Tag {data.contract.contact.full_name}, ", styleN))

            story.append(Paragraph((
                f"der Kontostand des Direktkreditvertrags Nr. {data.contract.number} beträgt heute, "
                f" am {today} {euro(data.contract.balance)}. "
                f"Die Zinsen für das Jahr {year} berechnen sich wie folgt:"
            )))
            story.append(interest_year_table(data.interest_rows))
            story.append(Spacer(1, 0.1*cm))
            story.append(Paragraph(f"Zinsen {year}: {euro(data.interest)}", styleB))
            story.append(Paragraph((
                "Wir werden die Zinsen in den nächsten Tagen auf das im Vertrag angegebene Konto "
                "überweisen. Bitte beachten Sie, dass Sie sich selbst um die Abführung von "
                "Kapitalertragssteuer und Solidaritätszuschlag kümmern sollten, da wir das nicht "
                "übernehmen können. "
            )))
            story.append(Paragraph("Vielen Dank!"))
            story.append(Paragraph("Mit freundlichen Grüßen"))
            story.append(Paragraph("Name Geschaeftsfuehrung"))
            story.append(Paragraph("für die GmbH Name"))

            story.append(HRFlowable(width="80%", thickness=1, lineCap='round', color=colors.black, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='BOTTOM', dash=None))

            story.append(self._footer())
            story.append(PageBreak())


        doc.build(story)
        self.buffer.seek(0)

    def _footer(self):
        return None
