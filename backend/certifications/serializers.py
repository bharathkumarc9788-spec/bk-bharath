from rest_framework import serializers
from .models import Certification


class CertificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Certification
        fields = ['id', 'student', 'student_name', 'name', 'issuing_organization',
                  'issue_date', 'expiry_date', 'credential_id', 'url', 'file', 'created_at']