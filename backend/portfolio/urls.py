from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PortfolioViewSet, PublicPortfolioView, TemplateViewSet

router = DefaultRouter()
router.register('templates', TemplateViewSet, basename='templates')
router.register('', PortfolioViewSet, basename='portfolios')

urlpatterns = [
    path('public/<slug:slug>/', PublicPortfolioView.as_view(), name='public-portfolio'),
    path('', include(router.urls)),
]