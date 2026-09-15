"""Role-Based Access Control — module registry.

Single source of truth for which modules every role can see.
Each module:

    key         unique identifier
    label       human name shown in the sidebar
    icon        emoji
    group       sidebar section label
    url         real route ('' → placeholder "coming soon" item)
    desc        short description (tooltip)
    kind        'live' (real page) | 'soon' (planned module)

Roles: SUPER_ADMIN, HR, TEACHER, STUDENT (school/college), PARENT.
"""

MANAGEMENT = 'Management'
OVERVIEW = 'Overview'
ACADEMICS = 'Academics'
STUDENT_DEV = 'Student Development'
PORTFOLIOS = 'Portfolios'
SYSTEM = 'System'


def _mod(key, label, icon, group, url='', desc='', kind='live'):
    return {
        'key': key, 'label': label, 'icon': icon, 'group': group,
        'url': url, 'desc': desc, 'kind': kind,
    }


# ---------------------------------------------------------------------------
# Module definitions by role. '' url == planned (coming-soon) module.
# ---------------------------------------------------------------------------
ROLE_MODULES = {

    'SUPER_ADMIN': [
        _mod('dashboard', 'Dashboard', '📊', OVERVIEW, '/dashboard/'),
        _mod('users', 'User Management', '👤', MANAGEMENT, '', 'Create & manage all accounts', 'soon'),
        _mod('roles', 'Role & Permission Management', '🛡️', MANAGEMENT, '', 'Assign modules per role', 'soon'),
        _mod('schools', 'School Management', '🏫', MANAGEMENT, '', 'Manage campuses', 'soon'),
        _mod('colleges', 'College Management', '🎓', MANAGEMENT, '/students/', 'Colleges & departments'),
        _mod('students', 'Student Management', '🧑‍🎓', MANAGEMENT, '/students/'),
        _mod('teachers', 'Teacher Management', '👨‍🏫', MANAGEMENT, '', '', 'soon'),
        _mod('parents', 'Parent Management', '👨‍👩‍👧', MANAGEMENT, '', '', 'soon'),
        _mod('academics', 'Academic Management', '📚', ACADEMICS, '', '', 'soon'),
        _mod('attendance', 'Attendance Management', '📋', ACADEMICS, '', '', 'soon'),
        _mod('exams', 'Examination & Results', '🗓️', ACADEMICS, '', '', 'soon'),
        _mod('homework', 'Homework / Assignment', '📝', ACADEMICS, '', '', 'soon'),
        _mod('lms', 'LMS Management', '💻', ACADEMICS, '', '', 'soon'),
        _mod('portfolios', 'Portfolio Management', '📁', PORTFOLIOS, '/portfolio/published/'),
        _mod('portfolio_gen', 'Portfolio Generator', '⚙️', PORTFOLIOS, '/portfolio/generator/'),
        _mod('generator_ai', 'AI Analytics', '🤖', PORTFOLIOS, '/analytics/', 'Insights & trends'),
        _mod('reports', 'Reports & Analytics', '📈', PORTFOLIOS, '/analytics/'),
        _mod('audit', 'Audit Logs', '🧾', SYSTEM, '', '', 'soon'),
        _mod('notifications', 'Notifications', '🔔', SYSTEM, '/notifications/'),
        _mod('settings', 'System Settings', '⚙️', SYSTEM, '', '', 'soon'),
        _mod('demo', 'Demo Data', '🧹', SYSTEM, '/demo-data/', 'Clear or reseed demo records'),
    ],

    'HR': [
        _mod('dashboard', 'Dashboard', '📊', OVERVIEW, '/dashboard/'),
        _mod('students', 'Student Management', '🧑‍🎓', MANAGEMENT, '/students/'),
        _mod('add_student', 'Add Student', '➕', MANAGEMENT, '/students/new/'),
        _mod('bulk', 'Bulk Upload', '📤', MANAGEMENT, '/bulk-upload/'),
        _mod('teachers', 'Teacher Management', '👨‍🏫', MANAGEMENT, '', '', 'soon'),
        _mod('parents', 'Parent Management', '👨‍👩‍👧', MANAGEMENT, '', '', 'soon'),
        _mod('classes', 'Class / Section', '🏷️', ACADEMICS, '', '', 'soon'),
        _mod('departments', 'Department Management', '🏢', ACADEMICS, '', '', 'soon'),
        _mod('attendance', 'Attendance', '📋', ACADEMICS, '', '', 'soon'),
        _mod('exams', 'Examination & Results', '🗓️', ACADEMICS, '', '', 'soon'),
        _mod('skills', 'Skills Management', '💡', STUDENT_DEV, '/students/', '360° skills'),
        _mod('projects', 'Project Management', '🛠️', STUDENT_DEV, '/students/', '360° projects'),
        _mod('internships', 'Internship Management', '💼', STUDENT_DEV, '/students/', '360° internships'),
        _mod('certs', 'Certification Management', '📜', STUDENT_DEV, '/students/', '360° certificates'),
        _mod('achievements', 'Achievement Management', '🏆', STUDENT_DEV, '/students/', '360° achievements'),
        _mod('portfolio_gen', 'Portfolio Generator', '⚙️', PORTFOLIOS, '/portfolio/generator/'),
        _mod('templates', 'Templates', '🎨', PORTFOLIOS, '/portfolio/templates/'),
        _mod('review', 'Portfolio Review', '🔎', PORTFOLIOS, '/portfolio/approval/'),
        _mod('approval', 'Portfolio Approval', '✅', PORTFOLIOS, '/portfolio/approval/'),
        _mod('published', 'Published Portfolios', '🌐', PORTFOLIOS, '/portfolio/published/'),
        _mod('reports', 'Reports & Analytics', '📈', PORTFOLIOS, '/analytics/'),
        _mod('notifications', 'Notifications', '🔔', SYSTEM, '/notifications/'),
        _mod('demo', 'Demo Data', '🧹', SYSTEM, '/demo-data/', 'Clear or reseed demo records'),
    ],

    'TEACHER': [
        _mod('dashboard', 'My Dashboard', '📊', OVERVIEW, '/dashboard/'),
        _mod('classes', 'My Classes', '🏷️', MANAGEMENT, '/students/', 'Assigned classes'),
        _mod('students', 'My Students', '🧑‍🎓', MANAGEMENT, '/students/'),
        _mod('profile', 'Student Profile', '🧾', MANAGEMENT, '/students/', '360° profile'),
        _mod('attendance', 'Attendance', '📋', ACADEMICS, '', '', 'soon'),
        _mod('homework', 'Homework', '📝', ACADEMICS, '', '', 'soon'),
        _mod('assignments', 'Assignments', '✅', ACADEMICS, '', '', 'soon'),
        _mod('lms', 'LMS / Study Materials', '💻', ACADEMICS, '', '', 'soon'),
        _mod('marks', 'Marks Entry', '🔢', ACADEMICS, '', '', 'soon'),
        _mod('performance', 'Academic Performance', '📊', ACADEMICS, '', '', 'soon'),
        _mod('skills', 'Student Skills', '💡', STUDENT_DEV, '/students/', '360° skills'),
        _mod('projects', 'Projects', '🛠️', STUDENT_DEV, '/students/', '360° projects'),
        _mod('remarks', 'Teacher Remarks', '💬', STUDENT_DEV, '/students/', '360° feedback'),
        _mod('portfolio_gen', 'Portfolio Generator', '⚙️', PORTFOLIOS, '/portfolio/generator/'),
        _mod('review', 'Portfolio Review', '🔎', PORTFOLIOS, '/portfolio/approval/'),
        _mod('approval', 'Portfolio Approval', '✅', PORTFOLIOS, '/portfolio/approval/'),
        _mod('reports', 'Academic Reports', '📄', PORTFOLIOS, '/analytics/'),
        _mod('notifications', 'Notifications', '🔔', SYSTEM, '/notifications/'),
    ],
'STUDENT': [
        _mod('dashboard', 'My Dashboard', '📊', OVERVIEW, '/dashboard/'),
        _mod('profile', 'My Profile', '🧾', STUDENT_DEV, '/students/', '360° profile'),
        _mod('academics', 'Academic Performance', '📚', ACADEMICS, '', '', 'soon'),
        _mod('marks', 'Subject Marks', '🔢', ACADEMICS, '', '', 'soon'),
        _mod('attendance', 'Attendance', '📋', ACADEMICS, '', '', 'soon'),
        _mod('homework', 'Homework', '📝', ACADEMICS, '', '', 'soon'),
        _mod('assignments', 'Assignments', '✅', ACADEMICS, '', '', 'soon'),
        _mod('exams', 'Examination & Results', '🗓️', ACADEMICS, '', '', 'soon'),
        _mod('timetable', 'Timetable', '🕒', ACADEMICS, '', '', 'soon'),
        _mod('lms', 'LMS / Study Materials', '💻', ACADEMICS, '', '', 'soon'),
        _mod('skills', 'Skills', '💡', STUDENT_DEV, '/students/', '360° skills'),
        _mod('projects', 'Projects', '🛠️', STUDENT_DEV, '/students/', '360° projects'),
        _mod('internships', 'Internships', '💼', STUDENT_DEV, '/students/'),
        _mod('certs', 'Certificates', '📜', STUDENT_DEV, '/students/'),
        _mod('workshops', 'Workshops & Seminars', '🎤', STUDENT_DEV, '/students/', '360° activities'),
        _mod('hackathons', 'Hackathons & Events', '⚡', STUDENT_DEV, '/students/', '360° activities'),
        _mod('achievements', 'Achievements', '🏆', STUDENT_DEV, '/students/'),
        _mod('portfolio', 'My Portfolio', '📁', PORTFOLIOS, '/portfolio/generator/'),
        _mod('qr', 'QR Portfolio', '🏷️', PORTFOLIOS, '/portfolio/generator/', 'Share via QR'),
        _mod('public', 'Public Portfolio', '🌐', PORTFOLIOS, '/portfolio/generator/', 'Recruiter view'),
        _mod('notifications', 'Notifications', '🔔', SYSTEM, '/notifications/'),
    ],

    'PARENT': [
        _mod('dashboard', 'My Dashboard', '📊', OVERVIEW, '/dashboard/'),
        _mod('child', 'Child Profile', '🧒', MANAGEMENT, '/students/', '360° view'),
        _mod('attendance', 'Attendance', '📋', ACADEMICS, '', '', 'soon'),
        _mod('marks', 'Subject Marks', '🔢', ACADEMICS, '', '', 'soon'),
        _mod('exams', 'Examination Results', '🗓️', ACADEMICS, '', '', 'soon'),
        _mod('homework', 'Homework', '📝', ACADEMICS, '', '', 'soon'),
        _mod('assignments', 'Assignment Status', '✅', ACADEMICS, '', '', 'soon'),
        _mod('remarks', 'Teacher Remarks', '💬', ACADEMICS, '/students/', '360° feedback'),
        _mod('skills', 'Skills', '💡', STUDENT_DEV, '/students/'),
        _mod('projects', 'Projects', '🛠️', STUDENT_DEV, '/students/'),
        _mod('achievements', 'Achievements', '🏆', STUDENT_DEV, '/students/'),
        _mod('portfolio', 'Student 360° Portfolio', '📁', PORTFOLIOS, '/portfolio/generator/'),
        _mod('notifications', 'Notifications', '🔔', SYSTEM, '/notifications/'),
    ],
}


def is_admin_role(role: str) -> bool:
    """True for management roles (Super Admin or HR)."""
    return role in ('SUPER_ADMIN', 'HR')


def is_management(user) -> bool:
    """True for management users (Super Admin or HR)."""
    return bool(getattr(user, 'is_authenticated', False)) and is_admin_role(getattr(user, 'role', ''))


def modules_for(role: str):
    """Return the list of modules a role can see."""
    return ROLE_MODULES.get(role, [])


def group_modules(role: str):
    """Return modules grouped by sidebar section, preserving order."""
    groups = []
    seen = set()
    for module in modules_for(role):
        if module['group'] not in seen:
            seen.add(module['group'])
            groups.append({'name': module['group'], 'items': []})
        groups[-1]['items'].append(module)
    return groups


ROLE_LABELS = {
    'SUPER_ADMIN': 'Super Admin',
    'HR': 'HR / Admin',
    'TEACHER': 'Teacher',
    'STUDENT': 'Student',
    'PARENT': 'Parent',
}