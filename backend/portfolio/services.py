"""Portfolio engine.

Responsible for:
- gathering all 360-degree student data into a structured snapshot
- generating / regenerating portfolios
- the approval workflow (submit -> review -> approve/reject/revision -> publish)
- public slugs + QR codes
- view analytics
"""
from notifications.models import Notification
from common.completion import overview
from .models import Portfolio


def build_portfolio_data(student):
    """Fetch every profile section and return a JSON-serialisable snapshot."""
    photo = getattr(student.profile_photo, 'url', '') if student.profile_photo else ''
    return {
        'personal': {
            'student_id': student.student_id,
            'admission_number': student.admission_number,
            'register_number': student.register_number,
            'name': student.name,
            'profile_photo': photo,
            'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
            'gender': student.gender,
            'email': student.email,
            'phone': student.phone,
            'address': student.address,
            'city': student.city,
            'state': student.state,
            'department': student.department,
            'github_url': student.github_url,
            'linkedin_url': student.linkedin_url,
            'professional_summary': student.professional_summary,
        },
        'education': [
            {
                'id': e.id, 'college': e.college, 'degree': e.degree,
                'department': e.department, 'academic_year': e.academic_year,
                'year_of_study': e.year_of_study, 'class': e.klass, 'section': e.section,
                'board': e.board,
                'cgpa': float(e.cgpa) if e.cgpa is not None else None,
                'percentage': float(e.percentage) if e.percentage is not None else None,
                'history': e.history, 'start_year': e.start_year, 'end_year': e.end_year,
            }
            for e in student.education_records.all()
        ],
        'skills': [
            {'id': s.id, 'category': s.category, 'name': s.name, 'proficiency': s.proficiency}
            for s in student.skills.all()
        ],
        'projects': [
            {
                'id': p.id, 'name': p.name, 'description': p.description,
                'problem_statement': p.problem_statement, 'technologies': p.technologies,
                'student_role': p.student_role,
                'start_date': p.start_date.isoformat() if p.start_date else None,
                'end_date': p.end_date.isoformat() if p.end_date else None,
                'github_url': p.github_url, 'live_url': p.live_url,
                'image': p.image.url if p.image else '',
                'key_features': p.key_features,
            }
            for p in student.projects.all()
        ],
'internships': [
            {
                'id': i.id, 'company': i.company, 'role_name': i.role_name,
                'start_date': i.start_date.isoformat() if i.start_date else None,
                'end_date': i.end_date.isoformat() if i.end_date else None,
                'responsibilities': i.responsibilities, 'technologies': i.technologies,
                'description': i.description,
                'certificate': i.certificate.url if i.certificate else '',
            }
            for i in student.internships.all()
        ],
        'certifications': [
            {
                'id': c.id, 'name': c.name, 'issuing_organization': c.issuing_organization,
                'issue_date': c.issue_date.isoformat() if c.issue_date else None,
                'expiry_date': c.expiry_date.isoformat() if c.expiry_date else None,
                'credential_id': c.credential_id, 'url': c.url,
                'file': c.file.url if c.file else '',
            }
            for c in student.certifications.all()
        ],
        'achievements': [
            {
                'id': a.id, 'title': a.title, 'organization': a.organization,
                'date': a.date.isoformat() if a.date else None,
                'level': a.level, 'description': a.description,
                'proof': a.proof.url if a.proof else '',
            }
            for a in student.achievements.all()
        ],
        'activities': [
            {
                'id': a.id, 'activity_type': a.activity_type,
                'activity_type_display': a.get_activity_type_display(),
                'title': a.title, 'organization': a.organization,
                'description': a.description,
                'date': a.date.isoformat() if a.date else None, 'role': a.role,
            }
            for a in student.activities.all()
        ],
        'feedback': {
            'teacher': [
                {
                    'id': f.id, 'teacher_name': f.teacher.get_full_name() or f.teacher.username,
                    'academic_performance': f.academic_performance,
                    'attendance': f.attendance, 'homework': f.homework, 'behaviour': f.behaviour,
                    'communication': f.communication, 'leadership': f.leadership,
                    'creativity': f.creativity, 'sports_pet': f.sports_pet,
                    'participation': f.participation, 'overall_rating': f.overall_rating,
                    'remarks': f.remarks, 'created_at': f.created_at.isoformat(),
                }
                for f in student.teacher_feedbacks.all()
            ],
            'parent': [
                {
                    'id': f.id, 'parent_name': f.parent.get_full_name() or f.parent.username,
                    'rating': f.rating, 'feedback_text': f.feedback_text,
                    'created_at': f.created_at.isoformat(),
                }
                for f in student.parent_feedbacks.all()
            ],
        },
        'goals': [
            {
                'id': g.id, 'category': g.category, 'title': g.title,
                'description': g.description,
                'target_date': g.target_date.isoformat() if g.target_date else None,
                'status': g.status,
            }
            for g in student.goals.all()
        ],
        'completion': overview(student),
    }


def auto_summary(student, data):
    """Generate a default professional summary from the profile."""
    education = data['education'][:1]
    degree = education[0]['degree'] if education else student.department or 'professional'
    college = education[0]['college'] if education else ''
    skill_names = ', '.join(s['name'] for s in data['skills'][:6])
    projects_n = len(data['projects'])
    base = (f'{student.name} is a {degree} candidate'
            + (f' at {college}' if college else '')
            + f' with {projects_n} project(s){" and hands-on skills in " + skill_names if skill_names else ""}.')
    return base


def validate_required(student):
    """Return a list of required-field gaps. Raises nothing."""
    missing = []
    if not student.name:
        missing.append('Student name')
    if not student.register_number:
        missing.append('Register number')
    if not student.email:
        missing.append('Email')
    if not student.education_records.exists():
        missing.append('Education (at least one entry)')
    if not student.skills.exists():
        missing.append('Skills (at least one skill)')
def generate_portfolio(student, template, user, comment=''):
    """Create or regenerate the portfolio snapshot for a student."""
    from .models import Portfolio, PortfolioVersion

    data = build_portfolio_data(student)
    comp = data['completion']

    portfolio, created = Portfolio.objects.get_or_create(
        student=student,
        defaults={'template': template, 'created_by': user,
                  'completion_percentage': comp['overall']},
    )
    if not created:
        portfolio.template = template
    portfolio.completion_percentage = comp['overall']
    portfolio.data = data
    portfolio.summary = student.professional_summary or auto_summary(student, data)
    if not portfolio.title:
        portfolio.title = f'{student.name} — Digital Portfolio'
    portfolio.save()

    latest = portfolio.versions.first()
    version_no = (latest.version_no + 1) if latest else 1
    PortfolioVersion.objects.create(portfolio=portfolio, version_no=version_no,
                                    data=data, created_by=user, comment=comment or f'Generated v{version_no}')
    return portfolio


def submit_portfolio(portfolio, user):
    from .models import PortfolioApproval
    portfolio.status = Portfolio.Status.SUBMITTED
    portfolio.save(update_fields=['status', 'updated_at'])
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='SUBMITTED', comments='Submitted for review')
    Notification.objects.create(role='HR', event='PORTFOLIO_SUBMITTED',
                                message=f'Portfolio of {portfolio.student.name} was submitted for review.',
                                link=f'/portfolio/approval?id={portfolio.id}')


def start_review(portfolio, user):
    from .models import PortfolioApproval
    portfolio.status = Portfolio.Status.UNDER_REVIEW
    portfolio.save(update_fields=['status', 'updated_at'])
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='UNDER_REVIEW', comments='Review in progress')
def approve_portfolio(portfolio, user, comments=''):
    from .models import PortfolioApproval
    from django.utils import timezone
    portfolio.status = Portfolio.Status.APPROVED
    portfolio.save(update_fields=['status', 'updated_at'])
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='APPROVED', comments=comments,
                                     review_date=timezone.now())
    _notify_student(portfolio, 'PORTFOLIO_APPROVED', 'Your portfolio has been approved!')


def reject_portfolio(portfolio, user, comments=''):
    from .models import PortfolioApproval
    from django.utils import timezone
    portfolio.status = Portfolio.Status.REJECTED
    portfolio.save(update_fields=['status', 'updated_at'])
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='REJECTED', comments=comments,
                                     revision_reason=comments, review_date=timezone.now())
    _notify_student(portfolio, 'PORTFOLIO_REJECTED', f'Portfolio rejected: {comments}')


def require_revision(portfolio, user, reason):
    from .models import PortfolioApproval
    from django.utils import timezone
    portfolio.status = Portfolio.Status.REVISION_REQUIRED
    portfolio.save(update_fields=['status', 'updated_at'])
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='REVISION_REQUIRED', comments=reason,
                                     revision_reason=reason, review_date=timezone.now())
    _notify_student(portfolio, 'REVISION_REQUIRED', f'Changes requested: {reason}')


def publish_portfolio(portfolio, user):
    from .models import PortfolioApproval, PortfolioView
    from django.utils import timezone
    if portfolio.status not in (Portfolio.Status.APPROVED, Portfolio.Status.PUBLISHED):
        raise ValueError('Only approved portfolios can be published. Approve first.')
    portfolio.status = Portfolio.Status.PUBLISHED
    portfolio.published_at = timezone.now()
    portfolio.save()
    PortfolioApproval.objects.create(portfolio=portfolio, reviewer=user,
                                     status='PUBLISHED', comments='Published',
                                     review_date=timezone.now())
    _notify_student(portfolio, 'PORTFOLIO_PUBLISHED', 'Your portfolio is now live.')
    return portfolio


def record_view(portfolio):
    from .models import PortfolioView
    PortfolioView.objects.create(portfolio=portfolio, viewer_label='public')
    portfolio.views_count += 1
    Portfolio.objects.filter(pk=portfolio.pk).update(views_count=portfolio.views_count)


def _notify_student(portfolio, event, message):
    if portfolio.student.user_id:
        Notification.objects.create(recipient=portfolio.student.user,
                                    event=event, message=message,
                                    link=f'/portfolio/generator?student={portfolio.student_id}')
    else:
        Notification.objects.create(role='STUDENT', event=event, message=message)


def build_public_data(portfolio):
    """Sanitised snapshot for the no-login public page."""
    data = portfolio.data
    return {
        'title': portfolio.title,
        'slug': portfolio.slug,
        'views_count': portfolio.views_count,
        'published_at': portfolio.published_at.isoformat() if portfolio.published_at else None,
        'personal': data.get('personal', {}),
        'education': data.get('education', []),
        'skills': data.get('skills', []),
        'projects': data.get('projects', []),
        'internships': data.get('internships', []),
        'certifications': data.get('certifications', []),
        'achievements': data.get('achievements', []),
        'activities': data.get('activities', []),
        'feedback_teacher': data.get('feedback', {}).get('teacher', []),
        'goals': data.get('goals', []),
        'completion': data.get('completion', {}),
    }