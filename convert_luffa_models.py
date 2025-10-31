import os
import shutil
import tensorflow as tf

# Set logging level to suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Disable GPU to force CPU usage
tf.config.set_visible_devices([], 'GPU')

# List of model paths to convert
models_to_convert = [
    "model/Luffa Spoonge/NASNetMobile_SpongeLuffa_final.keras",
    "model/Luffa Spoonge/VGG16_SpongeLuffa_final.keras",
    "model/Luffa_Smooth/MobileNetV2_SmoothLuffa_final.keras",
    "model/Luffa_Smooth/VGG16_SmoothLuffa_final.keras"
]

# Output directory for TFLite models
output_dir = "tflite"
os.makedirs(output_dir, exist_ok=True)

for model_path in models_to_convert:
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        continue

    try:
        # Load the Keras model
        model = tf.keras.models.load_model(model_path)
        print(f"Loaded model: {model_path}")

        # Save as SavedModel to temp directory
        temp_saved_model_dir = "temp_saved_model"
        if os.path.exists(temp_saved_model_dir):
            shutil.rmtree(temp_saved_model_dir)
        model.export(temp_saved_model_dir)  # TensorFlow 2.17 requires export for SavedModel
        print(f"Saved model as SavedModel: {temp_saved_model_dir}")

        # Convert to TFLite with optimizations and Flex ops fallback
        converter = tf.lite.TFLiteConverter.from_saved_model(temp_saved_model_dir)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS  # Enables fallback for unsupported ops
        ]
        tflite_model = converter.convert()
        print(f"Converted model: {model_path}")

        # Clean up temp SavedModel
        shutil.rmtree(temp_saved_model_dir)

        # Save the TFLite model
        base_name = os.path.splitext(os.path.basename(model_path))[0]
        tflite_path = os.path.join(output_dir, f"{base_name}.tflite")
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        print(f"Saved TFLite model: {tflite_path}")

    except Exception as e:
        print(f"Error converting {model_path}: {e}")

print("All conversions completed.")