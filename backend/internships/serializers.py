from rest_framework import serializers
from .models import Internship


class InternshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Internship
        fields = ['id', 'student', 'student_name', 'company', 'role_name', 'start_date',
                  'end_date', 'responsibilities', 'technologies', 'description',
                  'certificate', 'created_at']