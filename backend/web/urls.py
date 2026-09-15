from django.urls import path

from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index_redirect, name='index'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Dashboard / students
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.students_list, name='students'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:student_id>/personal/', views.personal_update, name='personal_update'),
    path('students/<int:student_id>/<str:section>/add/', views.section_add, name='section_add'),
    path('students/<int:student_id>/<str:section>/<int:item_id>/delete/',
         views.section_delete, name='section_delete'),

    # Bulk upload (HR)
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('bulk-upload/template/', views.download_template, name='bulk_template'),

    # Portfolios
    path('portfolio/generator/', views.portfolio_generator, name='portfolio_generator'),
    path('portfolio/templates/', views.portfolio_templates, name='portfolio_templates'),
    path('portfolio/approval/', views.portfolio_approval, name='portfolio_approval'),
    path('portfolio/published/', views.published_portfolios, name='published_portfolios'),
    path('portfolio/<int:pk>/submit/', views.portfolio_submit, name='portfolio_submit'),
    path('portfolio/<int:pk>/publish/', views.portfolio_publish, name='portfolio_publish'),
    path('portfolio/<int:pk>/review/', views.portfolio_review, name='portfolio_review'),
    path('portfolio/<int:pk>/qr/', views.portfolio_qr, name='portfolio_qr'),
    path('analytics/', views.analytics, name='analytics'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Demo data manager (Super Admin / HR only)
    path('demo-data/', views.demo_data, name='demo_data'),

    # Public portfolio (no login)
    path('portfolio/public/<slug:slug>/', views.public_portfolio, name='public_portfolio'),
]