from django.db import models


class Activity(models.Model):
    """Section 8 — Activities and participation."""
    TYPES = [
        ('HACKATHON', 'Hackathon'),
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('CLUB', 'Club'),
        ('VOLUNTEERING', 'Volunteering'),
        ('COMPETITION', 'Competition'),
        ('EVENT', 'Event'),
        ('CO_CURRICULAR', 'Co-curricular'),
        ('SPORTS', 'Sports / PET'),
        ('OTHER', 'Other'),
    ]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=TYPES, default='OTHER')
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'activities'

    def __str__(self):
        return f'{self.activity_type}: {self.title}'