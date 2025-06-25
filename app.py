from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from config import config
from models import db, User, UserProfile, UserPreferencesSubset, UserPreferencesSimilarity, UserImageTest
from datetime import datetime, date
from sklearn.metrics.pairwise import cosine_similarity
from api_routes import api
import numpy as np
import os
import uuid
import pickle
import joblib 
from PIL import Image
from functools import wraps
from ml_service import initialize_model_service, get_model_service
import logging
from ml_service import initialize_model_service
initialize_model_service('models')

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])

print("Initializing ML Model Service...")
if not initialize_model_service('models'):  # 'models' is your model directory
    print("Warning: ML Model Service failed to initialize. Clustering features may not work.")
    logging.warning("ML Model Service initialization failed")
else:
    print("ML Model Service initialized successfully!")


# Initialize extensions
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Initialize Flask-Migrate with the Flask app and SQLAlchemy instance
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(api)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email dan password diperlukan', 'error')
            return redirect(url_for('index'))
            
        # Validasi login
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Email atau password tidak valid', 'error')
            return redirect(url_for('index'))
            
        if not user.is_active:
            flash('Akun tidak aktif', 'error')
            return redirect(url_for('index'))
            
        # Login berhasil
        login_user(user)
        # Refresh user object untuk memastikan semua relasi terload dengan benar
        db.session.refresh(user)
        
        # Simpan data user di session
        session['user_id'] = user.id
        session['email'] = user.email
        flash('Login berhasil!', 'success')
        
        # Redirect based on user completion status
        # 1. Check if user has profile
        if not user.profile:
            return redirect(url_for('profile_setup'))
        
        # 2. Check if user has preferences
        elif not user.preferences_subset:
            return redirect(url_for('preferences'))
        
        # 3. Check if user has completed image test
        elif not user.image_tests:
            return redirect(url_for('image_test'))
        
        # 4. If all complete, go to match feed
        else:
            return redirect(url_for('match_feed'))
    
    return render_template('index.html')  # Use index.html as login page

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Ambil data dari form
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validasi form
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Cek apakah email sudah terdaftar
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        try:
            # Buat user baru
            user = User(email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# Helper function untuk cek login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/profile-setup', methods=['GET', 'POST'])
@login_required
def profile_setup():
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            # Ambil data dari form
            data = request.form
            file = request.files.get('profile_photo')  # Updated to match frontend
            
            # Get date of birth from form
            date_of_birth = None
            if data.get('date_of_birth'):
                try:
                    from datetime import datetime as dt
                    date_of_birth = dt.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
                    # Validate minimum age (21 years)
                    today = date.today()
                    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
                    if age < 21:
                        raise ValueError("Minimum age is 21 years")
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Please enter a valid date of birth: {str(e)}")
            # Fallback: Calculate date of birth from age if date_of_birth not provided
            elif data.get('age'):
                try:
                    age_int = int(data.get('age'))
                    if age_int < 21:
                        raise ValueError("Minimum age is 21 years")
                    current_year = datetime.now().year
                    birth_year = current_year - age_int
                    date_of_birth = date(birth_year, 1, 1)  # Default to January 1st
                except (ValueError, TypeError):
                    raise ValueError("Please enter a valid age")
            
            # Simpan file jika ada
            photo_url = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create unique filename to avoid conflicts
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join('static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                photo_path = os.path.join(upload_dir, unique_filename)
                file.save(photo_path)
                photo_url = '/' + photo_path.replace('\\', '/')  # Untuk dipakai di HTML nanti

            # Get or create profile
            profile = user.profile
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
                # Flush to ensure profile is created before creating related objects
                db.session.flush()
            
            # Get or create similarity preferences first
            similarity_prefs = None
            if profile:
                similarity_prefs = profile.preferences_similarity
            if not similarity_prefs:
                similarity_prefs = UserPreferencesSimilarity(user_id=user_id)
                db.session.add(similarity_prefs)
                db.session.flush()
            
            # Update profile fields sesuai field names dari frontend
            profile.first_name = data.get('first_name') 
            profile.last_name = data.get('last_name')
            profile.date_of_birth = date_of_birth
            profile.gender = data.get('gender')
            profile.bio = data.get('bio')
            profile.weight_kg = int(data.get('weight_kg')) if data.get('weight_kg') else None
            profile.height_cm = int(data.get('height_cm')) if data.get('height_cm') else None
            profile.education = data.get('education')
            profile.location = data.get('location')
            profile.religion = data.get('religion')
            profile.hobbies = data.get('hobbies')
            profile.language_used = data.get('language_used')
            profile.whatsapp = data.get('whatsapp')
            profile.instagram = data.get('instagram')
            profile.smoking = data.get('smoking') == 'yes' if data.get('smoking') else None
            profile.alcohol = data.get('alcohol') == 'yes' if data.get('alcohol') else None
            profile.relationship_goal = data.get('relationship_goal')
            
            # Handle active_time (multiple checkboxes) - now similarity_prefs is properly defined
            active_times = request.form.getlist('active_time')
            if active_times and similarity_prefs:
                similarity_prefs.set_active_time_list([int(time) for time in active_times])
            
            # Update similarity preferences
            if data.get('outdoor_activity'):
                similarity_prefs.outdoor_activity = int(data.get('outdoor_activity'))
            if data.get('care_social_issues'):
                similarity_prefs.care_social_issues = int(data.get('care_social_issues'))
            if data.get('sports_frequency'):
                similarity_prefs.sports_frequency = int(data.get('sports_frequency'))
            if data.get('has_pets'):
                similarity_prefs.has_pets = data.get('has_pets') == 'yes'
            
            # Handle photo removal or update
            if data.get('remove_photo') == 'true':
                profile.photo_url = None
            elif photo_url:
                profile.photo_url = photo_url
                
                # Automatic clustering for profile photo
                if profile.gender and file and file.filename:
                    cluster_result = get_model_service().get_cluster_assignment_and_distance(photo_path, profile.gender)
                    if cluster_result:
                        cluster_id, distance = cluster_result
                        profile.cluster_id = cluster_id
                        profile.cluster_distance = distance  # ⬅️ Save it here
                        print(f"User {user_id} assigned to cluster {cluster_id} with distance {distance:.3f}")
                    else:
                        print(f"Failed to predict cluster and distance for user {user_id}")

                    if cluster_id is not None:
                        profile.cluster_id = cluster_id
                        print(f"User {user_id} assigned to cluster {cluster_id}")
                    else:
                        print(f"Failed to predict cluster for user {user_id}")

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
            # Redirect based on completion status
            if not user.profile.preferences_subset:
                return redirect(url_for('preferences'))
            elif not user.profile.image_test:
                return redirect(url_for('preferences_text'))
            else:
                return redirect(url_for('match_feed'))
            
        except ValueError as e:
            flash(str(e), 'error')
            user_id = session['user_id']
            user = User.query.get(user_id)
            profile_data = user.profile if user else None
            preferences_similarity = profile_data.preferences_similarity if profile_data else None
            return render_template('profile-setup.html', profile_data=profile_data, preferences_similarity=preferences_similarity)
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update profile: {str(e)}', 'error')
            user_id = session['user_id']
            user = User.query.get(user_id)
            profile_data = user.profile if user else None
            preferences_similarity = profile_data.preferences_similarity if profile_data else None
            return render_template('profile-setup.html', profile_data=profile_data, preferences_similarity=preferences_similarity)
    
    # GET request - load existing profile data for prefill
    user_id = session['user_id']
    user = User.query.get(user_id)
    profile_data = user.profile if user else None
    
    # Get existing preferences similarity data for prefill
    preferences_similarity = None
    if profile_data:
        preferences_similarity = profile_data.preferences_similarity
    
    return render_template('profile-setup.html', profile_data=profile_data, preferences_similarity=preferences_similarity)

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            # Pastikan user memiliki profile
            if not user.profile:
                flash('Anda harus mengisi profil terlebih dahulu', 'error')
                return redirect(url_for('profile_setup'))
            
            # Get or create subset preferences
            subset_prefs = user.preferences_subset
            if not subset_prefs:
                subset_prefs = UserPreferencesSubset(user_id=user.profile.user_id)
                db.session.add(subset_prefs)
            
            # Get or create similarity preferences
            similarity_prefs = user.preferences_similarity
            if not similarity_prefs:
                similarity_prefs = UserPreferencesSimilarity(user_id=user.profile.user_id)
                db.session.add(similarity_prefs)
            
            # Update subset preferences from form data
            # Preferensi Usia
            if request.form.get('min_age'):
                subset_prefs.preferred_age_min = int(request.form.get('min_age'))
            if request.form.get('max_age'):
                subset_prefs.preferred_age_max = int(request.form.get('max_age'))
            
            # Validasi rentang usia
            if subset_prefs.preferred_age_min and subset_prefs.preferred_age_max:
                if subset_prefs.preferred_age_min > subset_prefs.preferred_age_max:
                    flash('Usia minimum harus lebih kecil dari usia maksimum', 'error')
                    return redirect(url_for('preferences'))
            
            # Preferensi Lokasi
            location_preference = request.form.get('location_preference')
            if location_preference:
                subset_prefs.same_location_only = (location_preference == 'same_city')
            
            # Tujuan Hubungan
            relationship_goal = request.form.get('relationship_goal')
            if relationship_goal:
                subset_prefs.serious_only = (relationship_goal == 'serious')
            
            # Preferensi Gaya Hidup - Merokok
            smoking_preference = request.form.get('smoking_preference')
            if smoking_preference:
                # Jika 'yes', berarti bermasalah dengan pasangan yang merokok
                # Jadi allow_smoking = False
                subset_prefs.allow_smoking = (smoking_preference == 'no')
            
            # Preferensi Gaya Hidup - Alkohol
            drinking_preference = request.form.get('drinking_preference')
            if drinking_preference:
                # Jika 'yes', berarti bermasalah dengan pasangan yang minum alkohol
                # Jadi allow_alcohol = False
                subset_prefs.allow_alcohol = (drinking_preference == 'no')
            
            # Preferensi Agama
            religion_preference = request.form.get('religion_preference')
            if religion_preference:
                subset_prefs.prefer_same_religion = (religion_preference == 'same_religion')
            
            # Preferensi Pendidikan
            education_preference = request.form.get('education_preference')
            if education_preference:
                subset_prefs.education_min = education_preference
            
            
            db.session.commit()
            flash('Preferensi berhasil diperbarui!', 'success')
            
            # Redirect ke halaman berikutnya
            if not user.profile.image_test:
                return redirect(url_for('image_test'))
            else:
                return redirect(url_for('match_feed'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui preferensi: {str(e)}', 'error')
            return redirect(url_for('preferences'))
    
    # GET request - load existing preferences for prefill
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get existing preferences for prefill
    preferences = None
    if user.profile and user.profile.preferences_subset:
        preferences = {
            'min_age': user.profile.preferences_subset.preferred_age_min,
            'max_age': user.profile.preferences_subset.preferred_age_max,
            'location_preference': 'same_city' if user.profile.preferences_subset.same_location_only else 'different_city',
            'relationship_goal': 'serious' if user.profile.preferences_subset.serious_only else 'casual',
            'smoking_preference': 'yes' if not user.profile.preferences_subset.allow_smoking else 'no',
            'drinking_preference': 'yes' if not user.profile.preferences_subset.allow_alcohol else 'no',
            'religion_preference': 'same_religion' if user.profile.preferences_subset.prefer_same_religion else 'different_religion',
            'education_preference': user.profile.preferences_subset.education_min,
            'social_care': user.profile.preferences_similarity.care_social_issues if user.profile.preferences_similarity else 3
        }
    
    return render_template('preferences.html', preferences=preferences)

@app.route('/match-feed')
@login_required
def match_feed():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get comprehensive matches (preferences + similarity + cluster)
    matches = find_comprehensive_matches(user_id)
    
    # Get user profiles for the matches
    match_profiles = []
    for match_data in matches:
        match_user = User.query.get(match_data['user_id'])
        if match_user and match_user.profile:
            profile_data = match_user.profile.to_dict()
            profile_data['total_score'] = round(match_data['total_score'] * 100, 1)
            profile_data['text_similarity'] = round(match_data['text_similarity'] * 100, 1)
            profile_data['cluster_distance'] = round(match_data['cluster_distance'] * 100, 1)
            match_profiles.append(profile_data)
    
    # Add current datetime for age calculation in template
    now = datetime.now()
    
    return render_template('match_feed.html', user=user, matches=match_profiles, now=now)

@app.route('/api/profile/<user_id>', methods=['GET'])
@login_required
def get_profile_api(user_id):
    """API endpoint untuk mendapatkan data profil pengguna untuk modal AJAX"""
    # Pastikan pengguna yang login memiliki akses ke profil ini
    current_user_id = session['user_id']
    
    # Cek apakah pengguna yang diminta ada dalam daftar kecocokan pengguna saat ini
    matches = find_comprehensive_matches(current_user_id)
    match_data = next((match for match in matches if match['user_id'] == user_id), None)
    
    if not match_data:
        return jsonify({'error': 'Profil tidak ditemukan atau Anda tidak memiliki akses'}), 404
    
    # Ambil data profil pengguna
    user = User.query.get(user_id)
    if not user or not user.profile:
        return jsonify({'error': 'Profil tidak ditemukan'}), 404
    
    # Siapkan data profil untuk respons JSON
    profile_data = user.profile.to_dict()
    profile_data['total_score'] = round(match_data['total_score'] * 100, 1)
    
    return jsonify(profile_data)

# Function to predict cluster for user photo
def predict_user_cluster(image_path, gender):
    """
    Predict cluster ID using the ML service
    """
    try:
        service = get_model_service()
        if service is None:
            logging.error("ML service not available")
            return None
        
        cluster_id,distance = service.predict_cluster(image_path, gender)
        
        if cluster_id is not None:
            logging.info(f"Predicted cluster {cluster_id} for {gender} user")
            
            # Optionally get confidence scores
            prob_info = service.get_cluster_probabilities(image_path, gender)
            if prob_info:
                logging.info(f"Prediction confidence: {prob_info['confidence']:.3f}")
        
        return cluster_id, distance
        
    except Exception as e:
        logging.error(f"Error in predict_user_cluster: {e}")
        return None

@app.route('/preferences-text', methods=['GET', 'POST'])
@login_required
def preferences_text():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            existing_test = UserPreferencesSimilarity.query.filter_by(user_id=user_id).first()
            
            if not existing_test:
                existing_test = UserPreferencesSimilarity(user_id=user_id)
                db.session.add(existing_test)
            
            # Mengambil data dari form
            existing_test.message_length = int(request.form.get('message_length', 3))
            existing_test.emoji_frequency = int(request.form.get('emoji_frequency', 3))
            existing_test.joke_frequency = int(request.form.get('joke_frequency', 3))
            existing_test.communication_type = int(request.form.get('communication_type', 1))
            existing_test.message_style = int(request.form.get('message_style', 1))
            existing_test.allow_informal = True if request.form.get('allow_informal') == 'yes' else False
            existing_test.abbreviation_frequency = int(request.form.get('abbreviation_frequency', 3))
            existing_test.punctuation_frequency = int(request.form.get('punctuation_frequency', 3))
            existing_test.capitalization_sensitive = True if request.form.get('capitalization_sensitive') == 'yes' else False
            
            db.session.commit()
            flash('Preferensi teks berhasil disimpan!', 'success')
            return redirect(url_for('image_test'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            # Get existing text test for prefill
            user_id = session['user_id']
            existing_test = UserPreferencesSimilarity.query.filter_by(user_id=user_id).first()
            return render_template('preferences_text.html', text_preferences=existing_test)
    
    # GET request - load existing data for prefill
    user_id = session['user_id']
    existing_test = UserPreferencesSimilarity.query.filter_by(user_id=user_id).first()
    return render_template('preferences_text.html', text_preferences=existing_test)

@app.route('/image-test', methods=['GET', 'POST'])
@login_required
def image_test():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        try:
            # Get preferred cluster IDs from form (multiple selection)
            preferred_cluster_ids = request.form.getlist('preferred_cluster_ids')
            redirect_to = request.form.get('redirect_to', 'match_feed')
            
            if not preferred_cluster_ids:
                flash('Silakan pilih setidaknya satu gaya visual yang Anda sukai.', 'error')
                return redirect(url_for('image_test'))
            
            # Get or create image test
            existing_test = UserImageTest.query.filter_by(user_id=user_id).first()
            if not existing_test:
                existing_test = UserImageTest(user_id=user_id)
                db.session.add(existing_test)
            
            # Set preferred cluster IDs
            existing_test.set_preferred_cluster_ids(preferred_cluster_ids)
            
            db.session.commit()
            flash('Preferensi visual berhasil disimpan!', 'success')
            
            # Redirect based on form parameter
            if redirect_to == 'match_feed':
                return redirect(url_for('match_feed'))
            else:
                return redirect(url_for('image_test'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('image_test'))
    
    # GET request - determine user's gender for showing appropriate images
    user_gender = 'male'  # default
    if user.profile and user.profile.gender:
        # Show opposite gender images for heterosexual matching
        user_gender = 'female' if user.profile.gender.lower() == 'male' else 'male'
    
    # Get existing image test for prefill
    existing_test = UserImageTest.query.filter_by(user_id=user_id).first()
    
    return render_template('image_test.html', target_gender=user_gender, existing_test=existing_test)


def find_comprehensive_matches(user_id, top_n=10):
    """
    Find matches using the new staged matching system
    """
    try:
        from matching_system import get_final_matches
        
        # Use the new staged matching system
        final_matches = get_final_matches(user_id)
        
        if not final_matches:
            print(f"No matches found for user {user_id}")
            return []
        
        # Limit to top_n results
        return final_matches[:top_n]
        
    except Exception as e:
        print(f"Error in find_comprehensive_matches: {e}")
        return []


@app.route('/comprehensive-matches')
def comprehensive_matches():
    """API endpoint for comprehensive matching system"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': 'Please log in to access this page.'
        }), 401
    
    try:
        matches = find_comprehensive_matches(session['user_id'])
        
        # Get user profiles for the matches
        match_profiles = []
        for match_data in matches:
            user = User.query.get(match_data['user_id'])
            if user and user.profile:
                profile_data = user.profile.to_dict()
                profile_data['total_score'] = round(match_data['total_score'] * 100, 1)
                profile_data['text_similarity'] = round(match_data['text_similarity'] * 100, 1)
                profile_data['cluster_distance'] = round(match_data['cluster_distance'] * 100, 1)
                match_profiles.append(profile_data)
        
        return jsonify({
            'success': True,
            'matches': matches
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# route about
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Bagus sudah dihapus semua
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080,debug=True)