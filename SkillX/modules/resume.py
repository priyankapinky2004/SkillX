"""
Resume Module - Handles resume analysis and feedback functionality
"""
import sqlite3
import os
import random
from werkzeug.utils import secure_filename

# For a real application, you would use NLP libraries for resume parsing
# such as spacy, nltk, or resume-parser
# For the hackathon demo, we'll simulate the analysis

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume(user_id, file):
    """Save a user's resume file"""
    if not file or not allowed_file(file.filename):
        return False, "Invalid file format. Please upload a PDF or Word document."
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create user uploads directory if it doesn't exist
    upload_dir = os.path.join('static', 'uploads', 'resumes', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # Update user record with resume file path
    conn = get_db_connection()
    conn.execute('UPDATE users SET resume_file = ? WHERE id = ?', (file_path, user_id))
    conn.commit()
    conn.close()
    
    return True, file_path

def analyze_resume(file_path):
    """Analyze a resume and provide feedback"""
    # In a real application, this would use NLP to parse and analyze the resume
    # For the hackathon, we'll simulate the analysis with random scores and feedback
    
    # Generate a random score for each section (for demo purposes)
    content_score = random.randint(60, 95)
    format_score = random.randint(65, 95)
    ats_score = random.randint(70, 95)
    overall_score = (content_score + format_score + ats_score) // 3
    
    # Generate feedback based on scores
    strengths = []
    improvements = []
    
    # Content feedback
    if content_score >= 85:
        strengths.append("Strong use of action verbs and quantifiable achievements")
    elif content_score >= 70:
        strengths.append("Good job descriptions with relevant details")
    else:
        improvements.append("Add more quantifiable achievements to showcase your impact")
    
    # Format feedback
    if format_score >= 85:
        strengths.append("Clean, professional formatting that's easy to read")
    elif format_score >= 70:
        strengths.append("Appropriate length and section organization")
    else:
        improvements.append("Improve layout consistency and readability")
    
    # ATS feedback
    if ats_score >= 85:
        strengths.append("Excellent keyword optimization for ATS systems")
    elif ats_score >= 70:
        strengths.append("Good use of industry-specific terminology")
    else:
        improvements.append("Include more relevant keywords from the job descriptions you're targeting")
    
    # Additional feedback points (always included for the demo)
    improvements.append("Customize your resume for specific job roles")
    
    if len(strengths) < 3:
        strengths.append("Clear and concise presentation of information")
    
    # ATS Compatibility rating
    if ats_score >= 90:
        ats_compatibility = "Excellent"
    elif ats_score >= 80:
        ats_compatibility = "Good"
    elif ats_score >= 70:
        ats_compatibility = "Medium"
    else:
        ats_compatibility = "Poor"
    
    # Generate the feedback object
    feedback = {
        'overall_score': overall_score,
        'content_score': content_score,
        'format_score': format_score,
        'ats_score': ats_score,
        'strengths': strengths,
        'improvements': improvements,
        'ats_compatibility': ats_compatibility
    }
    
    return feedback

def save_resume_feedback(user_id, feedback):
    """Save resume feedback to the database"""
    conn = get_db_connection()
    
    # Convert feedback to string format for storage
    import json
    feedback_json = json.dumps(feedback)
    
    # Check if feedback already exists
    existing = conn.execute('SELECT id FROM resume_feedback WHERE user_id = ?', (user_id,)).fetchone()
    
    if existing:
        # Update existing feedback
        conn.execute('''
            UPDATE resume_feedback 
            SET feedback = ?, updated_at = datetime('now')
            WHERE user_id = ?
        ''', (feedback_json, user_id))
    else:
        # Insert new feedback
        conn.execute('''
            INSERT INTO resume_feedback (user_id, feedback, created_at, updated_at)
            VALUES (?, ?, datetime('now'), datetime('now'))
        ''', (user_id, feedback_json))
    
    conn.commit()
    conn.close()
    
    return True

def get_resume_feedback(user_id):
    """Get saved resume feedback for a user"""
    conn = get_db_connection()
    
    feedback_row = conn.execute('SELECT feedback FROM resume_feedback WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    if feedback_row:
        import json
        return json.loads(feedback_row['feedback'])
    
    return None

def get_resume_tips():
    """Get general resume writing tips"""
    tips = [
        {
            "category": "Content",
            "tips": [
                "Use action verbs to start bullet points (e.g., 'Developed', 'Implemented', 'Led')",
                "Include quantifiable achievements (e.g., 'Increased sales by 25%')",
                "Customize your resume for each job application",
                "Focus on relevant experience and skills for the position",
                "Keep it concise and focused on your most impressive achievements"
            ]
        },
        {
            "category": "Format",
            "tips": [
                "Use a clean, professional template with consistent formatting",
                "Ensure your resume is easy to scan (use bullet points, headings, and white space)",
                "Keep your resume to 1-2 pages maximum",
                "Use a professional, readable font (e.g., Arial, Calibri, or Times New Roman)",
                "Save and send your resume as a PDF to preserve formatting"
            ]
        },
        {
            "category": "ATS Optimization",
            "tips": [
                "Include keywords from the job description",
                "Use standard section headings (e.g., 'Experience', 'Education', 'Skills')",
                "Avoid using tables, headers/footers, or text boxes",
                "Don't put important information in images",
                "Use a simple, straightforward layout without complex design elements"
            ]
        }
    ]
    
    return tips

def get_resume_templates():
    """Get resume templates for different career paths"""
    templates = [
        {
            "name": "Software Engineer Template",
            "description": "Highlights technical skills, projects, and coding experience",
            "file_path": "static/templates/software_engineer_template.docx",
            "preview_image": "static/img/resume_templates/software_engineer.png"
        },
        {
            "name": "Data Scientist Template",
            "description": "Emphasizes analytical skills, research experience, and data projects",
            "file_path": "static/templates/data_scientist_template.docx",
            "preview_image": "static/img/resume_templates/data_scientist.png"
        },
        {
            "name": "UI/UX Designer Template",
            "description": "Showcases design projects, user research experience, and creative skills",
            "file_path": "static/templates/uiux_designer_template.docx",
            "preview_image": "static/img/resume_templates/uiux_designer.png"
        },
        {
            "name": "Fresh Graduate Template",
            "description": "Perfect for recent graduates with limited work experience but relevant projects and education",
            "file_path": "static/templates/fresh_graduate_template.docx",
            "preview_image": "static/img/resume_templates/fresh_graduate.png"
        }
    ]
    
    return templates