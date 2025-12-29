# LuffaLense

AI-powered web app for Luffa leaf disease recognition with a Hugging Face-hosted prediction service and an optional AI chat assistant.

## What this project does
- Classifies Luffa leaf images using a remote model hosted on Hugging Face Spaces
- Supports two categories (models): Smooth Luffa and Sponge Luffa
- Returns human-friendly disease info alongside the prediction
- Optional AI chat assistant specialized in Luffa topics (via OpenRouter)

## Architecture overview
- Web framework: Django 5
- Prediction model: External Hugging Face Space endpoint
  - Base URL used by the app: https://Abid1012-luffa-disease-api.hf.space/predict/image
  - Category query parameter selects the model: Smooth or Spoonge
  - Image is sent as multipart/form-data under the file field name file
- Image processing: Pillow (PIL)
- Database: SQLite (dev) / PostgreSQL (prod)
- Frontend: HTML/CSS/JS (+ Bootstrap)

## Quick start (local)
1) Clone and enter the project

   git clone <repository-url>
   cd Luffa_Prediction

2) Create a virtual environment and activate it

   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # or
   source .venv/bin/activate  # macOS/Linux

3) Install dependencies

   pip install -r requirements.txt

4) Run migrations

   python manage.py migrate

5) Start the dev server

   python manage.py runserver

Then open http://localhost:8000

## Using the prediction feature
From the web UI:
- Go to Get Started
- Choose model type: Smooth or Sponge
- Upload a clear image of a Luffa leaf
- Receive the predicted disease and additional information

From the Django API endpoint (local):
- Endpoint: POST http://localhost:8000/predict/
- Form fields:
  - model_type: Smooth or Sponge (Sponge is internally mapped to Spoonge)
  - image: file upload
- Response shape:
  {
    "prediction": "<disease>",
    "category": "Smooth|Spoonge",
    "disease_info": "<human-readable details>",
    "status": "success"
  }

Notes
- The backend saves uploads to media/predictions/current.jpg and forwards the image to the Hugging Face Space.
- If you pass model_type=Sponge, the backend converts it to Spoonge to match the Space API.

## Hugging Face Space prediction API
This project relies on a remote prediction API hosted on Hugging Face Spaces.

Base URL used by the app
- https://Abid1012-luffa-disease-api.hf.space/predict/image

Request
- Method: POST
- Query param: category=Smooth or category=Spoonge
- Body: multipart/form-data with file=<image binary>

Example with curl (calling the HF Space directly)

  curl -X POST "https://Abid1012-luffa-disease-api.hf.space/predict/image?category=Smooth" \
       -H "Accept: application/json" \
       -F "file=@/path/to/leaf.jpg"

Example with Python (requests)

  import requests

  url = "https://Abid1012-luffa-disease-api.hf.space/predict/image?category=Spoonge"
  with open("/path/to/leaf.jpg", "rb") as f:
      files = {"file": f}
      r = requests.post(url, files=files)
      r.raise_for_status()
      print(r.json())

Expected successful response
- HTTP 200
- JSON body:
  {
    "status": "success",
    "prediction": "<disease label>",
    "category": "Smooth|Spoonge"
  }

Common errors
- 400 invalid input (e.g., missing image)
- 500 failure to get a prediction (e.g., model side issue)

Authentication
- The referenced Space is public and does not require a token. If your Space is private, add Authorization headers as needed.

## Supported labels
Smooth Luffa
- Alternaria
- Angular Spot
- Fresh
- Holed
- Mosaic Virus
- Others

Sponge Luffa
- Bacteria Leaf Spot
- Downy Mildew
- Fresh
- Insect
- Mosaic disease
- Others

## Configuration
- Hugging Face endpoint is defined in prediction/views.py as HF_API_BASE
  - Default: https://Abid1012-luffa-disease-api.hf.space/predict/image
  - To change it, update HF_API_BASE and restart the server.
- Chat assistant (optional): requires an OpenRouter API key in your Django settings (OPENROUTER_API_KEY)

## Development commands
- Run tests

  python manage.py test prediction

- Collect static (if needed)

  python manage.py collectstatic

## Deployment
- The project includes a render.yaml for deployment on Render. A typical setup involves:
  - Gunicorn WSGI server
  - PostgreSQL database
  - WhiteNoise for static files
- For local production-like run (where supported):

  pip install gunicorn
  gunicorn rice_prediction.wsgi:application --bind 0.0.0.0:8000

## Project structure (high level)
Luffa_Prediction/
├── rice_prediction/         Django project settings
├── prediction/              App with views and API integration
├── templates/               HTML templates
├── static/                  CSS/JS/assets
├── media/                   Uploaded images (runtime)
├── requirements.txt         Python deps
├── manage.py                Django CLI
└── README.md                This file

## Credits and license
- Developed by: ABID
- Supervised by: Mii (https://annex.bubt.edu.bd/mii/?chapter=profile)
- License: MIT