from django import template
from urllib.parse import urlencode


register = template.Library()


# https://stackoverflow.com/a/67526160
# replaces or makes a query parameter in the url
@register.simple_tag
def query_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value

    return dict_.urlencode()