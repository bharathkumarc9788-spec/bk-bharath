from django.conf import settings
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import log_action
from students.models import Student

from .models import Portfolio, PortfolioApproval, PortfolioTemplate, PortfolioVersion
from .serializers import (GeneratePortfolioSerializer, PortfolioApprovalSerializer,
                          PortfolioDetailSerializer, PortfolioSerializer,
                          PortfolioTemplateSerializer, PortfolioVersionSerializer)
from .services import (approve_portfolio, build_public_data, generate_portfolio,
                       publish_portfolio, record_view, reject_portfolio, require_revision,
                       start_review, submit_portfolio, validate_required)


class PublicPortfolioView(APIView):
    """No-login public portfolio by slug."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        portfolio = Portfolio.objects.filter(slug=slug).first()
        if not portfolio or portfolio.status != Portfolio.Status.PUBLISHED:
            return Response({'detail': 'Portfolio not found or not published.'},
                            status=status.HTTP_404_NOT_FOUND)
        record_view(portfolio)
        return Response(build_public_data(portfolio))


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PortfolioTemplate.objects.filter(is_active=True)
    serializer_class = PortfolioTemplateSerializer


class PortfolioViewSet(viewsets.ModelViewSet):
    """Core portfolio workflows: generate, preview, submit, review, publish, QR."""
    serializer_class = PortfolioSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        qs = Portfolio.objects.all()
        user = self.request.user
        if user.role == 'STUDENT':
            return qs.filter(student__user=user)
        if user.role == 'TEACHER':
            profile = getattr(user, 'teacher_profile', None)
            if profile:
                return qs.filter(student__teachers_assigned=profile)
            return qs.none()
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PortfolioDetailSerializer
        return PortfolioSerializer

    def _can_generate(self, student):
        user = self.request.user
        return user.role == 'HR' or (user.role == 'STUDENT' and student.user_id == user.id)

    def _can_review(self):
        return self.request.user.role in ('HR', 'TEACHER')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = GeneratePortfolioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = Student.objects.filter(pk=serializer.validated_data['student_id']).first()
        if not student:
            return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        if not self._can_generate(student):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        missing = validate_required(student)
        template_id = serializer.validated_data.get('template_id')
        template = PortfolioTemplate.objects.filter(pk=template_id).first() if template_id else None
        if not template:
            template = (PortfolioTemplate.objects.filter(is_default=True).first()
                        or PortfolioTemplate.objects.first())

        try:
            portfolio = generate_portfolio(student, template, request.user,
                                           comment=serializer.validated_data.get('comment', ''))
        except Exception as exc:  # pragma: no cover
            return Response({'detail': f'Generation failed: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)
        log_action(request.user, 'PORTFOLIO_GENERATED', 'Portfolio', str(portfolio.id),
                   f'Generated portfolio for {student.name}')
        return Response({
            'portfolio': PortfolioDetailSerializer(portfolio).data,
            'missing_required': missing,
        })
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        portfolio = self.get_object()
        submit_portfolio(portfolio, request.user)
        log_action(request.user, 'PORTFOLIO_SUBMITTED', 'Portfolio', str(portfolio.id))
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        if not self._can_review():
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        portfolio = self.get_object()
        start_review(portfolio, request.user)
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not self._can_review():
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        portfolio = self.get_object()
        approve_portfolio(portfolio, request.user,
                          comments=request.data.get('comments', 'Approved by reviewer'))
        log_action(request.user, 'PORTFOLIO_APPROVED', 'Portfolio', str(portfolio.id))
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if not self._can_review():
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        portfolio = self.get_object()
        comments = request.data.get('comments') or request.data.get('reason', '')
        reject_portfolio(portfolio, request.user, comments=comments)
        log_action(request.user, 'PORTFOLIO_REJECTED', 'Portfolio', str(portfolio.id), comments)
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['post'])
    def revision(self, request, pk=None):
        if not self._can_review():
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        portfolio = self.get_object()
        reason = request.data.get('revision_reason') or request.data.get('comments', '')
        require_revision(portfolio, request.user, reason)
        log_action(request.user, 'PORTFOLIO_REVISION', 'Portfolio', str(portfolio.id), reason)
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        if not self._can_review():
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        portfolio = self.get_object()
        try:
            publish_portfolio(portfolio, request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        log_action(request.user, 'PORTFOLIO_PUBLISHED', 'Portfolio', str(portfolio.id),
                   f'Public URL: /portfolio/public/{portfolio.slug}/')
        return Response(self.get_serializer(portfolio).data)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        portfolio = self.get_object()
        return Response(PortfolioVersionSerializer(portfolio.versions.all(), many=True).data)

    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        portfolio = self.get_object()
        return Response(PortfolioApprovalSerializer(portfolio.approvals.all(), many=True).data)

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        """Downloadable QR code pointing at the public portfolio URL."""
        import qrcode
        from io import BytesIO

        portfolio = self.get_object()
        if portfolio.status != Portfolio.Status.PUBLISHED or not portfolio.slug:
            return Response({'detail': 'Portfolio is not published.'},
                            status=status.HTTP_400_BAD_REQUEST)
        url = f'{settings.FRONTEND_URL}/portfolio/public/{portfolio.slug}'
        img = qrcode.make(url)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="portfolio-qr-{portfolio.slug}.png"'
        return response

    @action(detail=True, methods=['get'])
    def public_url(self, request, pk=None):
        portfolio = self.get_object()
        if not portfolio.slug:
            return Response({'public_url': None, 'message': 'Portfolio has no slug yet.'})
        return Response({
            'public_url': f'{settings.FRONTEND_URL}/portfolio/public/{portfolio.slug}',
            'slug': portfolio.slug,
        })