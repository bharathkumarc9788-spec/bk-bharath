from rest_framework.routers import DefaultRouter
from .views import EducationViewSet

router = DefaultRouter()
router.register('', EducationViewSet, basename='education')

urlpatterns = router.urls