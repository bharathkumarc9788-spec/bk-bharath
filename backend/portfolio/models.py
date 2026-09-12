from django.conf import settings
from django.db import models
from django.utils.text import slugify


class PortfolioTemplate(models.Model):
    """Available portfolio templates."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color_scheme = models.CharField(max_length=50, default='indigo')
    font = models.CharField(max_length=100, default='Inter')
    layout = models.CharField(max_length=50, default='classic')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    """A generated student portfolio + its approval/publish state."""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        REVISION_REQUIRED = 'REVISION_REQUIRED', 'Revision Required'
        PUBLISHED = 'PUBLISHED', 'Published'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='portfolios')
    template = models.ForeignKey(PortfolioTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='portfolios')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    summary = models.TextField(blank=True)
    completion_percentage = models.PositiveIntegerField(default=0)
    data = models.JSONField(default=dict, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='created_portfolios')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.student.name} — {self.status}'

    def save(self, *args, **kwargs):
        if not self.slug and self.student_id:
            base = slugify(f'{self.student.name}-{self.student.register_number}')[:80]
            base = base or f'student-{self.student_id}'
            slug, n = base, 2
            while Portfolio.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PortfolioVersion(models.Model):
    """A stored snapshot for every regeneration."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='versions')
    version_no = models.PositiveIntegerField(default=1)
    data = models.JSONField(default=dict)
    comment = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_no']

    def __str__(self):
        return f'v{self.version_no}'


class PortfolioApproval(models.Model):
    """Approval history record."""
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION_REQUIRED', 'Revision Required'),
    ]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='approvals')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='reviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comments = models.TextField(blank=True)
    revision_reason = models.TextField(blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.portfolio} -> {self.status}'


class PortfolioView(models.Model):
    """Analytics event: one row per public portfolio visit."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='view_events')
    viewer_label = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f'View of {self.portfolio_id}'