from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


def euro(value):
    value = round(float(value), 2)
    return f"{intcomma(int(value))},{('%0.2f' % value)[-2:]}€"


def fraction(value):
    return f"{int(value*100)},{('%0.2f' % (value * 100))[-2:]}%"


register.filter('euro', euro)
register.filter('faction', fraction)
