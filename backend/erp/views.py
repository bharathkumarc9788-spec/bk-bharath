"""ERP views — Administration, Board, Subjects, Homework, PET, Fees,
Hostel, HRMS, Inventory, Announcements, Audit Logs, Reports.

Simple management modules (school, academic years, boards, houses,
holidays, announcements) share one generic CRUD page; the complex
modules (subjects, homework, pet, fees, hostel, hrms, inventory) have
dedicated workflows. All pages are server-rendered Python templates.
"""
import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from academics.models import ClassSection, Department, Subject, TeacherProfile
from audit.models import AuditLog, log_action
from common.modules import is_admin_role
from students.models import Student

from .models import (AcademicYear, Announcement, Employee, FeePayment,
                     FeeStructure, Holiday, Homework, HomeworkSubmission,
                     Hostel, HostelAllocation, HostelRoom, House,
                     InventoryCategory, InventoryItem, InventoryMovement,
                     PetRecord, SchoolBoard, SchoolProfile)

User = get_user_model()


def _manage_access(user):
    """Super Admin / HR manage everything."""
    return is_admin_role(getattr(user, 'role', ''))


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _num(value):
    try:
        return max(0.0, float(value or 0))
    except (TypeError, ValueError):
        return 0.0


def _d(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Generic management modules (school, academic-years, boards, houses,
# holidays, announcements) — same pattern as academics module pages.
# ---------------------------------------------------------------------------
def _erp_choices():
    return {
        'school': {
            'model': SchoolProfile, 'title': 'School Profile',
            'sub': 'School Profile · Campus · Board · Working Days',
            'icon': '🏫', 'schema': [
                {'key': 'name', 'label': 'School Name', 'type': 'text'},
                {'key': 'code', 'label': 'School Code', 'type': 'text'},
                {'key': 'board', 'label': 'Board (CBSE / Matriculation)', 'type': 'text'},
                {'key': 'established_year', 'label': 'Established Year', 'type': 'number'},
                {'key': 'phone', 'label': 'Phone', 'type': 'text'},
                {'key': 'email', 'label': 'Email', 'type': 'text'},
                {'key': 'city', 'label': 'City', 'type': 'text'},
                {'key': 'address', 'label': 'Address', 'type': 'textarea'},
                {'key': 'motto', 'label': 'Motto', 'type': 'textarea'},
            ],
            'render': lambda s: (
                f"<b>{s.name}</b><span class='muted'>{s.board or '—'} · {s.city or '—'} · "
                f"est. {s.established_year or '—'} · {s.email or '—'}</span>"),
        },
        'academic-years': {
            'model': AcademicYear, 'title': 'Academic Year',
            'sub': 'Academic Years · Current Year · Working Days',
            'icon': '🗓️', 'schema': [
                {'key': 'name', 'label': 'Academic Year (e.g. 2025-2026)', 'type': 'text'},
                {'key': 'start_date', 'label': 'Start Date', 'type': 'date'},
                {'key': 'end_date', 'label': 'End Date', 'type': 'date'},
                {'key': 'is_current', 'label': 'Set as Current Year', 'type': 'checkbox'},
            ],
            'render': lambda y: (
                f"<b>{y.name}</b><span class='muted'>"
                f"{y.start_date or '—'} → {y.end_date or '—'} "
                f"{'· ✅ Current' if y.is_current else ''}</span>"),
        },
        'boards': {
            'model': SchoolBoard, 'title': 'Board Management',
            'sub': 'CBSE · Matriculation · State Board · ICSE configuration',
            'icon': '📖', 'schema': [
                {'key': 'name', 'label': 'Board Name', 'type': 'text'},
                {'key': 'board_type', 'label': 'Board Type', 'type': 'select',
                 'options': [{'value': t, 'label': l} for t, l in SchoolBoard.BOARD_TYPES]},
                {'key': 'exam_pattern', 'label': 'Examination Pattern', 'type': 'textarea'},
                {'key': 'grading_rules', 'label': 'Grade Structure / Rules', 'type': 'textarea'},
                {'key': 'promotion_rules', 'label': 'Promotion Rules', 'type': 'textarea'},
            ],
            'render': lambda b: (
                f"<b>{b.name}</b><span class='muted'>{b.get_board_type_display()} · "
                f"Pattern: {b.exam_pattern[:60] or '—'}</span>"),
        },
        'houses': {
            'model': House, 'title': 'House Management',
            'sub': 'Houses · Captains · Colours',
            'icon': '🏰', 'schema': [
                {'key': 'name', 'label': 'House Name', 'type': 'text'},
                {'key': 'color', 'label': 'Colour', 'type': 'text'},
                {'key': 'captain', 'label': 'Captain', 'type': 'text'},
                {'key': 'vice_captain', 'label': 'Vice Captain', 'type': 'text'},
            ],
            'render': lambda h: (
                f"<b>{h.name}</b><span class='muted'>{h.color or '—'} · "
                f"Captain {h.captain or '—'} · Vice {h.vice_captain or '—'}</span>"),
        },
        'holidays': {
            'model': Holiday, 'title': 'Holidays & Calendar',
            'sub': 'School Calendar · Holidays · Working Days',
            'icon': '🎉', 'schema': [
                {'key': 'title', 'label': 'Holiday Title', 'type': 'text'},
                {'key': 'date', 'label': 'Date', 'type': 'date'},
                {'key': 'description', 'label': 'Description', 'type': 'textarea'},
                {'key': 'is_working_day', 'label': 'Working Day (No Holiday)', 'type': 'checkbox'},
            ],
            'render': lambda h: (
                f"<b>{h.title}</b><span class='muted'>{h.date} "
                f"{'· Working Day' if h.is_working_day else '· Holiday'}</span>"),
        },
        'announcements': {
            'model': Announcement, 'title': 'Communication / Announcements',
            'sub': 'Notifications · Academic Updates · Alerts',
            'icon': '📢', 'schema': [
                {'key': 'title', 'label': 'Title', 'type': 'text'},
                {'key': 'audience', 'label': 'Audience', 'type': 'select',
                 'options': [{'value': a, 'label': l} for a, l in Announcement.AUDIENCE]},
                {'key': 'body', 'label': 'Message', 'type': 'textarea'},
            ],
            'render': lambda a: (
                f"<b>{a.title}</b><span class='muted'>{a.get_audience_display()} · "
                f"{a.created_by.get_full_name() or a.created_by.username if a.created_by else 'System'} · "
                f"{a.created_at:%Y-%m-%d %H:%M}</span>"),
        },
    }
@login_required
def erp_module_page(request, module):
    cfg = _erp_choices().get(module)
    if not cfg or request.user.role not in ('SUPER_ADMIN', 'HR'):
        return redirect('web:dashboard')
    rendered = [{'obj': item, 'html': cfg['render'](item)}
                for item in cfg['model'].objects.all()[:80]]
    return render(request, 'erp/module_page.html', {
        'module': module, 'title': cfg['title'], 'sub': cfg['sub'],
        'icon': cfg['icon'], 'schema': cfg['schema'], 'items': rendered,
        'stats': {'total': cfg['model'].objects.count()},
    })


@login_required
def erp_module_add(request, module):
    if not _manage_access(request.user):
        return redirect('web:dashboard')
    cfg = _erp_choices().get(module)
    if not cfg or request.method != 'POST':
        return redirect('web:dashboard')

    data = {f['key']: (request.POST.get(f['key'], '') or '').strip() for f in cfg['schema']}
    try:
        if module == 'school':
            obj = SchoolProfile.objects.first() or SchoolProfile()
            for k in ('name', 'code', 'board', 'phone', 'email', 'city', 'address', 'motto'):
                setattr(obj, k, data.get(k, '') or '')
            obj.established_year = _int_or_none(data.get('established_year'))
            obj.save()
            label = obj.name
        elif module == 'academic-years':
            name = data.get('name') or f'{date.today().year}-{date.today().year + 1}'
            year, created = AcademicYear.objects.get_or_create(
                name=name,
                defaults={'start_date': _d(data.get('start_date')),
                          'end_date': _d(data.get('end_date')),
                          'is_current': request.POST.get('is_current') == 'on'})
            if not created:
                year.start_date = _d(data.get('start_date'))
                year.end_date = _d(data.get('end_date'))
                year.save()
            if request.POST.get('is_current') == 'on':
                year.is_current = True
                year.save()
                AcademicYear.objects.exclude(pk=year.pk).update(is_current=False)
            label = year.name
        elif module == 'boards':
            board = SchoolBoard.objects.create(
                name=data.get('name') or 'Board',
                board_type=data.get('board_type') or 'CBSE',
                exam_pattern=data.get('exam_pattern', ''),
                grading_rules=data.get('grading_rules', ''),
                promotion_rules=data.get('promotion_rules', ''))
            label = board.name
        elif module == 'houses':
            house = House.objects.create(
                name=data.get('name') or 'House', color=data.get('color', ''),
                captain=data.get('captain', ''), vice_captain=data.get('vice_captain', ''))
            label = house.name
        elif module == 'holidays':
            holiday = Holiday.objects.create(
                title=data.get('title') or 'Holiday',
                date=_d(data.get('date')) or date.today(),
                description=data.get('description', ''),
                is_working_day=request.POST.get('is_working_day') == 'on')
            label = holiday.title
        else:  # announcements
            announcement = Announcement.objects.create(
                title=data.get('title') or 'Announcement',
                body=data.get('body', ''),
                audience=data.get('audience') or 'ALL',
                created_by=request.user)
            label = announcement.title
        log_action(request.user, f'{cfg["title"]} Created', 'erp', module, label)
        messages.success(request, f'{cfg["title"]} entry created.')
    except Exception as exc:  # noqa: BLE001
        messages.error(request, f'Could not create: {exc}')
    return redirect(f'/erp/{module}/')


@login_required
def erp_module_delete(request, module, pk):
    if not _manage_access(request.user):
        return redirect('web:dashboard')
    cfg = _erp_choices().get(module)
    if cfg and request.method == 'POST':
        cfg['model'].objects.filter(pk=pk).delete()
        messages.success(request, f'{cfg["title"]} entry deleted.')
    return redirect(f'/erp/{module}/')
# ---------------------------------------------------------------------------
# Subject Management (+ teacher allocation)
# ---------------------------------------------------------------------------
@login_required
def subjects_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR')
    if request.method == 'POST' and manage:
        action = request.POST.get('sub_action', '')
        if action == 'add':
            name = (request.POST.get('name', '') or '').strip()
            if name:
                dept_id = request.POST.get('department') or ''
                department = Department.objects.filter(pk=int(dept_id)).first() if dept_id.isdigit() else None
                if department is None:
                    department = Department.objects.first()
                    if department is None:
                        department = Department.objects.create(name='General')
                Subject.objects.get_or_create(
                    department=department, name=name,
                    defaults={'code': (request.POST.get('code', '') or '').strip()})
                messages.success(request, f'Subject «{name}» created.')
        elif action == 'allocate':
            subject = Subject.objects.filter(pk=request.POST.get('subject') or 0).first()
            teacher = TeacherProfile.objects.filter(pk=request.POST.get('teacher') or 0).first()
            if subject and teacher:
                teacher.subjects.add(subject)
                messages.success(request, f'{teacher.name} → {subject.name}')
        elif action == 'deallocate':
            subject = Subject.objects.filter(pk=request.POST.get('subject') or 0).first()
            teacher = TeacherProfile.objects.filter(pk=request.POST.get('teacher') or 0).first()
            if subject and teacher:
                teacher.subjects.remove(subject)
                messages.success(request, f'Removed {subject.name} from {teacher.name}')
        return redirect('/erp/subjects/')

    subjects = Subject.objects.all()
    rows = [{'subject': s, 'teachers': ', '.join(t.name for t in s.teachers.all()[:4]) or '—'}
            for s in subjects]
    return render(request, 'erp/subjects.html', {
        'rows': rows, 'departments': Department.objects.all(),
        'subjects': subjects, 'teachers': TeacherProfile.objects.all(),
        'manage': manage,
    })
# ---------------------------------------------------------------------------
# Homework & Assignment (create, submit, mark)
# ---------------------------------------------------------------------------
@login_required
def homework_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR', 'TEACHER')

    if request.method == 'POST':
        action = request.POST.get('hw_action', '')
        if action == 'create' and role in ('SUPER_ADMIN', 'HR', 'TEACHER'):
            klass = ClassSection.objects.filter(pk=request.POST.get('klass') or 0).first()
            if klass:
                Homework.objects.create(
                    klass=klass,
                    subject=Subject.objects.filter(pk=request.POST.get('subject') or 0).first(),
                    title=(request.POST.get('title', '') or 'Homework').strip(),
                    description=request.POST.get('description', ''),
                    due_date=_d(request.POST.get('due_date')),
                    max_marks=_int_or_none(request.POST.get('max_marks')) or 10,
                    created_by=request.user)
                messages.success(request, 'Homework created.')
        elif action == 'submit':
            student = getattr(request.user, 'student_profile', None)
            hw = Homework.objects.filter(pk=request.POST.get('homework') or 0).first()
            if student and hw and hw.klass.students.filter(pk=student.pk).exists():
                HomeworkSubmission.objects.update_or_create(
                    homework=hw, student=student,
                    defaults={'submitted_at': timezone.now(),
                              'text': request.POST.get('text', ''),
                              'status': 'SUBMITTED'})
                messages.success(request, 'Homework submitted.')
        elif action == 'grade' and role in ('SUPER_ADMIN', 'HR', 'TEACHER'):
            hw = Homework.objects.filter(pk=request.POST.get('homework') or 0).first()
            if hw:
                for key, value in request.POST.items():
                    if key.startswith('marks-'):
                        sub = HomeworkSubmission.objects.filter(pk=int(key.split('-')[1])).first()
                        if sub:
                            sub.marks_obtained = _num(value)
                            sub.feedback = request.POST.get(f'fb-{sub.id}', '')
                            sub.status = 'GRADED'
                            sub.save()
                messages.success(request, 'Submissions graded.')
        return redirect('/erp/homework/')

    homeworks = Homework.objects.all().order_by('-created_at')
    if role == 'TEACHER' and hasattr(request.user, 'academic_teacher'):
        homeworks = homeworks.filter(klass__class_teacher=request.user.academic_teacher)
    elif role == 'STUDENT' and hasattr(request.user, 'student_profile'):
        homeworks = homeworks.filter(klass__students=request.user.student_profile)
    elif role == 'PARENT' and hasattr(request.user, 'academic_parent'):
        homeworks = homeworks.filter(klass__students__in=request.user.academic_parent.children.all())

    rows = []
    for hw in homeworks[:30]:
        subs = {s.student_id: s for s in hw.submissions.all()}
        students = hw.klass.students.all()
        rows.append({
            'hw': hw, 'students': students, 'subs': subs,
            'submitted': sum(1 for s in students if subs.get(s.id)),
            'graded': sum(1 for s in students if subs.get(s.id) and subs[s.id].status == 'GRADED'),
            'total': students.count(),
        })
    return render(request, 'erp/homework.html', {
        'rows': rows, 'classes': ClassSection.objects.all(),
        'subjects': Subject.objects.all(), 'manage': manage, 'role': role,
    })
# ---------------------------------------------------------------------------
# PET / Physical Education
# ---------------------------------------------------------------------------
@login_required
def pet_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR', 'TEACHER')
    if request.method == 'POST' and manage:
        student = Student.objects.filter(pk=request.POST.get('student') or 0).first()
        if student:
            PetRecord.objects.create(
                student=student,
                assessment_date=_d(request.POST.get('assessment_date')) or date.today(),
                endurance=request.POST.get('endurance', 'Good'),
                flexibility=request.POST.get('flexibility', 'Good'),
                strength=request.POST.get('strength', 'Good'),
                agility=request.POST.get('agility', 'Good'),
                sports=request.POST.get('sports', ''),
                coach_remarks=request.POST.get('coach_remarks', ''))
            messages.success(request, f'PET assessment saved for {student.name}.')
        return redirect('/erp/pet/')

    records = PetRecord.objects.all().order_by('-assessment_date')
    if role == 'STUDENT' and hasattr(request.user, 'student_profile'):
        records = records.filter(student=request.user.student_profile)
    elif role == 'PARENT' and hasattr(request.user, 'academic_parent'):
        records = records.filter(student__in=request.user.academic_parent.children.all())
    return render(request, 'erp/pet.html', {
        'records': records[:60], 'students': Student.objects.all(),
        'ratings': PetRecord.RATING, 'manage': manage,
    })


# ---------------------------------------------------------------------------
# Finance & Fee Management (structures + payments ledger)
# ---------------------------------------------------------------------------
@login_required
def fees_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR')
    if request.method == 'POST' and manage:
        action = request.POST.get('fee_action', '')
        if action == 'structure':
            klass = ClassSection.objects.filter(pk=request.POST.get('klass') or 0).first()
            FeeStructure.objects.create(
                name=(request.POST.get('name', '') or 'Fee').strip(),
                klass=klass,
                amount=_num(request.POST.get('amount')),
                frequency=request.POST.get('frequency', 'YEARLY'),
                description=request.POST.get('description', ''))
            messages.success(request, 'Fee structure created.')
        elif action == 'payment':
            student = Student.objects.filter(pk=request.POST.get('student') or 0).first()
            if student:
                amount = _num(request.POST.get('amount'))
                fee = FeeStructure.objects.filter(pk=request.POST.get('fee') or 0).first()
                status = 'PAID' if (amount >= float(fee.amount) if fee else True) else 'PARTIAL'
                FeePayment.objects.create(
                    student=student, fee=fee, amount_paid=amount,
                    discount=_num(request.POST.get('discount')),
                    paid_on=_d(request.POST.get('paid_on')) or date.today(),
                    method=request.POST.get('method', 'CASH'),
                    reference=request.POST.get('reference', ''),
                    status=status)
                messages.success(request, f'Payment recorded for {student.name}.')
        return redirect('/erp/fees/')

    structures = FeeStructure.objects.all()
    payments = FeePayment.objects.all()
    students = Student.objects.all()

    # student fee ledger
    ledger = []
    for student in students[:40]:
        due = sum(float(f.amount) for f in structures
                  if f.klass is None or f.klass.students.filter(pk=student.pk).exists())
        paid = sum(float(p.amount_paid) for p in payments.filter(student=student))
        ledger.append({
            'student': student,
            'due': round(due, 2), 'paid': round(paid, 2),
            'balance': round(max(due - paid, 0), 2),
            'status': 'Paid' if due and paid >= due else ('Partial' if paid else 'Pending'),
            'payments': payments.filter(student=student).count(),
        })
    return render(request, 'erp/fees.html', {
        'structures': structures, 'ledger': ledger, 'students': students,
        'classes': ClassSection.objects.all(),
        'payments': payments[:20], 'manage': manage,
    })
# ---------------------------------------------------------------------------
# Hostel Management (hostels, rooms, allocations)
# ---------------------------------------------------------------------------
@login_required
def hostel_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR')
    if request.method == 'POST' and manage:
        action = request.POST.get('hostel_action', '')
        if action == 'hostel':
            Hostel.objects.create(
                name=(request.POST.get('name', '') or 'Hostel').strip(),
                address=request.POST.get('address', ''),
                warden_name=request.POST.get('warden', ''))
            messages.success(request, 'Hostel created.')
        elif action == 'room':
            hostel = Hostel.objects.filter(pk=request.POST.get('hostel') or 0).first()
            if hostel:
                HostelRoom.objects.create(
                    hostel=hostel,
                    room_number=(request.POST.get('room_number', '') or 'R1').strip(),
                    floor=request.POST.get('floor', ''),
                    capacity=_int_or_none(request.POST.get('capacity')) or 3,
                    room_type=request.POST.get('room_type', 'Triple'))
                messages.success(request, 'Room added.')
        elif action == 'allocate':
            student = Student.objects.filter(pk=request.POST.get('student') or 0).first()
            room = HostelRoom.objects.filter(pk=request.POST.get('room') or 0).first()
            if student and room:
                HostelAllocation.objects.create(
                    student=student, room=room,
                    bed_number=request.POST.get('bed', ''),
                    check_in=_d(request.POST.get('check_in')) or date.today())
                messages.success(request, f'{student.name} allocated to {room}.')
        return redirect('/erp/hostel/')

    hostels = Hostel.objects.all()
    rooms = HostelRoom.objects.all()
    allocations = HostelAllocation.objects.filter(is_active=True)
    rows = []
    for room in rooms[:60]:
        occupied = room.allocations.filter(is_active=True).count()
        rows.append({'room': room, 'occupied': occupied,
                     'free': max(room.capacity - occupied, 0)})
    return render(request, 'erp/hostel.html', {
        'hostels': hostels, 'rooms': rows, 'allocations': allocations[:30],
        'students': Student.objects.all(), 'manage': manage,
    })


# ---------------------------------------------------------------------------
# HRMS — Employee Master
# ---------------------------------------------------------------------------
@login_required
def hrms_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR')
    if not manage:
        return redirect('web:dashboard')
    if request.method == 'POST':
        username = (request.POST.get('username', '') or '').strip()
        if username:
            parts = ((request.POST.get('full_name', '') or 'Staff').split(' ', 1) + [''])
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': username, 'role': 'TEACHER',
                          'first_name': parts[0], 'last_name': parts[1] if len(parts) > 1 else ''})
            if request.POST.get('password'):
                user.set_password(request.POST['password'])
                user.save()
            dept = Department.objects.filter(pk=request.POST.get('department') or 0).first()
            emp, _ = Employee.objects.get_or_create(user=user)
            emp.emp_id = request.POST.get('emp_id', '')
            emp.department = dept
            emp.designation = request.POST.get('designation', '')
            emp.joining_date = _d(request.POST.get('joining_date'))
            emp.qualification = request.POST.get('qualification', '')
            emp.experience_years = _int_or_none(request.POST.get('experience_years')) or 0
            emp.phone = request.POST.get('phone', '')
            emp.employment_status = request.POST.get('employment_status', 'PERMANENT')
            emp.save()
            messages.success(request, f'Employee {emp.name} registered.')
        return redirect('/erp/hrms/')

    employees = Employee.objects.all()
    return render(request, 'erp/hrms.html', {
        'employees': employees[:60], 'departments': Department.objects.all(),
        'statuses': Employee.EMPLOYMENT, 'manage': manage,
    })
# ---------------------------------------------------------------------------
# Inventory Management (items + stock movements)
# ---------------------------------------------------------------------------
@login_required
def inventory_page(request):
    role = request.user.role
    manage = role in ('SUPER_ADMIN', 'HR')
    if not manage:
        return redirect('web:dashboard')
    if request.method == 'POST':
        action = request.POST.get('inventory_action', '')
        if action == 'category':
            name = (request.POST.get('name', '') or '').strip()
            if name:
                InventoryCategory.objects.get_or_create(name=name)
                messages.success(request, f'Category «{name}» created.')
        elif action == 'item':
            category = InventoryCategory.objects.filter(pk=request.POST.get('category') or 0).first()
            if category:
                InventoryItem.objects.create(
                    category=category,
                    name=(request.POST.get('name', '') or 'Item').strip(),
                    unit=request.POST.get('unit', 'pcs'),
                    quantity=_int_or_none(request.POST.get('quantity')) or 0,
                    reorder_level=_int_or_none(request.POST.get('reorder_level')) or 0,
                    supplier=request.POST.get('supplier', ''),
                    price=_num(request.POST.get('price')),
                    location=request.POST.get('location', ''))
                messages.success(request, 'Item created.')
        elif action == 'move':
            item = InventoryItem.objects.filter(pk=request.POST.get('item') or 0).first()
            if item:
                qty = _int_or_none(request.POST.get('quantity')) or 1
                mtype = request.POST.get('movement_type', 'PURCHASE')
                InventoryMovement.objects.create(item=item, movement_type=mtype,
                                                quantity=qty, date=_d(request.POST.get('date')) or date.today(),
                                                note=request.POST.get('note', ''))
                item.quantity = max(item.quantity + (qty if mtype == 'PURCHASE' else -qty), 0)
                item.save()
                messages.success(request, f'{mtype.title()} recorded → stock {item.quantity}.')
        return redirect('/erp/inventory/')

    items = InventoryItem.objects.all()
    categories = InventoryCategory.objects.all()
    low_stock = [i for i in items if i.low_stock]
    return render(request, 'erp/inventory.html', {
        'items': items[:80], 'categories': categories,
        'movements': InventoryMovement.objects.all()[:20],
        'low_stock': low_stock[:10], 'manage': manage,
    })
# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------
@login_required
def audit_logs_page(request):
    if request.user.role not in ('SUPER_ADMIN', 'HR'):
        return redirect('web:dashboard')
    return render(request, 'erp/audit_logs.html', {
        'logs': AuditLog.objects.all()[:100],
        'total': AuditLog.objects.count(),
    })


# ---------------------------------------------------------------------------
# Reports & Analytics (+ CSV export)
# ---------------------------------------------------------------------------
@login_required
def reports_page(request):
    role = request.user.role
    if request.GET.get('format') == 'csv':
        return _csv_export(request, request.GET.get('type', 'students'))

    from portfolio.models import Portfolio
    from common.completion import overall_completion
    students = Student.objects.all()
    portfolios = Portfolio.objects.all()
    completions = [overall_completion(s) for s in students]
    avg_completion = round(sum(completions) / len(completions), 1) if completions else 0
    dept_counts = {}
    for s in students:
        dept = s.department or 'Unknown'
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    context = {
        'students': students.count(),
        'portfolios': portfolios.count(),
        'published': portfolios.filter(status='PUBLISHED').count(),
        'avg_completion': avg_completion,
        'completion_bins': {
            '0-40': sum(1 for c in completions if c < 40),
            '40-70': sum(1 for c in completions if 40 <= c < 70),
            '70-100': sum(1 for c in completions if c >= 70),
        },
        'department_counts': dict(sorted(dept_counts.items())),
        'role': role,
    }
    return render(request, 'erp/reports.html', context)


def _csv_export(request, kind):
    """Emit CSV exports for students / attendance / marks."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="erp-{kind}.csv"'
    writer = csv.writer(response)
    if kind == 'students':
        from common.completion import overall_completion
        writer.writerow(['Name', 'Register No', 'Department', 'Email', 'Phone', 'Completion %'])
        for s in Student.objects.all():
            writer.writerow([s.name, s.register_number, s.department or '',
                             s.email, s.phone, overall_completion(s)])
    elif kind == 'attendance':
        from academics.models import AttendanceRecord
        writer.writerow(['Student', 'Class', 'Date', 'Status', 'Late (min)'])
        for r in AttendanceRecord.objects.all()[:2000]:
            writer.writerow([r.student.name, str(r.class_section), r.date,
                             r.status, r.late_minutes])
    elif kind == 'marks':
        from academics.models import MarkEntry
        writer.writerow(['Student', 'Exam', 'Subject', 'Internal', 'Practical', 'Obtained', 'Total'])
        for m in MarkEntry.objects.select_related('student', 'exam', 'subject').all()[:2000]:
            writer.writerow([m.student.name, m.exam.name, m.subject.name if m.subject else '',
                             m.internal_marks, m.practical_marks, m.obtained_marks, m.total])
    else:
        writer.writerow(['Report', 'No data'])
    return response