from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom template filter to access dictionary values by key.
    Usage in template: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, '') 