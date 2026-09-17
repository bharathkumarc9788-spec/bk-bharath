"""ERP url routing."""
from django.urls import path

from . import views

urlpatterns = [
    # Generic management modules
    path('school/', views.erp_module_page, {'module': 'school'}, name='erp-school'),
    path('academic-years/', views.erp_module_page, {'module': 'academic-years'}, name='erp-academic-years'),
    path('boards/', views.erp_module_page, {'module': 'boards'}, name='erp-boards'),
    path('houses/', views.erp_module_page, {'module': 'houses'}, name='erp-houses'),
    path('holidays/', views.erp_module_page, {'module': 'holidays'}, name='erp-holidays'),
    path('announcements/', views.erp_module_page, {'module': 'announcements'}, name='erp-announcements'),
    path('<str:module>/add/', views.erp_module_add, name='erp-module-add'),
    path('<str:module>/<int:pk>/delete/', views.erp_module_delete, name='erp-module-delete'),
    # Dedicated workflows
    path('subjects/', views.subjects_page, name='erp-subjects'),
    path('homework/', views.homework_page, name='erp-homework'),
    path('pet/', views.pet_page, name='erp-pet'),
    path('fees/', views.fees_page, name='erp-fees'),
    path('hostel/', views.hostel_page, name='erp-hostel'),
    path('hrms/', views.hrms_page, name='erp-hrms'),
    path('inventory/', views.inventory_page, name='erp-inventory'),
    path('audit-logs/', views.audit_logs_page, name='erp-audit'),
    path('reports/', views.reports_page, name='erp-reports'),
]