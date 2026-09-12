from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsOwnerOrHROrTeacher
from .models import ParentFeedback, Teacher, TeacherFeedback
from .serializers import ParentFeedbackSerializer, TeacherFeedbackSerializer, TeacherSerializer


class TeacherFeedbackViewSet(viewsets.ModelViewSet):
    """Teacher/HR create feedback; student view-only for own records."""
    serializer_class = TeacherFeedbackSerializer
    permission_classes = [IsOwnerOrHROrTeacher]

    def get_queryset(self):
        qs = TeacherFeedback.objects.all()
        student_id = self.request.query_params.get('student_id') or self.kwargs.get('student_id')
        user = self.request.user
        if student_id:
            qs = qs.filter(student_id=student_id)
        elif user.role == 'STUDENT' and user.student_profile_id:
            qs = qs.filter(student_id=user.student_profile_id)
        elif user.role == 'TEACHER':
            qs = qs.filter(teacher=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user,
                        student_id=self.request.data.get('student') or self.kwargs.get('student_id'))

    @action(detail=False, methods=['post'])
    def create_feedback(self, request):
        """Teacher/HR adds 360 feedback for a student."""
        if request.user.role not in ('TEACHER', 'HR'):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParentFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = ParentFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ParentFeedback.objects.all()
        student_id = self.request.query_params.get('student_id') or self.kwargs.get('student_id')
        user = self.request.user
        if student_id:
            qs = qs.filter(student_id=student_id)
        elif user.role == 'STUDENT' and user.student_profile_id:
            qs = qs.filter(student_id=user.student_profile_id)
        elif user.role == 'PARENT':
            qs = qs.filter(parent=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user,
                        student_id=self.request.data.get('student') or self.kwargs.get('student_id'))


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    http_method_names = ['get']

    @action(detail=False, methods=['post'])
    def assign_students(self, request):
        """POST {teacher_id, student_ids:[...]} — used by HR to manage assignments."""
        if request.user.role != 'HR':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        teacher = Teacher.objects.filter(user_id=request.data.get('teacher_id')).first()
        if not teacher:
            return Response({'detail': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        teacher.students.set(request.data.get('student_ids', []))
        return Response({'ok': True, 'students': list(teacher.students.values_list('id', flat=True))})