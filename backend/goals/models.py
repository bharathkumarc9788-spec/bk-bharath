from django.db import models


class StudentGoal(models.Model):
    """Section 9 — Student goals."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='goals')
    category = models.CharField(max_length=50, choices=[('SHORT_TERM', 'Short Term'), ('LONG_TERM', 'Long Term')], default='SHORT_TERM')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('ACHIEVED', 'Achieved')], default='IN_PROGRESS')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}'