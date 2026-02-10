from django.apps import AppConfig


class RawMaterialGateinConfig(AppConfig):
    name = 'raw_material_gatein'

    def ready(self):
        import raw_material_gatein.signals  # noqa: F401
