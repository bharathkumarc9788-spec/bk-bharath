from django.db import models


class Education(models.Model):
    """Section 2 — Academic Information."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='education_records')
    college = models.CharField(max_length=200, blank=True, verbose_name='College / School')
    degree = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    year_of_study = models.CharField(max_length=20, blank=True)
    klass = models.CharField(max_length=20, blank=True, verbose_name='Class')
    section = models.CharField(max_length=20, blank=True)
    board = models.CharField(max_length=100, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    history = models.TextField(blank=True, help_text='Academic history / remarks')
    start_year = models.CharField(max_length=20, blank=True)
    end_year = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-end_year']

    def __str__(self):
        return f'{self.degree} @ {self.college}'