from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
# Import your Spotify module if you need it
# import spotipy

app = FastAPI()

# Allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your emotion detection model (replace with your model path)
model = tf.keras.models.load_model("emotion_model.h5")
emotion_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

@app.post("/detect-emotion")
async def detect_emotion(file: UploadFile = File(...)):
    # Read uploaded image
    image = Image.open(BytesIO(await file.read())).convert("RGB")
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.resize(image, (48, 48))
    image = image / 255.0
    image = np.expand_dims(image, axis=(0, -1))

    # Predict emotion
    predictions = model.predict(image)
    emotion = emotion_labels[np.argmax(predictions)]

    return {"emotion": emotion}



