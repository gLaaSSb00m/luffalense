from django.core.management.base import BaseCommand
from prediction.models import LuffaDisease, LuffaModel
import os
from django.core.files import File
from django.conf import settings

LUFFA_DISEASES = [
    ("Alternaria", "Alternaria leaf spot is a fungal disease caused by Alternaria cucumerina. It appears as dark brown to black spots on leaves, often with concentric rings. The disease thrives in warm, humid conditions and can lead to defoliation if untreated."),
    ("Angular Spot", "Angular leaf spot, caused by Pseudomonas syringae pv. lachrymans, creates angular, water-soaked lesions on leaves. It spreads through water splash and can cause significant yield loss in cucurbit crops."),
    ("Fresh", "Healthy, fresh luffa leaves show no signs of disease. They are green, turgid, and free from spots, lesions, or discoloration."),
    ("Holed", "Holed leaves result from insect damage or severe fungal infections. Holes can be caused by various pests including beetles, caterpillars, or fungal pathogens that cause tissue breakdown."),
    ("Mosaic Virus", "Mosaic virus causes mottled, yellow-green patterns on leaves, often with distorted growth. It's transmitted by aphids and can severely reduce plant vigor and fruit production."),
    ("Others", "This category includes various other diseases or damage not fitting the main categories, such as nutritional deficiencies, environmental stress, or unidentified pathogens.")
]

class Command(BaseCommand):
    help = 'Populate the database with luffa diseases and model files'

    def handle(self, *args, **options):
        # Populate LuffaDisease with diseases
        for disease_name, info in LUFFA_DISEASES:
            disease, created = LuffaDisease.objects.get_or_create(
                disease_name=disease_name,
                defaults={'info': info}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created LuffaDisease: {disease_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'LuffaDisease {disease_name} already exists.'))

        # Populate LuffaModel with the model files
        models_to_add = [
            ('Smooth Luffa Ensemble', 'model\\Luffa_Smooth\\Luffa_smooth_ensemble_XGB_model.sav', True),
            ('Sponge Luffa Ensemble', 'model\\Luffa Spoonge\\Luffa_Spoonge_ensemble_XGB_model.sav', False),
            ('Smooth MobileNetV2', 'model\\Luffa_Smooth\\MobileNetV2_SmoothLuffa_final.keras', False),
            ('Smooth VGG16', 'model\\Luffa_Smooth\\VGG16_SmoothLuffa_final.keras', False),
            ('Sponge NASNetMobile', 'model\\Luffa Spoonge\\NASNetMobile_SpongeLuffa_final.keras', False),
            ('Sponge VGG16', 'model\\Luffa Spoonge\\VGG16_SpongeLuffa_final.keras', False),
        ]

        for model_name, file_name, is_active in models_to_add:
            model_path = os.path.join(settings.BASE_DIR, file_name)
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    file_obj = File(f, name=file_name)
                    model, created = LuffaModel.objects.get_or_create(
                        name=model_name,
                        defaults={'model_file': file_obj, 'is_active': is_active}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created LuffaModel: {model_name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'LuffaModel {model_name} already exists.'))
            else:
                self.stdout.write(self.style.ERROR(f'Model file not found at {model_path}'))
