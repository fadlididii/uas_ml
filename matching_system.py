import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import UserProfile, UserPreferencesSubset, UserPreferencesSimilarity, UserImageTest
from sqlalchemy import and_

def get_final_matches(user_id, top_n=20):
    try:
        user_profile = UserProfile.query.get(user_id)
        user_prefs_subset = UserPreferencesSubset.query.filter_by(user_id=user_id).first()
        user_prefs_similarity = UserPreferencesSimilarity.query.filter_by(user_id=user_id).first()
        user_image_test = UserImageTest.query.filter_by(user_id=user_id).first()

        if not user_profile or not user_prefs_subset or not user_prefs_similarity:
            print(f"Missing data for user {user_id}")
            return []

        # Tentukan gender lawan jenis
        user_gender = user_profile.gender.lower() if user_profile.gender else None
        opposite_gender = 'female' if user_gender == 'male' else 'male' if user_gender == 'female' else None

        # Ambil semua kandidat selain diri sendiri
        candidates_query = UserProfile.query.filter(UserProfile.user_id != user_id)

        if opposite_gender:
            candidates_query = candidates_query.filter(UserProfile.gender.ilike(opposite_gender))

        candidates = []
        for candidate in candidates_query.all():
            # Filter usia
            if candidate.date_of_birth:
                age = candidate.age
                if user_prefs_subset.preferred_age_min and age < user_prefs_subset.preferred_age_min:
                    continue
                if user_prefs_subset.preferred_age_max and age > user_prefs_subset.preferred_age_max:
                    continue
            else:
                continue  # skip jika tidak ada data umur

            # Filter lokasi
            if user_prefs_subset.same_location_only and candidate.location != user_profile.location:
                continue

            # Filter relationship goal
            if user_prefs_subset.serious_only and candidate.relationship_goal != 'serious':
                continue

            # Filter agama
            if user_prefs_subset.prefer_same_religion and candidate.religion != user_profile.religion:
                continue

            # Filter berdasarkan visual cluster (irisan)
            if user_image_test and candidate.cluster_id is not None:
                preferred_clusters = user_image_test.get_preferred_cluster_ids()
                if str(candidate.cluster_id) not in preferred_clusters:
                    continue  # skip kalau cluster-nya tidak dipilih user
            elif user_image_test:
                continue  # jika user punya preferensi cluster tapi kandidat tidak punya cluster_id, skip juga

            candidates.append(candidate)

        if not candidates:
            print(f"No candidates match all filters for user {user_id}")
            return []

        # Hitung cosine similarity
        user_vector = np.array(user_prefs_similarity.get_similarity_vector()).reshape(1, -1)

        results = []
        for candidate in candidates:
            candidate_prefs = UserPreferencesSimilarity.query.filter_by(user_id=candidate.user_id).first()
            if not candidate_prefs:
                continue

            candidate_vector = np.array(candidate_prefs.get_similarity_vector()).reshape(1, -1)
            similarity = float(cosine_similarity(user_vector, candidate_vector)[0][0])

            results.append({
                'user_id': candidate.user_id,
                'total_score': similarity,
                'text_similarity': similarity,
                'cluster_similarity': 1.0 
            })

        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results[:top_n]

    except Exception as e:
        import traceback
        print(f"Error in get_final_matches: {e}")
        print(traceback.format_exc())
        return []
