from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib import utils
from reportlab.lib.units import cm

def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def print_fonts():
    c = canvas.Canvas('tmp.pdf')
    print(c.getAvailableFonts())

