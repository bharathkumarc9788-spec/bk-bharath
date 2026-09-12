from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import ParentFeedback, Teacher, TeacherFeedback

User = get_user_model()


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'department', 'designation', 'students']


class TeacherFeedbackSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TeacherFeedback
        fields = ['id', 'student', 'student_name', 'teacher', 'teacher_name',
                  'academic_performance', 'attendance', 'homework', 'behaviour',
                  'communication', 'leadership', 'creativity', 'sports_pet',
                  'participation', 'overall_rating', 'remarks', 'created_at']


class ParentFeedbackSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = ParentFeedback
        fields = ['id', 'student', 'student_name', 'parent', 'parent_name',
                  'rating', 'feedback_text', 'created_at']