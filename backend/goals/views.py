from rest_framework import viewsets

from common.permissions import IsOwnerOrHR
from .models import StudentGoal
from .serializers import StudentGoalSerializer


class StudentGoalViewSet(viewsets.ModelViewSet):
    serializer_class = StudentGoalSerializer
    permission_classes = [IsOwnerOrHR]

    def get_queryset(self):
        qs = StudentGoal.objects.all()
        student_id = self.request.query_params.get('student_id') or self.kwargs.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        elif self.request.user.role == 'STUDENT' and self.request.user.student_profile_id:
            qs = qs.filter(student_id=self.request.user.student_profile_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(student_id=self.request.data.get('student') or self.kwargs.get('student_id'))