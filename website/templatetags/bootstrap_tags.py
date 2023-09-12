from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def display_name(value):
    words = value.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)


@register.inclusion_tag('website/templatetags/bs_input.html')
def bs_input(field: BoundField, input_type=None, name=None, **kwargs):
    base_widget = field.subwidgets[0]
    name = name if name else field.name
    attrs = base_widget.data.get('attrs')
    attrs.update(kwargs)
    return {'field': field, 'type': input_type, 'name': name, 'attrs': attrs}


@register.inclusion_tag('website/templatetags/bs_error.html')
def bs_errors(errors):
    return {'errors': errors}


@register.inclusion_tag('website/templatetags/bs_button.html')
def bs_button(button_name='Submit', button_class='btn-primary'):
    return {'button_name': button_name, 'button_class': button_class}


@register.inclusion_tag('website/templatetags/bs_select.html')
def bs_select(field: BoundField, input_type=None, name=None):
    base_widget = field.subwidgets[0]
    name = field.name
    attrs = base_widget.data.get('attrs')
    return {'fields': fields}
