from django import template

register = template.Library()


def euro(value):
    return "{:,.2f}€".format(value).replace(",", "X").replace(".", ",").replace("X", ".")


def fraction(value):
    return f"{int(value*100)},{('%0.2f' % (value * 100))[-2:]}%"


register.filter('euro', euro)
register.filter('fraction', fraction)
