import copy
import io

from reportlab.platypus import (
    Frame,
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
from reportlab.lib.enums import TA_RIGHT

from dkapp.operations.reports import InterestTransferListReport

from django.contrib.staticfiles.storage import staticfiles_storage

from dkapp.templatetags.my_filters import euro, fraction
from .util import get_image, interest_year_table, get_custom_texts


class InterestLettersGenerator:
    LOGO_WIDTH=6.5*cm

    def __init__(self, report: InterestTransferListReport, year: int, today: str):
        self.snippets = get_custom_texts()
        self.buffer = io.BytesIO()
        self.today = today
        story = []

        self._setup_styles()

        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.leftMargin = 1.5*cm
        doc.rightMargin = 1.5*cm
        doc.topMargin = 1.0*cm
        doc.bottomMargin = 1.5*cm

        for data in report.per_contract_data:
            story.extend(self._header(data))

            story.append(Spacer(1, 1.0*cm))
            story.append(Paragraph(f"Kontostand Direktkreditvertrag Nr. {data.contract.number}", self.styleH2))

            story.append(Spacer(1, 1.0*cm))
            story.append(Paragraph(f"Guten Tag {data.contract.contact.name}, ", self.styleN))

            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph((
                f"der Kontostand des Direktkreditvertrags Nr. {data.contract.number} beträgt heute, "
                f" am {today} {euro(data.contract.balance)}. "
                ), self.styleN))
            story.append(Paragraph(f"Die Zinsen für das Jahr {year} berechnen sich wie folgt:", self.styleN))
            story.append(Spacer(1, 0.3*cm))
            story.append(interest_year_table(data.interest_rows, narrow=True))
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(f"<b>Zinsen {year}:</b> {euro(data.interest)}", self.styleN))
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph((
                "Wir werden die Zinsen in den nächsten Tagen auf das im Vertrag angegebene Konto "
                "überweisen. Bitte beachten Sie, dass Sie sich selbst um die Abführung von "
                "Kapitalertragssteuer und Solidaritätszuschlag kümmern sollten, da wir das nicht "
                "übernehmen können. "
                ), self.styleN))
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("Vielen Dank!", self.styleN))
            story.append(Spacer(1, 1.5*cm))
            story.append(Paragraph("Mit freundlichen Grüßen", self.styleN))
            story.append(Spacer(1, 1.0*cm))
            story.append(Paragraph(self.snippets['your_name'], self.styleN))
            story.append(Paragraph(f"für die {self.snippets['gmbh_name']}", self.styleN))
            story.append(Spacer(1, 0.3*cm))

            story.append(PageBreak())


        doc.build(story, onFirstPage=self._draw_footer, onLaterPages=self._draw_footer)
        self.buffer.seek(0)

    def _setup_styles(self):
        self.lightgrey = colors.Color(0.8, 0.8, 0.8)
        self.grey = colors.Color(0.5, 0.5, 0.5)
        self.darkgrey = colors.Color(0.2, 0.2, 0.2)

        styles = getSampleStyleSheet()

        self.styleH2 = copy.deepcopy(styles['Heading2'])

        self.styleN = copy.deepcopy(styles['Normal'])
        self.styleN.fontName = 'Helvetica'
        self.styleN.fontSize = 12
        self.styleN.leading = 14

        self.styleNR = copy.deepcopy(self.styleN)
        self.styleNR.alignment = TA_RIGHT

        self.styleL = copy.deepcopy(self.styleN)
        self.styleL.fontSize = 8
        self.styleL.leading = 10

        self.styleG = copy.deepcopy(self.styleL)
        self.styleG.textColor = self.grey

        self.styleSS = copy.deepcopy(self.styleL)
        self.styleSS.fontSize = 6
        self.styleSS.leading = 8
        self.styleSS.textColor = self.darkgrey
        self.base_table_style = [
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]

    def _header(self, data):
        header = []
        img = get_image(staticfiles_storage.path('custom/logo.png'), width=self.LOGO_WIDTH)
        table_style = TableStyle([
            *self.base_table_style,
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        header.append(Table([[
            img,
        ]], style=table_style, colWidths='*'))

        table_style = TableStyle([
            *self.base_table_style,
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (0, -1), 'BOTTOM'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ])
        left_table_style = TableStyle([
            *self.base_table_style,
        ])
        right_table_style = TableStyle([
            *self.base_table_style,
        ])
        address_lines = data.contract.contact.address.split(',')
        left_column = Table([
            [Spacer(1, 1.2*cm)],
            [Paragraph(f"{self.snippets['gmbh_name']} - {self.snippets['street_no']} - {self.snippets['zipcode']} {self.snippets['city']}", self.styleSS)],
            [Spacer(1, 0.5*cm)],
            [Paragraph(data.contract.contact.name, self.styleN)],
            [Paragraph(address_lines[0], self.styleN)],
            [Spacer(1, 0.3*cm)],
            [Paragraph(address_lines[1], self.styleN)],
            ], style=left_table_style, colWidths='*')
        right_column = Table([
            [Paragraph("<i>Projekt im Mietshäuser Syndikat</i>", self.styleL)],
            [Spacer(1, 0.3*cm)],
            [Paragraph((
                f"{self.snippets['street_no']}<br/>"
                f"{self.snippets['zipcode']} {self.snippets['city']}"
            ), self.styleL)],
            [Spacer(1, 0.3*cm)],
            [Paragraph(f"e-mail: {self.snippets['email']}<br/>{self.snippets['web']}", self.styleL)],
        ], style=right_table_style, colWidths='*')
        date = Table([[ Paragraph(f"{self.snippets['city']}, {self.today}", self.styleNR) ]],
            style=TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]),
            colWidths=['*']
        )
        header.append(Table([[left_column, right_column]], style=table_style, colWidths=[13.4*cm, 4.2*cm]))

        header.append(Spacer(1, 1.5*cm))
        header.append(date)
        return header

    def _draw_footer(self, canvas, doc):
        footer = []
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ])
        footer.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.lightgrey,
            spaceBefore=2*cm,
            spaceAfter=0.2*cm,
            hAlign='CENTER',
            vAlign='BOTTOM',
        ))
        footer.append(Table([
            [
                Paragraph(f"{self.snippets['bank_name']},{self.snippets['bank_account_info']}", self.styleG),
                Paragraph(f"Geschäftsführung<br/>{self.snippets['gmbh_executive_board']}", self.styleG),
                Paragraph((
                    f"Registergericht: {self.snippets['gmbh_register_number']}<br/>"
                    f"Steuernummer: {self.snippets['gmbh_tax_number']}"
                ), self.styleG)
            ]
        ], style=table_style, colWidths='*'))
        Frame(1.5*cm, 0.5*cm, 18*cm, 2*cm).addFromList(footer, canvas)
