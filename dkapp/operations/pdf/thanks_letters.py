import io

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class ThanksLetters:
    def __init__(self):
        self.buffer = io.BytesIO()

        # p = canvas.Canvas(buffer)
        # p.drawString(100, 100, "Hello world.")
        # p.showPage()
        # p.save()
        # buffer.seek(0)
        # return FileResponse(buffer, filename='overview.pdf')

        doc = SimpleDocTemplate(self.buffer)
        styles = getSampleStyleSheet()
        Story = [Spacer(1,2*inch)]
        style = styles["Normal"]
        for i in range(100):
           bogustext = ("This is Paragraph number %s.  " % i) * 20
           p = Paragraph(bogustext, style)
           Story.append(p)
           Story.append(Spacer(1,0.2*inch))
        doc.build(Story)
        self.buffer.seek(0)
