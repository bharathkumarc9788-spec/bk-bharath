from django.conf import settings
from django.db import models


class Teacher(models.Model):
    """Teacher profile + assigned students."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=150, blank=True)
    designation = models.CharField(max_length=150, blank=True)
    students = models.ManyToManyField('students.Student', blank=True, related_name='teachers_assigned')

    def __str__(self):
        return self.user.display_name


class Parent(models.Model):
    """Parent profile linked to students."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    students = models.ManyToManyField('students.Student', blank=True, related_name='parents')

    def __str__(self):
        return self.user.display_name


class TeacherFeedback(models.Model):
    """Section 9 — 360° teacher feedback across development dimensions."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='teacher_feedbacks')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_feedbacks')
    academic_performance = models.TextField(blank=True)
    attendance = models.CharField(max_length=20, blank=True, choices=[(x, x) for x in ('Excellent', 'Good', 'Average', 'Poor')])
    homework = models.CharField(max_length=20, blank=True, choices=[(x, x) for x in ('Excellent', 'Good', 'Average', 'Poor')])
    behaviour = models.CharField(max_length=20, blank=True, choices=[(x, x) for x in ('Excellent', 'Good', 'Average', 'Poor')])
    communication = models.TextField(blank=True, verbose_name='Communication evaluation')
    leadership = models.TextField(blank=True, verbose_name='Leadership evaluation')
    creativity = models.TextField(blank=True, verbose_name='Creativity evaluation')
    sports_pet = models.TextField(blank=True, verbose_name='Sports / PET')
    participation = models.TextField(blank=True, verbose_name='Participation / Activities')
    overall_rating = models.PositiveSmallIntegerField(default=3, help_text='1-5')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Feedback for {self.student.name}'


class ParentFeedback(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='parent_feedbacks')
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_feedbacks')
    rating = models.PositiveSmallIntegerField(default=3, help_text='1-5')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Parent feedback for {self.student.name}'