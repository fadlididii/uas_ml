from flask import Flask
from models import db, User, UserProfile, UserPreferencesSubset, UserPreferencesSimilarity
from config import config
import os

def debug_matching():
    app = Flask(__name__)
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    with app.app_context():
        db.init_app(app)
        
        print("=== DEBUGGING MATCHING SYSTEM ===")
        
        total_users = User.query.count()
        total_profiles = UserProfile.query.count()
        total_subset_preferences = UserPreferencesSubset.query.count()
        total_similarity_preferences = UserPreferencesSimilarity.query.count()
        
        print(f"Total users: {total_users}")
        print(f"Total profiles: {total_profiles}")
        print(f"Total subset preferences: {total_subset_preferences}")
        print(f"Total similarity preferences: {total_similarity_preferences}")
        
        # Test dengan user pertama
        first_user = User.query.first()
        if first_user and first_user.profile:
            print(f"\nTesting with user: {first_user.email}")
            print(f"Profile: {first_user.profile.to_dict()}")
            
            # Check preferences
            subset_prefs = first_user.profile.preferences_subset
            similarity_prefs = first_user.profile.preferences_similarity
            
            if subset_prefs:
                print(f"Subset preferences: {subset_prefs.to_dict()}")
            else:
                print("No subset preferences found")
                
            if similarity_prefs:
                print(f"Similarity preferences: {similarity_prefs.to_dict()}")
            else:
                print("No similarity preferences found")

if __name__ == '__main__':
    debug_matching()