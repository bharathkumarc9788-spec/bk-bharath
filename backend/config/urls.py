from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('common.urls')),
    path('api/students/', include('students.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/goals/', include('goals.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/dashboard/', include('analytics.urls')),
    path('api/notifications/', include('notifications.urls')),
    # Academics (Teacher/Parent/Class/Department/Attendance/Exams)
    path('academics/', include('academics.urls')),
    # School ERP (Administration/Boards/Homework/PET/Fees/Hostel/HRMS/Inventory)
    path('erp/', include('erp.urls')),
    # Python (server-rendered) frontend — serves the app at http://localhost:8000/
    path('', include('web.urls')),
]

# Nested section endpoints: /api/students/{id}/education/ etc.
SECTION_PREFIX = 'api/students/<int:student_id>'
for section in ['education', 'skills', 'projects', 'internships',
                'certifications', 'achievements', 'activities']:
    urlpatterns.append(path(f'{SECTION_PREFIX}/{section}/', include(f'{section}.urls')))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)