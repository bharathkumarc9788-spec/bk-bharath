from django.db import models


class Achievement(models.Model):
    """Section 7 — Achievements with level."""
    LEVELS = [
        ('COLLEGE', 'College'),
        ('DISTRICT', 'District'),
        ('STATE', 'State'),
        ('NATIONAL', 'National'),
        ('INTERNATIONAL', 'International'),
    ]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200, verbose_name='Achievement')
    organization = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVELS, default='COLLEGE')
    description = models.TextField(blank=True)
    proof = models.FileField(upload_to='achievement_proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title