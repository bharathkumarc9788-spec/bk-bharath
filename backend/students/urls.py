from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BulkUploadView, StudentViewSet

router = DefaultRouter()
router.register('', StudentViewSet, basename='students')

urlpatterns = [
    path('bulk-upload/', BulkUploadView.as_view(), name='bulk-upload'),
    path('', include(router.urls)),
]