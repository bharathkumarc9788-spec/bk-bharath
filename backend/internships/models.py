from django.db import models


class Internship(models.Model):
    """Section 5 — Internships."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='internships')
    company = models.CharField(max_length=200)
    role_name = models.CharField(max_length=200, blank=True, verbose_name='Role / Designation')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    responsibilities = models.TextField(blank=True)
    technologies = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    certificate = models.FileField(upload_to='internship_certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f'{self.role_name} @ {self.company}'