from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(Q(recipient=user) | Q(recipient__isnull=True, role=user.role)).distinct()

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'ok': True})