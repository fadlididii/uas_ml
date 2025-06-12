from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, or_

db = SQLAlchemy()

class User(UserMixin, db.Model):
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
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')
    text_tests = db.relationship('UserTextTest', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
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
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.Text)
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    education = db.Column(db.String(100))
    location = db.Column(db.String(100))
    religion = db.Column(db.String(50))
    social_care = db.Column(db.Integer)
    smoking = db.Column(db.Boolean)
    drinking = db.Column(db.Boolean)
    have_pets = db.Column(db.Boolean)
    cluster_id = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'bio': self.bio,
            'photo_url': self.photo_url,
            'weight': self.weight,
            'height': self.height,
            'education': self.education,
            'location': self.location,
            'religion': self.religion,
            'social_care': self.social_care,
            'smoking': self.smoking,
            'drinking': self.drinking,
            'have_pets': self.have_pets,
            'cluster_id': self.cluster_id
        }

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    age_min = db.Column(db.Integer)
    age_max = db.Column(db.Integer)
    same_location = db.Column(db.Boolean)
    relationship_goal = db.Column(db.String(100))
    is_smoking = db.Column(db.Boolean)
    is_drinking = db.Column(db.Boolean)
    same_religion = db.Column(db.Boolean)
    partner_social_care = db.Column(db.Integer)
    partner_education = db.Column(db.String(100))
    comfortable_pets = db.Column(db.Boolean)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age_min': self.age_min,
            'age_max': self.age_max,
            'same_location': self.same_location,
            'relationship_goal': self.relationship_goal,
            'is_smoking': self.is_smoking,
            'is_drinking': self.is_drinking,
            'same_religion': self.same_religion,
            'partner_social_care': self.partner_social_care,
            'partner_education': self.partner_education,
            'comfortable_pets': self.comfortable_pets
        }

class UserTextTest(db.Model):
    __tablename__ = 'user_text_tests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    q1 = db.Column(db.Text)
    q2 = db.Column(db.Text)
    q3 = db.Column(db.Text)
    q4 = db.Column(db.Text)
    q5 = db.Column(db.Text)
    embedding = db.Column(db.PickleType)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'q1': self.q1,
            'q2': self.q2,
            'q3': self.q3,
            'q4': self.q4,
            'q5': self.q5,
            'embedding': self.embedding
        }

class UserImageTest(db.Model):
    __tablename__ = 'user_image_tests'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    preferred_cluster_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_cluster_id': self.preferred_cluster_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
