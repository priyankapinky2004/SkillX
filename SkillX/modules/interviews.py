"""
Interviews Module - Handles mock interview functionality
"""
import sqlite3
from datetime import datetime
import random

def get_db_connection():
    conn = sqlite3.connect('skillx.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_interview_categories():
    """Get all available interview categories"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM interview_categories').fetchall()
    conn.close()
    return categories

def get_category_by_id(category_id):
    """Get interview category by ID"""
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM interview_categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()
    return category

def get_interview_questions(category_id, count=10, difficulty=None):
    """Get interview questions for a specific category"""
    conn = get_db_connection()
    
    query = 'SELECT * FROM interview_questions WHERE category_id = ?'
    params = [category_id]
    
    if difficulty:
        query += ' AND difficulty_level = ?'
        params.append(difficulty)
    
    query += ' ORDER BY RANDOM() LIMIT ?'
    params.append(count)
    
    questions = conn.execute(query, params).fetchall()
    conn.close()
    
    return questions

def get_question_by_id(question_id):
    """Get a specific interview question by ID"""
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM interview_questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()
    return question

def get_user_interview_history(user_id, limit=5):
    """Get a user's interview history"""
    conn = get_db_connection()
    
    history = conn.execute('''
        SELECT mi.*, ic.name as category_name 
        FROM mock_interviews mi
        JOIN interview_categories ic ON mi.category_id = ic.id
        WHERE mi.user_id = ?
        ORDER BY mi.created_at DESC
        LIMIT ?
    ''', (user_id, limit)).fetchall()
    
    conn.close()
    return history

def start_mock_interview(user_id, category_id):
    """Start a new mock interview session"""
    # Get questions for this category
    questions = get_interview_questions(category_id)
    
    # Create a new interview record
    conn = get_db_connection()
    
    cursor = conn.execute('''
        INSERT INTO mock_interviews (user_id, category_id, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, category_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        'interview_id': interview_id,
        'questions': [dict(q) for q in questions]
    }

def save_interview_results(interview_id, answers, score):
    """Save the results of a completed mock interview"""
    conn = get_db_connection()
    
    # Generate feedback based on score
    if score >= 80:
        feedback = "Excellent performance! You demonstrated strong knowledge and communication skills."
    elif score >= 60:
        feedback = "Good performance with some areas for improvement. Review the questions you struggled with."
    else:
        feedback = "You need more practice. Focus on understanding the core concepts and improving your responses."
    
    # Update the interview record
    conn.execute('''
        UPDATE mock_interviews
        SET score = ?, feedback = ?
        WHERE id = ?
    ''', (score, feedback, interview_id))
    
    conn.commit()
    conn.close()
    
    return True

def get_interview_results(interview_id):
    """Get the results of a completed mock interview"""
    conn = get_db_connection()
    
    # Get interview data
    interview = conn.execute('''
        SELECT mi.*, ic.name as category_name 
        FROM mock_interviews mi
        JOIN interview_categories ic ON mi.category_id = ic.id
        WHERE mi.id = ?
    ''', (interview_id,)).fetchone()
    
    conn.close()
    
    if not interview:
        return None
    
    return dict(interview)

def get_interview_tips(category_id=None):
    """Get interview tips for a specific category"""
    general_tips = [
        "Research the company thoroughly before the interview.",
        "Prepare concise examples that highlight your skills and experiences.",
        "Practice the STAR method (Situation, Task, Action, Result) for behavioral questions.",
        "Prepare thoughtful questions to ask the interviewer.",
        "Follow up with a thank-you email after the interview."
    ]
    
    if not category_id:
        return general_tips
    
    # Category-specific tips
    category_tips = {
        1: [  # Technical Interviews
            "Review core computer science concepts like data structures and algorithms.",
            "Practice coding problems on platforms like LeetCode or HackerRank.",
            "Be prepared to explain your thought process while solving problems.",
            "Know the technologies listed in the job description inside out.",
            "Be familiar with system design concepts for senior roles."
        ],
        2: [  # HR Interviews
            "Prepare a clear and concise introduction about yourself.",
            "Reflect on your career goals and how they align with the position.",
            "Be ready to discuss your strengths, weaknesses, and areas for growth.",
            "Prepare examples of how you've handled challenges or conflicts.",
            "Research the company culture and values."
        ],
        3: [  # Design Interviews
            "Prepare your portfolio and be ready to explain your design process.",
            "Practice explaining design decisions and the rationale behind them.",
            "Be prepared to give and receive design feedback.",
            "Know user research methodologies and how to apply them.",
            "Understand design principles and how they impact user experience."
        ],
        4: [  # Data Science Interviews
            "Be prepared to explain complex statistical concepts in simple terms.",
            "Practice solving data-related case studies and scenarios.",
            "Know how to evaluate model performance and explain tradeoffs.",
            "Be familiar with data cleaning and preprocessing techniques.",
            "Prepare to discuss projects where you've applied data science."
        ],
        5: [  # Product Management
            "Be prepared to discuss product strategy and roadmap planning.",
            "Practice explaining how you prioritize features and make decisions.",
            "Know how to analyze metrics and use data to drive product decisions.",
            "Prepare examples of how you've worked with cross-functional teams.",
            "Be ready to discuss your approach to user research and feedback."
        ]
    }
    
    return category_tips.get(category_id, general_tips)

def evaluate_answer(question_id, answer):
    """Evaluate an interview answer (simplified version for hackathon)"""
    # In a real application, this would use NLP/AI to evaluate the answer
    # For the hackathon, we'll use a simple keyword matching approach
    
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM interview_questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()
    
    if not question:
        return {
            'score': 0,
            'feedback': "Question not found"
        }
    
    # Extract keywords from the sample answer
    sample_answer = question['sample_answer'].lower()
    key_phrases = [phrase.strip() for phrase in sample_answer.split('.') if phrase.strip()]
    
    # Check if the answer contains key phrases or similar content
    answer_lower = answer.lower()
    matched_phrases = 0
    
    for phrase in key_phrases:
        # Simple check if any key words from the phrase appear in the answer
        words = [word for word in phrase.split() if len(word) > 3]  # Only check significant words
        if any(word in answer_lower for word in words):
            matched_phrases += 1
    
    # Calculate score based on matched phrases
    if key_phrases:
        match_ratio = matched_phrases / len(key_phrases)
        score = int(match_ratio * 100)
    else:
        score = 50  # Default score
    
    # Add some randomness for demo purposes
    score = min(100, max(0, score + random.randint(-10, 10)))
    
    # Generate feedback
    if score >= 80:
        feedback = "Excellent answer! You covered the key points comprehensively."
    elif score >= 60:
        feedback = "Good answer with some important points covered. Consider also mentioning: " + random.choice(key_phrases)
    else:
        feedback = "Your answer could be improved. Make sure to address: " + random.choice(key_phrases)
    
    return {
        'score': score,
        'feedback': feedback
    }