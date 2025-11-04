from django.core.management.base import BaseCommand
from prediction.models import LuffaDisease

LUFFA_DISEASES = [
    ("Alternaria", "Alternaria leaf spot is a fungal disease caused by Alternaria cucumerina. It appears as dark brown to black spots on leaves, often with concentric rings. The disease thrives in warm, humid conditions and can lead to defoliation if untreated."),
    ("Angular Spot", "Angular leaf spot, caused by Pseudomonas syringae pv. lachrymans, creates angular, water-soaked lesions on leaves. It spreads through water splash and can cause significant yield loss in cucurbit crops."),
    ("Fresh", "Healthy, fresh luffa leaves show no signs of disease. They are green, turgid, and free from spots, lesions, or discoloration."),
    ("Holed", "Holed leaves result from insect damage or severe fungal infections. Holes can be caused by various pests including beetles, caterpillars, or fungal pathogens that cause tissue breakdown."),
    ("Mosaic Virus", "Mosaic virus causes mottled, yellow-green patterns on leaves, often with distorted growth. It's transmitted by aphids and can severely reduce plant vigor and fruit production."),
    ("Others", "This category includes various other diseases or damage not fitting the main categories, such as nutritional deficiencies, environmental stress, or unidentified pathogens."),
    ("Bacteria Leaf Spot", "Bacterial leaf spot causes small, dark lesions on leaves that may have a yellow halo."),
    ("Downy Mildew", "Downy mildew is a fungal disease that appears as white or gray patches on the underside of leaves."),
    ("Insect", "Signs of insect damage such as holes, chewing marks, or discoloration."),
    ("Mosaic disease", "Mosaic disease causes irregular patterns and discoloration on leaves.")
]

class Command(BaseCommand):
    help = 'Populate the database with luffa diseases'

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
