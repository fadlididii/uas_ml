#!/usr/bin/env python3
"""
Script untuk membuat semua tabel database yang diperlukan
"""

from app import app, db
from models import User, UserProfile, UserPreferences, UserTextTest
from sqlalchemy import text
import os

def create_all_tables():
    """
    Membuat semua tabel yang diperlukan di database
    """
    try:
        with app.app_context():
            print("Creating all database tables...")
            
            # Create all tables
            print("Creating tables...")
            db.create_all()
            
            # Verify tables were created
            result = db.engine.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"  ✅ {table[0]}")
            
            # Verify user_text_tests table structure specifically
            if any('user_text_tests' in str(table) for table in tables):
                result = db.engine.execute(text("""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'user_text_tests' 
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                print("\nuser_text_tests table structure:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            else:
                print("❌ user_text_tests table was not created")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_table_operations():
    """
    Test basic operations on the UserTextTest table
    """
    try:
        with app.app_context():
            print("\nTesting UserTextTest table operations...")
            
            # Test creating a record
            test_record = UserTextTest(
                user_id='test-user-id-123',
                q1='Test answer 1',
                q2='Test answer 2', 
                q3='Test answer 3',
                q4='Test answer 4',
                q5='Test answer 5',
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
            )
            
            db.session.add(test_record)
            db.session.commit()
            print("✅ Test record created successfully")
            
            # Query the record back
            retrieved = UserTextTest.query.filter_by(user_id='test-user-id-123').first()
            if retrieved:
                print("✅ Test record retrieved successfully")
                print(f"  - ID: {retrieved.id}")
                print(f"  - User ID: {retrieved.user_id}")
                print(f"  - Q1: {retrieved.q1}")
                print(f"  - Created at: {retrieved.created_at}")
                
                # Clean up test record
                db.session.delete(retrieved)
                db.session.commit()
                print("✅ Test record cleaned up")
            else:
                print("❌ Failed to retrieve test record")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Table operation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Database Table Creation Script")
    print("=" * 40)
    
    # Create tables
    success = create_all_tables()
    
    if success:
        print("\n✅ All tables created successfully!")
        
        # Test operations
        test_success = test_table_operations()
        
        if test_success:
            print("\n🎉 Database is ready! You can now run the Flask application.")
        else:
            print("\n⚠️ Tables created but operations test failed. Check the logs above.")
    else:
        print("\n❌ Failed to create tables! Check the error messages above.")