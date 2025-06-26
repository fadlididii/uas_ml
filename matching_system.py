import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import UserProfile, UserPreferencesSubset, UserPreferencesSimilarity, UserImageTest
from sqlalchemy import and_
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Simple cache to store coordinates
coordinates_cache = {}

# Fungsi untuk mendapatkan koordinat dari lokasi
def get_coordinates(location):
    # Check cache first
    if location in coordinates_cache:
        return coordinates_cache[location]
    
    try:
        # Increase timeout to 10 seconds and add a user agent
        geolocator = Nominatim(user_agent="heartlink_app", timeout=10)
        
        # Add a small delay to respect rate limits
        time.sleep(0.5)
        
        location_data = geolocator.geocode(location)
        if location_data:
            # Store in cache
            coordinates = (location_data.latitude, location_data.longitude)
            coordinates_cache[location] = coordinates
            return coordinates
        return None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None

# Fungsi untuk menghitung jarak antara dua lokasi
def calculate_distance(location1, location2):
    try:
        coords1 = get_coordinates(location1)
        coords2 = get_coordinates(location2)
        
        if coords1 and coords2:
            distance = geodesic(coords1, coords2).kilometers
            return distance
        return None
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return None

def get_final_matches(user_id, max_distance=None):
    try:
        user_profile = UserProfile.query.get(user_id)
        user_prefs_subset = UserPreferencesSubset.query.filter_by(user_id=user_id).first()
        user_prefs_similarity = UserPreferencesSimilarity.query.filter_by(user_id=user_id).first()
        user_image_test = UserImageTest.query.filter_by(user_id=user_id).first()

        if not user_profile or not user_prefs_subset or not user_prefs_similarity:
            print(f"[MATCHING] Missing data for user {user_id}")
            return []

        user_gender = user_profile.gender.lower() if user_profile.gender else None
        opposite_gender = 'female' if user_gender == 'male' else 'male' if user_gender == 'female' else None

        candidates_query = UserProfile.query.filter(UserProfile.user_id != user_id)
        if opposite_gender:
            candidates_query = candidates_query.filter(UserProfile.gender.ilike(opposite_gender))

        candidates = []
        for candidate in candidates_query.all():
            reason = None

            # Age filter
            if candidate.date_of_birth:
                age = candidate.age
                if user_prefs_subset.preferred_age_min and age < user_prefs_subset.preferred_age_min:
                    reason = f"Too young: {age}"
                if user_prefs_subset.preferred_age_max and age > user_prefs_subset.preferred_age_max:
                    reason = f"Too old: {age}"
            else:
                continue
                reason = "No birthdate"

            # Location filter
            if not reason and user_prefs_subset.same_location_only and candidate.location != user_profile.location:
                reason = f"Different location: {candidate.location}"

            # Relationship goal
            if not reason and user_prefs_subset.serious_only and candidate.relationship_goal != 'serious':
                reason = f"Relationship goal mismatch: {candidate.relationship_goal}"

            # Religion
            if not reason and user_prefs_subset.prefer_same_religion and candidate.religion != user_profile.religion:
                reason = f"Different religion: {candidate.religion}"

            # Cluster preference filter
            if not reason and user_image_test:
                preferred_clusters = set(map(int, user_image_test.get_preferred_cluster_ids()))
                if candidate.cluster_id is None:
                    reason = "Candidate has no cluster_id"
                elif candidate.cluster_id not in preferred_clusters:
                    reason = f"Cluster {candidate.cluster_id} not in preferred {preferred_clusters}"

            if reason:
                print(f"[SKIP] Candidate {candidate.user_id} - {reason}")
                continue

            if user_image_test and candidate.cluster_id is not None:
                preferred_clusters = user_image_test.get_preferred_cluster_ids()
                if str(candidate.cluster_id) not in preferred_clusters:
                    continue
            elif user_image_test:
                continue

            candidates.append(candidate)

        if not candidates:
            print(f"[MATCHING] No candidates match all filters for user {user_id}")
            return []

        user_vector = np.array(user_prefs_similarity.get_similarity_vector()).reshape(1, -1)
        results = []

        for candidate in candidates:
            candidate_prefs = UserPreferencesSimilarity.query.filter_by(user_id=candidate.user_id).first()
            if not candidate_prefs:
                print(f"[SKIP] Candidate {candidate.user_id} has no preferences similarity vector.")
                continue

            candidate_vector = np.array(candidate_prefs.get_similarity_vector()).reshape(1, -1)
            similarity = float(cosine_similarity(user_vector, candidate_vector)[0][0])
            
            # Hitung jarak jika max_distance ditentukan
            distance = None
            if max_distance is not None and user_profile.location and candidate.location:
                distance = calculate_distance(user_profile.location, candidate.location)
                # Skip kandidat jika jarak melebihi max_distance
                if distance is not None and distance > max_distance:
                    continue

            # Cluster distance score: inverse of distance, higher = better
            raw_distance = candidate.cluster_distance if candidate.cluster_distance is not None else 0
            cluster_distance = 1.0 - min(raw_distance / 10.0, 1.0)  # Normalize distance into similarity-like score (0 to 1)

            final_score = ((similarity * 50) + (cluster_distance * 50))/100

            results.append({
                'user_id': candidate.user_id,
                'total_score': final_score,
                'text_similarity': similarity,
                'cluster_similarity': 1.0,
                'distance': distance  # Tambahkan informasi jarak
                'cluster_distance': cluster_distance
            })

        results.sort(key=lambda x: x['total_score'], reverse=True)
        print(f"[MATCHING] Returning top {len(results)} matches for user {user_id}")
        return results
  

    except Exception as e:
        import traceback
        print(f"[ERROR] Error in get_final_matches: {e}")
        print(traceback.format_exc())
        return []
