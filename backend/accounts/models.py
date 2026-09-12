from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role for role-based access control."""

    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        HR = 'HR', 'HR / Admin'
        STUDENT = 'STUDENT', 'Student'
        TEACHER = 'TEACHER', 'Teacher'
        PARENT = 'PARENT', 'Parent'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    REQUIRED_FIELDS = ['role']

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def is_staff_role(self) -> bool:
        """True for management roles (Super Admin / HR)."""
        return self.role in (self.Roles.SUPER_ADMIN, self.Roles.HR)

    def grant_role_modules(self) -> None:
        """No-op hook kept for API symmetry (module set is derived from role)."""
        return None

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'