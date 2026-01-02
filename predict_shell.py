import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luffa_prediction.settings')
django.setup()

from prediction.views import load_all_models, load_meta_model, preprocess_for_ensemble, CLASS_LABELS
from prediction.models import LuffaDisease

# Set model type and image path
model_type = 'smooth'
image_path = "Luffa Smooth\Alternaria\slAlt-005.jpg"

# Load CNN models for the model type
model_paths = [
    "model/Luffa_Smooth/MobileNetV2_SmoothLuffa_final.keras",
    "model/Luffa_Smooth/VGG16_SmoothLuffa_final.keras"
]
members = load_all_models(model_paths)

# Load meta model (XGBoost)
meta_model = load_meta_model(model_type)

# Preprocess the image and predict
stackX_single = preprocess_for_ensemble(image_path, members)
y_pred = meta_model.predict(stackX_single)
predicted_class = CLASS_LABELS[int(y_pred[0])]

# Get disease info from database
disease_info = LuffaDisease.objects.filter(disease_name=predicted_class).first()
info = disease_info.info if disease_info else "No info available."

# Output the results
print(f"Predicted Disease: {predicted_class}")
print(f"Disease Info: {info}")
