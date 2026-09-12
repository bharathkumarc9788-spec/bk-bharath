from rest_framework import serializers
from .models import StudentGoal


class StudentGoalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = StudentGoal
        fields = ['id', 'student', 'student_name', 'category', 'title', 'description',
                  'target_date', 'status', 'created_at']