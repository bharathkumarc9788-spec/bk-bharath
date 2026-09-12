from django.db import models


class Project(models.Model):
    """Section 4 — Projects."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    problem_statement = models.TextField(blank=True)
    technologies = models.CharField(max_length=500, blank=True, help_text='Comma separated')
    student_role = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    key_features = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f'{self.name}'