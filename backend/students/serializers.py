from rest_framework import serializers

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Slim serializer for list views."""
    completion = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(read_only=True, source='user.id')

    class Meta:
        model = Student
        fields = ['id', 'user_id', 'student_id', 'admission_number', 'register_number',
                  'name', 'profile_photo', 'email', 'phone', 'department', 'city', 'state',
                  'gender', 'is_active', 'created_at', 'completion']

    def get_completion(self, obj):
        from common.completion import overall_completion
        return overall_completion(obj)


class StudentDetailSerializer(StudentSerializer):
    """Full profile payload used by the portfolio/public endpoints."""
    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + [
            'date_of_birth', 'address', 'github_url', 'linkedin_url', 'portfolio_url',
            'professional_summary', 'updated_at',
        ]


class BulkUploadRowSerializer(serializers.Serializer):
    """One CSV/Excel row for validation preview."""
    register_number = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Student.Gender.choices, required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    admission_number = serializers.CharField(required=False, allow_blank=True)


class BulkUploadSerializer(serializers.Serializer):
    preview = serializers.BooleanField(default=True)
    rows = serializers.ListField(
        child=BulkUploadRowSerializer(), required=False, default=list
    )