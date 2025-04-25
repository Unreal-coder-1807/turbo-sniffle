# rail_utils/face_encoder.py

import face_recognition
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
import os

# Define path to models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

PREDICTOR_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
RECOGNITION_MODEL_PATH = os.path.join(MODEL_DIR, "dlib_face_recognition_resnet_model_v1.dat")

# Patch the model paths into face_recognition
face_recognition.api.pose_predictor_68_point_model_location = lambda: PREDICTOR_PATH
face_recognition.api.face_recognition_model_location = lambda: RECOGNITION_MODEL_PATH

def encode_face(image_bytes) -> list | None:
    """
    Encodes a face from a given image in bytes.
    Returns a list (JSON serializable) encoding or None if no face is found.
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        image = np.array(image.convert('RGB'))

        face_locations = face_recognition.face_locations(image, model="hog")
        if not face_locations:
            return None

        face_encoding = face_recognition.face_encodings(image, known_face_locations=face_locations)[0]
        return face_encoding.tolist()
    except Exception as e:
        print(f"⚠️ Face encoding failed: {e}")
        return None

def encode_image_array(image: np.ndarray) -> np.ndarray | None:
    """
    Encodes a face from an OpenCV image (numpy array).
    Returns the raw 128-d encoding or None if no face is found.
    """
    try:
        rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if len(face_locations) == 0:
            return None

        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        if face_encodings:
            return face_encodings[0]
        return None
    except Exception as e:
        print(f"⚠️ Face encoding failed (array input): {e}")
        return None
