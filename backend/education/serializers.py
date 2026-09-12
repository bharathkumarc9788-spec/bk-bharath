from rest_framework import serializers
from .models import Education


class EducationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Education
        fields = ['id', 'student', 'student_name', 'college', 'degree', 'department',
                  'academic_year', 'year_of_study', 'klass', 'section', 'board',
                  'cgpa', 'percentage', 'history', 'start_year', 'end_year', 'created_at']