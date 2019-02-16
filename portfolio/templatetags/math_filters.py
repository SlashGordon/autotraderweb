from django import template

register = template.Library()


@register.simple_tag
def price_total(price, size, commission):
    # you would need to do any localization of the result here
    return abs(price * size + commission)
