from rest_framework import serializers
from students.models import Student

from .models import (Portfolio, PortfolioApproval, PortfolioTemplate,
                     PortfolioVersion)


class PortfolioTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioTemplate
        fields = ['id', 'name', 'slug', 'description', 'color_scheme', 'font',
                  'layout', 'is_default', 'is_active']


class PortfolioSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    register_number = serializers.CharField(source='student.register_number', read_only=True)
    profile_photo = serializers.ImageField(source='student.profile_photo', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'student', 'student_name', 'register_number', 'profile_photo',
                  'template', 'template_name', 'status', 'status_display', 'title',
                  'slug', 'summary', 'completion_percentage', 'views_count',
                  'published_at', 'created_at', 'updated_at']


class PortfolioVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = PortfolioVersion
        fields = ['id', 'portfolio', 'version_no', 'data', 'comment',
                  'created_by', 'created_by_name', 'created_at']


class PortfolioApprovalSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True, default='')

    class Meta:
        model = PortfolioApproval
        fields = ['id', 'portfolio', 'reviewer', 'reviewer_name', 'status', 'comments',
                  'revision_reason', 'submitted_date', 'review_date', 'created_at']


class PortfolioDetailSerializer(PortfolioSerializer):
    versions = PortfolioVersionSerializer(many=True, read_only=True)
    approvals = PortfolioApprovalSerializer(many=True, read_only=True)
    template_details = PortfolioTemplateSerializer(source='template', read_only=True)

    class Meta(PortfolioSerializer.Meta):
        fields = PortfolioSerializer.Meta.fields + ['data', 'versions', 'approvals',
                                                    'template_details']


class GeneratePortfolioSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    template_id = serializers.IntegerField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)