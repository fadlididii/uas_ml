from app import app
from models import db, User, UserProfile, UserPreferences
from app import find_comprehensive_matches
from datetime import date

def debug_matching():
    with app.app_context():
        print("=== DEBUG MATCHING SYSTEM ===")
        
        # Check total users
        total_users = User.query.count()
        total_profiles = UserProfile.query.count()
        total_preferences = UserPreferences.query.count()
        
        print(f"\nDatabase Stats:")
        print(f"Total Users: {total_users}")
        print(f"Total Profiles: {total_profiles}")
        print(f"Total Preferences: {total_preferences}")
        
        if total_users == 0:
            print("\n❌ No users found! Please run generate_users.py first.")
            return
        
        # Get first user for testing
        first_user = User.query.filter_by(email="sandi.hakim577@example.com").first()
        print(f"\nTesting with user: {first_user.email}")
        
        # Check user's preferences
        user_prefs = UserPreferences.query.filter_by(user_id=first_user.id).first()
        if not user_prefs:
            print("❌ No preferences found for user!")
            return
        
        print(f"\nUser Preferences:")
        print(f"Age range: {user_prefs.age_min} - {user_prefs.age_max}")
        print(f"Same location: {user_prefs.same_location}")
        print(f"Same religion: {user_prefs.same_religion}")
        print(f"Partner education: {user_prefs.partner_education}")
        print(f"Smoking preference: {user_prefs.is_smoking}")
        print(f"Drinking preference: {user_prefs.is_drinking}")
        print(f"Pets preference: {user_prefs.comfortable_pets}")
        print(f"Social care preference: {user_prefs.partner_social_care}")
        print(f"Relationship goal: {user_prefs.relationship_goal}")
        
        # Check user's profile
        user_profile = UserProfile.query.filter_by(user_id=first_user.id).first()
        if not user_profile:
            print("❌ No profile found for user!")
            return
        
        print(f"\nUser Profile:")
        print(f"Location: {user_profile.location}")
        print(f"Religion: {user_profile.religion}")
        print(f"Education: {user_profile.education}")
        print(f"Age: {calculate_age(user_profile.date_of_birth)}")
        print(f"Smoking: {user_profile.smoking}")
        print(f"Drinking: {user_profile.drinking}")
        print(f"Pets: {user_profile.have_pets}")
        print(f"Social care: {user_profile.social_care}")
        
        # Test filtering step by step
        print(f"\n=== STEP BY STEP FILTERING ===")
        
        # Start with all other users
        all_other_profiles = UserProfile.query.filter(UserProfile.user_id != first_user.id).all()
        print(f"1. All other users: {len(all_other_profiles)}")
        
        if len(all_other_profiles) == 0:
            print("❌ No other users to match with!")
            return
        
        # Age filtering
        age_filtered = []
        today = date.today()
        for profile in all_other_profiles:
            if profile.date_of_birth:
                age = calculate_age(profile.date_of_birth)
                if (user_prefs.age_min is None or age >= user_prefs.age_min) and \
                   (user_prefs.age_max is None or age <= user_prefs.age_max):
                    age_filtered.append(profile)
        print(f"2. After age filter ({user_prefs.age_min}-{user_prefs.age_max}): {len(age_filtered)}")
        
        # Location filtering
        location_filtered = age_filtered
        if user_prefs.same_location and user_profile.location:
            location_filtered = [p for p in age_filtered if p.location == user_profile.location]
        print(f"3. After location filter (same_location={user_prefs.same_location}): {len(location_filtered)}")
        
        # Religion filtering
        religion_filtered = location_filtered
        if user_prefs.same_religion and user_profile.religion:
            religion_filtered = [p for p in location_filtered if p.religion == user_profile.religion]
        print(f"4. After religion filter (same_religion={user_prefs.same_religion}): {len(religion_filtered)}")
        
        # Education filtering
        education_filtered = religion_filtered
        if user_prefs.partner_education:
            education_filtered = [p for p in religion_filtered if p.education == user_prefs.partner_education]
        print(f"5. After education filter ({user_prefs.partner_education}): {len(education_filtered)}")
        
        # Smoking filtering
        smoking_filtered = education_filtered
        if user_prefs.is_smoking is not None:
            smoking_filtered = [p for p in education_filtered if p.smoking == user_prefs.is_smoking]
        print(f"6. After smoking filter ({user_prefs.is_smoking}): {len(smoking_filtered)}")
        
        # Drinking filtering
        drinking_filtered = smoking_filtered
        if user_prefs.is_drinking is not None:
            drinking_filtered = [p for p in smoking_filtered if p.drinking == user_prefs.is_drinking]
        print(f"7. After drinking filter ({user_prefs.is_drinking}): {len(drinking_filtered)}")
        
        # Pets filtering
        pets_filtered = drinking_filtered
        if user_prefs.comfortable_pets is not None:
            pets_filtered = [p for p in drinking_filtered if p.have_pets == user_prefs.comfortable_pets]
        print(f"8. After pets filter ({user_prefs.comfortable_pets}): {len(pets_filtered)}")
        
        # Social care filtering
        social_care_filtered = pets_filtered
        if user_prefs.partner_social_care is not None:
            social_care_filtered = [p for p in pets_filtered if p.social_care == user_prefs.partner_social_care]
        print(f"9. After social care filter ({user_prefs.partner_social_care}): {len(social_care_filtered)}")
        
        print(f"\n=== FINAL RESULT ===")
        print(f"Matches found: {len(social_care_filtered)}")
        
        # Test with actual function
        actual_matches = find_comprehensive_matches(first_user.id, top_n=10)        
        print(f"Actual function result: {len(actual_matches)} matches")
        
        if len(social_care_filtered) == 0:
            print("\n❌ NO MATCHES FOUND!")
            print("\n💡 RECOMMENDATIONS:")
            print("1. Make preferences less restrictive (set some to None/False)")
            print("2. Generate more diverse user data")
            print("3. Check if all users have similar characteristics")
            
            # Show sample of other users
            print("\n📊 Sample of other users:")
            for i, profile in enumerate(all_other_profiles[:5]):
                age = calculate_age(profile.date_of_birth) if profile.date_of_birth else 'N/A'
                print(f"  User {i+1}: Age {age}, Location: {profile.location}, Religion: {profile.religion}, Education: {profile.education}")
        else:
            print(f"\n✅ Found {len(social_care_filtered)} potential matches!")

def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

if __name__ == '__main__':
    debug_matching()