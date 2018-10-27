from django import template
from django.utils.html import format_html
from django.utils.encoding import force_text

register = template.Library()


@register.filter()
def to_accusative(value, model):
    verbose_name = str(model._meta.verbose_name)  # declared in Meta
    try:
        new_name = force_text(model.accusative_case())  # a custom class method (lives in your Model)
    except AttributeError:
        return format_html(value)
    return format_html(value.replace(verbose_name, new_name))
