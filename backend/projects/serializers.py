from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'student', 'student_name', 'name', 'description', 'problem_statement',
                  'technologies', 'student_role', 'start_date', 'end_date', 'github_url',
                  'live_url', 'image', 'key_features', 'created_at']


class ProjectBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'technologies']