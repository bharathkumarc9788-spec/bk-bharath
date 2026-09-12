from rest_framework import serializers
from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'student', 'student_name', 'activity_type', 'activity_type_display',
                  'title', 'organization', 'description', 'date', 'role', 'created_at']