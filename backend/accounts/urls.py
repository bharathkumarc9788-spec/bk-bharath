from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', MeView.as_view(), name='auth-logout'),  # token discarded client-side
    path('me/', MeView.as_view(), name='auth-me'),
]