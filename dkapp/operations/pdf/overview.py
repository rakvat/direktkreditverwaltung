import io
import copy

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4


from dkapp.operations.reports import InterestTransferListReport
from dkapp.templatetags.my_filters import euro, fraction
from .util import print_fonts


class OverviewGenerator:

    TABLE_HEADERS = [
        "Datum",
        "Vorgang",
        "Betrag",
        "Zinssatz",
        "verbleibende Tage im Jahr",
        "verbleibender Anteil am Jahr",
        "Zinsen",
    ]

    def __init__(self, report: InterestTransferListReport, year: int, today: str):
        print_fonts()
        self.buffer = io.BytesIO()
        story = []

        styles = getSampleStyleSheet()
        styleH1 = styles['Heading2']
        styleH2 = styles['Heading3']
        styleB = copy.deepcopy(styles['Normal'])
        styleB.spaceAfter = 0.1*cm
        styleB.fontName = 'Helvetica-Bold'
        styleTableN = copy.deepcopy(styles['Normal'])
        styleTableN.fontSize = 8
        styleTableB = copy.deepcopy(styles['Normal'])
        styleTableB.fontName = 'Helvetica-Bold'
        styleTableB.fontSize = 8
        table_style = TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.Color(1,1,1), colors.Color(0.95,0.95,0.95)]),
            ('GRID', (0,0), (-1,-1), 0.05, colors.grey),
        ])

        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.leftMargin = 1*cm
        doc.rightMargin = 1*cm
        doc.topMargin = 1*cm
        doc.bottomMargin = 1*cm
        header_row = [Paragraph(text, styleTableB) for text in self.TABLE_HEADERS]

        story.append(Paragraph(f"Zinsen für das Jahr {year}", styleH1))
        for data in report.per_contract_data:
            story.append(Paragraph(f"Direktkreditvertrag Nr. {data.contract.number}, {data.contract.contact}", styleH2))
            story.append(Paragraph(f"Kontostand {today}: {euro(data.contract.balance)}", styleB))
            story.append(Paragraph(f"Zinsberechung {year}:", styleB))
            story.append(Table(
                [header_row, *[
                    [
                        Paragraph(row.date.strftime('%d.%m.%Y'), styleTableN),
                        Paragraph(row.label, styleTableN),
                        Paragraph(euro(row.amount), styleTableN),
                        Paragraph(fraction(row.interest_rate), styleTableN),
                        Paragraph(str(row.days_left_in_year), styleTableN),
                        Paragraph(fraction(row.fraction_of_year), styleTableN),
                        Paragraph(euro(row.interest), styleTableN),
                    ]
                    for row in data.interest_rows
                ]],
                style=table_style,
                colWidths=[2*cm, 2*cm, 2.7*cm, 1.6*cm, 4*cm, 4.3*cm, 2*cm],
            ))
            story.append(Spacer(1, 0.1*cm))
            story.append(Paragraph(f"Zinsen {year}: {euro(data.interest)}", styleB))

        doc.build(story)
        self.buffer.seek(0)
