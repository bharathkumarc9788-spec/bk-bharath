from django.conf import settings
from django.db import models


class Notification(models.Model):
    EVENT_CHOICES = [
        ('PROFILE_CREATED', 'Profile Created'),
        ('PORTFOLIO_SUBMITTED', 'Portfolio Submitted'),
        ('PORTFOLIO_APPROVED', 'Portfolio Approved'),
        ('REVISION_REQUIRED', 'Revision Required'),
        ('PORTFOLIO_REJECTED', 'Portfolio Rejected'),
        ('PORTFOLIO_PUBLISHED', 'Portfolio Published'),
        ('GENERIC', 'Generic'),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                  on_delete=models.CASCADE, related_name='notifications')
    role = models.CharField(max_length=20, blank=True)  # broadcast target role
    event = models.CharField(max_length=50, choices=EVENT_CHOICES, default='GENERIC')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event}: {self.message[:60]}'