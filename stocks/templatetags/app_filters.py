from django import template

register = template.Library()


@register.filter(name='get_type')
def get_type(value):
    value_type = type(value).__name__
    return value_type


@register.filter(name='index')
def index(list_type, i):
    return list_type[int(i)]
