from app import app  # pastikan ini mengimpor Flask app kamu
from models import db, User, UserProfile, UserPreferencesSubset, UserPreferencesSimilarity, UserImageTest
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import uuid
import random
import json

def create_dummy_users(n=10):
    with app.app_context():
        for i in range(n):
            user_id = str(uuid.uuid4())
            email = f'testuser{i+1}@example.com'
            password = generate_password_hash('password123')

            # 1. User
            user = User(id=user_id, email=email, password_hash=password)
            db.session.add(user)

            # 2. UserProfile
            gender = random.choice(['male', 'female'])
            dob = date(2000 - i, 6, 15)
            profile = UserProfile(
                user_id=user_id,
                first_name=f'User{i+1}',
                last_name='Tester',
                gender=gender,
                date_of_birth=dob,
                bio='Just a test user',
                location=random.choice(['Jakarta', 'Bandung', 'Surabaya']),
                height_cm=160 + i,
                weight_kg=50 + i,
                religion='islam',
                education='Bachelor',
                hobbies='Running, Reading',
                language_used='Indonesian, English',
                smoking=False,
                alcohol=False,
                relationship_goal='serious',
                cluster_id=random.randint(0, 6),
            )
            db.session.add(profile)

            # 3. UserPreferencesSubset
            prefs_subset = UserPreferencesSubset(
                user_id=user_id,
                preferred_age_min=20,
                preferred_age_max=50,
                same_location_only=False,
                serious_only=True,
                allow_smoking=False,
                allow_alcohol=False,
                prefer_same_religion=True,
                education_min='Bachelor'
            )
            db.session.add(prefs_subset)

            # 4. UserPreferencesSimilarity
            prefs_similarity = UserPreferencesSimilarity(
                user_id=user_id,
                sports_frequency=random.randint(1, 5),
                care_social_issues=random.randint(1, 5),
                message_length=random.randint(1, 5),
                emoji_frequency=random.randint(1, 5),
                joke_frequency=random.randint(1, 5),
                communication_type=random.randint(1, 3),
                message_style=random.randint(1, 3),
                allow_informal=random.choice([True, False]),
                abbreviation_frequency=random.randint(1, 5),
                punctuation_frequency=random.randint(1, 5),
                capitalization_sensitive=random.choice([True, False]),
                has_pets=random.choice([True, False]),
                outdoor_activity=random.randint(1, 5),
                active_time=json.dumps(random.sample([1, 2, 3, 4], k=random.randint(1, 4)))
            )
            db.session.add(prefs_similarity)

            # 5. UserImageTest
            image_test = UserImageTest(
                user_id=user_id,
                preferred_cluster_ids=json.dumps(random.sample(range(0, 7), k=3))
            )
            db.session.add(image_test)

        db.session.commit()
        print(f'{n} dummy users created successfully.')

if __name__ == '__main__':
    create_dummy_users(100)
