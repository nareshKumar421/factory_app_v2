from django.apps import AppConfig


class QualityControlConfig(AppConfig):
    name = 'quality_control'

    def ready(self):
        import quality_control.signals  # noqa: F401
