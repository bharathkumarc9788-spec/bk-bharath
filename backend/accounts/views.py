from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import CustomTokenObtainPairSerializer, UserSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    """POST username + password -> access + refresh tokens with user payload."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'user': UserSerializer(request.user).data,
            'student_id': getattr(getattr(request.user, 'student_profile', None), 'id', None),
        })


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SUPER_ADMIN', 'HR'):
            return self.queryset
        return self.queryset.filter(id=user.id)