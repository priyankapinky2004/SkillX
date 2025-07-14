"""
Authentication Module - Handles user authentication and session management
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_user(email, password):
    """Authenticate a user and create a session"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        # Set session variables
        session['user_id'] = user['id']
        session['username'] = user['name']
        return True, user
    
    return False, None

def register_user(name, email, password, college, year):
    """Register a new user"""
    conn = get_db_connection()
    
    # Check if email already exists
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if existing_user:
        conn.close()
        return False, "Email already registered"
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Insert the new user
    conn.execute('''
        INSERT INTO users (name, email, password, college, year_of_study) 
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, hashed_password, college, year))
    
    conn.commit()
    conn.close()
    
    return True, None

def logout_user():
    """Log out the current user by clearing the session"""
    session.pop('user_id', None)
    session.pop('username', None)
    return True

def is_authenticated():
    """Check if the current user is authenticated"""
    return 'user_id' in session

def get_current_user():
    """Get the current authenticated user"""
    if not is_authenticated():
        return None
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return user

def change_password(user_id, current_password, new_password):
    """Change a user's password"""
    conn = get_db_connection()
    
    # Get the user
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return False, "User not found"
    
    # Verify current password
    if not check_password_hash(user['password'], current_password):
        conn.close()
        return False, "Current password is incorrect"
    
    # Update to new password
    hashed_password = generate_password_hash(new_password)
    conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
    
    conn.commit()
    conn.close()
    
    return True, "Password changed successfully"

def require_login(route_function):
    """Decorator to require login for routes"""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    
    return decorated_function