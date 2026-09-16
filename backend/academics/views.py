"""Academics modules — Teacher / Parent / Class / Department / Attendance / Exams.

Each management module follows a consistent pattern:
    GET  /academics/<module>/     -> list + stats + add form
    POST /academics/<module>/add/ -> create
    POST /academics/<module>/<pk>/delete/ -> remove

Attendance and Exams have their own richer workflows (marking grids, results,
report cards). Roles: SUPER_ADMIN / HR manage everything; TEACHER works with
assigned classes, attendance and marks; PARENT / STUDENT get read-only views
scoped to their children / themselves.
"""
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from audit.models import log_action
from common.modules import is_admin_role
from students.models import Student

from .models import (AttendanceRecord, ClassSection, Department, Exam,
                     ExamSchedule, LeaveRequest, MarkEntry, ParentProfile,
                     Subject, TeacherAttendance, TeacherProfile, TimetableEntry)

User = get_user_model()


def _manage_access(user):
    """Management roles (Super Admin / HR) can manage everything."""
    return is_admin_role(getattr(user, 'role', ''))
# ---------------------------------------------------------------------------
# Generic management modules (Teacher / Parent / Department / ClassSection)
# ---------------------------------------------------------------------------
def _module_choices():
    return {
        'teacher': {
            'model': TeacherProfile, 'title': 'Teacher Management',
            'sub': 'Registration · Profile · Qualification · Allocation',
            'icon': '👨‍🏫', 'schema': [
                {'key': 'username', 'label': 'Username / Email', 'type': 'text'},
                {'key': 'password', 'label': 'Password', 'type': 'password'},
                {'key': 'full_name', 'label': 'Full Name', 'type': 'text'},
                {'key': 'emp_id', 'label': 'Employee ID', 'type': 'text'},
                {'key': 'qualification', 'label': 'Qualification & Experience', 'type': 'text'},
                {'key': 'experience_years', 'label': 'Experience (years)', 'type': 'number'},
                {'key': 'phone', 'label': 'Phone', 'type': 'text'},
                {'key': 'department', 'label': 'Department', 'type': 'select',
                 'options': [{'value': d.id, 'label': d.name} for d in Department.objects.all()]},
            ],
            'render': lambda t: (
                f"<b>{t.name}</b><span class='muted'>{t.emp_id or '—'} · {t.department or '—'} · "
                f"{t.qualification or '—'} · {t.experience_years}y exp</span>"),
        },
        'parent': {
            'model': ParentProfile, 'title': 'Parent Management',
            'sub': 'Registration · Profile · Student Mapping · Contact',
            'icon': '👨‍👩‍👧', 'schema': [
                {'key': 'username', 'label': 'Username / Email', 'type': 'text'},
                {'key': 'password', 'label': 'Password', 'type': 'password'},
                {'key': 'full_name', 'label': 'Full Name', 'type': 'text'},
                {'key': 'phone', 'label': 'Phone', 'type': 'text'},
                {'key': 'emergency_contact', 'label': 'Emergency Contact', 'type': 'text'},
                {'key': 'occupation', 'label': 'Occupation', 'type': 'text'},
                {'key': 'address', 'label': 'Address', 'type': 'textarea'},
                {'key': 'children', 'label': 'Children (student ids, comma)', 'type': 'text'},
            ],
            'render': lambda p: (
                f"<b>{p.name}</b><span class='muted'>{p.phone or '—'} · {p.occupation or '—'} · "
                f"children: {p.children.count()}</span>"),
        },
        'department': {
            'model': Department, 'title': 'Department Management',
            'sub': 'Creation · Head · Subjects · Staff',
            'icon': '🏢', 'schema': [
                {'key': 'name', 'label': 'Department Name', 'type': 'text'},
                {'key': 'code', 'label': 'Code', 'type': 'text'},
                {'key': 'description', 'label': 'Description', 'type': 'textarea'},
                {'key': 'subjects', 'label': 'Subjects (comma separated)', 'type': 'text'},
            ],
            'render': lambda d: (
                f"<b>{d.name}</b><span class='muted'>{d.code or '—'} · staff: {d.teachers.count()} · "
                f"subjects: {d.subjects.count()}</span>"),
        },
        'class': {
            'model': ClassSection, 'title': 'Class / Section Management',
            'sub': 'Creation · Class Teacher · Students · Academic Year',
            'icon': '🏷️', 'schema': [
                {'key': 'name', 'label': 'Class Name (e.g. Computer Science)', 'type': 'text'},
                {'key': 'section', 'label': 'Section', 'type': 'text'},
                {'key': 'academic_year', 'label': 'Academic Year', 'type': 'text'},
                {'key': 'capacity', 'label': 'Capacity', 'type': 'number'},
                {'key': 'students', 'label': 'Student ids (comma)', 'type': 'text'},
            ],
            'render': lambda c: (
                f"<b>{c}</b><span class='muted'>class teacher: {c.class_teacher or '—'} · "
                f"strength: {c.strength}/{c.capacity}</span>"),
        },
    }


@login_required
def module_page(request, module):
    if not _manage_access(request.user):
        messages.error(request, 'Only management staff can access this module.')
        return redirect('web:dashboard')
    cfg = _module_choices().get(module)
    if not cfg:
        return redirect('web:dashboard')

    rendered = []
    for item in cfg['model'].objects.all().order_by('-pk')[:80]:
        rendered.append({'obj': item, 'html': cfg['render'](item)})
    stats = {
        'total': cfg['model'].objects.count(),
    }
    return render(request, 'academics/module_page.html', {
        'module': module, 'title': cfg['title'], 'sub': cfg['sub'],
        'icon': cfg['icon'], 'schema': cfg['schema'], 'items': rendered,
        'stats': stats,
    })


@login_required
def module_add(request, module):
    if not _manage_access(request.user):
        return redirect('web:dashboard')
    cfg = _module_choices().get(module)
    if not cfg or request.method != 'POST':
        return redirect('web:dashboard')

    data = {k: (request.POST.get(k, '') or '').strip() for k in (
        'name', 'description', 'username', 'password', 'full_name', 'emp_id', 'qualification',
        'experience_years', 'phone', 'department', 'emergency_contact',
        'occupation', 'address', 'children', 'code', 'subjects', 'section',
        'academic_year', 'capacity', 'students')}

    try:
        if module == 'teacher':
            parts = (data.get('full_name') or 'Teacher').split(' ', 1)
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['username'], 'role': 'TEACHER',
                          'first_name': parts[0],
                          'last_name': parts[1] if len(parts) > 1 else ''})
            if data['password']:
                user.set_password(data['password'])
                user.save()
            dept_id = int(data['department']) if data['department'].isdigit() else None
            tp, _ = TeacherProfile.objects.get_or_create(user=user)
            tp.emp_id = data['emp_id']; tp.qualification = data['qualification']
            tp.experience_years = int(data['experience_years'] or 0)
            tp.phone = data['phone']
            tp.department_id = dept_id
            tp.save()
            label = tp.name
        elif module == 'parent':
            parts = (data.get('full_name') or 'Parent').split(' ', 1)
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['username'], 'role': 'PARENT',
                          'first_name': parts[0],
                          'last_name': parts[1] if len(parts) > 1 else ''})
            if data['password']:
                user.set_password(data['password'])
                user.save()
            pp, _ = ParentProfile.objects.get_or_create(user=user)
            pp.phone = data['phone']; pp.emergency_contact = data['emergency_contact']
            pp.occupation = data['occupation']; pp.address = data['address']
            pp.save()
            ids = [int(i) for i in data['children'].split(',') if i.strip().isdigit()]
            pp.children.set(Student.objects.filter(pk__in=ids))
            label = pp.name
        elif module == 'department':
            dept = Department.objects.create(name=data['name'], code=data['code'],
                                             description=data['description'])
            for s in [s.strip() for s in data['subjects'].split(',') if s.strip()]:
                Subject.objects.get_or_create(department=dept, name=s)
            label = dept.name
        else:  # class
            klass = ClassSection.objects.create(
                name=data['name'], section=data['section'] or 'A',
                academic_year=data['academic_year'] or '2025-2026',
                capacity=int(data['capacity'] or 60))
            ids = [int(i) for i in data['students'].split(',') if i.strip().isdigit()]
            klass.students.set(Student.objects.filter(pk__in=ids))
            label = str(klass)
        log_action(request.user, f'{module.title()} Created', module, '', label)
        messages.success(request, f'{cfg["title"]} entry created.')
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f'Could not create: {exc}')
    return redirect(f'/academics/{module}/')


@login_required
def module_delete(request, module, pk):
    if not _manage_access(request.user):
        return redirect('web:dashboard')
    cfg = _module_choices().get(module)
    if cfg and request.method == 'POST':
        cfg['model'].objects.filter(pk=pk).delete()
        messages.success(request, f'{cfg["title"]} entry deleted.')
    return redirect(f'/academics/{module}/')
# ---------------------------------------------------------------------------
# Attendance Management
# ---------------------------------------------------------------------------
@login_required
def attendance_page(request):
    role = request.user.role
    classes = ClassSection.objects.all()

    # scope: teachers see only their own classes
    if role == 'TEACHER' and hasattr(request.user, 'academic_teacher'):
        classes = classes.filter(class_teacher=request.user.academic_teacher)
    if role == 'STUDENT' and hasattr(request.user, 'student_profile'):
        classes = classes.filter(students=request.user.student_profile)
    if role == 'PARENT' and hasattr(request.user, 'academic_parent'):
        classes = classes.filter(students__in=request.user.academic_parent.children.all())

    selected_id = request.GET.get('class', '')
    selected = ClassSection.objects.filter(pk=selected_id).first() if selected_id else classes.first()
    sel_date = request.GET.get('date') or date.today().isoformat()

    rows = []
    if selected:
        students = selected.students.all()
        for student in students:
            rec = AttendanceRecord.objects.filter(student=student, date=sel_date).first()
            rows.append({'student': student,
                         'record': rec,
                         'status': rec.status if rec else 'PRESENT',
                         'present_pct': _attendance_pct(student)})
    # summary
    recent = AttendanceRecord.objects.select_related('student').order_by('-date')[:20]
    alerts = (
        Student.objects.filter(attendance_records__status__in=['ABSENT', 'LATE', 'LEAVE'])
        .annotate(missed=Count('attendance_records'))
        .filter(missed__gte=3).distinct()[:10]
    )

    if request.method == 'POST' and selected:
        for key, value in request.POST.items():
            if key.startswith('att-'):
                sid = int(key.split('-')[1])
                late = int(request.POST.get(f'late-{sid}', '0') or 0)
                AttendanceRecord.objects.update_or_create(
                    student_id=sid, date=sel_date,
                    defaults={'class_section': selected, 'status': value, 'late_minutes': late})
        messages.success(request, f'Attendance saved for {selected} on {sel_date}')
        return redirect(f'/academics/attendance/?class={selected.id}&date={sel_date}')

    return render(request, 'academics/attendance.html', {
        'classes': classes, 'selected': selected, 'sel_date': sel_date,
        'rows': rows, 'recent': recent, 'alerts': alerts,
        'can_mark': role in ('SUPER_ADMIN', 'HR', 'TEACHER'),
    })


def _attendance_pct(student, days=30):
    records = student.attendance_records.filter(date__gte=date.today() - timedelta(days=days))
    total = records.count()
    present = records.filter(status='PRESENT').count()
    return round(present * 100 / total, 1) if total else None
@login_required
def teacher_attendance_page(request):
    role = request.user.role
    queryset = TeacherAttendance.objects.select_related('teacher')
    if role != 'SUPER_ADMIN' and role != 'HR':
        if hasattr(request.user, 'academic_teacher'):
            queryset = queryset.filter(teacher=request.user.academic_teacher)
        else:
            queryset = queryset.none()
    recent = queryset.order_by('-date')[:30]

    if request.method == 'POST' and (role in ('SUPER_ADMIN', 'HR')):  # noqa: SIM102
        for key, value in request.POST.items():
            if key.startswith('tat-'):
                tid = int(key.split('-')[1])
                TeacherAttendance.objects.update_or_create(
                    teacher_id=tid, date=(request.POST.get('tdate') or date.today().isoformat()),
                    defaults={'status': value})
        messages.success(request, 'Teacher attendance saved')
        return redirect('/academics/attendance/teacher/')
    return render(request, 'academics/teacher_attendance.html', {
        'recent': recent,
        'teachers': TeacherProfile.objects.all(),
        'can_mark': role in ('SUPER_ADMIN', 'HR'),
    })


# ---------------------------------------------------------------------------
# Examination & Results
# ---------------------------------------------------------------------------
@login_required
def exams_page(request):
    exams = Exam.objects.select_related('class_section').order_by('-start_date')
    if request.user.role == 'TEACHER' and hasattr(request.user, 'academic_teacher'):
        exams = exams.filter(class_section__class_teacher=request.user.academic_teacher)
    if request.user.role == 'STUDENT' and hasattr(request.user, 'student_profile'):
        exams = exams.filter(class_section__students=request.user.student_profile)
    if request.user.role == 'PARENT' and hasattr(request.user, 'academic_parent'):
        exams = exams.filter(class_section__students__in=request.user.academic_parent.children.all())

    if request.method == 'POST':
        form = request.POST
        try:
            Exam.objects.create(
                name=form.get('name'), class_section_id=int(form.get('class_section')),
                start_date=form.get('start_date'), end_date=form.get('end_date') or None,
                status=form.get('status', 'SCHEDULED'))
            messages.success(request, 'Exam created.')
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f'Exam create failed: {exc}')
        return redirect('/academics/exams/')

    return render(request, 'academics/exams.html', {
        'exams': exams,
        'classes': ClassSection.objects.all(),
    })


@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':  # add schedule subject
        try:
            ExamSchedule.objects.create(
                exam=exam, subject_id=int(request.POST.get('subject')) or None,
                date=request.POST.get('date') or None,
                start_time=request.POST.get('start_time') or None,
                max_marks=int(request.POST.get('max_marks') or 100))
            messages.success(request, 'Subject added to schedule.')
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f'Could not add subject: {exc}')
        return redirect(f'/academics/exams/{exam.id}/')
    # results summary per student
    results = []
    for student in exam.class_section.students.all():
        marks = exam.marks.filter(student=student)
        if marks.exists():
            total = sum(m.total for m in marks)
            percent = round(total / (len(marks) * 100) * 100, 1)
            passed = all(m.is_passed for m in marks) and percent >= 50
            results.append({'student': student, 'marks': marks, 'total': total,
                            'percent': percent, 'passed': passed})
    results.sort(key=lambda r: -r['percent'])
    for rank, r in enumerate(results, start=1):
        r['rank'] = rank

    return render(request, 'academics/exam_detail.html', {
        'exam': exam, 'schedule': exam.schedule.all(),
        'subjects': Subject.objects.all(), 'results': results,
    })


@login_required
def mark_entry(request, exam_id, subject_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    subject = get_object_or_404(Subject, pk=subject_id)
    students = exam.class_section.students.all()

    if request.method == 'POST':
        for student in students:
            internal = _num(request.POST.get(f'internal-{student.id}'))
            practical = _num(request.POST.get(f'practical-{student.id}'))
            obtained = _num(request.POST.get(f'obtained-{student.id}'))
            MarkEntry.objects.update_or_create(
                exam=exam, student=student, subject=subject,
                defaults={'internal_marks': internal, 'practical_marks': practical,
                          'obtained_marks': obtained,
                          'is_passed': internal + practical + obtained >= 35})
        messages.success(request, f'Marks saved for {subject}')
        return redirect(f'/academics/exams/{exam.id}/')

    entries = {m.student_id: m for m in exam.marks.filter(subject=subject)}
    return render(request, 'academics/mark_entry.html', {
        'exam': exam, 'subject': subject, 'students': students, 'entries': entries,
    })


def _num(value):
    try:
        return max(0.0, float(value or 0))
    except (TypeError, ValueError):
        return 0.0
@login_required
def report_card(request, student_id):
    """Consolidated report card for one student (HR / parent / student)."""
    student = get_object_or_404(Student, pk=student_id)
    role = request.user.role
    if role == 'STUDENT' and student.user_id != request.user.id:
        return redirect('web:dashboard')
    if role == 'PARENT' and not student.academic_parents.filter(user=request.user).exists():
        return redirect('web:dashboard')

    results = []
    for exam in Exam.objects.filter(class_section__students=student).order_by('-start_date'):
        marks = exam.marks.filter(student=student)
        if marks.exists():
            total = sum(m.total for m in marks)
            percent = round(total / (len(marks) * 100) * 100, 1)
            passed = all(m.is_passed for m in marks) and percent >= 50
            results.append({'exam': exam, 'marks': marks, 'total': total,
                            'percent': percent, 'passed': passed})

    attendance = student.attendance_records.order_by('-date')[:30]
    return render(request, 'academics/report_card.html', {
        'student': student,
        'results': results,
        'attendance_pct': _attendance_pct(student),
        'attendance': attendance,
    })


@login_required
def leave_page(request):
    """Leave requests — staff request / approve, parents & students view."""
    role = request.user.role
    if request.method == 'POST':
        uid = request.POST.get('uid')
        action = request.POST.get('action')
        if uid and action and role in ('SUPER_ADMIN', 'HR'):
            LeaveRequest.objects.filter(requester_id=uid, status='PENDING').update(status=action.upper())
            messages.success(request, 'Leave updated.')
        else:
            LeaveRequest.objects.create(
                requester=request.user,
                leave_type=request.POST.get('leave_type', 'CASUAL'),
                from_date=request.POST.get('from_date'),
                to_date=request.POST.get('to_date') or request.POST.get('from_date'),
                reason=request.POST.get('reason', ''))
            messages.success(request, 'Leave request submitted.')
        return redirect('/academics/leaves/')

    pending = LeaveRequest.objects.filter(status='PENDING').order_by('-created_at')
    mine = LeaveRequest.objects.filter(requester=request.user).order_by('-created_at')
    return render(request, 'academics/leaves.html',
                  {'pending': pending, 'mine': mine, 'role': role})