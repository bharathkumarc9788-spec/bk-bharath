from django.urls import path

from . import views

urlpatterns = [
    # Generic management modules
    path('teacher/', views.module_page, {'module': 'teacher'}),
    path('parent/', views.module_page, {'module': 'parent'}),
    path('department/', views.module_page, {'module': 'department'}),
    path('class/', views.module_page, {'module': 'class'}),
    path('<str:module>/add/', views.module_add, name='academics-add'),
    path('<str:module>/<int:pk>/delete/', views.module_delete, name='academics-delete'),

    # Attendance
    path('attendance/', views.attendance_page, name='academics-attendance'),
    path('attendance/teacher/', views.teacher_attendance_page, name='academics-teacher-attendance'),

    # Exams & results
    path('exams/', views.exams_page, name='academics-exams'),
    path('exams/<int:exam_id>/', views.exam_detail, name='academics-exam-detail'),
    path('exams/<int:exam_id>/marks/<int:subject_id>/', views.mark_entry, name='academics-marks'),

    # Leaves & report card
    path('leaves/', views.leave_page, name='academics-leaves'),
    path('report-card/<int:student_id>/', views.report_card, name='academics-report-card'),
]