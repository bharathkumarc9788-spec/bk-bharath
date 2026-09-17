"""ERP app — School ERP modules."""

from django.apps import AppConfig


class ErpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'erp'
    verbose_name = 'School ERP'