import joblib
import os
import numpy as np
import cv2
import face_recognition
from PIL import Image, ImageEnhance
from pathlib import Path

class ModelLoader:
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.scaler = None
        self.dimensionality_reducer = None
        self.kmeans = None
        self.cluster_centers = None
        self.n_clusters = None
        self.processed_features = None
        self.model_data = None

    def load_models(self):
        try:
            self.model_data = joblib.load(self.model_path)
            if isinstance(self.model_data, dict):
                self.kmeans = self.model_data.get('final_model')
                self.cluster_labels = self.model_data.get('final_labels')
                self.processed_features = self.model_data.get('best_features')
                config = self.model_data.get('best_configuration', {})
                self.n_clusters = config.get('n_clusters')
                dim_red_info = self.model_data.get('dimensionality_reduction')
                if isinstance(dim_red_info, dict):
                    self.dimensionality_reducer = dim_red_info.get('reducer')
                if hasattr(self.kmeans, 'cluster_centers_'):
                    self.cluster_centers = self.kmeans.cluster_centers_
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def load_and_prepare_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                image_array = np.array(img)
                if image_array.dtype != np.uint8:
                    image_array = (image_array * 255).astype(np.uint8)
                return image_array
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def extract_face_encodings(self, image_path, model="hog", num_jitters=1):
        image = self.load_and_prepare_image(image_path)
        if image is None:
            return []
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        try:
            locations = face_recognition.face_locations(image, model=model)
            encodings = face_recognition.face_encodings(image, locations, num_jitters=num_jitters)
            return encodings
        except Exception as e:
            print(f"Face encoding error: {e}")
            return []

    def extract_additional_features(self, image_path):
        image = self.load_and_prepare_image(image_path)
        if image is None:
            return np.array([])
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(image, 1.1, 4)
        if len(faces) == 0:
            return np.array([])
        x, y, w, h = faces[0]
        face = image[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (64, 64))
        hist = cv2.calcHist([face_resized], [0], None, [16], [0, 256]).flatten()
        hist /= (np.sum(hist) + 1e-7)
        return np.array(hist)

    def predict_cluster(self, image_path, return_confidence=False):
        face_encodings = self.extract_face_encodings(image_path)
        if not face_encodings:
            return None
        additional = self.extract_additional_features(image_path)
        features = face_encodings[0]
        if additional.size > 0 and self.processed_features is not None:
            expected = self.processed_features.shape[1] - 128
            if additional.size < expected:
                additional = np.pad(additional, (0, expected - additional.size), 'constant')
            elif additional.size > expected:
                additional = additional[:expected]
            features = np.hstack([features, additional])
        X = features.reshape(1, -1)
        cluster = self.kmeans.predict(X)[0]
        if return_confidence and hasattr(self.kmeans, 'transform'):
            dists = self.kmeans.transform(X)[0]
            conf = 1 - (np.min(dists) / (np.max(dists) + 1e-7))
            return {'cluster': int(cluster), 'confidence': float(conf), 'distance_to_center': float(np.min(dists))}
        return int(cluster)
