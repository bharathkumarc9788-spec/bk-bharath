from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Activity / approval history record."""
    action = models.CharField(max_length=100)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='audit_logs')
    actor_role = models.CharField(max_length=20, blank=True)
    target_type = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.actor} - {self.action}'


def log_action(actor, action, target_type='', target_id='', details=''):
    """Small helper to record an audit entry (never raises)."""
    try:
        AuditLog.objects.create(
            action=action,
            actor=actor,
            actor_role=getattr(actor, 'role', '') if actor else '',
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else '',
            details=details,
        )
    except Exception:
        pass