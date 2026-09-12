from rest_framework import serializers
from .models import Achievement


class AchievementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'student', 'student_name', 'title', 'organization', 'date',
                  'level', 'description', 'proof', 'created_at']