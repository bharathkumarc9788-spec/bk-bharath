from rest_framework.routers import DefaultRouter
from .views import InternshipViewSet

router = DefaultRouter()
router.register('', InternshipViewSet, basename='internships')

urlpatterns = router.urls