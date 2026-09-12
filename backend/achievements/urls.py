from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet

router = DefaultRouter()
router.register('', AchievementViewSet, basename='achievements')

urlpatterns = router.urls