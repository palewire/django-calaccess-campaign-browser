import json
from django import template
from django.forms.models import model_to_dict
from calaccess_campaign_browser.utils.lazyencoder import LazyEncoder
register = template.Library()


@register.filter
def jsonify(obj):
    """
    Renders a Django model object as a JSON object.
    """
    d = model_to_dict(obj)
    return json.dumps(d, cls=LazyEncoder)
