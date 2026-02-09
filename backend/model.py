"""
U-Net Model Implementation for Plant Disease Segmentation
This module provides a U-Net implementation for demonstration.
In production, replace with actual trained model weights.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model
import numpy as np


def unet_model(input_size=(256, 256, 3), num_classes=1):
    """
    Build U-Net architecture for image segmentation.
    
    Args:
        input_size: Tuple of (height, width, channels)
        num_classes: Number of output classes (1 for binary segmentation)
    
    Returns:
        Keras Model instance
    """
    inputs = layers.Input(input_size)
    
    # Encoder (Contracting Path)
    # Block 1
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D((2, 2))(c1)
    
    # Block 2
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D((2, 2))(c2)
    
    # Block 3
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D((2, 2))(c3)
    
    # Bottleneck
    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(c4)
    
    # Decoder (Expanding Path)
    # Block 4
    u5 = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(c4)
    u5 = layers.concatenate([u5, c3])
    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(u5)
    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c5)
    
    # Block 5
    u6 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = layers.concatenate([u6, c2])
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c6)
    
    # Block 6
    u7 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = layers.concatenate([u7, c1])
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c7)
    
    # Output layer
    outputs = layers.Conv2D(num_classes, (1, 1), activation='sigmoid')(c7)
    
    model = Model(inputs=[inputs], outputs=[outputs])
    return model


class DiseaseSegmentationModel:
    """
    Wrapper class for disease segmentation using U-Net.
    """
    
    # Disease database with recommendations
    DISEASE_DB = {
        'wheat_brown_rust': {
            'name': 'Wheat Brown Rust',
            'pesticide': 'Propiconazole 25% EC',
            'dosage': '1ml per liter of water',
            'description': 'Fungal disease causing brown pustules on leaves'
        },
        'tomato_early_blight': {
            'name': 'Tomato Early Blight',
            'pesticide': 'Mancozeb 75% WP',
            'dosage': '2g per liter of water',
            'description': 'Alternaria solani causing concentric rings on leaves'
        },
        'rice_blast': {
            'name': 'Rice Blast',
            'pesticide': 'Tricyclazole 75% WP',
            'dosage': '1g per liter of water',
            'description': 'Pyricularia oryzae causing diamond-shaped lesions'
        },
        'potato_late_blight': {
            'name': 'Potato Late Blight',
            'pesticide': 'Metalaxyl 8% + Mancozeb 64% WP',
            'dosage': '2.5g per liter of water',
            'description': 'Phytophthora infestans causing dark lesions'
        },
        'healthy': {
            'name': 'Healthy Plant',
            'pesticide': 'None required',
            'dosage': 'N/A',
            'description': 'No disease detected'
        }
    }
    
    def __init__(self, model_path=None):
        """
        Initialize the segmentation model.
        
        Args:
            model_path: Path to saved model weights (optional)
        """
        self.model = unet_model()
        self.img_size = (256, 256)
        
        if model_path:
            self.model.load_weights(model_path)
        
        print("U-Net Model initialized successfully")
    
    def preprocess_image(self, image):
        """
        Preprocess image for model inference.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Preprocessed numpy array
        """
        from PIL import Image as PILImage
        
        if isinstance(image, PILImage.Image):
            image = np.array(image)
        
        # Resize to model input size
        image = tf.image.resize(image, self.img_size)
        
        # Normalize to [0, 1]
        image = image / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image):
        """
        Run inference on an image.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Tuple of (prediction_mask, disease_type, confidence)
        """
        # Preprocess
        processed = self.preprocess_image(image)
        
        # Run inference (dummy prediction for demo)
        # In production: prediction = self.model.predict(processed)
        
        # Simulate prediction with random mask
        prediction_mask = self._dummy_segmentation(processed[0])
        
        # Classify disease type
        disease_type, confidence = self._classify_disease(prediction_mask)
        
        return prediction_mask, disease_type, confidence
    
    def _dummy_segmentation(self, image):
        """
        Generate dummy segmentation mask for demonstration.
        Replace with actual model prediction in production.
        """
        from scipy import ndimage
        
        # Create a random mask simulating disease regions
        mask = np.random.rand(256, 256) > 0.85
        mask = mask.astype(np.float32)
        
        # Add some structure to make it look realistic
        mask = ndimage.gaussian_filter(mask, sigma=2)
        mask = (mask > 0.3).astype(np.float32)
        
        return mask
    
    def _classify_disease(self, mask):
        """
        Classify disease based on segmentation mask features.
        Dummy implementation - replace with actual classifier.
        """
        import random
        
        # Randomly select a disease for demo
        diseases = list(self.DISEASE_DB.keys())[:-1]  # Exclude 'healthy'
        disease_key = random.choice(diseases)
        confidence = random.uniform(0.75, 0.95)
        
        return disease_key, confidence
    
    def calculate_infection_level(self, mask):
        """
        Calculate infection percentage from segmentation mask.
        
        Args:
            mask: Binary segmentation mask (numpy array)
            
        Returns:
            Infection level as percentage (0-100)
        """
        total_pixels = mask.size
        diseased_pixels = np.sum(mask > 0.5)
        
        infection_level = (diseased_pixels / total_pixels) * 100
        return round(infection_level, 2)
    
    def get_recommendation(self, disease_key, infection_level):
        """
        Get treatment recommendation for detected disease.
        
        Args:
            disease_key: Key from DISEASE_DB
            infection_level: Calculated infection percentage
            
        Returns:
            Dictionary with treatment details
        """
        disease_info = self.DISEASE_DB.get(disease_key, self.DISEASE_DB['healthy'])
        
        recommendation = {
            'disease_name': disease_info['name'],
            'description': disease_info['description'],
            'infection_level': infection_level,
            'severity': self._get_severity(infection_level),
            'pesticide': disease_info['pesticide'],
            'dosage': disease_info['dosage'],
            'spray_recommended': infection_level > 15,
            'spray_duration': self.calculate_spray_duration(infection_level)
        }
        
        return recommendation
    
    def _get_severity(self, infection_level):
        """
        Determine severity level based on infection percentage.
        """
        if infection_level < 10:
            return 'Low'
        elif infection_level < 30:
            return 'Moderate'
        elif infection_level < 50:
            return 'High'
        else:
            return 'Severe'
    
    def calculate_spray_duration(self, infection_level):
        """
        Calculate spray duration based on infection level.
        
        Args:
            infection_level: Calculated infection percentage
            
        Returns:
            Spray duration in seconds
        """
        if infection_level <= 0:
            return 0
        elif infection_level < 25:
            return 3
        elif infection_level < 50:
            return 5
        elif infection_level < 75:
            return 8
        else:
            return 10


# Singleton instance
_segmentation_model = None

def get_model():
    """
    Get or create singleton model instance.
    """
    global _segmentation_model
    if _segmentation_model is None:
        _segmentation_model = DiseaseSegmentationModel()
    return _segmentation_model
