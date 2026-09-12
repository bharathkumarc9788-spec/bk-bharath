from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHR(BasePermission):
    """HR / Admin only."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'HR'


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'TEACHER'


class IsHROrReadOnly(BasePermission):
    """HR full access; others read-only."""
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.role == 'HR':
            return True
        return request.method in SAFE_METHODS


class IsOwnerOrHR(BasePermission):
    """Owner may edit own record; HR may edit all; others read-only."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'HR':
            return True
        owner = getattr(obj, 'student', None)
        if owner and owner.user_id == user.id:
            return True
        return request.method in SAFE_METHODS


class IsOwnerOrHROrTeacher(BasePermission):
    """Owners and HR may write; teachers read-only."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ('HR', 'TEACHER'):
            return True
        owner = getattr(obj, 'student', None)
        if owner and owner.user_id == user.id:
            return True
        return request.method in SAFE_METHODS