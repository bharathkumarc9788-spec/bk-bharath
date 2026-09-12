from django.apps import AppConfig


class WebConfig(AppConfig):
    """Server-rendered Python frontend (replaces the React app)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'