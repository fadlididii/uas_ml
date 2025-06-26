import os
import shutil
import logging
from ml_service import initialize_model_service

def setup_model_directory():
    """
    Set up the model directory structure
    """
    model_dir = 'models'
    os.makedirs(model_dir, exist_ok=True)
    
    # Create subdirectories
    os.makedirs(os.path.join(model_dir, 'arcface'), exist_ok=True)
    os.makedirs(os.path.join(model_dir, 'clusters'), exist_ok=True)
    
    print(f"Model directory structure created at: {model_dir}")
    print("Expected model files:")
    print("- models/male_cluster_model.pkl")
    print("- models/female_cluster_model.pkl")
    print("- ArcFace models will be downloaded automatically by insightface")
    
    return model_dir

def validate_model_files(model_dir='models'):
    """
    Validate that required model files exist
    """
    required_files = [
        'male_cluster_model.pkl',
        'female_cluster_model.pkl'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing model files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease place your .pkl model files in the models directory")
        return False
    
    print("All required model files found!")
    return True

def test_ml_pipeline():
    """
    Test the ML pipeline with a sample image
    """
    try:
        # Initialize the service
        if not initialize_model_service():
            print("Failed to initialize ML service")
            return False
        
        print("ML service initialized successfully!")
        
        # You can add a test image here
        # test_image_path = 'path/to/test/image.jpg'
        # result = predict_user_cluster(test_image_path, 'male')
        # print(f"Test prediction result: {result}")
        
        return True
        
    except Exception as e:
        print(f"Error testing ML pipeline: {e}")
        return False

def main():
    """
    Main setup function
    """
    print("Setting up ML models for dating app...")
    
    # Step 1: Create directory structure
    model_dir = setup_model_directory()
    
    # Step 2: Validate model files
    if not validate_model_files(model_dir):
        print("\nSetup incomplete. Please add missing model files.")
        return
    
    # Step 3: Test the pipeline
    print("\nTesting ML pipeline...")
    if test_ml_pipeline():
        print("Setup completed successfully!")
    else:
        print("Setup completed with warnings. Check the logs.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()