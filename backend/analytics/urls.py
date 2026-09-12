from django.urls import path
from .views import AnalyticsView, DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('data/', AnalyticsView.as_view(), name='analytics'),
]