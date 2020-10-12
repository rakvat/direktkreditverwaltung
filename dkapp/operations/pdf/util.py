import copy
from typing import List

from reportlab.lib import colors, utils
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, TableStyle, Table, Paragraph

from dkapp.operations.reports import InterestDataRow
from dkapp.templatetags.my_filters import euro, fraction

INTEREST_TABLE_HEADERS = [
    "Datum",
    "Vorgang",
    "Betrag",
    "Zinssatz",
    "verbleibende Tage im Jahr",
    "verbleibender Anteil am Jahr",
    "Zinsen",
]

INTERST_TABLE_STYLE = TableStyle([
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.Color(1,1,1), colors.Color(0.95,0.95,0.95)]),
    ('GRID', (0,0), (-1,-1), 0.05, colors.grey),
])

INTEREST_TABLE_WIDTHS = [2*cm, 2*cm, 2.7*cm, 1.6*cm, 4*cm, 4.3*cm, 2*cm]


def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def print_fonts():
    c = canvas.Canvas('tmp.pdf')
    print(c.getAvailableFonts())


def interest_year_table(rows: List[InterestDataRow]):
    styles = getSampleStyleSheet()
    styleTableN = copy.deepcopy(styles['Normal'])
    styleTableN.fontSize = 8
    styleTableB = copy.deepcopy(styles['Normal'])
    styleTableB.fontName = 'Helvetica-Bold'
    styleTableB.fontSize = 8
    header_row = [Paragraph(text, styleTableB) for text in INTEREST_TABLE_HEADERS]

    return Table(
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
            for row in rows
        ]],
        style=INTERST_TABLE_STYLE,
        colWidths=INTEREST_TABLE_WIDTHS,
    )
