from django.db import models


class Skill(models.Model):
    """Section 3 — Skills with categories and proficiency."""
    CATEGORIES = [
        ('PROGRAMMING', 'Programming'),
        ('TECHNICAL', 'Technical Skills'),
        ('FRAMEWORK', 'Frameworks'),
        ('DATABASE', 'Database'),
        ('CLOUD', 'Cloud'),
        ('TOOL', 'Tools'),
        ('SOFT', 'Soft Skills'),
        ('OTHER', 'Other'),
    ]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='skills')
    category = models.CharField(max_length=20, choices=CATEGORIES, default='OTHER')
    name = models.CharField(max_length=100)
    proficiency = models.PositiveSmallIntegerField(default=3, help_text='1-5')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'skills'

    def __str__(self):
        return f'{self.name} ({self.category})'