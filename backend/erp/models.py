"""ERPS — School ERP modules.

Covers the full School ERP tree requested by the client:

    Administration (school profile, academic years, boards, houses, holidays)
    Board Management (CBSE / Matriculation configuration)
    Subject Management (+ teacher allocation)
    Homework & Assignment (+ submissions & grading)
    PET / Physical Education
    Finance & Fee Management (+ payments / ledger)
    Hostel Management (hostels, rooms, allocations)
    HRMS (employee master)
    Inventory Management (items + stock movements)
    Communication (announcements)
    Audit Logs (system activity)
    Reports & Analytics (+ CSV exports)

Role rules: SUPER_ADMIN / HR manage everything; TEACHER creates homework,
PET records and grades; STUDENT / PARENT get read-only scoped views.
"""
from django.conf import settings
from django.db import models

from academics.models import ClassSection, Department, Subject  # noqa: F401


# ---------------------------------------------------------------------------
# Administration Management
# ---------------------------------------------------------------------------
class SchoolProfile(models.Model):
    name = models.CharField(max_length=200, default='My School')
    code = models.CharField(max_length=20, blank=True)
    board = models.CharField(max_length=40, blank=True, default='CBSE')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    motto = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    name = models.CharField(max_length=30, unique=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class SchoolBoard(models.Model):
    BOARD_TYPES = [('CBSE', 'CBSE'), ('MATRIC', 'Matriculation'),
                   ('STATE', 'State Board'), ('ICSE', 'ICSE')]
    name = models.CharField(max_length=60)
    board_type = models.CharField(max_length=10, choices=BOARD_TYPES, default='CBSE')
    exam_pattern = models.TextField(blank=True)
    grading_rules = models.TextField(blank=True)
    promotion_rules = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_board_type_display()})'


class House(models.Model):
    name = models.CharField(max_length=60)
    color = models.CharField(max_length=30, blank=True)
    captain = models.CharField(max_length=100, blank=True)
    vice_captain = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Holiday(models.Model):
    title = models.CharField(max_length=120)
    date = models.DateField()
    description = models.TextField(blank=True)
    is_working_day = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.title} ({self.date})'


# ---------------------------------------------------------------------------
# Homework & Assignment
# ---------------------------------------------------------------------------
class Homework(models.Model):
    STATUS = [('OPEN', 'Open'), ('CLOSED', 'Closed')]
    klass = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='homeworks')
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    max_marks = models.PositiveSmallIntegerField(default=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.klass} · {self.title}'


class HomeworkSubmission(models.Model):
    STATUS = [('SUBMITTED', 'Submitted'), ('PENDING', 'Pending'),
              ('LATE', 'Late'), ('GRADED', 'Graded')]
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE,
                                related_name='homework_submissions')
    submitted_at = models.DateTimeField(null=True, blank=True)
    text = models.TextField(blank=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PENDING')

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'{self.student} → {self.homework}'


# ---------------------------------------------------------------------------
# PET / Physical Education
# ---------------------------------------------------------------------------
class PetRecord(models.Model):
    RATING = [('Excellent', 'Excellent'), ('Good', 'Good'),
              ('Average', 'Average'), ('Needs Work', 'Needs Work')]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE,
                                related_name='pet_records')
    assessment_date = models.DateField()
    endurance = models.CharField(max_length=20, choices=RATING, default='Good')
    flexibility = models.CharField(max_length=20, choices=RATING, default='Good')
    strength = models.CharField(max_length=20, choices=RATING, default='Good')
    agility = models.CharField(max_length=20, choices=RATING, default='Good')
    sports = models.CharField(max_length=120, blank=True)
    coach_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-assessment_date']

    def __str__(self):
        return f'PET · {self.student}'
# ---------------------------------------------------------------------------
# Finance & Fee Management
# ---------------------------------------------------------------------------
class FeeStructure(models.Model):
    FREQ = [('TERM', 'Term'), ('HALF_YEARLY', 'Half-Yearly'),
            ('YEARLY', 'Yearly'), ('MONTHLY', 'Monthly')]
    name = models.CharField(max_length=120)
    klass = models.ForeignKey(ClassSection, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=12, choices=FREQ, default='YEARLY')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FeePayment(models.Model):
    METHOD = [('CASH', 'Cash'), ('CARD', 'Card'), ('UPI', 'UPI'), ('BANK', 'Bank Transfer')]
    STATUS = [('PAID', 'Paid'), ('PARTIAL', 'Partial'), ('PENDING', 'Pending')]
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE,
                                related_name='fee_payments')
    fee = models.ForeignKey(FeeStructure, null=True, blank=True, on_delete=models.SET_NULL)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_on = models.DateField()
    method = models.CharField(max_length=10, choices=METHOD, default='CASH')
    reference = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PAID')

    class Meta:
        ordering = ['-paid_on']

    def __str__(self):
        return f'{self.student} {self.amount_paid}'


# ---------------------------------------------------------------------------
# Hostel Management
# ---------------------------------------------------------------------------
class Hostel(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    warden_name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HostelRoom(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveSmallIntegerField(default=3)
    room_type = models.CharField(max_length=30, blank=True, default='Triple')

    class Meta:
        ordering = ['hostel__name', 'room_number']

    def __str__(self):
        return f'{self.hostel} · {self.room_number}'


class HostelAllocation(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE,
                                related_name='hostel_allocations')
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='allocations')
    bed_number = models.CharField(max_length=10, blank=True)
    check_in = models.DateField()
    check_out = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'{self.student} → {self.room}'
# ---------------------------------------------------------------------------
# HRMS — Employee Master
# ---------------------------------------------------------------------------
class Employee(models.Model):
    EMPLOYMENT = [('PERMANENT', 'Permanent'), ('CONTRACT', 'Contract'),
                  ('INTERN', 'Intern'), ('PROBATION', 'Probation')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='erp_employee')
    emp_id = models.CharField(max_length=30, blank=True)
    department = models.ForeignKey(Department, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='employees')
    designation = models.CharField(max_length=120, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    employment_status = models.CharField(max_length=12, choices=EMPLOYMENT, default='PERMANENT')

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.designation})'

    @property
    def name(self):
        return str(self)


# ---------------------------------------------------------------------------
# Inventory Management
# ---------------------------------------------------------------------------
class InventoryCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=20, blank=True, default='pcs')
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    supplier = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def low_stock(self):
        return self.quantity <= self.reorder_level


class InventoryMovement(models.Model):
    MOVEMENT = [('PURCHASE', 'Purchase'), ('ISSUE', 'Issue'), ('TRANSFER', 'Transfer'),
                ('ADJUSTMENT', 'Adjustment'), ('DAMAGED', 'Damaged'), ('LOST', 'Lost')]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=12, choices=MOVEMENT, default='PURCHASE')
    quantity = models.IntegerField(default=1)
    date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.item} · {self.movement_type} {self.quantity}'


# ---------------------------------------------------------------------------
# Communication — Announcements
# ---------------------------------------------------------------------------
class Announcement(models.Model):
    AUDIENCE = [('ALL', 'Everyone'), ('PARENT', 'Parents'),
                ('TEACHER', 'Teachers'), ('STUDENT', 'Students')]
    title = models.CharField(max_length=150)
    body = models.TextField()
    audience = models.CharField(max_length=12, choices=AUDIENCE, default='ALL')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
        return f'{self.title} ({self.date})'