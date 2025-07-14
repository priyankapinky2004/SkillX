"""
User Module - Handles user-related operations
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_user(name, email, password, college, year):
    """Create a new user"""
    conn = get_db_connection()
    
    # Check if email already exists
    existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing_user:
        conn.close()
        return False, "Email already registered"
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Insert the new user
    conn.execute(
        'INSERT INTO users (name, email, password, college, year_of_study) VALUES (?, ?, ?, ?, ?)',
        (name, email, hashed_password, college, year)
    )
    conn.commit()
    
    # Get the user ID
    user = conn.execute('SELECT id, name FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    return True, user

def update_user_profile(user_id, name=None, bio=None, profile_pic=None):
    """Update user profile"""
    conn = get_db_connection()
    
    # Build the update query dynamically based on provided fields
    query_parts = []
    params = []
    
    if name:
        query_parts.append("name = ?")
        params.append(name)
        
    if bio:
        query_parts.append("bio = ?")
        params.append(bio)
        
    if profile_pic:
        query_parts.append("profile_pic = ?")
        params.append(profile_pic)
    
    # Add user_id to params
    params.append(user_id)
    
    if query_parts:
        query = f"UPDATE users SET {', '.join(query_parts)} WHERE id = ?"
        conn.execute(query, params)
        conn.commit()
    
    conn.close()
    return True

def validate_login(email, password):
    """Validate user login credentials"""
    user = get_user_by_email(email)
    
    if not user:
        return False, "Invalid email or password"
    
    if not check_password_hash(user['password'], password):
        return False, "Invalid email or password"
    
    # Set session variables
    session['user_id'] = user['id']
    session['username'] = user['name']
    
    return True, user

def logout():
    """Log out the current user"""
    session.pop('user_id', None)
    session.pop('username', None)
    return True

def get_user_skills(user_id):
    """Get skills for a specific user"""
    conn = get_db_connection()
    skills = conn.execute('SELECT skill_name, proficiency_level FROM user_skills WHERE user_id = ?', 
                        (user_id,)).fetchall()
    conn.close()
    return skills

def update_user_skills(user_id, skills_data):
    """Update user skills"""
    conn = get_db_connection()
    
    # Clear existing skills
    conn.execute('DELETE FROM user_skills WHERE user_id = ?', (user_id,))
    
    # Add new skills
    for skill_name, level in skills_data.items():
        conn.execute(
            'INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES (?, ?, ?)',
            (user_id, skill_name, level)
        )
    
    conn.commit()
    conn.close()
    return True

def get_user_profile_completion(user_id):
    """Calculate profile completion percentage"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Get skills count
    skills_count = conn.execute('SELECT COUNT(*) as count FROM user_skills WHERE user_id = ?', 
                               (user_id,)).fetchone()['count']
    
    conn.close()
    
    # Define total profile fields
    total_fields = 7  # name, email, college, year, bio, profile_pic, skills
    filled_fields = 2  # name and email are always filled
    
    # Check additional fields
    if user['college']:
        filled_fields += 1
    if user['year_of_study']:
        filled_fields += 1
    if user['bio']:
        filled_fields += 1
    if user['profile_pic']:
        filled_fields += 1
    if skills_count > 0:
        filled_fields += 1
    
    # Calculate percentage
    completion_percentage = round((filled_fields / total_fields) * 100)
    
    return completion_percentage