from rest_framework.routers import DefaultRouter
from .views import ParentFeedbackViewSet, TeacherFeedbackViewSet, TeacherViewSet

router = DefaultRouter()
router.register('teacher-feedback', TeacherFeedbackViewSet, basename='teacher-feedback')
router.register('parent-feedback', ParentFeedbackViewSet, basename='parent-feedback')
router.register('teachers', TeacherViewSet, basename='teachers')

urlpatterns = router.urls