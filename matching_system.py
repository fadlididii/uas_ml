from models import UserProfile, UserPreferences, UserTextTest, UserImageTest
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def filter_by_preferences_stage1(user_id):
    """
    Stage 1: Hard filter based on user preferences
    Returns list of user IDs that match the basic preferences
    """
    try:
        # Get user preferences
        user_prefs = UserPreferences.query.filter_by(user_id=user_id).first()
        if not user_prefs:
            return []
        
        # Get all other users
        all_users = UserProfile.query.filter(UserProfile.user_id != user_id).all()
        
        filtered_users = []
        
        for user in all_users:
            # Age filter
            if user.age < user_prefs.min_age or user.age > user_prefs.max_age:
                continue
            
            # Location filter (if specified)
            if user_prefs.location and user.location != user_prefs.location:
                continue
            
            # Smoking preference
            if user_prefs.smoking_preference == 'no' and user.smoking == 'yes':
                continue
            elif user_prefs.smoking_preference == 'yes' and user.smoking == 'no':
                continue
            
            # Drinking preference
            if user_prefs.drinking_preference == 'no' and user.drinking == 'yes':
                continue
            elif user_prefs.drinking_preference == 'yes' and user.drinking == 'no':
                continue
            
            # Pet preference
            if user_prefs.pet_preference == 'no' and user.pets == 'yes':
                continue
            elif user_prefs.pet_preference == 'yes' and user.pets == 'no':
                continue
            
            # Education filter - works as minimum requirement
            education_hierarchy = {
                'SMA': 1, 'high_school': 1,
                'D3': 2,
                'S1': 3, 'bachelor': 3,
                'S2': 4, 'master': 4,
                'S3': 5, 'phd': 5,
                'other': 0
            }
            
            user_education_level = education_hierarchy.get(user.education, 0)
            preferred_education_level = education_hierarchy.get(user_prefs.education, 0)
            
            # Only include users with same or higher education level
            if user_education_level < preferred_education_level:
                continue
            
            filtered_users.append(user.user_id)
        
        return filtered_users
        
    except Exception as e:
        print(f"Error in filter_by_preferences_stage1: {e}")
        return []


def get_text_similar_users(user_id, candidate_ids, threshold=0.5):
    """
    Stage 2: Filter candidates based on text similarity using cosine similarity
    Returns list of user IDs with similarity > threshold
    """
    try:
        # Get current user's most recent text test
        current_user_test = UserTextTest.query.filter_by(user_id=user_id).order_by(UserTextTest.created_at.desc()).first()
        if not current_user_test or not current_user_test.embedding:
            print(f"No text test embedding found for user {user_id}")
            return []
        
        current_embedding = np.array(current_user_test.embedding).reshape(1, -1)
        similar_users = []
        
        for candidate_id in candidate_ids:
            # Get candidate's most recent text test
            candidate_test = UserTextTest.query.filter_by(user_id=candidate_id).order_by(UserTextTest.created_at.desc()).first()
            
            if candidate_test and candidate_test.embedding:
                candidate_embedding = np.array(candidate_test.embedding).reshape(1, -1)
                similarity = cosine_similarity(current_embedding, candidate_embedding)[0][0]
                
                if similarity > threshold:
                    similar_users.append(candidate_id)
        
        return similar_users
        
    except Exception as e:
        print(f"Error in get_text_similar_users: {e}")
        return []


def get_text_similar_users_with_scores(user_id, candidate_ids, threshold=0.5):
    """
    Stage 2: Filter candidates based on text test similarity using cosine similarity
    Returns list of dictionaries with user_id and text_similarity score
    """
    try:
        # Get current user's most recent text test
        current_user_test = UserTextTest.query.filter_by(user_id=user_id).order_by(UserTextTest.created_at.desc()).first()
        if not current_user_test or not current_user_test.embedding:
            print(f"No text test found for user {user_id}")
            return []
        
        # Get embeddings for candidate users
        similar_users = []
        current_embedding = np.array(current_user_test.embedding).reshape(1, -1)
        
        for candidate_id in candidate_ids:
            candidate_test = UserTextTest.query.filter_by(user_id=candidate_id).order_by(UserTextTest.created_at.desc()).first()
            
            if candidate_test and candidate_test.embedding:
                candidate_embedding = np.array(candidate_test.embedding).reshape(1, -1)
                similarity = cosine_similarity(current_embedding, candidate_embedding)[0][0]
                
                if similarity > threshold:
                    similar_users.append({
                        'user_id': candidate_id,
                        'text_similarity': similarity
                    })
        
        # Sort by similarity (highest first)
        similar_users.sort(key=lambda x: x['text_similarity'], reverse=True)
        
        return similar_users
        
    except Exception as e:
        print(f"Error in get_text_similar_users_with_scores: {e}")
        return []


def filter_by_visual_preference(user_id, candidate_ids):
    """
    Stage 3: Filter candidates based on visual cluster preferences
    Returns list of user IDs whose cluster_id matches user's preferred clusters
    """
    try:
        # Get current user's image test preferences
        current_user_image_test = UserImageTest.query.filter_by(user_id=user_id).order_by(UserImageTest.created_at.desc()).first()
        
        if not current_user_image_test or not current_user_image_test.preferred_cluster_id:
            print(f"No image test preferences found for user {user_id}")
            return []
        
        # Parse preferred clusters (assuming it's stored as comma-separated string or single value)
        preferred_clusters = []
        if isinstance(current_user_image_test.preferred_cluster_id, str):
            if ',' in current_user_image_test.preferred_cluster_id:
                preferred_clusters = [int(x.strip()) for x in current_user_image_test.preferred_cluster_id.split(',')]
            else:
                preferred_clusters = [int(current_user_image_test.preferred_cluster_id)]
        else:
            preferred_clusters = [current_user_image_test.preferred_cluster_id]
        
        visual_matches = []
        
        for candidate_id in candidate_ids:
            # Get candidate's profile to check cluster_id
            candidate_profile = UserProfile.query.filter_by(user_id=candidate_id).first()
            
            if candidate_profile and candidate_profile.cluster_id in preferred_clusters:
                visual_matches.append(candidate_id)
        
        return visual_matches
        
    except Exception as e:
        print(f"Error in filter_by_visual_preference: {e}")
        return []


def get_final_matches(user_id):
    """
    Stage 4: Final matching function that runs all three stages sequentially
    Returns list of dictionaries with user_id and scores
    """
    try:
        print(f"Starting final matching process for user {user_id}")
        
        # Stage 1: Hard filter by preferences
        stage1_candidates = filter_by_preferences_stage1(user_id)
        print(f"Stage 1 (Preference Filter): {len(stage1_candidates)} candidates")
        
        if not stage1_candidates:
            print("No candidates passed Stage 1 filtering")
            return []
        
        # Stage 2: Text similarity filter with scores
        stage2_results = get_text_similar_users_with_scores(user_id, stage1_candidates, threshold=0.5)
        print(f"Stage 2 (Text Similarity): {len(stage2_results)} candidates")
        
        if not stage2_results:
            print("No candidates passed Stage 2 filtering")
            return []
        
        # Stage 3: Visual cluster preference filter
        final_matches = []
        for result in stage2_results:
            candidate_id = result['user_id']
            if candidate_id in filter_by_visual_preference(user_id, [candidate_id]):
                # Calculate cluster similarity (simplified - can be enhanced)
                cluster_similarity = 1.0  # Perfect match since they passed visual filter
                
                # Calculate total score (weighted average)
                total_score = (result['text_similarity'] * 0.7) + (cluster_similarity * 0.3)
                
                final_matches.append({
                    'user_id': candidate_id,
                    'text_similarity': result['text_similarity'],
                    'cluster_similarity': cluster_similarity,
                    'total_score': total_score
                })
        
        # Sort by total score (highest first)
        final_matches.sort(key=lambda x: x['total_score'], reverse=True)
        
        print(f"Stage 3 (Visual Preference): {len(final_matches)} final matches")
        return final_matches
        
    except Exception as e:
        print(f"Error in get_final_matches: {e}")
        return []