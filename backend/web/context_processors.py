"""Template context processor — injects the role's module menu into every page."""
from common.modules import group_modules, is_admin_role, ROLE_LABELS


def user_role_context(request):
    """Expose the current user's role-based module menu to all templates."""
    user = request.user
    if not getattr(user, 'is_authenticated', False):
        return {
            'nav_groups': [],
            'is_management': False,
            'role_label': '',
        }
    role = getattr(user, 'role', '')
    return {
        'nav_groups': group_modules(role),
        'is_management': is_admin_role(role),
        'role_label': ROLE_LABELS.get(role, role),
    }