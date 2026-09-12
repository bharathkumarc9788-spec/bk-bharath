import csv
from io import StringIO

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import log_action
from common.completion import overview
from common.permissions import IsHROrReadOnly
from notifications.models import Notification

from .models import Student
from .serializers import StudentDetailSerializer, StudentSerializer

User = get_user_model()


def _ensure_student_user(student, password='student123'):
    """Create/link a login-able student user account."""
    if student.user_id:
        return student.user
    username = (student.email or student.register_number).lower().strip()
    username = username or f'student{student.id}'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'role': 'STUDENT', 'email': student.email,
                  'first_name': student.name.split()[0] if student.name.split() else '',
                  'last_name': ' '.join(student.name.split()[1:])},
    )
    if created:
        user.set_password(password)
        user.save()
    student.user = user
    student.save(update_fields=['user'])
    return user


class StudentViewSet(viewsets.ModelViewSet):
    """
    Student CRUD.
    HR has full access; students (and parents) see / update only their own record.
    Supports search (name / register / department / email / skills / project)
    and filters (department, year, status).
    """
    serializer_class = StudentSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        return [IsHROrReadOnly()]

    def get_queryset(self):
        qs = Student.objects.all()
        user = self.request.user
        if user.role in ('STUDENT', 'PARENT'):
            return qs.filter(user=user)
        if user.role == 'TEACHER':
            profile = getattr(user, 'teacher_profile', None)
            if profile:
                return qs.filter(teachers_assigned=profile)
            return qs.none()
        return qs
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) |
                           Q(register_number__icontains=search) |
                           Q(email__icontains=search) |
                           Q(department__icontains=search) |
                           Q(admission_number__icontains=search) |
                           Q(skills__name__icontains=search) |
                           Q(projects__name__icontains=search)).distinct()

        department = request.query_params.get('department', '').strip()
        if department:
            qs = qs.filter(department__icontains=department)

        year = request.query_params.get('year', '').strip()
        if year:
            qs = qs.filter(education_records__year_of_study=year).distinct()

        status_ = request.query_params.get('status', '').strip()
        if status_:
            qs = qs.filter(portfolios__status=status_).distinct()

        qs = qs.distinct()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = StudentDetailSerializer(instance)
        data = serializer.data
        data['completion_overview'] = overview(instance)
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        log_action(request.user, 'CREATE', 'Student', instance.id, f'Created student {instance.name}')
        Notification.objects.create(
            role='STUDENT', recipient=instance.user if instance.user_id else None,
            message='Your student profile has been created.', event='PROFILE_CREATED',
        )
        return Response(StudentDetailSerializer(instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request.user, 'DELETE', 'Student', instance.id, f'Deleted student {instance.name}')
        return super().destroy(request, *args, **kwargs)


class BulkUploadView(APIView):
    """
    POST a CSV/XLSX file -> parses + validates -> returns preview rows.
    POST {preview: False, rows: [...]} -> imports valid rows and returns a report.
    """
    permission_classes = [IsHROrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if file:
            rows, errors = self._parse(file)
            return Response({
                'preview': True,
                'total': len(rows) + len(errors),
                'valid': rows,
                'invalid': errors,
            })
        return self._confirm_import(request)

    def _confirm_import(self, request):
        rows = request.data.get('rows') or []
        created, failed = [], []
        for row in rows:
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
                created.append({'register_number': student.register_number, 'name': student.name})
                log_action(request.user, 'student_bulk_create', 'Student', str(student.id))
            except IntegrityError:
                failed.append({'row': row, 'reason': 'Register number already exists'})
            except Exception as exc:  # pragma: no cover
                failed.append({'row': row, 'reason': str(exc)})
        return Response({
            'report': {
                'total': len(rows),
                'valid': len(created),
                'invalid': len(failed),
                'created': created,
                'failed': failed,
            }
        })

    def _parse(self, file):
        rows, errors = [], []
        name = file.name.lower()
        if name.endswith('.xlsx'):
            import openpyxl
            from io import BytesIO
            file.seek(0)
            workbook = openpyxl.load_workbook(BytesIO(file.read()))
            sheet = workbook.active
            headers = [str(c.value).strip().lower().replace(' ', '_') if c.value else '' for c in sheet[1]]
            for r in sheet.iter_rows(min_row=2, values_only=True):
                row = dict(zip(headers, r))
                self._collect(row, rows, errors)
            return rows, errors
        try:
            content = file.read().decode('utf-8-sig')
        except Exception:
            return [], ['Unable to read file. Upload a UTF-8 CSV or .xlsx file.']
        reader = csv.DictReader(StringIO(content))
        for row in reader:
            self._collect(row, rows, errors)
        return rows, errors

    def _collect(self, row, rows, errors):
        if row.get('register_number') and row.get('name'):
            rows.append({k: v for k, v in row.items() if k})
        else:
            errors.append({'row': {k: v for k, v in row.items() if k},
                           'reason': 'Missing register_number or name'})