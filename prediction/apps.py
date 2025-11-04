from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        # No model preloading needed since using external API
        print("✅ Using Hugging Face API for predictions")
