from django.conf import settings
from django.db import models


# ---------------------------------------------------------------------------
# Department & Subjects
# ---------------------------------------------------------------------------
class Department(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)
    head = models.ForeignKey('TeacherProfile', null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='head_of_departments')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})' if self.code else self.name


# ---------------------------------------------------------------------------
# Teacher Management
# ---------------------------------------------------------------------------
class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='academic_teacher')
    emp_id = models.CharField(max_length=30, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='teachers')
    subjects = models.ManyToManyField(Subject, blank=True, related_name='teachers')
    date_joined_institute = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def name(self):
        return str(self)


class TeacherAttendance(models.Model):
    STATUS = [('PRESENT', 'Present'), ('ABSENT', 'Absent'),
              ('LEAVE', 'Leave'), ('LATE', 'Late')]
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='PRESENT')
    late_minutes = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ('teacher', 'date')

    def __str__(self):
        return f'{self.teacher} - {self.date} ({self.status})'


class LeaveRequest(models.Model):
    LEAVE_TYPES = [('CASUAL', 'Casual'), ('SICK', 'Sick'), ('EARNED', 'Earned')]
    STATUS = [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')]
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='leave_requests')
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES, default='CASUAL')
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.requester} {self.leave_type} {self.from_date}'


# ---------------------------------------------------------------------------
# Parent Management
# ---------------------------------------------------------------------------
class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='academic_parent')
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    children = models.ManyToManyField('students.Student', blank=True, related_name='academic_parents')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def name(self):
        return str(self)
# ---------------------------------------------------------------------------
# Class / Section Management
# ---------------------------------------------------------------------------
class ClassSection(models.Model):
    name = models.CharField(max_length=120, help_text='e.g. Computer Science')
    section = models.CharField(max_length=20, default='A')
    academic_year = models.CharField(max_length=20, default='2025-2026')
    class_teacher = models.ForeignKey(TeacherProfile, null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='classes_taught')
    capacity = models.PositiveSmallIntegerField(default=60)
    students = models.ManyToManyField('students.Student', blank=True, related_name='class_sections')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-academic_year', 'name']
        unique_together = ('name', 'section', 'academic_year')

    def __str__(self):
        return f'{self.name} - {self.section} ({self.academic_year})'

    @property
    def strength(self):
        return self.students.count()


class TimetableEntry(models.Model):
    DAYS = [('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'),
            ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday')]
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='timetable')
    day = models.CharField(max_length=3, choices=DAYS, default='MON')
    period = models.PositiveSmallIntegerField(default=1)
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    teacher = models.ForeignKey(TeacherProfile, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['day', 'period']

    def __str__(self):
        return f'{self.class_section} {self.get_day_display()} P{self.period}'


# ---------------------------------------------------------------------------
# Attendance Management
# ---------------------------------------------------------------------------
class AttendanceRecord(models.Model):
    STATUS = [('PRESENT', 'Present'), ('ABSENT', 'Absent'),
              ('LEAVE', 'Leave'), ('LATE', 'Late')]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_records')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='PRESENT')
    late_minutes = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'date')

    def __str__(self):
        return f'{self.student} {self.date} {self.status}'
# ---------------------------------------------------------------------------
# Examination & Results
# ---------------------------------------------------------------------------
class Exam(models.Model):
    STATUS = [('SCHEDULED', 'Scheduled'), ('IN_PROGRESS', 'In Progress'),
              ('COMPLETED', 'Completed')]
    name = models.CharField(max_length=150)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='exams')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} — {self.class_section}'


class ExamSchedule(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedule')
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    max_marks = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.exam} · {self.subject}'


class MarkEntry(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_marks')
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_passed = models.BooleanField(default=True)

    class Meta:
        ordering = ['student__name']

    def __str__(self):
        return f'{self.student} · {self.subject} · {self.obtained_marks}'

    @property
    def total(self):
        return float(self.internal_marks) + float(self.practical_marks) + float(self.obtained_marks)

    @property
    def percentage(self):
        schedule = self.exam.schedule.filter(subject=self.subject).first()
        maximum = schedule.max_marks if schedule else 100
        return round(self.total * 100 / maximum, 1) if maximum else 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 90:
            return 'A+'
        if p >= 80:
            return 'A'
        if p >= 70:
            return 'B+'
        if p >= 60:
            return 'B'
        if p >= 50:
            return 'C'
        return 'F'