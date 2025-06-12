from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user
from matching_system import get_final_matches
from werkzeug.utils import secure_filename
from config import config
from models import db, User, UserProfile, UserPreferences, UserTextTest, UserImageTest
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from api_routes import api
import numpy as np
import os
import uuid
import pickle
from PIL import Image
from functools import wraps

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])

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
        
        # Validasi login
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_active:
                # Login berhasil
                login_user(user)
                session['user_id'] = user.id
                session['email'] = user.email
                flash('Login successful!', 'success')
                
                # Redirect based on user completion status
                # 1. Check if user has profile
                if not user.profile:
                    return redirect(url_for('profile_setup'))
                
                # 2. Check if user has preferences
                elif not user.preferences:
                    return redirect(url_for('preferences'))
                
                # 3. Check if user has completed text test
                elif not UserTextTest.query.filter_by(user_id=user.id).first():
                    return redirect(url_for('text_test'))
                
                # 4. Check if user has completed image test (placeholder for now)
                elif not user.image_test_completed:
                    return redirect(url_for('image_test'))
                
                # 5. If all complete, go to match feed
                else:
                    return redirect(url_for('match_feed'))
            else:
                flash('Account is deactivated', 'error')
        else:
            flash('Invalid email or password', 'error')
    
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
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if request.method == 'GET':
        # Prepare profile data for form pre-filling
        profile_data = {}
        if user.profile:
            profile = user.profile
            profile_data = {
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else '',
                'gender': profile.gender or '',
                'bio': profile.bio or '',
                'weight': profile.weight or '',
                'height': profile.height or '',
                'education': profile.education or '',
                'location': profile.location or '',
                'religion': profile.religion or '',
                'social_care': profile.social_care or 5,
                'smoking': 'yes' if profile.smoking else 'no' if profile.smoking is not None else '',
                'have_pets': 'yes' if profile.have_pets else 'no' if profile.have_pets is not None else '',
                'photo_url': profile.photo_url or ''
            }
        
        return render_template('profile-setup.html', profile_data=profile_data)
    
    elif request.method == 'POST':
        try:
            # Ambil data dari form
            data = request.form
            file = request.files.get('profilePhoto')
            
            # Simpan file jika ada
            photo_url = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join('static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                photo_path = os.path.join(upload_dir, filename)
                file.save(photo_path)
                photo_url = '/' + photo_path.replace('\\', '/')  # Untuk dipakai di HTML nanti

            # Get or create profile
            profile = user.profile
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
            
            # Update profile fields
            profile.first_name = data.get('firstName')
            profile.last_name = data.get('lastName')
            profile.date_of_birth = datetime.strptime(data.get('dateOfBirth'), '%Y-%m-%d') if data.get('dateOfBirth') else None
            profile.gender = data.get('gender')
            profile.bio = data.get('bio')
            profile.weight = int(data.get('weight')) if data.get('weight') else None
            profile.height = int(data.get('height')) if data.get('height') else None
            profile.education = data.get('education')
            profile.location = data.get('location')
            profile.religion = data.get('religion')
            profile.social_care = int(data.get('socialCare')) if data.get('socialCare') else None
            profile.smoking = True if data.get('smoking') == 'yes' else False
            profile.drinking = None  # Tidak ada di form HTML
            profile.have_pets = True if data.get('pets') == 'yes' else False
            
            if photo_url:
                profile.photo_url = photo_url
                
                # Automatic clustering for profile photo
                if profile.gender and file and file.filename:
                    cluster_id = predict_user_cluster(photo_path, profile.gender)
                    if cluster_id is not None:
                        profile.cluster_id = cluster_id
                        print(f"User {user_id} assigned to cluster {cluster_id}")
                    else:
                        print(f"Failed to predict cluster for user {user_id}")

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
            # Redirect based on completion status
            if not user.preferences:
                return redirect(url_for('preferences'))
            elif not UserTextTest.query.filter_by(user_id=user.id).first():
                return redirect(url_for('text_test'))
            else:
                return redirect(url_for('match_feed'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'error')
            return redirect(url_for('profile_setup'))



@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    if request.method == 'POST':
        try:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            # Get or create preferences
            prefs = user.preferences
            if not prefs:
                prefs = UserPreferences(user_id=user_id)
                db.session.add(prefs)
            
            # Update preferences from form data
            if request.form.get('age_min'):
                prefs.age_min = int(request.form.get('age_min'))
            if request.form.get('age_max'):
                prefs.age_max = int(request.form.get('age_max'))
            
            prefs.relationship_goal = request.form.get('relationship_goal')
            prefs.partner_education = request.form.get('partner_education')
            
            # Handle boolean fields - sesuaikan dengan nilai form HTML
            prefs.same_location = request.form.get('same_location') == 'yes'
            prefs.is_smoking = request.form.get('smoking') == 'yes'
            prefs.is_drinking = request.form.get('drinking') == 'yes'
            prefs.same_religion = request.form.get('same_religion') == 'yes'
            prefs.comfortable_pets = request.form.get('comfortable_pets') == 'yes'
            
            if request.form.get('partner_social_care'):
                prefs.partner_social_care = int(request.form.get('partner_social_care'))
            
            db.session.commit()
            flash('Preferences updated successfully!', 'success')
            return redirect(url_for('text_test'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to update preferences. Please try again.', 'error')
    
    # Get existing preferences for prefill
    user_id = session['user_id']
    user = User.query.get(user_id)
    existing_prefs = user.preferences
    
    return render_template('preferences.html', preferences=existing_prefs)

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
            profile_data['cluster_similarity'] = round(match_data['cluster_similarity'] * 100, 1)
            match_profiles.append(profile_data)
    
    return render_template('match_feed.html', 
                         user=user, 
                         matches=match_profiles)


# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to preprocess image for clustering
def preprocess_image_for_clustering(image_path, target_size=(64, 64)):
    """
    Preprocess image for clustering: resize, flatten, normalize
    """
    try:
        # Open and convert image to RGB
        img = Image.open(image_path).convert('RGB')
        
        # Resize image
        img = img.resize(target_size)
        
        # Convert to numpy array and flatten
        img_array = np.array(img)
        img_flattened = img_array.flatten()
        
        # Normalize pixel values to 0-1 range
        img_normalized = img_flattened / 255.0
        
        return img_normalized.reshape(1, -1)  # Reshape for model prediction
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# Function to predict cluster for user photo
def predict_user_cluster(image_path, gender):
    """
    Predict cluster ID for user's profile photo
    """
    try:
        # Preprocess image
        processed_image = preprocess_image_for_clustering(image_path)
        if processed_image is None:
            return None
        
        # Load appropriate model based on gender
        model_filename = f'model_{gender.lower()}.pkl'
        model_path = os.path.join('static', 'models', model_filename)
        
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None
        
        # Load clustering model
        with open(model_path, 'rb') as f:
            clustering_model = pickle.load(f)
        
        # Predict cluster
        cluster_id = clustering_model.predict(processed_image)[0]
        return int(cluster_id)
    
    except Exception as e:
        print(f"Error predicting cluster: {e}")
        return None

@app.route('/text-test', methods=['GET', 'POST'])
def text_test():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get answers from form
            q1 = request.form.get('q1', '').strip()
            q2 = request.form.get('q2', '').strip()
            q3 = request.form.get('q3', '').strip()
            q4 = request.form.get('q4', '').strip()
            q5 = request.form.get('q5', '').strip()
            
            # Validate that all questions are answered
            if not all([q1, q2, q3, q4, q5]):
                flash('Please answer all questions.', 'error')
                # Get existing text test for prefill
                user_id = session['user_id']
                existing_test = UserTextTest.query.filter_by(user_id=user_id).first()
                return render_template('text_test.html', text_test=existing_test)
            
            # Combine all answers into one string
            combined_text = f"{q1} {q2} {q3} {q4} {q5}"
            
            # Generate embedding using sentence-transformers
            embedding = model.encode(combined_text).tolist()
            
            # Check if user already has a text test
            existing_test = UserTextTest.query.filter_by(user_id=session['user_id']).first()
            
            if existing_test:
                # Update existing test
                existing_test.q1 = q1
                existing_test.q2 = q2
                existing_test.q3 = q3
                existing_test.q4 = q4
                existing_test.q5 = q5
                existing_test.embedding = embedding
            else:
                # Create new test
                text_test = UserTextTest(
                    user_id=session['user_id'],
                    q1=q1,
                    q2=q2,
                    q3=q3,
                    q4=q4,
                    q5=q5,
                    embedding=embedding
                )
                db.session.add(text_test)
            
            db.session.commit()
            flash('Personality test completed successfully!', 'success')
            return redirect(url_for('image_test'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            # Get existing text test for prefill
            user_id = session['user_id']
            existing_test = UserTextTest.query.filter_by(user_id=user_id).first()
            return render_template('text_test.html', text_test=existing_test)
    
    # GET request - load existing data for prefill
    user_id = session['user_id']
    existing_test = UserTextTest.query.filter_by(user_id=user_id).first()
    return render_template('text_test.html', text_test=existing_test)

@app.route('/image-test', methods=['GET', 'POST'])
@login_required
def image_test():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        try:
            # Get preferred cluster from form
            preferred_cluster_id = request.form.get('preferred_cluster_id')
            
            if not preferred_cluster_id:
                flash('Please select your preferred visual style.', 'error')
                return redirect(url_for('image_test'))
            
            # Check if user already has image test
            existing_test = UserImageTest.query.filter_by(user_id=user_id).first()
            
            if existing_test:
                # Update existing test
                existing_test.preferred_cluster_id = int(preferred_cluster_id)
                existing_test.updated_at = datetime.utcnow()
            else:
                # Create new test
                image_test = UserImageTest(
                    user_id=user_id,
                    preferred_cluster_id=int(preferred_cluster_id)
                )
                db.session.add(image_test)
            
            db.session.commit()
            flash('Visual preference test completed successfully!', 'success')
            return redirect(url_for('match_feed'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('image_test'))
    
    # GET request - determine user's gender for showing appropriate cluster images
    user_gender = 'male'  # default
    if user.profile and user.profile.gender:
        # Show opposite gender clusters for heterosexual matching
        user_gender = 'female' if user.profile.gender.lower() == 'male' else 'male'
    
    # Get existing image test for prefill
    existing_test = UserImageTest.query.filter_by(user_id=user_id).first()
    
    return render_template('image_test.html', target_gender=user_gender,existing_test=existing_test)


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
                profile_data['cluster_similarity'] = round(match_data['cluster_similarity'] * 100, 1)
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

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)