from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, or_

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User login credentials and status"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def preferences_subset(self):
        """Access user preferences subset through profile"""
        return self.profile.preferences_subset if self.profile else None
    
    @property
    def preferences_similarity(self):
        """Access user preferences similarity through profile"""
        return self.profile.preferences_similarity if self.profile else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserProfile(db.Model):
    """User demographic and personal information"""
    __tablename__ = 'user_profile'
    
    # Agama yang diakui di Indonesia berdasarkan UU No. 1/PNPS/1965
    RELIGION_CHOICES = [
        ('islam', 'Islam'),
        ('kristen_protestan', 'Kristen Protestan'),
        ('kristen_katolik', 'Kristen Katolik'),
        ('hindu', 'Hindu'),
        ('buddha', 'Buddha'),
        ('konghucu', 'Konghucu')
    ]
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    height_cm = db.Column(db.Integer)
    weight_kg = db.Column(db.Integer)
    religion = db.Column(db.String(50))  # Harus sesuai dengan RELIGION_CHOICES
    education = db.Column(db.String(50))
    hobbies = db.Column(db.Text)
    language_used = db.Column(db.Text)
    photo_url = db.Column(db.String(255))
    whatsapp = db.Column(db.String(20))  # Nomor WhatsApp
    instagram = db.Column(db.String(100))  # Username Instagram
    smoking = db.Column(db.Boolean)  # Kebiasaan merokok
    alcohol = db.Column(db.Boolean)  # Kebiasaan alkohol
    relationship_goal = db.Column(db.String(20))  # 'casual' atau 'serious'
    cluster_id = db.Column(db.Integer)
    cluster_distance = db.Column(db.Float) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    # Relationships
    preferences_subset = db.relationship('UserPreferencesSubset', backref='profile', uselist=False, cascade='all, delete-orphan')
    preferences_similarity = db.relationship('UserPreferencesSimilarity', backref='profile', uselist=False, cascade='all, delete-orphan')
    image_test = db.relationship('UserImageTest', backref='profile', uselist=False, cascade='all, delete-orphan')
    
    @property
    def age(self):
        """Calculate age from date_of_birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,  # Age dihitung secara dinamis
            'bio': self.bio,
            'location': self.location,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'religion': self.religion,
            'education': self.education,
            'hobbies': self.hobbies,
            'language_used': self.language_used,
            'photo_url': self.photo_url,
            'whatsapp': self.whatsapp,
            'instagram': self.instagram,
            'smoking': self.smoking,
            'alcohol': self.alcohol,
            'relationship_goal': self.relationship_goal,
            'cluster_id': self.cluster_id
        }
    
    def get_religion_display(self):
        """Get human-readable religion name"""
        religion_dict = dict(self.RELIGION_CHOICES)
        return religion_dict.get(self.religion, self.religion)
    
    @classmethod
    def get_religion_choices(cls):
        """Get list of valid religion choices"""
        return cls.RELIGION_CHOICES

class UserPreferencesSubset(db.Model):
    """User preferences for rule-based matching"""
    __tablename__ = 'user_preferences_subset'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user_profile.user_id'), unique=True, nullable=False)
    preferred_age_min = db.Column(db.Integer)
    preferred_age_max = db.Column(db.Integer)
    same_location_only = db.Column(db.Boolean)
    serious_only = db.Column(db.Boolean)
    allow_smoking = db.Column(db.Boolean)
    allow_alcohol = db.Column(db.Boolean)
    prefer_same_religion = db.Column(db.Boolean)
    education_min = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_age_min': self.preferred_age_min,
            'preferred_age_max': self.preferred_age_max,
            'same_location_only': self.same_location_only,
            'serious_only': self.serious_only,
            'allow_smoking': self.allow_smoking,
            'allow_alcohol': self.allow_alcohol,
            'prefer_same_religion': self.prefer_same_religion,
            'education_min': self.education_min
        }

class UserPreferencesSimilarity(db.Model):
    """User preferences for similarity-based (cosine) matching"""
    __tablename__ = 'user_preferences_similarity'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user_profile.user_id'), unique=True, nullable=False)
    sports_frequency = db.Column(db.Integer)  # Skala Likert 1-5
    care_social_issues = db.Column(db.Integer)  # Skala Likert 1-5
    message_length = db.Column(db.Integer)  # Skala Likert 1-5
    emoji_frequency = db.Column(db.Integer)  # Skala Likert 1-5
    joke_frequency = db.Column(db.Integer)  # Skala Likert 1-5
    communication_type = db.Column(db.Integer)  # 1=formal, 2=informal, 3=mixed
    message_style = db.Column(db.Integer)  # 1=short, 2=medium, 3=long
    allow_informal = db.Column(db.Boolean)
    abbreviation_frequency = db.Column(db.Integer)  # Skala Likert 1-5
    punctuation_frequency = db.Column(db.Integer)  # Skala Likert 1-5
    capitalization_sensitive = db.Column(db.Boolean)
    has_pets = db.Column(db.Boolean)
    outdoor_activity = db.Column(db.Integer)  # Skala Likert 1-5: Seberapa rutin beraktivitas di luar rumah
    active_time = db.Column(db.Text)  # JSON string untuk menyimpan array: "[1,3]" (1=pagi, 2=siang, 3=sore, 4=malam)
    
    def get_active_time_list(self):
        """Parse active_time JSON string to list of integers"""
        if not self.active_time:
            return []
        try:
            import json
            return json.loads(self.active_time)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_active_time_list(self, time_list):
        """Set active_time from list of integers"""
        import json
        self.active_time = json.dumps(time_list) if time_list else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sports_frequency': self.sports_frequency,
            'care_social_issues': self.care_social_issues,
            'message_length': self.message_length,
            'emoji_frequency': self.emoji_frequency,
            'joke_frequency': self.joke_frequency,
            'communication_type': self.communication_type,
            'message_style': self.message_style,
            'allow_informal': self.allow_informal,
            'abbreviation_frequency': self.abbreviation_frequency,
            'punctuation_frequency': self.punctuation_frequency,
            'capitalization_sensitive': self.capitalization_sensitive,
            'has_pets': self.has_pets,
            'outdoor_activity': self.outdoor_activity,
            'active_time': self.get_active_time_list()
        }
    
    def get_similarity_vector(self):
        """Convert preferences to numerical vector for cosine similarity"""
        # Get active time as list and create binary encoding
        active_times = self.get_active_time_list()
        # Create binary encoding for each time slot (1=pagi, 2=siang, 3=sore, 4=malam)
        morning_active = 1 if 1 in active_times else 0
        afternoon_active = 1 if 2 in active_times else 0
        evening_active = 1 if 3 in active_times else 0
        night_active = 1 if 4 in active_times else 0
        
        vector = [
            self.sports_frequency or 0,
            self.care_social_issues or 0,
            self.message_length or 0,
            self.emoji_frequency or 0,
            self.joke_frequency or 0,
            self.communication_type or 0,
            self.message_style or 0,
            int(self.allow_informal) if self.allow_informal is not None else 0,
            self.abbreviation_frequency or 0,
            self.punctuation_frequency or 0,
            int(self.capitalization_sensitive) if self.capitalization_sensitive is not None else 0,
            int(self.has_pets) if self.has_pets is not None else 0,
            self.outdoor_activity or 0,
            morning_active,
            afternoon_active,
            evening_active,
            night_active
        ]
        return vector

class UserImageTest(db.Model):
    """User visual input for image-based matching"""
    __tablename__ = 'user_image_tests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user_profile.user_id'), unique=True, nullable=False)
    preferred_cluster_ids = db.Column(db.Text)  # JSON string untuk menyimpan array cluster IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_preferred_cluster_ids(self):
        """Parse preferred_cluster_ids JSON string to list of strings"""
        if not self.preferred_cluster_ids:
            return []
        try:
            import json
            return [str(cluster_id) for cluster_id in json.loads(self.preferred_cluster_ids)]
        except (json.JSONDecodeError, TypeError, ValueError):
            return []
    
    def set_preferred_cluster_ids(self, cluster_ids):
        """Set preferred_cluster_ids from list of integers or strings"""
        import json
        if cluster_ids:
            # Convert all values to integers
            int_cluster_ids = [int(cluster_id) for cluster_id in cluster_ids]
            self.preferred_cluster_ids = json.dumps(int_cluster_ids)
        else:
            self.preferred_cluster_ids = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_cluster_ids': self.get_preferred_cluster_ids(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
