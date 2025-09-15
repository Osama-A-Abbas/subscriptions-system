"""
Custom template filters for form handling and styling.
"""

from django import template

register = template.Library()


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to a form field.
    
    Usage:
    {{ field|add_class:"form-control" }}
    """
    if not field:
        return field
    
    # Get existing classes
    existing_classes = field.field.widget.attrs.get('class', '')
    
    # Add new class if not already present
    if css_class and css_class not in existing_classes:
        if existing_classes:
            field.field.widget.attrs['class'] = f"{existing_classes} {css_class}"
        else:
            field.field.widget.attrs['class'] = css_class
    
    return field


@register.filter
def add_attr(field, attr_string):
    """
    Add attributes to a form field.
    
    Usage:
    {{ field|add_attr:"placeholder:Enter your name" }}
    {{ field|add_attr:"data-toggle:tooltip" }}
    """
    if not field or not attr_string:
        return field
    
    # Parse attribute string (format: "key:value" or "key")
    if ':' in attr_string:
        key, value = attr_string.split(':', 1)
        field.field.widget.attrs[key] = value
    else:
        # Boolean attribute
        field.field.widget.attrs[attr_string] = True
    
    return field


@register.filter
def field_type(field):
    """
    Get the widget type of a form field.
    
    Usage:
    {% if field|field_type == "TextInput" %}
        <!-- Handle text input -->
    {% endif %}
    """
    if not field:
        return None
    
    return field.field.widget.__class__.__name__


@register.filter
def is_checkbox(field):
    """
    Check if a field is a checkbox.
    
    Usage:
    {% if field|is_checkbox %}
        <!-- Handle checkbox -->
    {% endif %}
    """
    if not field:
        return False
    
    return field.field.widget.__class__.__name__ == 'CheckboxInput'


@register.filter
def is_select(field):
    """
    Check if a field is a select dropdown.
    
    Usage:
    {% if field|is_select %}
        <!-- Handle select -->
    {% endif %}
    """
    if not field:
        return False
    
    return field.field.widget.__class__.__name__ == 'Select'


@register.filter
def is_textarea(field):
    """
    Check if a field is a textarea.
    
    Usage:
    {% if field|is_textarea %}
        <!-- Handle textarea -->
    {% endif %}
    """
    if not field:
        return False
    
    return field.field.widget.__class__.__name__ == 'Textarea'


@register.filter
def has_error(field):
    """
    Check if a field has errors.
    
    Usage:
    {% if field|has_error %}
        <!-- Show error styling -->
    {% endif %}
    """
    if not field:
        return False
    
    return bool(field.errors)


@register.filter
def error_class(field, base_class="form-control"):
    """
    Add error class to a field if it has errors.
    
    Usage:
    {{ field|error_class:"form-control" }}
    """
    if not field:
        return base_class
    
    if field.errors:
        return f"{base_class} is-invalid"
    
    return base_class
