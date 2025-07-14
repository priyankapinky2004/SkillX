"""
Jobs Module - Handles job listings and job market trends
"""
import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_job_listings(limit=50, offset=0):
    """Get all job listings with pagination"""
    conn = get_db_connection()
    jobs = conn.execute('''
        SELECT * FROM job_listings
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset)).fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    """Get a specific job by ID"""
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM job_listings WHERE id = ?', (job_id,)).fetchone()
    
    if job:
        # Get job skills
        skills = conn.execute('''
            SELECT skill_name FROM job_skills
            WHERE job_id = ?
        ''', (job_id,)).fetchall()
        
        job_dict = dict(job)
        job_dict['skills'] = [skill['skill_name'] for skill in skills]
    else:
        job_dict = None
    
    conn.close()
    return job_dict

def search_jobs(query=None, location=None, job_type=None, experience_level=None, limit=20):
    """Search for jobs based on various criteria"""
    conn = get_db_connection()
    
    # Build the query
    sql_query = 'SELECT * FROM job_listings WHERE 1=1'
    params = []
    
    if query:
        sql_query += ' AND (job_title LIKE ? OR company_name LIKE ? OR description LIKE ?)'
        query_param = f'%{query}%'
        params.extend([query_param, query_param, query_param])
    
    if location:
        sql_query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    if job_type:
        sql_query += ' AND job_type = ?'
        params.append(job_type)
    
    if experience_level:
        sql_query += ' AND experience_level = ?'
        params.append(experience_level)
    
    sql_query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    # Execute the query
    jobs = conn.execute(sql_query, params).fetchall()
    conn.close()
    
    return jobs

def filter_jobs_by_skill(skill, limit=20):
    """Get jobs that require a specific skill"""
    conn = get_db_connection()
    
    jobs = conn.execute('''
        SELECT jl.* FROM job_listings jl
        JOIN job_skills js ON jl.id = js.job_id
        WHERE js.skill_name LIKE ?
        GROUP BY jl.id
        ORDER BY jl.created_at DESC
        LIMIT ?
    ''', (f'%{skill}%', limit)).fetchall()
    
    conn.close()
    return jobs

def get_trending_job_roles(limit=10):
    """Get trending job roles based on count of job listings"""
    conn = get_db_connection()
    
    trending_roles = conn.execute('''
        SELECT job_title, COUNT(*) as job_count
        FROM job_listings
        GROUP BY job_title
        ORDER BY job_count DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    
    conn.close()
    return trending_roles

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

def get_job_salary_trends():
    """Get salary trends for different job roles"""
    conn = get_db_connection()
    
    # Get distinct job titles
    job_titles = conn.execute('''
        SELECT DISTINCT job_title 
        FROM job_listings
        WHERE job_title IN (
            'Software Engineer', 'Data Scientist', 'Full Stack Developer',
            'UI/UX Designer', 'DevOps Engineer', 'Product Manager'
        )
    ''').fetchall()
    
    salary_trends = []
    
    for job in job_titles:
        title = job['job_title']
        
        # Get entry level salary
        entry_level = conn.execute('''
            SELECT salary_range
            FROM job_listings
            WHERE job_title = ? AND experience_level = 'Entry Level'
            LIMIT 1
        ''', (title,)).fetchone()
        
        # Get mid level salary
        mid_level = conn.execute('''
            SELECT salary_range
            FROM job_listings
            WHERE job_title = ? AND (experience_level = '1-3 years' OR experience_level = '3-5 years')
            LIMIT 1
        ''', (title,)).fetchone()
        
        # Get senior level salary
        senior_level = conn.execute('''
            SELECT salary_range
            FROM job_listings
            WHERE job_title = ? AND (experience_level = '5-8 years' OR experience_level = '8+ years')
            LIMIT 1
        ''', (title,)).fetchone()
        
        salary_trends.append({
            'role': title,
            'entry_level': entry_level['salary_range'] if entry_level else '₹3-5 LPA',
            'mid_level': mid_level['salary_range'] if mid_level else '₹6-10 LPA',
            'senior_level': senior_level['salary_range'] if senior_level else '₹12-25 LPA'
        })
    
    conn.close()
    return salary_trends

def get_location_wise_jobs():
    """Get job distribution by location"""
    conn = get_db_connection()
    
    location_data = conn.execute('''
        SELECT location, COUNT(*) as job_count
        FROM job_listings
        GROUP BY location
        ORDER BY job_count DESC
    ''').fetchall()
    
    conn.close()
    
    return location_data

def get_job_type_distribution():
    """Get distribution of job types (full-time, part-time, etc.)"""
    conn = get_db_connection()
    
    distribution = conn.execute('''
        SELECT job_type, COUNT(*) as job_count
        FROM job_listings
        GROUP BY job_type
        ORDER BY job_count DESC
    ''').fetchall()
    
    conn.close()
    
    return distribution

def get_remote_work_trends():
    """Get trends related to remote work opportunities"""
    conn = get_db_connection()
    
    # Count remote jobs
    remote_count = conn.execute('''
        SELECT COUNT(*) as count FROM job_listings
        WHERE location LIKE '%Remote%' OR job_type LIKE '%Remote%'
    ''').fetchone()['count']
    
    # Count all jobs
    total_count = conn.execute('SELECT COUNT(*) as count FROM job_listings').fetchone()['count']
    
    # Calculate percentage
    remote_percentage = (remote_count / total_count * 100) if total_count > 0 else 0
    
    # Get top remote-friendly roles
    remote_roles = conn.execute('''
        SELECT job_title, COUNT(*) as job_count
        FROM job_listings
        WHERE location LIKE '%Remote%' OR job_type LIKE '%Remote%'
        GROUP BY job_title
        ORDER BY job_count DESC
        LIMIT 5
    ''').fetchall()
    
    # Calculate hybrid and onsite percentages (simplified for hackathon)
    hybrid_percentage = 45
    onsite_percentage = 100 - remote_percentage - hybrid_percentage
    
    trends = {
        'remote_percentage': round(remote_percentage),
        'hybrid_percentage': hybrid_percentage,
        'onsite_percentage': round(onsite_percentage),
        'top_remote_roles': [dict(role) for role in remote_roles]
    }
    
    conn.close()
    
    return trends

def get_recommended_jobs_for_user(user_id, limit=5):
    """Get job recommendations for a specific user based on their skills"""
    conn = get_db_connection()
    
    # Get user skills
    user_skills = conn.execute('''
        SELECT skill_name FROM user_skills
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    
    user_skill_names = [skill['skill_name'] for skill in user_skills]
    
    # If user has no skills, return recent jobs
    if not user_skill_names:
        jobs = conn.execute('''
            SELECT * FROM job_listings
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        return [dict(job) for job in jobs]
    
    # Get jobs with matching skills
    # This is a simple implementation for the hackathon
    # A real recommendation engine would be more sophisticated
    jobs = conn.execute('''
        SELECT jl.*, COUNT(js.skill_name) as skill_match_count
        FROM job_listings jl
        JOIN job_skills js ON jl.id = js.job_id
        WHERE js.skill_name IN ({})
        GROUP BY jl.id
        ORDER BY skill_match_count DESC, jl.created_at DESC
        LIMIT ?
    '''.format(','.join(['?'] * len(user_skill_names))), 
    (*user_skill_names, limit)).fetchall()
    
    conn.close()
    
    return [dict(job) for job in jobs]