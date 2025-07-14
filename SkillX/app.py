from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'skillx_hackathon_secret_key'

# Database setup
DB_PATH = 'skillx.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Context processors
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Helper functions
def is_logged_in():
    return 'user_id' in session

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        college = request.form.get('college')
        year = request.form.get('year')
        
        conn = get_db_connection()
        user_exists = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user_exists:
            flash('Email already registered', 'danger')
            conn.close()
        else:
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (name, email, password, college, year_of_study) VALUES (?, ?, ?, ?, ?)',
                        (name, email, hashed_password, college, year))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash('Please login to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get user profile
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Get user skills
    skills = conn.execute('SELECT * FROM user_skills WHERE user_id = ?', (user_id,)).fetchall()
    
    # Get recommended paths
    recommended_paths = conn.execute('''
        SELECT cp.* FROM career_paths cp
        JOIN user_career_interests uci ON cp.id = uci.career_path_id
        WHERE uci.user_id = ?
    ''', (user_id,)).fetchall()

    # If there are no recommended paths, get all paths
    if not recommended_paths:
        recommended_paths = conn.execute('SELECT * FROM career_paths LIMIT 3').fetchall()
    
    # Get job recommendations
    jobs = conn.execute('''
        SELECT * FROM job_listings
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                          user=user, 
                          skills=skills,
                          recommended_paths=recommended_paths,
                          jobs=jobs)

@app.route('/skill-assessment', methods=['GET', 'POST'])
def skill_assessment():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        skills_data = request.form.to_dict()
        
        conn = get_db_connection()
        
        # Clear existing skills first
        conn.execute('DELETE FROM user_skills WHERE user_id = ?', (user_id,))
        
        # Add new skills
        for skill, level in skills_data.items():
            if skill.startswith('skill_'):
                skill_name = skill.replace('skill_', '').replace('_', ' ')
                if level and int(level) > 0:  # Only add skills with a level
                    conn.execute('INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES (?, ?, ?)',
                              (user_id, skill_name, level))
        
        conn.commit()
        conn.close()
        
        flash('Skills updated successfully!', 'success')
        return redirect(url_for('career_paths'))
    
    # Get all available skill categories
    conn = get_db_connection()
    skill_categories = conn.execute('SELECT * FROM skill_categories').fetchall()
    
    # Get user's existing skills
    user_id = session['user_id']
    user_skills = conn.execute('SELECT * FROM user_skills WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    user_skills_dict = {skill['skill_name']: skill['proficiency_level'] for skill in user_skills}
    
    return render_template('skill_assessment.html', 
                          skill_categories=skill_categories,
                          user_skills=user_skills_dict)

@app.route('/career-paths')
def career_paths():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get user skills
    skills = conn.execute('SELECT skill_name, proficiency_level FROM user_skills WHERE user_id = ?', 
                         (user_id,)).fetchall()
    
    # Convert to dict for easier processing
    skills_dict = {skill['skill_name']: skill['proficiency_level'] for skill in skills}
    
    # Get all career paths
    career_paths = conn.execute('SELECT * FROM career_paths').fetchall()
    
    # Simple recommendation algorithm - match skills to required skills for career paths
    recommended_paths = []
    
    for path in career_paths:
        required_skills = json.loads(path['required_skills'])
        match_score = 0
        total_skills = len(required_skills)
        
        for skill, required_level in required_skills.items():
            if skill in skills_dict:
                user_level = int(skills_dict[skill])
                if user_level >= int(required_level):
                    match_score += 1
                else:
                    match_score += user_level / int(required_level)
        
        if total_skills > 0:
            match_percentage = (match_score / total_skills) * 100
        else:
            match_percentage = 0
            
        path_dict = dict(path)
        path_dict['match_percentage'] = round(match_percentage)
        recommended_paths.append(path_dict)
    
    # Sort by match percentage
    recommended_paths.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    conn.close()
    
    return render_template('career_paths.html', career_paths=recommended_paths)

@app.route('/job-trends')
def job_trends():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get trending skills
    trending_skills = conn.execute('''
        SELECT skill_name, COUNT(*) as job_count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY job_count DESC
        LIMIT 10
    ''').fetchall()
    
    # Get trending job roles
    trending_roles = conn.execute('''
        SELECT job_title, COUNT(*) as job_count
        FROM job_listings
        GROUP BY job_title
        ORDER BY job_count DESC
        LIMIT 10
    ''').fetchall()
    
    # Get latest job listings
    latest_jobs = conn.execute('''
        SELECT * FROM job_listings
        ORDER BY created_at DESC
        LIMIT 20
    ''').fetchall()
    
    conn.close()
    
    return render_template('job_trends.html', 
                          trending_skills=trending_skills,
                          trending_roles=trending_roles,
                          latest_jobs=latest_jobs)

@app.route('/mock-interview')
def mock_interview():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get interview categories
    categories = conn.execute('SELECT * FROM interview_categories').fetchall()
    
    # Get user's previous interviews
    user_id = session['user_id']
    previous_interviews = conn.execute('''
        SELECT * FROM mock_interviews
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('mock_interview.html', 
                          categories=categories,
                          previous_interviews=previous_interviews)

@app.route('/start-interview/<int:category_id>')
def start_interview(category_id):
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    # Get category
    category = conn.execute('SELECT * FROM interview_categories WHERE id = ?', (category_id,)).fetchone()
    
    # Get questions for this category
    questions = conn.execute('''
        SELECT * FROM interview_questions
        WHERE category_id = ?
        ORDER BY RANDOM()
        LIMIT 10
    ''', (category_id,)).fetchall()
    
    conn.close()
    
    return render_template('interview_session.html', 
                          category=category,
                          questions=questions)

@app.route('/resume-review', methods=['GET', 'POST'])
def resume_review():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # In a real app, we would handle file upload and processing here
        flash('Resume uploaded successfully! Analysis in progress...', 'success')
        return redirect(url_for('resume_feedback'))
    
    return render_template('resume_review.html')

@app.route('/resume-feedback')
def resume_feedback():
    if not is_logged_in():
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    # This would be dynamically generated in a real app
    feedback = {
        'score': 75,
        'strengths': [
            'Good use of action verbs',
            'Clear job descriptions',
            'Appropriate length'
        ],
        'improvements': [
            'Add more quantifiable achievements',
            'Customize for specific job roles',
            'Include more relevant keywords'
        ],
        'ats_compatibility': 'Medium'
    }
    
    return render_template('resume_feedback.html', feedback=feedback)

# API Routes for dynamic content
@app.route('/api/job-listings')
def api_job_listings():
    # Parameters
    skill = request.args.get('skill')
    role = request.args.get('role')
    
    conn = get_db_connection()
    
    if skill:
        jobs = conn.execute('''
            SELECT jl.* FROM job_listings jl
            JOIN job_skills js ON jl.id = js.job_id
            WHERE js.skill_name LIKE ?
            ORDER BY jl.created_at DESC
            LIMIT 20
        ''', ('%' + skill + '%',)).fetchall()
    elif role:
        jobs = conn.execute('''
            SELECT * FROM job_listings
            WHERE job_title LIKE ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', ('%' + role + '%',)).fetchall()
    else:
        jobs = conn.execute('''
            SELECT * FROM job_listings
            ORDER BY created_at DESC
            LIMIT 20
        ''').fetchall()
    
    conn.close()
    
    # Convert to list of dicts
    result = [dict(job) for job in jobs]
    return jsonify(result)

# Route for static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Special route to test CSS loading
@app.route('/test-css')
def test_css():
    return """
    <html>
    <head>
        <title>CSS Test Page</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            body { padding: 20px; }
            .test-box { 
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CSS Testing Page</h1>
            <p>This page is used to test if CSS is loading properly.</p>
            
            <div class="test-box bg-primary text-white">
                <h3>Bootstrap Test</h3>
                <p>If you see this box with a blue background and white text, Bootstrap CSS is working!</p>
            </div>
            
            <div class="test-box">
                <h3>Custom CSS Test</h3>
                <p>If you see this element with custom styling, your styles.css file is working!</p>
                <p>Elements that should be styled from styles.css:</p>
                <ul>
                    <li>Cards should have rounded corners</li>
                    <li>The navbar should have a shadow</li>
                    <li>Buttons should have a transition effect on hover</li>
                </ul>
            </div>
            
            <a href="/" class="btn btn-primary">Back to Home</a>
        </div>
    </body>
    </html>
    """

# Ensure the static directories exist
@app.before_first_request
def create_static_dirs():
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/img', exist_ok=True)

if __name__ == '__main__':
    # Create tables if they don't exist
    if not os.path.exists(DB_PATH):
        from db_setup import init_db
        init_db()
    
    app.run(debug=True)