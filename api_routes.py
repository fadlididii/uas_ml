from flask import Blueprint, request, jsonify, session, current_app as app
from models import db, User, UserProfile, UserPreferences
from datetime import datetime, date
import uuid
import os
from functools import wraps

api = Blueprint('api', __name__, url_prefix='/api')

# Helper function untuk validasi session
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper function untuk response format
def success_response(data=None, message="Success", status_code=200):
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error occurred", status_code=400):
    return jsonify({'success': False, 'error': message}), status_code

@api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field} is required', 400)
        
        # Cek apakah email sudah terdaftar
        if User.query.filter_by(email=data['email']).first():
            return error_response('Email already registered', 409)
        
        # Buat user baru
        user = User(
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            data={'user_id': user.id, 'email': user.email},
            message='User registered successfully',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', 500)

@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validasi input
        if not data.get('email') or not data.get('password'):
            return error_response('Email and password are required', 400)
        
        # Cari user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return error_response('Invalid email or password', 401)
        
        if not user.is_active:
            return error_response('Account is deactivated', 401)
        
        # Set session
        session['user_id'] = user.id
        session['email'] = user.email
        
        return success_response(
            data={
                'user_id': user.id,
                'email': user.email,
                'has_profile': user.profile is not None,
                'has_preferences': user.preferences is not None
            },
            message='Login successful'
        )
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', 500)

@api.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return success_response(message='Logout successful')

@api.route('/profile', methods=['GET', 'POST', 'PUT'])
@login_required
def profile():
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Get profile
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        profile_data = user.to_dict()
        if user.profile:
            profile_data['profile'] = user.profile.to_dict()
        
        return success_response(data=profile_data)
    
    elif request.method in ['POST', 'PUT']:
        # Create or update profile
        try:
            # Handle both JSON and form data (for file uploads)
            if request.content_type and 'application/json' in request.content_type:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            user = User.query.get(user_id)
            if not user:
                return error_response('User not found', 404)
            
            # Get or create profile
            profile = user.profile
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
            
            # Handle photo upload
            photo_url = None
            if 'profilePhoto' in request.files:
                photo_file = request.files['profilePhoto']
                if photo_file and photo_file.filename:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    file_extension = photo_file.filename.rsplit('.', 1)[1].lower() if '.' in photo_file.filename else ''
                    
                    if file_extension not in allowed_extensions:
                        return error_response('Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed.', 400)
                    
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
                    file_path = os.path.join(upload_dir, filename)
                    
                    # Save file
                    photo_file.save(file_path)
                    
                    # Store relative URL
                    photo_url = f"/static/uploads/profiles/{filename}"
            
            # Update profile fields
            profile_fields = [
                'first_name', 'last_name', 'gender', 'bio',
                'weight', 'height', 'education', 'location', 'religion',
                'social_care', 'smoking', 'drinking', 'have_pets', 'cluster_id'
            ]
            
            for field in profile_fields:
                if field in data:
                    value = data[field]
                    # Convert string values to appropriate types
                    if field in ['weight', 'height', 'social_care'] and value:
                        value = int(value)
                    elif field in ['smoking', 'drinking', 'have_pets'] and value:
                        value = value.lower() == 'true'
                    setattr(profile, field, value)
            
            # Set photo URL if uploaded
            if photo_url:
                profile.photo_url = photo_url
            
            # Handle date_of_birth
            if 'date_of_birth' in data and data['date_of_birth']:
                try:
                    profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    return error_response('Invalid date format. Use YYYY-MM-DD', 400)
            
            db.session.commit()
            
            # For HTML form submission, redirect to welcome page
            if request.content_type and 'application/json' not in request.content_type:
                from flask import redirect, url_for
                return redirect('/welcome')
            
            # For API calls, return JSON response
            return success_response(
                data=profile.to_dict(),
                message='Profile updated successfully'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Profile update failed: {str(e)}', 500)

@api.route('/preferences', methods=['GET', 'POST', 'PUT'])
@login_required
def preferences():
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Get preferences
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        if user.preferences:
            return success_response(data=user.preferences.to_dict())
        else:
            return success_response(data=None, message='No preferences set')
    
    elif request.method in ['POST', 'PUT']:
        # Create or update preferences
        try:
            data = request.get_json()
            
            user = User.query.get(user_id)
            if not user:
                return error_response('User not found', 404)
            
            # Get or create preferences
            preferences = user.preferences
            if not preferences:
                preferences = UserPreferences(user_id=user_id)
                db.session.add(preferences)
            
            # Update preferences fields
            preference_fields = [
                'age_min', 'age_max', 'same_location', 'relationship_goal',
                'is_smoking', 'is_drinking', 'same_religion', 'partner_social_care',
                'partner_education', 'comfortable_pets'
            ]
            
            for field in preference_fields:
                if field in data:
                    setattr(preferences, field, data[field])
            
            db.session.commit()
            
            return success_response(
                data=preferences.to_dict(),
                message='Preferences updated successfully'
            )
            
        except Exception as e:
            db.session.rollback()
            return error_response(f'Preferences update failed: {str(e)}', 500)

@api.route('/user/status', methods=['GET'])
@login_required
def user_status():
    """Get user completion status"""
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', 404)
    
    status = {
        'user_id': user.id,
        'email': user.email,
        'has_profile': user.profile is not None,
        'has_preferences': user.preferences is not None,
        'profile_complete': False,
        'preferences_complete': False
    }
    
    # Check if profile is complete
    if user.profile:
        required_profile_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
        status['profile_complete'] = all(
            getattr(user.profile, field) is not None 
            for field in required_profile_fields
        )
    
    # Check if preferences are complete
    if user.preferences:
        required_preference_fields = ['age_min', 'age_max', 'relationship_goal']
        status['preferences_complete'] = all(
            getattr(user.preferences, field) is not None 
            for field in required_preference_fields
        )
    
    return success_response(data=status)

@api.route('/users', methods=['GET'])
@login_required
def get_users():
    """Get all users (for admin or matching purposes)"""
    try:
        users = User.query.filter_by(is_active=True).all()
        users_data = []
        
        for user in users:
            user_data = user.to_dict()
            if user.profile:
                user_data['profile'] = user.profile.to_dict()
            if user.preferences:
                user_data['preferences'] = user.preferences.to_dict()
            users_data.append(user_data)
        
        return success_response(data=users_data)
        
    except Exception as e:
        return error_response(f'Failed to get users: {str(e)}', 500)

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return error_response('Endpoint not found', 404)

@api.errorhandler(405)
def method_not_allowed(error):
    return error_response('Method not allowed', 405)

@api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return error_response('Internal server error', 500)