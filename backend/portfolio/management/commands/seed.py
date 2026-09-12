from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo users, students and portfolios.'

    def handle(self, *args, **options):
        self.seed_users()
        self.seed_templates()
        self.seed_students()
        self.seed_student_users()

    def seed_student_users(self):
        """Create login-able student accounts (username = email, password = student123)."""
        from students.models import Student
        count = 0
        for student in Student.objects.filter(user__isnull=True):
            username = (student.email or student.register_number).lower().strip() or f'student{student.id}'
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'role': 'STUDENT', 'email': student.email,
                              'first_name': student.name.split()[0] if student.name.split() else '',
                              'last_name': ' '.join(student.name.split()[1:])})
                if created:
                    user.set_password('student123')
                    user.save()
                student.user = user
                student.save(update_fields=['user'])
                count += 1
            except Exception:
                continue
        if count:
            self.stdout.write(self.style.SUCCESS(f'Linked {count} student login accounts (password: student123)'))

    def seed_users(self):
        hr, _ = User.objects.get_or_create(
            username='admin',
            defaults={'role': 'HR', 'email': 'hr@college.edu',
                      'first_name': 'HR', 'last_name': 'Admin', 'is_staff': True,
                      'is_superuser': True})
        hr.set_password('admin123')
        hr.save()

        teacher_user, _ = User.objects.get_or_create(
            username='teacher',
            defaults={'role': 'TEACHER', 'email': 'teacher@college.edu',
                      'first_name': 'R.', 'last_name': 'Ramesh'})
        teacher_user.set_password('teacher123')
        teacher_user.save()

        parent_user, _ = User.objects.get_or_create(
            username='parent',
            defaults={'role': 'PARENT', 'email': 'parent@example.com',
                      'first_name': 'S.', 'last_name': 'Kumar'})
        parent_user.set_password('parent123')
        parent_user.save()

        from feedback.models import Parent, Teacher
        from students.models import Student as Stu
        teacher, _ = Teacher.objects.get_or_create(user=teacher_user)
        parent, _ = Parent.objects.get_or_create(user=parent_user)
        std = Stu.objects.filter(register_number='21CSE001').first()
        if not std:
            std = self.make_student('21CSE001', 'Bharath Kumar', 'bharath@college.edu',
                                    department='Computer Science')
            std.save()
        teacher.students.add(std)
        parent.students.add(std)
        # assign a few more demo students to the teacher profile
        for s in Stu.objects.all()[:6]:
            teacher.students.add(s)
        self.stdout.write(self.style.SUCCESS(
            'Seeded users -> admin/admin123 | teacher/teacher123 | parent/parent123'))

    def seed_templates(self):
        from portfolio.models import PortfolioTemplate
        templates = [
            {'name': 'Professional', 'slug': 'professional', 'color_scheme': 'navy',
             'font': 'Inter', 'layout': 'classic', 'is_default': True,
             'description': 'Clean corporate layout ideal for campus-placement profiles.'},
            {'name': 'Modern', 'slug': 'modern', 'color_scheme': 'indigo',
             'font': 'Poppins', 'layout': 'split',
             'description': 'Two-column modern layout with bold accents.'},
            {'name': 'Developer', 'slug': 'developer', 'color_scheme': 'dark',
             'font': 'JetBrains Mono', 'layout': 'terminal',
             'description': 'Developer-themed dark layout with code styling.'},
            {'name': 'Creative', 'slug': 'creative', 'color_scheme': 'violet',
             'font': 'Dancing Script', 'layout': 'hero',
             'description': 'Expressive hero layout for creative students.'},
            {'name': 'Minimal', 'slug': 'minimal', 'color_scheme': 'gray',
             'font': 'Inter', 'layout': 'single',
             'description': 'Ultra-minimal single column layout.'},
        ]
        for t in templates:
            obj, created = PortfolioTemplate.objects.get_or_create(slug=t['slug'], defaults=t)
            if not created:
                for k, v in t.items():
                    setattr(obj, k, v)
                obj.save()

    def seed_students(self):
        from students.models import Student
        students = [
            self.make_student('21CSE002', 'Priya Sharma', 'priya@college.edu', 'Information Technology'),
            self.make_student('21CSE003', 'Arjun Nair', 'arjun@college.edu', 'Computer Science'),
            self.make_student('21CSE004', 'Divya Menon', 'divya@college.edu', 'Electronics'),
            self.make_student('21CSE005', 'Rahul Verma', 'rahul@college.edu', 'Mechanical'),
            self.make_student('21CSE006', 'Ananya Gupta', 'ananya@college.edu', 'Computer Science'),
            self.make_student('21CSE007', 'Karthik Raja', 'karthik@college.edu', 'Information Technology'),
            self.make_student('21CSE008', 'Sneha Iyer', 'sneha@college.edu', 'Computer Science'),
            self.make_student('21CSE009', 'Vikram Singh', 'vikram@college.edu', 'Electronics'),
            self.make_student('21CSE010', 'Meera Pillai', 'meera@college.edu', 'Computer Science'),
            self.make_student('21CSE011', 'Aditya Rao', 'aditya@college.edu', 'Information Technology'),
        ]
        count = 0
        for s in students:
            if Student.objects.filter(register_number=s.register_number).exists():
                continue
            s.save()
            self.populate_sections(s)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {count} demo students with 360-degree profiles'))

    def make_student(self, reg, name, email, department):
        from students.models import Student
        gender = 'FEMALE' if name.split()[0] in ('Priya', 'Divya', 'Ananya', 'Sneha', 'Meera') else 'MALE'
        return Student(
            register_number=reg, student_id=reg, admission_number=f'ADM-{reg}',
            name=name, email=email, phone=f'+91 98{reg[-4:]}00000',
            gender=gender, address='123 Campus Road', city='Chennai', state='Tamil Nadu',
            department=department, date_of_birth=date(2002, 5, 10),
            github_url='https://github.com/example', linkedin_url='https://linkedin.com/in/example',
            professional_summary=f'{name} is an enthusiastic {department} student passionate about '
                                 'building products and solving real-world problems with technology.',
        )

    def populate_sections(self, student):
        from education.models import Education
        from skills.models import Skill
        from projects.models import Project
        from internships.models import Internship
        from certifications.models import Certification
        from achievements.models import Achievement
        from activities.models import Activity
        from feedback.models import ParentFeedback, TeacherFeedback
        from goals.models import StudentGoal
        from portfolio.models import Portfolio, PortfolioTemplate
        from portfolio.services import (generate_portfolio, publish_portfolio,
                                        start_review, submit_portfolio)

        Education.objects.create(student=student, college='Anna University',
                                 degree='B.E. Computer Science', department=student.department,
                                 year_of_study='3', academic_year='2024-2025',
                                 cgpa=8.2, percentage=82.5,
                                 start_year='2021', end_year='2025', klass='III', section='A')

        for cat, skills in [
            ('PROGRAMMING', ['Python', 'Java', 'C']),
            ('FRAMEWORK', ['React', 'Django']),
            ('DATABASE', ['SQL', 'PostgreSQL']),
            ('CLOUD', ['AWS']),
            ('TOOL', ['Git', 'Docker']),
            ('SOFT', ['Communication', 'Leadership']),
        ]:
            for name in skills:
                Skill.objects.create(student=student, category=cat, name=name, proficiency=4)

        Project.objects.create(student=student, name='Student Portfolio System',
                               description='Full-stack portfolio automation for students.',
                               problem_statement='Manual portfolio creation is slow and inconsistent.',
                               technologies='React, Django, PostgreSQL',
                               student_role='Full-stack developer',
                               start_date=date(2024, 1, 1), end_date=date(2024, 6, 1),
                               github_url='https://github.com/example/spas',
                               live_url='https://example.com/spas',
                               key_features='Approval workflow, public URL, QR code, analytics')
        Project.objects.create(student=student, name='E-commerce Website',
                               description='A responsive shopping platform.',
                               technologies='React, Node.js, MongoDB',
                               student_role='Frontend developer',
                               start_date=date(2023, 6, 1), end_date=date(2023, 12, 1))

        Internship.objects.create(student=student, company='Tech Corp',
                                  role_name='Software Engineer Intern',
                                  start_date=date(2024, 6, 1), end_date=date(2024, 8, 1),
                                  technologies='Python, Django, React',
                                  responsibilities='Built REST APIs and fixed frontend bugs.',
                                  description='Worked within an agile team of 8.')

        for cert, org in [('Python for Everybody', 'Coursera'),
                          ('AWS Cloud Practitioner', 'Amazon Web Services')]:
            Certification.objects.create(student=student, name=cert,
                                         issuing_organization=org,
                                         issue_date=date(2024, 3, 1),
                                         credential_id=f'CRED-{student.register_number[:4]}')

        Achievement.objects.create(
            student=student, title='Smart India Hackathon Finalist',
            organization='SIH 2024', level='NATIONAL', date=date(2024, 8, 20),
            description='Reached the national finale with a healthcare solution.')
        Achievement.objects.create(
            student=student, title='Best Project Award',
            organization='College Expo', level='COLLEGE', date=date(2024, 2, 10))

        Activity.objects.create(student=student, activity_type='HACKATHON',
                                title='24-hour Hackathon', organization='TechVenture',
                                date=date(2024, 8, 15), role='Team Lead')
        Activity.objects.create(student=student, activity_type='CLUB',
                                title='Coding Club Coordinator', organization='College',
                                date=date(2024, 1, 1), role='Coordinator')
        Activity.objects.create(student=student, activity_type='SPORTS',
                                title='Cricket Team Vice Captain', organization='College',
                                date=date(2024, 6, 1), role='Vice Captain')

        teacher = User.objects.filter(role='TEACHER').first()
        if teacher:
            TeacherFeedback.objects.create(
                student=student, teacher=teacher,
                academic_performance='Consistently above class average.',
                attendance='Good', homework='Excellent', behaviour='Excellent',
                communication='Clear and confident communicator.',
                leadership='Takes initiative in group work.', creativity='Thinks outside the box.',
                sports_pet='Active participant in sports.', participation='Regular contributor in class.',
                overall_rating=4, remarks='A dependable and bright student.')
        parent = User.objects.filter(role='PARENT').first()
        if parent:
            ParentFeedback.objects.create(student=student, parent=parent, rating=5,
                                          feedback_text='Very proud of my child\'s consistent progress.')

        StudentGoal.objects.create(student=student, category='SHORT_TERM',
                                   title='Complete AWS certification',
                                   description='Pass AWS Solutions Architect by December.',
                                   status='IN_PROGRESS')
        StudentGoal.objects.create(student=student, category='LONG_TERM',
                                   title='Become a full-stack developer',
                                   description='Master system design and cloud.', status='IN_PROGRESS')

        template = PortfolioTemplate.objects.filter(is_default=True).first()
        if template and not Portfolio.objects.filter(student=student).exists():
            portfolio = generate_portfolio(student, template, teacher,
                                           comment='Auto-generated demo portfolio')
            idx = int(student.register_number[-1]) % 5
            if idx == 0:
                submit_portfolio(portfolio, teacher)
                portfolio.status = Portfolio.Status.APPROVED
                portfolio.save(update_fields=['status'])
                publish_portfolio(portfolio, teacher)
            elif idx == 1:
                submit_portfolio(portfolio, teacher)
            elif idx == 2:
                submit_portfolio(portfolio, teacher)
                start_review(portfolio, teacher)
            elif idx == 3:
                submit_portfolio(portfolio, teacher)
                from portfolio.services import require_revision
                require_revision(portfolio, teacher, 'Please add at least 3 projects.')
            else:
                submit_portfolio(portfolio, teacher)
                portfolio.status = Portfolio.Status.APPROVED
                portfolio.save(update_fields=['status'])
            from audit.models import log_action
            log_action(teacher, 'DEMO_SEED', 'Portfolio', str(portfolio.id))
        self.stdout.write(self.style.SUCCESS('Seeded 5 portfolio templates'))