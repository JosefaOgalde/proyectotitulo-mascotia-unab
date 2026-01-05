from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario o lista usando una clave/índice"""
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    elif isinstance(dictionary, (list, tuple)):
        try:
            return dictionary[key] if 0 <= key < len(dictionary) else None
        except (IndexError, TypeError):
            return None
    return None

