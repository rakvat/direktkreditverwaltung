import io
import copy

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4


from dkapp.operations.reports import InterestTransferListReport
from dkapp.templatetags.my_filters import euro, fraction

from .util import interest_year_table


class OverviewGenerator:

    def __init__(self, report: InterestTransferListReport, year: int, today: str):
        self.buffer = io.BytesIO()
        story = []

        styles = getSampleStyleSheet()
        styleH1 = styles['Heading2']
        styleH2 = styles['Heading3']
        styleB = copy.deepcopy(styles['Normal'])
        styleB.spaceAfter = 0.1*cm
        styleB.fontName = 'Helvetica-Bold'

        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.leftMargin = 1*cm
        doc.rightMargin = 1*cm
        doc.topMargin = 1*cm
        doc.bottomMargin = 1*cm

        story.append(Paragraph(f"Zinsen für das Jahr {year}", styleH1))
        for data in report.per_contract_data:
            story.append(Paragraph(f"Direktkreditvertrag Nr. {data.contract.number}, {data.contract.contact}", styleH2))
            story.append(Paragraph(f"Kontostand {today}: {euro(data.contract.balance)}", styleB))
            story.append(Paragraph(f"Zinsberechung {year}:", styleB))
            story.append(interest_year_table(data.interest_rows))
            story.append(Spacer(1, 0.1*cm))
            story.append(Paragraph(f"Zinsen {year}: {euro(data.interest)}", styleB))

        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"SUMME ZINSEN {year}: {euro(report.sum_interest)}", styleB))

        doc.build(story)
        self.buffer.seek(0)
