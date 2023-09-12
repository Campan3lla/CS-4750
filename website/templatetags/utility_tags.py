from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def display_name(value):
    words = value.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)


@register.filter
def get(obj, key):
    return obj.__getitem__(key) if obj.__contains__(key) else ''
