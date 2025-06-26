from django import template


register=template.Library()

@register.filter
def percent(part,whole):
    try:
        return round((part/whole)*100)
    except(ZeroDivisionError,TypeError):
        return 0

