import warnings
warnings.filterwarnings("ignore")
import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.conf import settings
import openai

# ====================================================
# Hugging Face API Configuration
# ====================================================
HF_API_BASE = "https://Abid1012-luffa-disease-api.hf.space/predict/image"

# ====================================================
# Disease Information Dictionary
# ====================================================
DISEASE_INFO_DICT = {
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

@csrf_exempt
@never_cache
def predict(request):
    if request.method == "POST":
        try:
            image_file = request.FILES.get("image")
            category = request.POST.get("model_type", "Smooth").capitalize()  # Default to Smooth, capitalize

            if not image_file:
                return JsonResponse({"error": "No image provided"}, status=400)

            if category not in ["Smooth", "Sponge"]:
                return JsonResponse({"error": "Invalid category. Must be 'Smooth' or 'Sponge'"}, status=400)

            # Prepare API request
            url = f"{HF_API_BASE}?category={category}"
            files = {"file": image_file}
            response = requests.post(url, files=files)

            if response.status_code != 200:
                return JsonResponse({"error": f"API request failed: {response.status_code}"}, status=500)

            api_result = response.json()

            if api_result.get("status") != "success":
                return JsonResponse({"error": "Prediction failed"}, status=500)

            predicted_disease = api_result.get("prediction")
            category = api_result.get("category")

            # Get disease info
            info = DISEASE_INFO_DICT.get(predicted_disease, "No info available.")

            return JsonResponse({
                "prediction": predicted_disease,
                "category": category,
                "disease_info": info,
                "status": "success"
            })

        except Exception as e:
            import logging
            logging.error(f"Error in predict function: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "prediction/predict.html")

def home(request):
    return render(request, "prediction/home.html")

def chat(request):
    return render(request, "prediction/chat.html")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            # Initialize OpenAI client with OpenRouter
            client = openai.OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )

            # Create chat completion
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized assistant for Luffa plant information. You can only provide information about Luffa plants, their cultivation, diseases, health, and related topics. If the user asks about anything else, politely decline and redirect the conversation back to Luffa plants. Always respond in plain text without using markdown formatting, bold text, italics, or special characters like emojis."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                stream=False
            )

            # Extract the response content
            bot_response = response.choices[0].message.content

            return JsonResponse({
                "status": "success",
                "response": bot_response
            })

        except Exception as e:
            import logging
            logging.error(f"Error in chat_api function: {str(e)}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
