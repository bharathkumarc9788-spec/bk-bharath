"""End-to-end smoke test for the Python frontend.

Run from the `backend/` directory:

    venv/bin/python ../tests/smoke_test.py

It uses Django's test client against the live dev database and verifies that
every page renders (GET) and every core workflow works (POST). Requires seeded
data: `python manage.py seed` first.
"""
import os
import sys

BACKEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, BACKEND)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from portfolio.models import Portfolio
from students.models import Student

User = get_user_model()


def probe(client, label, urls):
    errors = []
    for url in urls:
        try:
            resp = client.get(url)
            if resp.status_code >= 400:
                errors.append((url, resp.status_code))
        except Exception as exc:  # noqa: BLE001
            errors.append((url, 'EXC', str(exc)[:150]))
    print(f'{label}: {"OK" if not errors else "FAIL"} ({len(urls) - len(errors)}/{len(urls)})')
    for error in errors:
        print('   ', error[:2] if len(error) == 2 else error)
    return errors


def main():
    published = Portfolio.objects.filter(status='PUBLISHED', slug__isnull=False).first()
    public_url = f'/portfolio/public/{published.slug}/' if published else '/portfolio/public/nope/'

    total_errors = []
    total_errors += probe(Client(), 'ANONYMOUS', ['/', '/login/', '/reset-password/', public_url])

    hr = Client()
    hr.login(username='admin', password='admin123')
    total_errors += probe(hr, 'HR', [
        '/dashboard/', '/students/', '/students/new/', '/students/1/',
        '/students/1/?tab=education', '/students/1/?tab=skills', '/students/1/?tab=projects',
        '/students/1/?tab=internships', '/students/1/?tab=certifications',
        '/students/1/?tab=achievements', '/students/1/?tab=activities',
        '/students/1/?tab=feedback', '/students/1/?tab=goals',
        '/students/1/?tab=completion', '/students/1/?tab=personal',
        '/bulk-upload/', '/bulk-upload/template/',
        '/portfolio/generator/', '/portfolio/templates/', '/portfolio/approval/',
        '/portfolio/published/', '/analytics/', '/notifications/',
        '/portfolio/approval/?status=SUBMITTED',
    ])

    teacher = Client()
    teacher.login(username='teacher', password='teacher123')
    total_errors += probe(teacher, 'TEACHER', [
        '/dashboard/', '/students/', '/portfolio/generator/',
        '/portfolio/approval/', '/analytics/', '/notifications/',
    ])

    student_user = User.objects.filter(role='STUDENT').first()
    if student_user:
        student = Client()
        student.login(username=student_user.username, password='student123')
        total_errors += probe(student, 'STUDENT', [
            '/dashboard/', '/students/', '/portfolio/generator/', '/notifications/',
        ])

    # POST workflow through the rendered forms
    reg = 'SMOKE001'
    Student.objects.filter(register_number=reg).delete()
    created = hr.post('/students/new/', {
        'register_number': reg, 'name': 'Smoke Tester', 'email': 'smoke@college.edu',
        'gender': 'MALE', 'department': 'Computer Science', 'city': 'Chennai',
    })
    student_row = Student.objects.get(register_number=reg)
    print('POST create student ->', created.status_code)

    # partial personal save must not wipe other fields
    hr.post(f'/students/{student_row.id}/personal/', {'city': 'Coimbatore'})
    student_row.refresh_from_db()
    assert student_row.name == 'Smoke Tester', 'personal partial save wiped name field'
    print('POST partial personal save keeps name -> OK')

    hr.post(f'/students/{student_row.id}/skills/add/',
            {'name': 'Python', 'category': 'PROGRAMMING', 'proficiency': '4'})
    gen = hr.post('/portfolio/generator/', {'student_id': student_row.id, 'template_id': ''})
    portfolio_row = Portfolio.objects.get(student=student_row)
    print('POST generate portfolio ->', gen.status_code, 'slug:', portfolio_row.slug)

    hr.post(f'/portfolio/{portfolio_row.id}/submit/')
    hr.post(f'/portfolio/{portfolio_row.id}/review/',
            {'action': 'approve', 'comments': 'Good'})
    hr.post(f'/portfolio/{portfolio_row.id}/review/', {'action': 'publish'})
    portfolio_row.refresh_from_db()
    assert portfolio_row.status == 'PUBLISHED'
    public_resp = Client().get(f'/portfolio/public/{portfolio_row.slug}/')
    print('POST publish + public page ->', public_resp.status_code)

    qr_resp = hr.get(f'/portfolio/{portfolio_row.id}/qr/')
    assert qr_resp.status_code == 200 and qr_resp['Content-Type'] == 'image/png'
    print('POST QR endpoint ->', qr_resp.status_code, qr_resp['Content-Type'])

    # cleanup smoke data
    Portfolio.objects.filter(student=student_row).delete()
    Student.objects.filter(id=student_row.id).delete()
    User.objects.filter(username='smoke@college.edu').delete()

    # ---- RBAC: each role gets its own dashboard + sidebar, and is blocked
    # ---- from management pages it must not see.
    role_checks = [
        ('superadmin', 'superadmin123', 'SUPER_ADMIN'),
        ('admin', 'admin123', 'HR'),
        ('teacher', 'teacher123', 'TEACHER'),
        ('parent', 'parent123', 'PARENT'),
    ]
    for username, password, role in role_checks:
        c = Client()
        ok = c.login(username=username, password=password)
        resp = c.get('/dashboard/')
        body = resp.content.decode()
        assert ok, f'login failed for {role}'
        assert resp.status_code == 200, f'{role} dashboard = {resp.status_code}'
        assert '<aside class="sidebar">' in body, f'{role} sidebar missing'
        print(f'RBAC {role}: dashboard OK')

    student_role = User.objects.filter(role='STUDENT').first()
    if student_role:
        sc = Client()
        sc.login(username=student_role.username, password='student123')
        blocked = sc.get('/analytics/').status_code
        assert blocked in (302, 403), f'student should be blocked from analytics, got {blocked}'
        print('RBAC STUDENT: dashboard OK, analytics blocked')

    print('SMOKE TEST', 'PASSED' if not total_errors else f'FAILED ({len(total_errors)} errors)')
    return 1 if total_errors else 0


if __name__ == '__main__':
    sys.exit(main())