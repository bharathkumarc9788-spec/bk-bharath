"""Template filters used by the Python (server-rendered) frontend."""
from django import template

register = template.Library()

STATUS_BADGES = {
    'DRAFT': 'badge-gray',
    'SUBMITTED': 'badge-blue',
    'UNDER_REVIEW': 'badge-amber',
    'APPROVED': 'badge-green',
    'REJECTED': 'badge-red',
    'REVISION_REQUIRED': 'badge-red',
    'PUBLISHED': 'badge-violet',
}


@register.filter
def status_badge(value):
    """Map a portfolio status code to a CSS badge class."""
    return STATUS_BADGES.get(value, 'badge-gray')


@register.filter
def humanize(value):
    """Replace underscores with spaces (e.g. UNDER_REVIEW -> UNDER REVIEW)."""
    if value is None:
        return ''
    return str(value).replace('_', ' ').strip()


@register.filter
def split(value, sep=','):
    """Split a comma-separated string into a list of trimmed tokens."""
    if not value:
        return []
    return [part.strip() for part in str(value).split(sep) if part.strip()]


@register.filter
def initial(value):
    """First character used for avatar initials."""
    return (str(value or '').strip() or ' ')[0]