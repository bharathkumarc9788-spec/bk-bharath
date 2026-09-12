from rest_framework.routers import DefaultRouter
from .views import StudentGoalViewSet

router = DefaultRouter()
router.register('', StudentGoalViewSet, basename='goals')

urlpatterns = router.urls