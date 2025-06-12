import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import db, User, UserProfile, UserPreferences, UserTextTest
from app import app
import os

def generate_users(count=100):
    """Generate specified number of users with varied data"""
    
    with app.app_context():
        users_created = 0
        
        # Lists for varied data
        genders = ['male', 'female']
        educations = ['high_school', 'bachelor', 'master', 'phd', 'other']
        religions = ['christian', 'muslim', 'hindu', 'buddhist', 'jewish', 'other', 'none']
        locations = [
            'Jakarta, Indonesia', 'Surabaya, Indonesia', 'Bandung, Indonesia',
            'Medan, Indonesia', 'Semarang, Indonesia', 'Makassar, Indonesia',
            'Palembang, Indonesia', 'Tangerang, Indonesia', 'Depok, Indonesia',
            'Bekasi, Indonesia', 'Yogyakarta, Indonesia', 'Malang, Indonesia'
        ]
        
        # Sample names
        male_names = ['Ahmad', 'Budi', 'Candra', 'Dedi', 'Eko', 'Fajar', 'Gilang', 'Hadi', 'Indra', 'Joko',
                     'Kevin', 'Lukman', 'Mario', 'Nanda', 'Oscar', 'Putra', 'Qori', 'Rizki', 'Sandi', 'Toni',
                     'Umar', 'Vino', 'Wahyu', 'Xavier', 'Yoga', 'Zaki', 'Andi', 'Bayu', 'Cahyo', 'Dimas']
        
        female_names = ['Ayu', 'Bella', 'Citra', 'Dewi', 'Eka', 'Fitri', 'Gita', 'Hana', 'Indah', 'Jihan',
                       'Kirana', 'Lina', 'Maya', 'Nisa', 'Olivia', 'Putri', 'Qonita', 'Rina', 'Sari', 'Tika',
                       'Ulfa', 'Vera', 'Wulan', 'Xenia', 'Yuni', 'Zahra', 'Anisa', 'Bunga', 'Cinta', 'Diana']
        
        last_names = ['Pratama', 'Sari', 'Wijaya', 'Kusuma', 'Santoso', 'Permata', 'Utama', 'Cahaya',
                     'Indah', 'Mulia', 'Jaya', 'Lestari', 'Maharani', 'Putra', 'Dewi', 'Anggraini',
                     'Wibowo', 'Handoko', 'Setiawan', 'Rahayu', 'Susanto', 'Kurniawan', 'Safitri',
                     'Nugroho', 'Purnama', 'Sartika', 'Hakim', 'Wardani', 'Saputra', 'Melati']
        
        # Sample bio templates
        bio_templates = [
             "Suka traveling dan fotografi. Mencari seseorang yang bisa diajak jalan-jalan.",
             "Pekerja keras yang suka olahraga. Hobi main musik di waktu senggang.",
             "Foodie sejati yang suka mencoba kuliner baru. Mari jelajahi rasa bersama!",
             "Pecinta buku dan film. Senang diskusi hal-hal menarik.",
             "Suka hiking dan aktivitas outdoor. Cari partner petualangan!",
             "Designer grafis yang kreatif. Suka seni dan hal-hal aesthetic.",
             "Programmer yang geek tapi fun. Hobi gaming dan teknologi.",
             "Guru yang sabar dan penyayang. Suka anak-anak dan pendidikan.",
             "Dokter muda yang peduli kesehatan. Work hard, play hard!",
             "Entrepreneur yang ambisius. Suka tantangan dan inovasi.",
             "Chef yang passionate dengan masakan. Mari masak bersama!",
             "Atlet yang disiplin. Hidup sehat adalah prioritas utama.",
             "Seniman yang ekspresif. Suka melukis dan berkarya.",
             "Traveler yang sudah keliling dunia. Banyak cerita menarik!",
             "Mahasiswa yang aktif organisasi. Suka kegiatan sosial."
         ]
         
         # Text test question templates
        text_test_templates = {
             'q1': [
                 "Saya adalah orang yang sangat menghargai kejujuran dan keterbukaan dalam hubungan.",
                 "Saya lebih suka menghabiskan waktu di rumah daripada pergi ke tempat ramai.",
                 "Saya sangat menyukai petualangan dan selalu mencari pengalaman baru.",
                 "Saya adalah tipe orang yang sangat terorganisir dan suka merencanakan segala sesuatu.",
                 "Saya lebih suka spontanitas dan tidak suka terikat dengan rencana yang kaku."
             ],
             'q2': [
                 "Dalam hubungan, komunikasi yang baik adalah hal yang paling penting bagi saya.",
                 "Saya mencari pasangan yang memiliki tujuan hidup yang sama dengan saya.",
                 "Kesetiaan dan komitmen adalah fondasi utama dalam hubungan yang sehat.",
                 "Saya ingin pasangan yang bisa menjadi sahabat terbaik sekaligus kekasih.",
                 "Kepercayaan dan saling menghormati adalah kunci hubungan yang langgeng."
             ],
             'q3': [
                 "Saya sangat menyukai aktivitas outdoor seperti hiking, camping, dan olahraga.",
                 "Saya lebih suka aktivitas indoor seperti membaca, menonton film, atau memasak.",
                 "Saya gemar bersosialisasi dan bertemu dengan orang-orang baru.",
                 "Saya menikmati waktu sendiri untuk refleksi dan pengembangan diri.",
                 "Saya suka mencoba hal-hal baru dan keluar dari zona nyaman."
             ],
             'q4': [
                 "Keluarga adalah prioritas utama dalam hidup saya.",
                 "Karir dan pencapaian profesional sangat penting bagi saya.",
                 "Keseimbangan antara kehidupan pribadi dan pekerjaan adalah kunci kebahagiaan.",
                 "Saya ingin membangun keluarga yang harmonis dan bahagia di masa depan.",
                 "Kebebasan dan independensi adalah hal yang sangat saya hargai."
             ],
             'q5': [
                 "Saya percaya bahwa cinta sejati akan datang pada waktu yang tepat.",
                 "Saya lebih suka hubungan yang berkembang secara alami dari pertemanan.",
                 "Saya mencari hubungan yang serius dan berkomitmen jangka panjang.",
                 "Saya ingin pasangan yang bisa mendukung impian dan aspirasi saya.",
                 "Saya percaya bahwa hubungan yang baik membutuhkan usaha dari kedua belah pihak."
             ]
         }
        
        for i in range(count):
            try:
                # Generate basic user data
                gender = random.choice(genders)
                if gender == 'male':
                    first_name = random.choice(male_names)
                else:
                    first_name = random.choice(female_names)
                
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i+1}@example.com"
                
                # Check if email already exists
                if User.query.filter_by(email=email).first():
                    continue
                
                # Create user
                user = User(
                    email=email,
                    password_hash=generate_password_hash('password123')  # Default password
                )
                db.session.add(user)
                db.session.flush()  # Get user ID
                
                # Generate profile data
                # Generate random birth date (18-65 years old)
                current_year = datetime.now().year
                birth_year = random.randint(current_year - 65, current_year - 18)
                birth_month = random.randint(1, 12)
                birth_day = random.randint(1, 28)  # Safe day range
                birth_date = datetime(birth_year, birth_month, birth_day).date()
                
                profile = UserProfile(
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birth_date,
                    gender=gender,
                    bio=random.choice(bio_templates),
                    weight=random.randint(45, 120),
                    height=random.randint(150, 200),
                    education=random.choice(educations),
                    location=random.choice(locations),
                    religion=random.choice(religions),
                    social_care=random.randint(1, 10),
                    smoking=random.choice([True, False]),
                    drinking=random.choice([True, False, None]),
                    have_pets=random.choice([True, False]),
                    cluster_id=random.randint(0, 10)  # Random cluster assignment
                )
                db.session.add(profile)
                
                # Create user preferences
                preferences = UserPreferences(
                    user_id=user.id,
                    age_min=random.randint(21, 25),
                    age_max=random.randint(26, 40),
                    partner_education=random.choice([None, 'SMA', 'D3', 'S1', 'S2', 'S3']),
                    same_religion=random.choice([True, False]),
                    same_location=random.choice([True, False]),
                    relationship_goal=random.choice(['casual', 'serious']),
                    is_smoking=random.choice([None, True, False]),
                    is_drinking=random.choice([None, True, False]),
                    comfortable_pets=random.choice([None, True, False]),
                    partner_social_care=random.choice([None] + list(range(1, 11)))
                )
                db.session.add(preferences)
                
                # Create text test
                text_test = UserTextTest(
                    user_id=user.id,
                    q1=random.choice(text_test_templates['q1']),
                    q2=random.choice(text_test_templates['q2']),
                    q3=random.choice(text_test_templates['q3']),
                    q4=random.choice(text_test_templates['q4']),
                    q5=random.choice(text_test_templates['q5'])
                )
                db.session.add(text_test)
                
                users_created += 1
                
                if users_created % 10 == 0:
                    print(f"Created {users_created} users...")
                    
            except Exception as e:
                print(f"Error creating user {i+1}: {str(e)}")
                db.session.rollback()
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\nSuccessfully created {users_created} users with profiles and preferences!")
            
            # Print summary
            total_users = User.query.count()
            total_profiles = UserProfile.query.count()
            total_preferences = UserPreferences.query.count()
            
            print(f"\nDatabase Summary:")
            print(f"Total Users: {total_users}")
            print(f"Total Profiles: {total_profiles}")
            print(f"Total Preferences: {total_preferences}")
            
        except Exception as e:
            print(f"Error committing to database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("Starting user generation...")
    generate_users(100)
    print("User generation completed!")