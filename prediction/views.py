import warnings
warnings.filterwarnings("ignore")
import numpy as np
import os
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, array_to_img
import pickle
from xgboost import XGBClassifier
import tensorflow as tf
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
# Removed database models import

# ====================================================
# 1️⃣ Load all CNN models
# ====================================================
def load_all_models(model_paths):
    all_models = []
    for path in model_paths:
        model = load_model(path, compile=False)
        model_name = os.path.basename(path)
        all_models.append(model)
        print(f"✅ Loaded model: {model_name}")
    return all_models

# Removed database function

# Get model paths based on model_type
def get_model_paths_by_type(model_type):
    if model_type == 'smooth':
        return [
            "model/Luffa_Smooth/MobileNetV2_SmoothLuffa_final.keras",
            "model/Luffa_Smooth/VGG16_SmoothLuffa_final.keras"
        ]
    elif model_type == 'sponge':
        return [
            "model/Luffa Spoonge/NASNetMobile_SpongeLuffa_final.keras",
            "model/Luffa Spoonge/VGG16_SpongeLuffa_final.keras"
        ]
    else:
        raise ValueError("Invalid model type")

# ====================================================
# 2️⃣ Load trained meta-model (XGBoost)
# ====================================================
def load_meta_model(model_type):
    if model_type == 'smooth':
        meta_model_path = "model/Luffa_Smooth/Luffa_smooth_ensemble_XGB_model.json"
    elif model_type == 'sponge':
        meta_model_path = "model/Luffa Spoonge/Luffa_spoonge_ensemble_XGB_model.json"
    else:
        raise ValueError("Invalid model type")

    meta_model = XGBClassifier()
    
    meta_model.load_model(meta_model_path)
    print(f"✅ Loaded XGBoost meta learner for {model_type}")
    return meta_model

# Cache loaded models to avoid reloading on every request
MODEL_CACHE = {}

def get_cached_models(model_type):
    if model_type not in MODEL_CACHE:
        model_paths = get_model_paths_by_type(model_type)
        MODEL_CACHE[model_type] = {
            'cnn_models': load_all_models(model_paths),
            'meta_model': load_meta_model(model_type)
        }
    return MODEL_CACHE[model_type]

# ====================================================
# 3️⃣ Preprocess a single image for all models
# ====================================================
def preprocess_for_ensemble(image_path, members):
    img = Image.open(image_path).convert('RGB')
    img_array = img_to_array(img)

    stackX = None
    for model in members:
        expected_shape = model.input_shape[1:3]  # Example (224, 224)
        resized_img = np.array(
            img_to_array(array_to_img(img_array).resize(expected_shape, resample=Image.BICUBIC))
        ) / 255.0  # normalize

        resized_img = np.expand_dims(resized_img, axis=0)  # (1, H, W, C)
        yhat = model.predict(resized_img, verbose=0)
        yhat = yhat.numpy() if hasattr(yhat, 'numpy') else yhat

        if stackX is None:
            stackX = yhat
        else:
            stackX = np.dstack((stackX, yhat))

    # Flatten to [1, members × probabilities]
    stackX = stackX.reshape((stackX.shape[0], stackX.shape[1] * stackX.shape[2]))
    return stackX

# ====================================================
# 4️⃣ Map class index → label name
# ====================================================
def get_class_labels(model_type):
    if model_type == 'smooth':
        return ['Alternaria', 'Angular Spot', 'Fresh', 'Holed', 'Mosaic Virus', 'Others']
    elif model_type == 'sponge':
        return ['Bacteria Leaf Spot', 'Downy Mildew', 'Fresh', 'Insect', 'Mosaic disease', 'Others']
    else:
        raise ValueError("Invalid model type")

@csrf_exempt
@never_cache
def predict(request):
    if request.method == "POST":
        try:
            image_file = request.FILES.get("luffa_image")
            model_type = request.POST.get("model_type", "smooth")  # default to smooth

            if not image_file:
                return JsonResponse({"error": "No image provided"}, status=400)

            if model_type not in ['smooth', 'sponge']:
                return JsonResponse({"error": "Invalid model type"}, status=400)

            # Save the uploaded image to media/predictions/current.jpg
            media_path = os.path.join('media', 'predictions')
            os.makedirs(media_path, exist_ok=True)
            image_path = os.path.join(media_path, 'current.jpg')
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # Load models using cache
            cached_models = get_cached_models(model_type)
            members = cached_models['cnn_models']
            meta_model = cached_models['meta_model']

            # Preprocess and predict
            stackX_single = preprocess_for_ensemble(image_path, members)
            y_pred = meta_model.predict(stackX_single)
            class_labels = get_class_labels(model_type)
            predicted_class = class_labels[int(y_pred[0])]

            # Get disease info from hardcoded dictionary
            disease_info_dict = {
                'Alternaria': 'Alternaria leaf spot is a fungal disease that causes dark spots on leaves. It thrives in warm, humid conditions.',
                'Angular Spot': 'Angular leaf spot is a bacterial disease causing angular water-soaked lesions on leaves.',
                'Fresh': 'The leaf appears healthy and fresh with no visible signs of disease.',
                'Holed': 'Holes in leaves may be caused by insect damage or physical injury.',
                'Mosaic Virus': 'Mosaic virus causes mottled patterns on leaves and can stunt plant growth.',
                'Others': 'Other unidentified diseases or conditions affecting the plant.',
                'Bacteria Leaf Spot': 'Bacterial leaf spot causes small, dark lesions on leaves that may have a yellow halo.',
                'Downy Mildew': 'Downy mildew is a fungal disease that appears as white or gray patches on the underside of leaves.',
                'Insect': 'Signs of insect damage such as holes, chewing marks, or discoloration.',
                'Mosaic disease': 'Mosaic disease causes irregular patterns and discoloration on leaves.'
            }
            info = disease_info_dict.get(predicted_class, "No info available.")

            return JsonResponse({
                "predicted_disease": predicted_class,
                "disease_info": info,
                "message": f"Predicted Disease: {predicted_class}"
            })

        except Exception as e:
            import logging
            logging.error(f"Error in predict function: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "prediction/predict.html")

def home(request):
    return render(request, "prediction/home.html")
