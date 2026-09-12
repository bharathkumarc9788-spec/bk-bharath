from rest_framework.routers import DefaultRouter
from .views import CertificationViewSet

router = DefaultRouter()
router.register('', CertificationViewSet, basename='certifications')

urlpatterns = router.urls