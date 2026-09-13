"""Server-rendered Python frontend.

Replaces the React/Vite app with plain Django views + templates.
All data access goes through the ORM and the existing service layer
(portfolio.services, common.completion, analytics._BaseDashboard, audit.log_action).
"""
from datetime import date as date_cls
from datetime import timedelta
from functools import wraps
from io import BytesIO, StringIO

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from achievements.models import Achievement
from activities.models import Activity
from analytics.views import _BaseDashboard
from audit.models import AuditLog, log_action
from certifications.models import Certification
from common.completion import overall_completion, overview
from education.models import Education
from feedback.models import TeacherFeedback
from goals.models import StudentGoal
from internships.models import Internship
from notifications.models import Notification
from portfolio.models import (Portfolio, PortfolioApproval, PortfolioTemplate,
                              PortfolioVersion, PortfolioView)
from portfolio.services import (
    approve_portfolio, build_public_data, generate_portfolio, publish_portfolio,
    record_view, reject_portfolio, require_revision, submit_portfolio,
    validate_required,
)
from projects.models import Project
from skills.models import Skill
from students.models import Student
from students.views import BulkUploadView, _ensure_student_user

User = get_user_model()

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def role_required(*roles):
    """Decorator: require login, and optionally one of the given roles."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('web:login')
            if roles and request.user.role not in roles and not (
                    'HR' in roles and request.user.role == 'SUPER_ADMIN'):
                messages.error(request, 'You do not have access to that page.')
                return redirect('web:dashboard')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def visible_students(user):
    """Same scoping as the students API: students/parents only see their own."""
    if user.role in ('STUDENT', 'PARENT'):
        return Student.objects.filter(user=user)
    return Student.objects.all()


def visible_portfolios(user):
    """Same scoping as the portfolios API."""
    if user.role == 'STUDENT':
        return Portfolio.objects.filter(student__user=user)
    if user.role == 'TEACHER':
        profile = getattr(user, 'teacher_profile', None)
        if profile:
            return Portfolio.objects.filter(student__teachers_assigned=profile)
        return Portfolio.objects.none()
    return Portfolio.objects.all()


def can_edit_student(student, user):
    """Management may edit all; a student may edit their own profile."""
    return user.role in ('SUPER_ADMIN', 'HR') or (user.role == 'STUDENT' and student.user_id == user.id)


def _to_date(value):
    if not value:
        return None
    try:
        return date_cls.fromisoformat(str(value))
    except ValueError:
        return None


def _to_int(value):
    try:
        return int(value) if value not in (None, '') else None
    except (TypeError, ValueError):
        return None


def _to_decimal(value):
    from decimal import Decimal, InvalidOperation
    if not value:
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


DATE_FIELDS = {
    'projects': {'start_date', 'end_date'},
    'internships': {'start_date', 'end_date'},
    'certifications': {'issue_date', 'expiry_date'},
    'achievements': {'date'},
    'activities': {'date'},
    'goals': {'target_date'},
}
DECIMAL_FIELDS = {'education': {'cgpa', 'percentage'}}
INT_FIELDS = {'skills': {'proficiency'}}


def clean_section_data(section, raw):
    """Convert POST strings into model-ready values for a section."""
    data = {k: v for k, v in raw.items()}
    for field in DATE_FIELDS.get(section, ()):
        if field in data:
            data[field] = _to_date(data.get(field))
    for field in DECIMAL_FIELDS.get(section, ()):
        if field in data:
            data[field] = _to_decimal(data.get(field))
    for field in INT_FIELDS.get(section, ()):
        if field in data:
            data[field] = _to_int(data.get(field))
    return data


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------


# Demo credentials used by the login page role selector (professional demo UX).
DEMO_ACCOUNTS = {
    'SUPER_ADMIN': ('superadmin', 'superadmin123'),
    'HR': ('admin', 'admin123'),
    'TEACHER': ('teacher', 'teacher123'),
    'PARENT': ('parent', 'parent123'),
}
DEMO_ROLE_ORDER = ['SUPER_ADMIN', 'HR', 'STUDENT', 'TEACHER', 'PARENT']
DEMO_ROLE_LABELS = {
    'SUPER_ADMIN': 'Super Admin', 'HR': 'HR / Admin', 'STUDENT': 'Student',
    'TEACHER': 'Teacher', 'PARENT': 'Parent',
}


def _demo_student_credentials():
    """Pick the first seeded student so the Student role has a working demo login."""
    student = Student.objects.filter(user__isnull=False).first()
    if student and student.user:
        return (student.user.username, 'student123')
    return ('student@college.edu', 'student123')


def _login_credentials(role):
    """Resolve demo username/password for a requested role."""
    if role == 'STUDENT':
        return _demo_student_credentials()
    return DEMO_ACCOUNTS.get(role, (None, None))


def index_redirect(request):
    """Professional landing page for visitors; dashboard for signed-in users."""
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    published_qs = Portfolio.objects.filter(status=Portfolio.Status.PUBLISHED,
                                            slug__isnull=False).exclude(slug='')
    return render(request, 'web/landing.html', {
        'landing_stats': {
            'students': Student.objects.count(),
            'portfolios': Portfolio.objects.count(),
            'published': published_qs.count(),
            'views': sum(p.views_count for p in published_qs),
        },
        'published_samples': [
            {'slug': p.slug, 'name': p.student.name, 'dept': p.student.department,
             'views': p.views_count} for p in published_qs[:3]
        ],
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('web:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.display_name}!')
            return redirect('web:dashboard')
        messages.error(request, 'Invalid credentials. Try again.')
        return render(request, 'web/login.html', {'username': username})

    # Professional role selector: /login/?role=STUDENT prefills demo credentials.
    requested_role = request.GET.get('role', '')
    username = request.GET.get('username', '')
    password = request.GET.get('password', '')
    if requested_role:
        credentials = _login_credentials(requested_role)
        if credentials and credentials[0] and not username:
            username, password = credentials

    return render(request, 'web/login.html', {
        'username': username or 'admin',
        'password': password,
        'active_role': requested_role,
        'demo_role_options': [
            {'key': 'SUPER_ADMIN', 'label': 'Super Admin', 'tagline': 'Full system'},
            {'key': 'HR', 'label': 'HR / Admin', 'tagline': 'Management'},
            {'key': 'STUDENT', 'label': 'Student', 'tagline': 'My 360°'},
            {'key': 'TEACHER', 'label': 'Teacher', 'tagline': 'Teaching'},
            {'key': 'PARENT', 'label': 'Parent', 'tagline': 'Monitoring'},
        ],
        'demo_student_username': _demo_student_credentials()[0],
    })


def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request, 'You have been signed out.')
    return redirect('web:login')


def reset_password(request):
    return render(request, 'web/reset_password.html')


# --------------------------------------------------------------------------
# Dashboard  (mirrors analytics.views.DashboardView)
# --------------------------------------------------------------------------


@login_required
def dashboard(request):
    """Role-aware dashboard.

    SUPER_ADMIN / HR  → management overview (KPIs, charts, approval queue)
    TEACHER           → teaching overview (assigned students, review queue)
    STUDENT           → personal overview (own progress + portfolio status)
    PARENT            → monitoring overview (child's profile overview)
    """
    user = request.user
    base = _BaseDashboard()

    if user.role in ('SUPER_ADMIN', 'HR'):
        return _dashboard_management(request, user, base)
    if user.role == 'TEACHER':
        return _dashboard_teacher(request, user, base)
    if user.role == 'PARENT':
        return _dashboard_parent(request, user, base)
    return _dashboard_student(request, user, base)


def _dashboard_management(request, user, base):
    students = Student.objects.all()
    portfolios = Portfolio.objects.all()

    kpis = base._kpis(students, portfolios)
    bins = base._completion_bins(students)
    dept = base._department_analysis(students)
    support = base._support_students(students)

    status_counts = []
    for code, label in Portfolio.Status.choices:
        count = portfolios.filter(status=code).count()
        if count:
            status_counts.append({'status': code, 'label': label, 'count': count})

    approval_queue = portfolios.filter(
        status__in=[Portfolio.Status.SUBMITTED, Portfolio.Status.UNDER_REVIEW]
    ).order_by('updated_at')[:8]

    recent_students = [{
        'id': s.id, 'name': s.name, 'register_number': s.register_number,
        'department': s.department, 'email': s.email,
        'photo': s.profile_photo.url if s.profile_photo else '',
        'completion': overall_completion(s),
    } for s in students.order_by('-created_at')[:8]]

    recent_activities = AuditLog.objects.all()[:12]

    return render(request, 'web/dashboard.html', {
        'view_role': 'management',
        'kpis': kpis,
        'completion_bins': bins,
        'bins_max': max([b['value'] for b in bins] or [1]),
        'department_analysis': dept,
        'dept_max': max([d['count'] for d in dept] or [1]),
        'portfolio_status': status_counts,
        'support': support,
        'approval_queue': approval_queue,
        'recent_students': recent_students,
        'recent_activities': recent_activities,
        'is_teacher': False,
        'role_title': 'Management Overview',
    })


def _dashboard_teacher(request, user, base):
    teacher = getattr(user, 'teacher_profile', None)
    if teacher:
        students = teacher.students.all()
        portfolios = Portfolio.objects.filter(student__teachers_assigned=teacher)
    else:
        students = Student.objects.none()
        portfolios = Portfolio.objects.none()

    kpis = base._kpis(students, portfolios)
    support = base._support_students(students)

    approval_queue = portfolios.filter(
        status__in=[Portfolio.Status.SUBMITTED, Portfolio.Status.UNDER_REVIEW]
    ).order_by('updated_at')[:8]

    recent_students = [{
        'id': s.id, 'name': s.name, 'register_number': s.register_number,
        'department': s.department, 'email': s.email,
        'photo': s.profile_photo.url if s.profile_photo else '',
        'completion': overall_completion(s),
    } for s in students.order_by('-created_at')[:8]]

    return render(request, 'web/dashboard.html', {
        'view_role': 'teacher',
        'kpis': kpis,
        'completion_bins': base._completion_bins(students),
        'bins_max': 1,
        'department_analysis': [],
        'dept_max': 1,
        'portfolio_status': [],
        'support': support,
        'approval_queue': approval_queue,
        'recent_students': recent_students,
        'recent_activities': [],
        'is_teacher': True,
        'role_title': 'Teaching Overview',
    })


# --------------------------------------------------------------------------
# Students
# --------------------------------------------------------------------------


def _dashboard_student(request, user, base):
    student = getattr(user, 'student_profile', None)
    if not student:
        return render(request, 'web/dashboard.html', {
            'view_role': 'student', 'role_title': 'Student Overview',
        })
    portfolio = student.portfolios.first()
    status_counts = []
    if portfolio:
        status_counts.append({'status': portfolio.status, 'label': portfolio.get_status_display(), 'count': 1})
    return render(request, 'web/dashboard.html', {
        'view_role': 'student',
        'student': student,
        'completion': overview(student),
        'portfolio': portfolio,
        'portfolio_status': status_counts,
        'recent_activities': [],
        'support': [],
        'role_title': 'My Student Dashboard',
        'kpis': {'total_students': 1,
                 'portfolios_generated': 1 if portfolio else 0,
                 'pending_approval': 1 if portfolio and portfolio.status in ('SUBMITTED', 'UNDER_REVIEW') else 0,
                 'published_portfolios': 1 if portfolio and portfolio.status == 'PUBLISHED' else 0,
                 'incomplete_profiles': 1 if overall_completion(student) < 100 else 0,
                 'portfolio_views': portfolio.views_count if portfolio else 0,
                 'avg_completion': overall_completion(student)},
        'completion_bins': base._completion_bins(Student.objects.filter(pk=student.pk)),
        'bins_max': 1,
        'department_analysis': [],
        'dept_max': 1,
        'approval_queue': [],
    })


def _dashboard_parent(request, user, base):
    parent = getattr(user, 'parent_profile', None)
    children = parent.students.all() if parent else Student.objects.none()

    children_info = [{
        'id': s.id, 'name': s.name, 'register_number': s.register_number,
        'department': s.department, 'email': s.email,
        'completion': overall_completion(s),
        'portfolio_status': s.portfolios.first().status if s.portfolios.exists() else None,
    } for s in children]

    return render(request, 'web/dashboard.html', {
        'view_role': 'parent',
        'children': children_info,
        'role_title': 'Parent Dashboard',
        'kpis': {'total_students': len(children_info),
                 'portfolios_generated': 0, 'pending_approval': 0,
                 'published_portfolios': 0, 'incomplete_profiles': 0,
                 'portfolio_views': 0, 'avg_completion': 0},
        'completion_bins': [], 'bins_max': 1,
        'department_analysis': [], 'dept_max': 1,
        'portfolio_status': [], 'support': [], 'approval_queue': [],
        'recent_students': [], 'recent_activities': [], 'is_teacher': False,
    })


def students_list(request):
    qs = visible_students(request.user)

    search = request.GET.get('search', '').strip()
    department = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search:
        qs = qs.filter(Q(name__icontains=search) |
                       Q(register_number__icontains=search) |
                       Q(email__icontains=search) |
                       Q(department__icontains=search) |
                       Q(admission_number__icontains=search) |
                       Q(skills__name__icontains=search) |
                       Q(projects__name__icontains=search)).distinct()
    if department:
        qs = qs.filter(department__icontains=department)
    if status_filter:
        qs = qs.filter(portfolios__status=status_filter).distinct()

    departments = list(Student.objects.exclude(department='')
                       .values_list('department', flat=True).distinct().order_by('department'))

    students = [{
        'obj': s, 'completion': overall_completion(s),
        'status': s.portfolios.first().status if s.portfolios.exists() else None,
    } for s in qs.distinct()]

    return render(request, 'web/students.html', {
        'students': students,
        'departments': departments,
        'search': search,
        'department': department,
        'status': status_filter,
        'is_hr': request.user.role in ('SUPER_ADMIN', 'HR'),
    })


@role_required('HR')
def student_create(request):
    if request.method == 'POST':
        data = {k: request.POST.get(k, '') for k in (
            'register_number', 'name', 'student_id', 'admission_number', 'email',
            'phone', 'gender', 'date_of_birth', 'department', 'address', 'city',
            'state', 'github_url', 'linkedin_url', 'professional_summary')}
        data['date_of_birth'] = _to_date(data.get('date_of_birth'))
        if not data.get('register_number') or not data.get('name'):
            messages.error(request, 'Register number and name are required.')
            return render(request, 'web/student_form.html', {'form': data})
        try:
            student = Student.objects.create(**data)
        except IntegrityError:
            messages.error(request, 'A student with this register number already exists.')
            return render(request, 'web/student_form.html', {'form': data})
        _ensure_student_user(student)
        log_action(request.user, 'CREATE', 'Student', student.id,
                   f'Created student {student.name}')
        Notification.objects.create(
            recipient=student.user if student.user_id else None,
            role='STUDENT', event='PROFILE_CREATED',
            message='Your student profile has been created.')
        messages.success(request, f'Student {student.name} created!')
        return redirect('web:student_detail', student_id=student.id)

    return render(request, 'web/student_form.html', {'form': {}})


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    user = request.user
    if user.role in ('STUDENT', 'PARENT') and student.user_id != user.id:
        messages.error(request, 'You do not have access to that profile.')
        return redirect('web:students')

    return render(request, 'web/student_detail.html', {
        'student': student,
        'completion': overview(student),
        'tab': request.GET.get('tab', 'overview'),
        'show_form': request.GET.get('new') == '1',
        'can_edit': can_edit_student(student, user),
        'can_review': user.role in ('SUPER_ADMIN', 'HR', 'TEACHER'),
        'is_hr': user.role in ('SUPER_ADMIN', 'HR'),
        'education': student.education_records.all(),
        'skills': student.skills.all(),
        'projects': student.projects.all(),
        'internships': student.internships.all(),
        'certifications': student.certifications.all(),
        'achievements': student.achievements.all(),
        'activities': student.activities.all(),
        'feedbacks': student.teacher_feedbacks.all(),
        'goals': student.goals.all(),
        'section_schemas': {k: _normalize_schema(v) for k, v in SECTION_SCHEMAS.items()},
        'feedback_schema': _normalize_schema(FEEDBACK_SCHEMA),
    })


def _can_edit_or_deny(request, student):
    if not can_edit_student(student, request.user):
        messages.error(request, 'You do not have permission to edit this profile.')
        return False
    return True


@login_required
def personal_update(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if not _can_edit_or_deny(request, student):
        return redirect('web:student_detail', student_id=student.id)

    fields = ('name', 'register_number', 'student_id', 'admission_number', 'email',
              'phone', 'gender', 'date_of_birth', 'department', 'address', 'city',
              'state', 'github_url', 'linkedin_url', 'professional_summary')
    # Only touch fields that were actually submitted so a partial save never wipes data.
    changed = False
    for field in fields:
        if field not in request.POST:
            continue
        value = request.POST.get(field, '')
        if field == 'date_of_birth':
            value = _to_date(value)
        setattr(student, field, value)
        changed = True

    if not changed:
        messages.error(request, 'No fields were submitted.')
        return redirect(f"{reverse('web:student_detail', args=[student.id])}?tab=personal")

    try:
        student.save()
    except IntegrityError:
        messages.error(request, 'Could not save — register number already exists.')
    else:
        messages.success(request, 'Personal information saved')
    return redirect(f"{reverse('web:student_detail', args=[student.id])}?tab=personal")


SECTION_REGISTRY = {
    'education': {'model': Education, 'fields': (
        'college', 'degree', 'department', 'academic_year', 'year_of_study',
        'klass', 'section', 'board', 'cgpa', 'percentage', 'start_year',
        'end_year', 'history')},
    'skills': {'model': Skill, 'fields': ('name', 'category', 'proficiency')},
    'projects': {'model': Project, 'fields': (
        'name', 'description', 'problem_statement', 'technologies',
        'student_role', 'start_date', 'end_date', 'github_url', 'live_url',
        'key_features')},
    'internships': {'model': Internship, 'fields': (
        'company', 'role_name', 'start_date', 'end_date', 'responsibilities',
        'technologies', 'description')},
    'certifications': {'model': Certification, 'fields': (
        'name', 'issuing_organization', 'issue_date', 'expiry_date',
        'credential_id', 'url')},
    'achievements': {'model': Achievement, 'fields': (
        'title', 'organization', 'date', 'level', 'description')},
    'activities': {'model': Activity, 'fields': (
        'title', 'activity_type', 'organization', 'role', 'date', 'description')},
    'goals': {'model': StudentGoal, 'fields': (
        'title', 'category', 'target_date', 'status', 'description')},
}

FEEDBACK_FIELDS = (
    'academic_performance', 'attendance', 'homework', 'behaviour',
    'communication', 'leadership', 'creativity', 'sports_pet', 'participation',
    'overall_rating', 'remarks')

# (key, label, type, extra) — used by the generic section add-forms.
# type: text / number / date / url / select / textarea ; extra: step or options list
SECTION_SCHEMAS = {
    'education': [
        ('college', 'College / School'), ('degree', 'Degree'), ('department', 'Department'),
        ('academic_year', 'Academic Year'), ('year_of_study', 'Year of Study'),
        ('klass', 'Class'), ('section', 'Section'), ('board', 'Board'),
        ('cgpa', 'CGPA', 'number', '0.01'), ('percentage', 'Percentage', 'number', '0.01'),
        ('start_year', 'Start Year'), ('end_year', 'End Year'),
        ('history', 'Academic History', 'textarea'),
    ],
    'skills': [
        ('name', 'Skill Name'), ('category', 'Category', 'select',
                                 ['PROGRAMMING', 'TECHNICAL', 'FRAMEWORK', 'DATABASE',
                                  'CLOUD', 'TOOL', 'SOFT', 'OTHER']),
        ('proficiency', 'Proficiency (1-5)', 'number'),
    ],
    'projects': [
        ('name', 'Project Name'), ('description', 'Description', 'textarea'),
        ('problem_statement', 'Problem Statement', 'textarea'),
        ('technologies', 'Technologies (comma separated)'),
        ('student_role', 'Your Role'),
        ('start_date', 'Start Date', 'date'), ('end_date', 'End Date', 'date'),
        ('github_url', 'GitHub URL', 'url'), ('live_url', 'Live URL', 'url'),
        ('key_features', 'Key Features', 'textarea'),
    ],
    'internships': [
        ('company', 'Company'), ('role_name', 'Role / Designation'),
        ('start_date', 'Start Date', 'date'), ('end_date', 'End Date', 'date'),
        ('technologies', 'Technologies'), ('responsibilities', 'Responsibilities', 'textarea'),
        ('description', 'Description', 'textarea'),
    ],
    'certifications': [
        ('name', 'Certificate Name'), ('issuing_organization', 'Issuing Organization'),
        ('issue_date', 'Issue Date', 'date'), ('expiry_date', 'Expiry Date', 'date'),
        ('credential_id', 'Credential ID'), ('url', 'Certificate URL', 'url'),
    ],
    'achievements': [
        ('title', 'Achievement'), ('organization', 'Organization'), ('date', 'Date', 'date'),
        ('level', 'Level', 'select', ['COLLEGE', 'DISTRICT', 'STATE', 'NATIONAL', 'INTERNATIONAL']),
        ('description', 'Description', 'textarea'),
    ],
    'activities': [
        ('title', 'Title'), ('activity_type', 'Type', 'select',
                             ['HACKATHON', 'WORKSHOP', 'SEMINAR', 'CLUB', 'VOLUNTEERING',
                              'COMPETITION', 'EVENT', 'CO_CURRICULAR', 'SPORTS', 'OTHER']),
        ('organization', 'Organization'), ('role', 'Your Role'),
        ('date', 'Date', 'date'), ('description', 'Description', 'textarea'),
    ],
    'goals': [
        ('title', 'Goal'), ('category', 'Category', 'select',
                            [('SHORT_TERM', 'Short Term'), ('LONG_TERM', 'Long Term')]),
        ('target_date', 'Target Date', 'date'), ('status', 'Status', 'select',
            [('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('ACHIEVED', 'Achieved')]),
        ('description', 'Description', 'textarea'),
    ],
}

FEEDBACK_SCHEMA = [
    ('academic_performance', 'Academic Performance', 'textarea'),
    ('behaviour', 'Behaviour', 'select', ['Excellent', 'Good', 'Average', 'Poor']),
    ('communication', 'Communication Evaluation', 'textarea'),
    ('leadership', 'Leadership Evaluation', 'textarea'),
    ('creativity', 'Creativity', 'textarea'),
    ('sports_pet', 'Sports / PET', 'textarea'),
    ('participation', 'Participation / Activities', 'textarea'),
    ('overall_rating', 'Rating (1-5)', 'number'),
    ('remarks', 'Remarks', 'textarea'),
]


def _section_tab_redirect(student_id, section):
    return f"{reverse('web:student_detail', args=[student_id])}?tab={section}"


def _normalize_schema(fields):
    """Convert (key, label, type, extra) tuples into dicts templates can loop over."""
    out = []
    for f in fields:
        key, label = f[0], f[1]
        ftype = f[2] if len(f) > 2 else 'text'
        extra = f[3] if len(f) > 3 else None
        if ftype == 'select':
            options = [
                {'value': str(o[0]), 'label': str(o[1])}
                if isinstance(o, (tuple, list)) else {'value': str(o), 'label': str(o)}
                for o in (extra or [])
            ]
        else:
            options = []
        out.append({
            'key': key, 'label': label, 'type': ftype,
            'options': options,
            'step': str(extra) if ftype == 'number' else '',
        })
    return out


@login_required
def section_add(request, student_id, section):
    student = get_object_or_404(Student, pk=student_id)

    # Teacher feedback is written by teachers/HR — a separate permission gate,
    # because teachers do not otherwise get to edit a student's sections.
    if section == 'feedback':
        if request.user.role not in ('SUPER_ADMIN', 'HR', 'TEACHER'):
            messages.error(request, 'Only teachers/HR can add feedback.')
            return redirect(_section_tab_redirect(student_id, section))
        data = {k: request.POST.get(k, '') for k in FEEDBACK_FIELDS}
        data['overall_rating'] = _to_int(data.get('overall_rating')) or 3
        TeacherFeedback.objects.create(student=student, teacher=request.user, **data)
        log_action(request.user, 'FEEDBACK_ADDED', 'Student', student.id)
        if request.user.role == 'TEACHER' and not student.teachers_assigned.filter(user=request.user).exists():
            messages.warning(request, 'Feedback saved. You are not assigned to this student in the system.')
        else:
            messages.success(request, 'Teacher feedback added')
        return redirect(_section_tab_redirect(student_id, 'feedback'))

    if not _can_edit_or_deny(request, student):
        return redirect('web:student_detail', student_id=student.id)

    spec = SECTION_REGISTRY.get(section)
    if not spec:
        messages.error(request, 'Unknown section.')
        return redirect('web:student_detail', student_id=student.id)

    data = clean_section_data(section, {k: request.POST.get(k, '') for k in spec['fields']})
    try:
        spec['model'].objects.create(student=student, **data)
    except IntegrityError as exc:
        messages.error(request, f'Could not add: {exc}')
    else:
        log_action(request.user, 'SECTION_ADD', section.title(), student.id,
                   f'Added {section} for {student.name}')
        messages.success(request, 'Added successfully')
    return redirect(_section_tab_redirect(student_id, section))


@login_required
def section_delete(request, student_id, section, item_id):
    student = get_object_or_404(Student, pk=student_id)
    if not _can_edit_or_deny(request, student):
        return redirect('web:student_detail', student_id=student.id)

    spec = SECTION_REGISTRY.get(section)
    if spec:
        spec['model'].objects.filter(pk=item_id, student_id=student.id).delete()
        messages.success(request, 'Deleted')
    return redirect(_section_tab_redirect(student_id, section))


# --------------------------------------------------------------------------
# Bulk upload  (HR only)
# --------------------------------------------------------------------------


@role_required('HR')
def bulk_upload(request):
    preview = request.session.get('bulk_preview')
    report = request.session.pop('bulk_report', None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'import' and preview:
            created, failed = [], []
            for row in preview['valid']:
                try:
                    student = Student.objects.create(
                        register_number=row.get('register_number') or f'STU-{row.get("name", "")[:10]}',
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        phone=row.get('phone', ''),
                        gender=(row.get('gender') or 'MALE').upper(),
                        department=row.get('department', ''),
                        admission_number=row.get('admission_number', ''),
                    )
                    created.append(student)
                    log_action(request.user, 'student_bulk_create', 'Student', str(student.id))
                except IntegrityError:
                    failed.append({'row': row, 'reason': 'Register number already exists'})
            report = {
                'total': len(preview['valid']),
                'valid': len(created),
                'invalid': len(failed),
                'failed': failed,
            }
            request.session.pop('bulk_preview', None)
            request.session['bulk_report'] = report
            messages.success(request, f'Imported {len(created)} students')
            return redirect('web:bulk_upload')
        elif action == 'parse':
            file = request.FILES.get('file')
            if not file:
                messages.error(request, 'Choose a CSV or Excel file first')
            else:
                rows, errors = BulkUploadView()._parse(file)
                preview = {'total': len(rows) + len(errors), 'valid': rows, 'invalid': errors}
                request.session['bulk_preview'] = preview
                messages.success(request, f'Parsed {len(rows)} valid records')

    return render(request, 'web/bulk_upload.html', {
        'preview': preview,
        'report': report,
    })


@role_required('HR')
def download_template(request):
    csv_text = ('register_number,name,email,phone,gender,department,admission_number\n'
                '21CSE100,John Doe,john@college.edu,+919800000000,MALE,Computer Science,ADM-21CSE100\n')
    response = HttpResponse(csv_text, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students-upload-template.csv"'
    return response


# --------------------------------------------------------------------------
# Portfolio generator & templates
# --------------------------------------------------------------------------

TEMPLATE_PALETTES = {
    'navy': 'linear-gradient(135deg, #1e293b, #334155)',
    'indigo': 'linear-gradient(135deg, #312e81, #4f46e5)',
    'dark': 'linear-gradient(135deg, #0a0a0a, #1f2937)',
    'violet': 'linear-gradient(135deg, #4c1d95, #7c3aed)',
    'gray': 'linear-gradient(135deg, #475569, #64748b)',
}

TEMPLATE_ICONS = {
    'Developer': '\U0001F468\U0000200D\U0001F4BB', 'Creative': '\U0001F3A8',
    'Minimal': '\u2B1C', 'Modern': '\u2728',
}


def _can_generate(user, student):
    return user.role in ('SUPER_ADMIN', 'HR') or (user.role == 'STUDENT' and student.user_id == user.id)


@login_required
def portfolio_generator(request):
    user = request.user
    students = visible_students(user)
    templates = PortfolioTemplate.objects.filter(is_active=True)

    student_id = request.GET.get('student', request.POST.get('student_id', ''))
    template_id = request.GET.get('template', request.POST.get('template_id', ''))
    portfolio = None
    missing = []

    if request.method == 'POST':
        student = Student.objects.filter(pk=student_id).first() if student_id else None
        if not student:
            messages.error(request, 'Please select a student first.')
        elif not _can_generate(user, student):
            messages.error(request, 'You are not allowed to generate a portfolio for this student.')
        else:
            missing = validate_required(student)
            template = None
            if template_id:
                template = PortfolioTemplate.objects.filter(pk=template_id).first()
            if not template:
                template = (PortfolioTemplate.objects.filter(is_default=True).first()
                            or PortfolioTemplate.objects.first())
            try:
                portfolio = generate_portfolio(student, template, user)
            except Exception as exc:
                messages.error(request, f'Generation failed: {exc}')
            else:
                log_action(user, 'PORTFOLIO_GENERATED', 'Portfolio', str(portfolio.id),
                           f'Generated portfolio for {student.name}')
                messages.success(request, 'Portfolio generated!')

    return render(request, 'web/portfolio_generator.html', {
        'students': students,
        'templates': templates,
        'student_id': str(student_id) if student_id else '',
        'template_id': str(template_id) if template_id else '',
        'portfolio': portfolio,
        'missing': missing,
    })


@login_required
def portfolio_templates(request):
    templates = PortfolioTemplate.objects.filter(is_active=True)
    styled = []
    for t in templates:
        styled.append({
            'obj': t,
            'background': TEMPLATE_PALETTES.get(t.color_scheme, TEMPLATE_PALETTES['indigo']),
            'icon': TEMPLATE_ICONS.get(t.name, '\U0001F4BC'),
        })
    return render(request, 'web/portfolio_templates.html', {'templates': styled})


# --------------------------------------------------------------------------
# Portfolio workflow actions
# --------------------------------------------------------------------------


def _get_portfolio_for(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    qs = visible_portfolios(request.user)
    if not qs.filter(pk=pk).exists():
        messages.error(request, 'You do not have access to that portfolio.')
        return None
    return portfolio


@login_required
def portfolio_submit(request, pk):
    portfolio = _get_portfolio_for(request, pk)
    if portfolio:
        submit_portfolio(portfolio, request.user)
        log_action(request.user, 'PORTFOLIO_SUBMITTED', 'Portfolio', str(portfolio.id))
        messages.success(request, 'Submitted for review')
    return redirect('web:portfolio_generator')


@login_required
def portfolio_publish(request, pk):
    portfolio = _get_portfolio_for(request, pk)
    if portfolio and request.user.role in ('SUPER_ADMIN', 'HR', 'TEACHER'):
        try:
            publish_portfolio(portfolio, request.user)
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            log_action(request.user, 'PORTFOLIO_PUBLISHED', 'Portfolio', str(portfolio.id),
                       f'Public URL: /portfolio/public/{portfolio.slug}/')
            messages.success(request, 'Portfolio published!')
    return redirect('web:portfolio_generator')


@login_required
def portfolio_review(request, pk):
    portfolio = _get_portfolio_for(request, pk)
    if not portfolio or request.user.role not in ('SUPER_ADMIN', 'HR', 'TEACHER'):
        messages.error(request, 'Not authorized.')
        return redirect('web:portfolio_approval')
    action = request.POST.get('action')
    comments = request.POST.get('comments', '')
    if action == 'approve':
        approve_portfolio(portfolio, request.user, comments=comments or 'Approved by reviewer')
        log_action(request.user, 'PORTFOLIO_APPROVED', 'Portfolio', str(portfolio.id))
        messages.success(request, 'Portfolio approved')
    elif action == 'reject':
        reject_portfolio(portfolio, request.user, comments=comments)
        log_action(request.user, 'PORTFOLIO_REJECTED', 'Portfolio', str(portfolio.id), comments)
        messages.success(request, 'Portfolio rejected')
    elif action == 'revision':
        require_revision(portfolio, request.user, comments or 'Please make the requested changes.')
        log_action(request.user, 'PORTFOLIO_REVISION', 'Portfolio', str(portfolio.id), comments)
        messages.success(request, 'Revision requested')
    elif action == 'publish':
        try:
            publish_portfolio(portfolio, request.user)
        except ValueError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, 'Portfolio published!')
    return redirect(f"{reverse('web:portfolio_approval')}?portfolio={pk}")


@login_required
def portfolio_qr(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if portfolio.status != Portfolio.Status.PUBLISHED or not portfolio.slug:
        messages.error(request, 'QR is only available for published portfolios.')
        return redirect('web:portfolio_generator')
    import qrcode
    url = f"{settings.FRONTEND_URL}/portfolio/public/{portfolio.slug}/"
    img = qrcode.make(url)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="portfolio-qr-{portfolio.slug}.png"'
    return response


@role_required('HR', 'TEACHER')
def portfolio_approval(request):
    user = request.user
    portfolios = visible_portfolios(user)

    status_filter = request.GET.get('status', '')
    if status_filter:
        portfolios = portfolios.filter(status=status_filter)

    selected_id = request.GET.get('portfolio')
    if selected_id:
        detail = portfolios.filter(pk=selected_id).first()
    else:
        detail = portfolios.first()

    return render(request, 'web/portfolio_approval.html', {
        'portfolios': portfolios,
        'status_filter': status_filter,
        'status_choices': [
            'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REVISION_REQUIRED', 'REJECTED', 'PUBLISHED',
        ],
        'detail': detail,
    })


# --------------------------------------------------------------------------
# Published portfolios & analytics
# --------------------------------------------------------------------------


@role_required('HR', 'TEACHER')
def published_portfolios(request):
    portfolios = Portfolio.objects.filter(status=Portfolio.Status.PUBLISHED).order_by('-published_at')

    now = timezone.now()
    last_30 = PortfolioView.objects.filter(viewed_at__gte=now - timedelta(days=30))
    daily = {}
    for v in last_30:
        key = v.viewed_at.date().isoformat()
        daily[key] = daily.get(key, 0) + 1
    views = [{'date': d, 'views': c} for d, c in sorted(daily.items())][-14:]
    views_max = max([v['views'] for v in views] or [1])

    return render(request, 'web/published_portfolios.html', {
        'portfolios': portfolios,
        'views': views,
        'views_max': views_max,
    })


@role_required('HR', 'TEACHER')
def analytics(request):
    base = _BaseDashboard()
    now = timezone.now()
    last_30 = PortfolioView.objects.filter(viewed_at__gte=now - timedelta(days=30))
    daily = {}
    for v in last_30:
        key = v.viewed_at.date().isoformat()
        daily[key] = daily.get(key, 0) + 1
    views_series = [{'date': d, 'views': c} for d, c in sorted(daily.items())]

    students = Student.objects.all()
    portfolios = Portfolio.objects.all()

    avg_by_dept = []
    for dept in students.exclude(department='').values_list('department', flat=True).distinct()[:10]:
        items = students.filter(department=dept)
        if not items:
            continue
        avg = sum(overall_completion(s) for s in items[:100]) / items.count()
        avg_by_dept.append({'department': dept, 'avg_completion': round(avg)})

    status_counts = []
    for code, label in Portfolio.Status.choices:
        count = portfolios.filter(status=code).count()
        if count:
            status_counts.append({'status': code, 'label': label, 'count': count})

    published_by_dept = [
        {'department': p['student__department'] or 'Unknown', 'count': p['count']}
        for p in portfolios.filter(status=Portfolio.Status.PUBLISHED)
        .values('student__department').annotate(count=Count('id'))
    ]

    bins = base._completion_bins(students)
    views_max = max([v['views'] for v in views_series] or [1])
    dept_max = max([d['avg_completion'] for d in avg_by_dept] or [1])
    pub_max = max([d['count'] for d in published_by_dept] or [1])
    bins_max = max([b['value'] for b in bins] or [1])

    return render(request, 'web/analytics.html', {
        'views_series': views_series,
        'views_max': views_max,
        'total_views_30_days': last_30.count(),
        'published_by_department': published_by_dept,
        'pub_max': pub_max,
        'avg_by_dept': avg_by_dept,
        'dept_max': dept_max,
        'portfolio_status': status_counts,
        'completion_bins': bins,
        'bins_max': bins_max,
    })


# --------------------------------------------------------------------------
# Notifications
# --------------------------------------------------------------------------


def _user_notifications(user):
    return Notification.objects.filter(Q(recipient=user) | Q(recipient__isnull=True, role=user.role)).distinct()


@login_required
def notifications(request):
    items = _user_notifications(request.user)
    unread = items.filter(is_read=False).count()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all':
            items.update(is_read=True)
            messages.success(request, 'All notifications marked as read')
            return redirect('web:notifications')
        delete_id = request.POST.get('delete_id')
        if delete_id:
            items.filter(pk=delete_id).delete()
            messages.success(request, 'Notification removed')
            return redirect('web:notifications')

    return render(request, 'web/notifications.html', {'items': items, 'unread': unread})


# --------------------------------------------------------------------------
# Public portfolio (no login)
# --------------------------------------------------------------------------


def public_portfolio(request, slug):
    portfolio = Portfolio.objects.filter(slug=slug).first()
    if not portfolio or portfolio.status != Portfolio.Status.PUBLISHED:
        return render(request, 'web/public_portfolio.html', {
            'error': 'Portfolio not found or not published.',
        })

    record_view(portfolio)
    data = build_public_data(portfolio)
    return render(request, 'web/public_portfolio.html', {'data': data})