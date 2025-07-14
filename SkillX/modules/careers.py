"""
Careers Module - Handles career path recommendations and related operations
"""
import sqlite3
import json
from modules.skills import get_user_skills_dict

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_career_paths():
    """Get all available career paths"""
    conn = get_db_connection()
    career_paths = conn.execute('SELECT * FROM career_paths').fetchall()
    conn.close()
    return career_paths

def get_career_path_by_id(path_id):
    """Get a specific career path by ID"""
    conn = get_db_connection()
    career_path = conn.execute('SELECT * FROM career_paths WHERE id = ?', (path_id,)).fetchone()
    conn.close()
    return career_path

def get_user_career_interests(user_id):
    """Get career paths a user is interested in"""
    conn = get_db_connection()
    interests = conn.execute('''
        SELECT cp.*, uci.interest_level 
        FROM career_paths cp
        JOIN user_career_interests uci ON cp.id = uci.career_path_id
        WHERE uci.user_id = ?
        ORDER BY uci.interest_level DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return interests

def set_user_career_interest(user_id, career_path_id, interest_level):
    """Set or update a user's interest in a career path"""
    conn = get_db_connection()
    
    # Check if interest already exists
    existing = conn.execute('''
        SELECT id FROM user_career_interests 
        WHERE user_id = ? AND career_path_id = ?
    ''', (user_id, career_path_id)).fetchone()
    
    if existing:
        # Update existing interest
        conn.execute('''
            UPDATE user_career_interests 
            SET interest_level = ? 
            WHERE user_id = ? AND career_path_id = ?
        ''', (interest_level, user_id, career_path_id))
    else:
        # Create new interest
        conn.execute('''
            INSERT INTO user_career_interests (user_id, career_path_id, interest_level)
            VALUES (?, ?, ?)
        ''', (user_id, career_path_id, interest_level))
    
    conn.commit()
    conn.close()
    return True

def get_recommended_career_paths(user_id, limit=5):
    """Generate career path recommendations based on user skills"""
    conn = get_db_connection()
    
    # Get user skills
    user_skills = get_user_skills_dict(user_id)
    
    # Get all career paths
    career_paths = conn.execute('SELECT * FROM career_paths').fetchall()
    
    # Calculate match score for each career path
    recommended_paths = []
    
    for path in career_paths:
        required_skills = json.loads(path['required_skills'])
        match_score = 0
        total_skills = len(required_skills)
        
        for skill, required_level in required_skills.items():
            if skill in user_skills:
                user_level = int(user_skills[skill])
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
    
    return recommended_paths[:limit]

def get_learning_resources_for_career(career_path_id):
    """Get learning resources for a specific career path"""
    conn = get_db_connection()
    
    # Get career path details
    career_path = conn.execute('SELECT * FROM career_paths WHERE id = ?', (career_path_id,)).fetchone()
    
    if not career_path:
        conn.close()
        return []
    
    # Get learning resources from the career path
    resources = json.loads(career_path['learning_resources'])
    
    conn.close()
    
    return resources

def get_career_roadmap(career_path_id):
    """Get a roadmap for the given career path with progression stages"""
    conn = get_db_connection()
    
    # Get career path details
    career_path = conn.execute('SELECT * FROM career_paths WHERE id = ?', (career_path_id,)).fetchone()
    
    if not career_path:
        conn.close()
        return None
    
    # Create a roadmap with progression stages
    # This would be more dynamic in a real application, but for the hackathon we'll create a static structure
    roadmap = {
        'title': career_path['title'],
        'stages': [
            {
                'name': 'Entry Level (0-2 years)',
                'description': 'Focus on building fundamental skills through internships and entry-level positions.',
                'key_skills': [],
                'goals': [
                    'Master fundamental technical skills',
                    'Gain real-world project experience',
                    'Build professional network',
                    'Contribute to team projects'
                ]
            },
            {
                'name': 'Mid-Level (2-5 years)',
                'description': 'Take on more responsibility and specialize in specific areas of expertise.',
                'key_skills': [],
                'goals': [
                    'Develop specialized knowledge',
                    'Lead small to medium projects',
                    'Mentor junior team members',
                    'Contribute to technical decisions'
                ]
            },
            {
                'name': 'Senior Level (5+ years)',
                'description': 'Lead projects, mentor junior team members, and influence strategic decisions.',
                'key_skills': [],
                'goals': [
                    'Lead complex projects and initiatives',
                    'Make high-level architectural decisions',
                    'Mentor and develop team members',
                    'Contribute to organizational strategy'
                ]
            }
        ]
    }
    
    # Add some skills for each stage based on the required skills
    required_skills = json.loads(career_path['required_skills'])
    skill_items = list(required_skills.items())
    
    # Distribute skills across stages
    for i, (skill, level) in enumerate(skill_items):
        stage_index = min(i % 3, 2)  # Distribute across 3 stages
        roadmap['stages'][stage_index]['key_skills'].append(skill)
    
    conn.close()
    
    return roadmap

def get_career_job_outlook(career_path_id):
    """Get job outlook information for a specific career path"""
    conn = get_db_connection()
    
    # Get career path details
    career_path = conn.execute('SELECT * FROM career_paths WHERE id = ?', (career_path_id,)).fetchone()
    
    if not career_path:
        conn.close()
        return None
    
    # Get job counts for this career
    job_count = conn.execute('''
        SELECT COUNT(*) as count FROM job_listings
        WHERE job_title LIKE ?
    ''', (f'%{career_path["title"]}%',)).fetchone()['count']
    
    # Create job outlook object
    outlook = {
        'title': career_path['title'],
        'job_count': job_count,
        'average_salary': career_path['average_salary'],
        'growth_potential': career_path['growth_potential'],
        'top_hiring_companies': [
            'Microsoft', 'Google', 'Amazon', 'TCS', 'Infosys', 'Wipro'
        ],
        'industry_trends': [
            'Growing demand across startups and established companies',
            'Increasing adoption of remote work options',
            'Rising emphasis on specialized skills and certifications',
            'Integration with emerging technologies like AI and blockchain'
        ]
    }
    
    conn.close()
    
    return outlook