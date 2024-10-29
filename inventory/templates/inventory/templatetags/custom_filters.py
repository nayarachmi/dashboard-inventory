# inventory/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value, total):
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0