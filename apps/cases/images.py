"""Compatibility helper. The database owns the image association."""
def image_for(obj):
    return obj.imagen_url or '/static/core/images/item-placeholder.svg'
