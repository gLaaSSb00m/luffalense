from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        # Preload all models on startup
        from .views import get_cached_models
        print("🔄 Preloading models...")
        get_cached_models('smooth')
        get_cached_models('sponge')
        print("✅ All models preloaded successfully!")
