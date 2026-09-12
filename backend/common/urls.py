from django.urls import path
from django.http import JsonResponse


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'Student Portfolio Automation System'})


urlpatterns = [
    path('health/', health),
]