import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

print('TensorFlow version:', tf.__version__)
print('Available devices:', tf.config.list_physical_devices())

model = tf.keras.models.load_model('model/Luffa Spoonge/NASNetMobile_SpongeLuffa_final.keras')
print('Model loaded successfully')
print(model.build(input_shape=(None, height, width, channels)))  # e.g., (None, 224, 224, 3)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
print('Converter created')

tflite_model = converter.convert()
print('Conversion completed')

with open('test.tflite', 'wb') as f:
    f.write(tflite_model)
print('TFLite model saved')
