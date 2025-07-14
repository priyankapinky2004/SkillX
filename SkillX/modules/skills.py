"""
Skills Module - Handles skill-related operations
"""
import sqlite3
import json

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_skill_categories():
    """Get all skill categories"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM skill_categories').fetchall()
    conn.close()
    return categories

def get_skills_by_category(category_id):
    """Get skills for a specific category"""
    conn = get_db_connection()
    skills = conn.execute('''
        SELECT * FROM skills 
        WHERE category_id = ?
        ORDER BY name
    ''', (category_id,)).fetchall()
    conn.close()
    return skills

def get_user_skills(user_id):
    """Get skills for a specific user"""
    conn = get_db_connection()
    skills = conn.execute('''
        SELECT * FROM user_skills 
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return skills

def get_user_skills_dict(user_id):
    """Get user skills as dictionary with skill_name as key and level as value"""
    conn = get_db_connection()
    skills = conn.execute('''
        SELECT skill_name, proficiency_level FROM user_skills 
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    
    skills_dict = {skill['skill_name']: skill['proficiency_level'] for skill in skills}
    return skills_dict

def update_user_skills(user_id, skills_data):
    """Update user skills from form data"""
    conn = get_db_connection()
    
    # Clear existing skills
    conn.execute('DELETE FROM user_skills WHERE user_id = ?', (user_id,))
    
    # Add new skills
    for skill_key, level in skills_data.items():
        if skill_key.startswith('skill_') and level:
            # Extract skill name from the form key
            skill_name = skill_key.replace('skill_', '').replace('_', ' ')
            
            # Skip if no proficiency level was selected
            if not level or int(level) == 0:
                continue
                
            conn.execute('''
                INSERT INTO user_skills (user_id, skill_name, proficiency_level) 
                VALUES (?, ?, ?)
            ''', (user_id, skill_name, level))
    
    conn.commit()
    conn.close()
    return True

def get_trending_skills(limit=10):
    """Get trending skills based on job listings"""
    conn = get_db_connection()
    trending_skills = conn.execute('''
        SELECT skill_name, COUNT(*) as job_count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY job_count DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return trending_skills

def get_skill_gap_analysis(user_id, career_path_id=None):
    """Analyze skill gaps for a user compared to their target career path"""
    conn = get_db_connection()
    
    # Get user's skills
    user_skills = get_user_skills_dict(user_id)
    
    # Get required skills for career path
    if career_path_id:
        career_path = conn.execute('SELECT required_skills FROM career_paths WHERE id = ?', 
                                  (career_path_id,)).fetchone()
        if career_path:
            required_skills = json.loads(career_path['required_skills'])
        else:
            required_skills = {}
    else:
        # Get recommended career path if none specified
        career_path = conn.execute('''
            SELECT cp.* FROM career_paths cp
            JOIN user_career_interests uci ON cp.id = uci.career_path_id
            WHERE uci.user_id = ?
            ORDER BY uci.interest_level DESC
            LIMIT 1
        ''', (user_id,)).fetchone()
        
        if career_path:
            required_skills = json.loads(career_path['required_skills'])
        else:
            # Default to popular skills if no clear career path
            required_skills = {
                'Python': 4,
                'JavaScript': 3,
                'HTML/CSS': 3,
                'SQL': 3,
                'Communication': 4,
                'Problem Solving': 4
            }
    
    # Identify strengths and gaps
    strengths = []
    gaps = []
    
    for skill, required_level in required_skills.items():
        user_level = user_skills.get(skill, 0)
        
        if user_level >= required_level:
            strengths.append({
                'name': skill,
                'user_level': user_level,
                'required_level': required_level
            })
        else:
            gaps.append({
                'name': skill,
                'user_level': user_level,
                'required_level': required_level,
                'gap': required_level - user_level
            })
    
    # Sort gaps by largest gap first
    gaps.sort(key=lambda x: x['gap'], reverse=True)
    
    conn.close()
    
    return {
        'strengths': strengths,
        'gaps': gaps
    }

def get_learning_resources_for_skills(skill_names, limit=3):
    """Get learning resources for given skills"""
    conn = get_db_connection()
    
    resources = []
    
    for skill in skill_names:
        skill_resources = conn.execute('''
            SELECT * FROM learning_resources
            WHERE skill_id IN (
                SELECT id FROM skill_categories
                WHERE name LIKE ?
            )
            ORDER BY rating DESC
            LIMIT ?
        ''', (f'%{skill}%', limit)).fetchall()
        
        resources.extend([dict(r) for r in skill_resources])
    
    conn.close()
    
    return resources