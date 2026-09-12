from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from audit.models import AuditLog
from common.completion import overall_completion, section_completion
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from portfolio.models import Portfolio, PortfolioView
from students.models import Student


class _BaseDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def _kpis(self, students, portfolios):
        incomplete = 0
        for s in students[:400]:
            if overall_completion(s) < 70:
                incomplete += 1
        return {
            'total_students': students.count(),
            'portfolios_generated': portfolios.count(),
            'pending_approval': portfolios.filter(
                status__in=[Portfolio.Status.SUBMITTED, Portfolio.Status.UNDER_REVIEW]).count(),
            'published_portfolios': portfolios.filter(status=Portfolio.Status.PUBLISHED).count(),
            'incomplete_profiles': incomplete,
            'portfolio_views': sum(p.views_count for p in portfolios),
            'avg_completion': self._avg_completion(students),
        }

    def _avg_completion(self, students):
        if not students.exists():
            return 0
        seen = students[:200]
        total = sum(overall_completion(s) for s in seen)
        return round(total / max(1, len(seen)))

    def _completion_bins(self, students):
        bins = {'0-49%': 0, '50-69%': 0, '70-89%': 0, '90-100%': 0}
        for s in students[:400]:
            c = overall_completion(s)
            if c < 50:
                bins['0-49%'] += 1
            elif c < 70:
                bins['50-69%'] += 1
            elif c < 90:
                bins['70-89%'] += 1
            else:
                bins['90-100%'] += 1
        return [{'label': k, 'value': v} for k, v in bins.items()]

    def _department_analysis(self, students):
        depts = (students.exclude(department='')
                 .values('department').annotate(count=Count('id'))
                 .order_by('-count')[:10])
        return [{'department': d['department'], 'count': d['count']} for d in depts]

    def _portfolio_status(self, portfolios):
        counts = portfolios.values('status').annotate(count=Count('id'))
        status_map = dict(portfolios.model.Status.choices)
        result = {label: 0 for _, label in status_map.items()}
        for item in counts:
            label = status_map.get(item['status'], item['status'])
            if label in result:
                result[label] = item['count']
        return [{'status': k, 'count': v} for k, v in result.items() if v > 0]

    def _support_students(self, students, limit=10):
        support = []
        for s in students[:400]:
            sections = section_completion(s)
            missing = [sec['section'] for sec in sections if sec['percent'] < 100]
            portfolio = Portfolio.objects.filter(student=s).first()
            support.append({
                'id': s.id,
                'name': s.name,
                'register_number': s.register_number,
                'department': s.department,
                'completion': overall_completion(s),
                'missing': missing[:5],
                'status': portfolio.get_status_display() if portfolio else 'No portfolio',
            })
        support.sort(key=lambda x: x['completion'])
        return support[:limit]


class DashboardView(_BaseDashboard):
    """All KPIs + chart data for the admin dashboard."""

    def get(self, request):
        if request.user.role == 'TEACHER' and hasattr(request.user, 'teacher_profile'):
            qs = request.user.teacher_profile.students.all()
        else:
            qs = Student.objects.all()
        portfolios = Portfolio.objects.all()

        approval_queue = portfolios.filter(
            status__in=[Portfolio.Status.SUBMITTED, Portfolio.Status.UNDER_REVIEW]
        ).order_by('updated_at')[:8]
        audit_logs = AuditLog.objects.all()[:12]

        return Response({
            'kpis': self._kpis(qs, portfolios),
            'completion_bins': self._completion_bins(qs),
            'department_analysis': self._department_analysis(qs),
            'portfolio_status': self._portfolio_status(portfolios),
            'students_requiring_support': self._support_students(qs),
            'recent_students': [
                {'id': s.id, 'name': s.name, 'register_number': s.register_number,
                 'department': s.department, 'email': s.email,
                 'completion': overall_completion(s), 'created_at': s.created_at}
                for s in qs.order_by('-created_at')[:8]
            ],
            'approval_queue': [{
                'id': p.id, 'student_name': p.student.name, 'student_id': p.student_id,
                'status': p.status, 'completion': p.completion_percentage,
                'updated_at': p.updated_at,
            } for p in approval_queue],
            'recent_activities': [
                {'id': a.id, 'actor': a.actor.username if a.actor else 'system',
                 'action': a.action, 'details': a.details, 'created_at': a.created_at}
                for a in audit_logs
            ],
        })


class AnalyticsView(_BaseDashboard):
    """Views over time + deeper analytics."""

    def get(self, request):
        now = timezone.now()
        last_30 = PortfolioView.objects.filter(viewed_at__gte=now - timedelta(days=30))
        daily = {}
        for v in last_30:
            key = v.viewed_at.date().isoformat()
            daily[key] = daily.get(key, 0) + 1
        views_series = [{'date': d, 'views': c} for d, c in sorted(daily.items())]

        students = Student.objects.all()
        portfolios = Portfolio.objects.all()

        avg_by_dept = []
        depts = students.exclude(department='').values_list('department', flat=True).distinct()[:10]
        for dept in sorted(depts):
            qs = students.filter(department=dept)
            avg = sum(overall_completion(s) for s in qs[:100]) / max(1, qs.count())
            avg_by_dept.append({'department': dept, 'avg_completion': round(avg)})

        return Response({
            'views_30_days': views_series,
            'total_views_30_days': last_30.count(),
            'published_by_department': [
                {'department': p['student__department'] or 'Unknown', 'count': p['count']}
                for p in portfolios.filter(status=Portfolio.Status.PUBLISHED)
                .values('student__department').annotate(count=Count('id'))],
            'avg_completion_by_department': avg_by_dept,
            'completion_bins': self._completion_bins(students),
            'portfolio_status': self._portfolio_status(portfolios),
        })
        return support[:limit]