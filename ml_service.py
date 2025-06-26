import os
import numpy as np
import pickle
import joblib
from PIL import Image, ImageEnhance
import insightface
from sklearn.manifold import Isomap
import logging
from typing import Optional, Dict, Any, Tuple
import cv2
import warnings

class MLModelService:
    """
    Complete ML pipeline service for dating app clustering
    Handles: Image preprocessing -> ArcFace encoding -> ISOMAP -> Clustering
    """
    
    def __init__(self, model_dir='models'):
        """
        Initialize the ML service
        
        Args:
            model_dir: Directory containing the model files
        """
        self.model_dir = model_dir
        self.arcface_model = None
        self.male_isomap_reducer = None
        self.female_isomap_reducer = None
        self.male_cluster_model = None
        self.female_cluster_model = None
        self.male_reference_embeddings = None
        self.female_reference_embeddings = None
        
        # Suppress warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        # Initialize models
        self._load_models()
    
    def _load_models(self):
        """Load all required models"""
        try:
            # Load ArcFace model
            self._load_arcface_model()
            
            # Load clustering models
            self._load_clustering_models()
            
            logging.info("All ML models loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            raise
    
    def _load_arcface_model(self):
        """Load ArcFace model from insightface"""
        try:
            # Initialize insightface with suppressed warnings
            self.arcface_model = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
            self.arcface_model.prepare(ctx_id=0, det_size=(640, 640))
            logging.info("ArcFace model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading ArcFace model: {e}")
            raise
    
    def _load_clustering_models(self):
        """Load pre-trained clustering models"""
        try:
            # Load male clustering model
            male_model_path = os.path.join(self.model_dir, 'male_cluster_model.pkl')
            if os.path.exists(male_model_path):
                with open(male_model_path, 'rb') as f:
                    male_data = pickle.load(f)
                    self._process_model_data(male_data, 'male')
            else:
                logging.warning(f"Male model not found at {male_model_path}")
            
            # Load female clustering model
            female_model_path = os.path.join(self.model_dir, 'female_cluster_model.pkl')
            if os.path.exists(female_model_path):
                with open(female_model_path, 'rb') as f:
                    female_data = pickle.load(f)
                    self._process_model_data(female_data, 'female')
            else:
                logging.warning(f"Female model not found at {female_model_path}")
                
        except Exception as e:
            logging.error(f"Error loading clustering models: {e}")
            raise
    
    def _process_model_data(self, model_data, gender):
        """Process loaded model data and extract components"""
        try:
            if isinstance(model_data, dict):
                # Extract the clustering model
                if 'final_model' in model_data:
                    cluster_model = model_data['final_model']
                elif 'model' in model_data:
                    cluster_model = model_data['model']
                else:
                    logging.error(f"No valid model found in {gender} model data")
                    return
                
                # Extract features for ISOMAP fitting
                features = None
                if 'best_features' in model_data:
                    features = model_data['best_features']
                elif 'feature_info' in model_data and 'original_face_encodings' in model_data['feature_info']:
                    features = model_data['feature_info']['original_face_encodings']
                
                # Set up ISOMAP reducer
                if features is not None:
                    isomap_reducer = Isomap(n_components=50, n_neighbors=min(10, len(features)-1))
                    try:
                        isomap_reducer.fit(features)
                        if gender == 'male':
                            self.male_isomap_reducer = isomap_reducer
                            self.male_reference_embeddings = features
                        else:
                            self.female_isomap_reducer = isomap_reducer
                            self.female_reference_embeddings = features
                        logging.info(f"ISOMAP fitted for {gender} with {len(features)} samples")
                    except Exception as e:
                        logging.warning(f"Could not fit ISOMAP for {gender}: {e}")
                
                # Store the clustering model
                if gender == 'male':
                    self.male_cluster_model = cluster_model
                else:
                    self.female_cluster_model = cluster_model
                    
                logging.info(f"Successfully loaded {gender} clustering model")
                
            else:
                # Handle case where model_data is directly the model
                if gender == 'male':
                    self.male_cluster_model = model_data
                else:
                    self.female_cluster_model = model_data
                logging.info(f"Loaded {gender} model (direct format)")
                
        except Exception as e:
            logging.error(f"Error processing {gender} model data: {e}")
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int] = (512, 512)) -> Optional[np.ndarray]:
        """
        Preprocess image for face recognition
        
        Args:
            image_path: Path to the image file
            target_size: Target size for the image
            
        Returns:
            Preprocessed image as numpy array or None if failed
        """
        try:
            # Load and preprocess image (same as your preprocessing pipeline)
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                width, height = img.size
                
                # Handle small images by upscaling
                quality_threshold = 50
                if width < quality_threshold or height < quality_threshold:
                    scale_factor = max(quality_threshold / width, quality_threshold / height)
                    new_width = int(width * scale_factor * 1.1)
                    new_height = int(height * scale_factor * 1.1)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Enhance image quality
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.1)
                
                # Resize while maintaining aspect ratio
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Center on white background
                processed_img = Image.new('RGB', target_size, (255, 255, 255))
                x = (target_size[0] - img.width) // 2
                y = (target_size[1] - img.height) // 2
                processed_img.paste(img, (x, y))
                
                # Convert to numpy array for OpenCV/insightface
                img_array = np.array(processed_img)
                return img_array
                
        except Exception as e:
            logging.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def extract_face_embedding(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding using ArcFace
        
        Args:
            image_array: Preprocessed image as numpy array
            
        Returns:
            Face embedding vector or None if no face detected
        """
        try:
            # Detect faces and extract embeddings
            faces = self.arcface_model.get(image_array)
            
            if len(faces) == 0:
                logging.warning("No face detected in image")
                return None
            
            # Use the first face (largest face if multiple detected)
            face = faces[0]
            embedding = face.embedding
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logging.error(f"Error extracting face embedding: {e}")
            return None
    
    def reduce_dimensionality(self, embedding: np.ndarray, gender: str) -> Optional[np.ndarray]:
        """
        Reduce dimensionality using ISOMAP
        
        Args:
            embedding: Face embedding vector
            gender: User gender ('male' or 'female')
            
        Returns:
            Reduced dimensionality embedding or None if failed
        """
        try:
            # Get the appropriate ISOMAP reducer
            isomap_reducer = None
            reference_embeddings = None
            
            if gender.lower() == 'male':
                isomap_reducer = self.male_isomap_reducer
                reference_embeddings = self.male_reference_embeddings
            elif gender.lower() == 'female':
                isomap_reducer = self.female_isomap_reducer
                reference_embeddings = self.female_reference_embeddings
            
            if isomap_reducer is None:
                logging.warning(f"ISOMAP reducer not available for {gender}, returning original embedding")
                return embedding
            
            # For new data point, we need to use a different approach
            # Since ISOMAP doesn't have a direct transform method for new points,
            # we'll use the fitted embedding space and find nearest neighbors
            if hasattr(isomap_reducer, 'embedding_') and reference_embeddings is not None:
                # Find k nearest neighbors in the original space
                from sklearn.metrics.pairwise import cosine_similarity
                
                similarities = cosine_similarity(embedding.reshape(1, -1), reference_embeddings)[0]
                k_neighbors = min(10, len(similarities))
                nearest_indices = np.argsort(similarities)[-k_neighbors:]
                
                # Get corresponding points in the reduced space
                reduced_neighbors = isomap_reducer.embedding_[nearest_indices]
                weights = similarities[nearest_indices]
                weights = weights / np.sum(weights)  # Normalize weights
                
                # Weighted average of reduced embeddings
                reduced_embedding = np.average(reduced_neighbors, axis=0, weights=weights)
                
                return reduced_embedding
            else:
                logging.warning(f"ISOMAP not properly fitted for {gender}, returning original embedding")
                return embedding
                
        except Exception as e:
            logging.error(f"Error reducing dimensionality: {e}")
            return embedding  # Return original if reduction fails
    
    def predict_cluster(self, image_path: str, gender: str) -> Optional[int]:
        """
        Complete pipeline: predict cluster ID for a user image
        
        Args:
            image_path: Path to user's profile image
            gender: User gender ('male' or 'female')
            
        Returns:
            Predicted cluster ID or None if failed
        """
        try:
            # Step 1: Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                logging.error("Failed to preprocess image")
                return None
            
            # Step 2: Extract face embedding
            embedding = self.extract_face_embedding(processed_image)
            if embedding is None:
                logging.error("Failed to extract face embedding")
                return None
            
            # Step 3: Reduce dimensionality
            reduced_embedding = self.reduce_dimensionality(embedding, gender)
            if reduced_embedding is None:
                logging.error("Failed to reduce dimensionality")
                return None
            
            # Step 4: Predict cluster
            gender_key = gender.strip().lower()
            
            if gender_key == 'male':
                cluster_model = self.male_cluster_model
            elif gender_key == 'female':
                cluster_model = self.female_cluster_model
            else:
                logging.error(f"Invalid gender: {gender}")
                return None
            
            if cluster_model is None:
                logging.error(f"Cluster model is None for gender '{gender_key}' — model file might be corrupted or loading failed.")
                return None
            
            # Predict cluster
            cluster_id = cluster_model.predict(reduced_embedding.reshape(1, -1))[0]
            logging.info(f"Successfully predicted cluster {cluster_id} for gender {gender}")
            
            return int(cluster_id)
            
        except Exception as e:
            logging.error(f"Error predicting cluster: {e}")
            return None
        
    def get_cluster_assignment_and_distance(self, image_path: str, gender: str) -> Optional[Tuple[int, float]]:
        """
        Predict the cluster assignment and compute the distance to the assigned cluster centroid.
        
        Args:
            image_path: Path to user's profile image
            gender: User gender ('male' or 'female')
        
        Returns:
            Tuple of (cluster_id, distance_to_centroid), or (None, None) if failed
        """
        try:
            # Step 1: Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                logging.error("Failed to preprocess image")
                return None, None

            # Step 2: Extract face embedding
            embedding = self.extract_face_embedding(processed_image)
            if embedding is None:
                logging.error("Failed to extract face embedding")
                return None, None

            # Step 3: Reduce dimensionality
            reduced_embedding = self.reduce_dimensionality(embedding, gender)
            if reduced_embedding is None:
                logging.error("Failed to reduce dimensionality")
                return None, None

            # Step 4: Select appropriate cluster model
            gender_key = gender.strip().lower()
            if gender_key == 'male':
                cluster_model = self.male_cluster_model
            elif gender_key == 'female':
                cluster_model = self.female_cluster_model
            else:
                logging.error(f"Invalid gender: {gender}")
                return None, None

            if cluster_model is None:
                logging.error(f"Cluster model is None for gender '{gender_key}'")
                return None, None

            # Step 5: Predict cluster and compute distance
            cluster_id = cluster_model.predict(reduced_embedding.reshape(1, -1))[0]
            centroid = cluster_model.cluster_centers_[cluster_id]
            distance = float(np.linalg.norm(reduced_embedding - centroid))

            return int(cluster_id), distance

        except Exception as e:
            logging.error(f"Error in get_cluster_assignment_and_distance: {e}")
            return None, None

    
    def get_cluster_probabilities(self, image_path: str, gender: str) -> Optional[Dict[str, Any]]:
        """
        Get cluster prediction probabilities (if model supports it)
        
        Args:
            image_path: Path to user's profile image
            gender: User gender ('male' or 'female')
            
        Returns:
            Dictionary with probabilities and confidence info
        """
        try:
            # Follow same pipeline as predict_cluster
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return None
            
            embedding = self.extract_face_embedding(processed_image)
            if embedding is None:
                return None
            
            reduced_embedding = self.reduce_dimensionality(embedding, gender)
            if reduced_embedding is None:
                return None
            
            gender_key = gender.strip().lower()
            
            if gender_key == 'male':
                cluster_model = self.male_cluster_model
            elif gender_key == 'female':
                cluster_model = self.female_cluster_model
            else:
                return None
            
            if cluster_model is None:
                return None
            
            # Get probabilities if model supports it
            if hasattr(cluster_model, 'predict_proba'):
                probabilities = cluster_model.predict_proba(reduced_embedding.reshape(1, -1))[0]
                predicted_cluster = np.argmax(probabilities)
                confidence = probabilities[predicted_cluster]
                
                return {
                    'predicted_cluster': int(predicted_cluster),
                    'confidence': float(confidence),
                    'probabilities': probabilities.tolist()
                }
            else:
                # If model doesn't support probabilities, just return prediction
                predicted_cluster = cluster_model.predict(reduced_embedding.reshape(1, -1))[0]
                return {
                    'predicted_cluster': int(predicted_cluster),
                    'confidence': 1.0,  # No probability info available
                    'probabilities': None
                }
                
        except Exception as e:
            logging.error(f"Error getting cluster probabilities: {e}")
            return None
    
    def batch_predict_clusters(self, image_paths: list, genders: list) -> list:
        """
        Predict clusters for multiple images
        
        Args:
            image_paths: List of image paths
            genders: List of corresponding genders
            
        Returns:
            List of predicted cluster IDs
        """
        results = []
        for image_path, gender in zip(image_paths, genders):
            cluster_id = self.predict_cluster(image_path, gender)
            results.append(cluster_id)
        return results

# Global instance
model_service = None

def initialize_model_service(model_dir='models'):
    """Initialize the global model service instance"""
    global model_service
    try:
        model_service = MLModelService(model_dir)
        logging.info("ML Model Service initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize ML Model Service: {e}")
        return False

def get_model_service():
    """Get the global model service instance"""
    global model_service
    if model_service is None:
        initialize_model_service()
    return model_service

# Convenience functions for Flask app
def predict_user_cluster(image_path: str, gender: str) -> Optional[int]:
    """Convenience function for predicting user cluster"""
    service = get_model_service()
    if service:
        return service.predict_cluster(image_path, gender)
    return None

def get_user_cluster_probabilities(image_path: str, gender: str) -> Optional[Dict[str, Any]]:
    """Convenience function for getting cluster probabilities"""
    service = get_model_service()
    if service:
        return service.get_cluster_probabilities(image_path, gender)
    return None

def get_user_cluster_and_distance(image_path: str, gender: str) -> Optional[Tuple[int, float]]:
    """Convenience function for getting cluster and distance"""
    service = get_model_service()
    if service:
        return service.get_cluster_assignment_and_distance(image_path, gender)
    return None, None