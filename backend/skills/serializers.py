from rest_framework import serializers
from .models import Skill


class SkillSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'student', 'student_name', 'category', 'name', 'proficiency', 'created_at']