"""Profile completion calculation.

Completion is computed dynamically from real database records (never hard-coded).

Each section maps to a percentage; the overall score is the average of all
sections. Used by the student profile, portfolio generator and the dashboard.
"""


def _pc(numerator, denominator):
    if denominator <= 0:
        return 0
    return min(100, round(numerator * 100 / denominator))


def personal_information(student):
    fields = ['name', 'register_number', 'email', 'phone', 'gender',
              'date_of_birth', 'city', 'state', 'department', 'address']
    present = [f for f in fields if getattr(student, f, None)]
    return _pc(len(present), len(fields)), present, fields


def education(student):
    entries = list(student.education_records.all())
    complete = sum(1 for e in entries if e.college and e.degree)
    return _pc(min(complete, 1), 1), len(entries), complete


def skills(student):
    count = student.skills.count()
    return _pc(count, 5), count, None  # 5 skills = 100%


def projects(student):
    count = student.projects.count()
    complete = sum(1 for p in student.projects.all() if p.name and p.description)
    return _pc(complete, 2), count, complete  # 2 solid projects = 100%


def internships(student):
    has = student.internships.exists()
    return (100 if has else 0), student.internships.count(), None


def certifications(student):
    count = student.certifications.count()
    return _pc(count, 2), count, None


def achievements(student):
    count = student.achievements.count()
    return _pc(count, 2), count, None


def activities(student):
    count = student.activities.count()
    return _pc(count, 2), count, None


def feedback(student):
    teacher = student.teacher_feedbacks.exists()
    parent = student.parent_feedbacks.exists()
    if teacher and parent:
        return 100, {'teacher': teacher, 'parent': parent}, None
    if teacher or parent:
        return 70, {'teacher': teacher, 'parent': parent}, None
    return 0, {'teacher': teacher, 'parent': parent}, None


def goals(student):
    count = student.goals.count()
    return (100 if count > 0 else 0), count, None


SECTIONS = [
    ('Personal Information', personal_information),
    ('Education', education),
    ('Skills', skills),
    ('Projects', projects),
    ('Internship', internships),
    ('Certifications', certifications),
    ('Achievements', achievements),
    ('Activities', activities),
    ('Feedback', feedback),
    ('Goals', goals),
]


def section_completion(student):
    """Return a list of {section, percent, detail} for the student."""
    result = []
    for label, fn in SECTIONS:
        percent, count, detail = fn(student)
        result.append({
            'section': label,
            'percent': percent,
            'count': count,
            'detail': detail,
            'complete': percent >= 100,
        })
    return result


def overall_completion(student):
    """Overall completion score (integer 0-100)."""
    sections = section_completion(student)
    if not sections:
        return 0
    return round(sum(s['percent'] for s in sections) / len(sections))


def overview(student):
    """Convenience dict used by the frontend progress panel."""
    sections = section_completion(student)
    return {
        'overall': overall_completion(student),
        'sections': sections,
        'missing': [s['section'] for s in sections if s['percent'] < 100],
    }