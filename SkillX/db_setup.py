import sqlite3
import json
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# Database configuration
DB_PATH = 'skillx.db'

def init_db():
    """Initialize the database with tables and sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        college TEXT,
        year_of_study TEXT,
        bio TEXT,
        profile_pic TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Skill categories
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # User skills
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        skill_name TEXT NOT NULL,
        proficiency_level INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Career paths
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS career_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        required_skills TEXT,  -- JSON string of skill:level pairs
        learning_resources TEXT, -- JSON array of resources
        average_salary TEXT,
        growth_potential TEXT
    )
    ''')
    
    # User career interests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_career_interests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        career_path_id INTEGER,
        interest_level INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (career_path_id) REFERENCES career_paths (id)
    )
    ''')
    
    # Job listings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        job_title TEXT NOT NULL,
        description TEXT,
        location TEXT,
        salary_range TEXT,
        experience_level TEXT,
        job_type TEXT,
        url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Job skills
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        skill_name TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES job_listings (id)
    )
    ''')
    
    # Interview categories
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # Interview questions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        question TEXT NOT NULL,
        sample_answer TEXT,
        difficulty_level INTEGER DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES interview_categories (id)
    )
    ''')
    
    # Mock interviews
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mock_interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category_id INTEGER,
        score INTEGER,
        feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (category_id) REFERENCES interview_categories (id)
    )
    ''')
    
    # Learning resources
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learning_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        resource_type TEXT,
        url TEXT,
        description TEXT,
        rating FLOAT DEFAULT 0.0,
        skill_id INTEGER,
        FOREIGN KEY (skill_id) REFERENCES skill_categories (id)
    )
    ''')
    
    # Check if we need to insert sample data
    user_count = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count == 0:
        print("Inserting sample data...")
        insert_sample_data(conn, cursor)
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

def insert_sample_data(conn, cursor):
    """Insert sample data into the database"""
    
    # Insert skill categories
    skill_categories = [
        ('Programming', 'Coding and development skills'),
        ('Design', 'Visual design skills'),
        ('Data Science', 'Data analysis and machine learning'),
        ('Soft Skills', 'Communication and collaboration'),
        ('Business', 'Business and entrepreneurship skills'),
        ('Marketing', 'Digital and traditional marketing')
    ]
    
    cursor.executemany('INSERT INTO skill_categories (name, description) VALUES (?, ?)', skill_categories)
    
    # Insert interview categories
    interview_categories = [
        ('Technical Interviews', 'Coding, problem-solving, and technical questions'),
        ('HR Interviews', 'Behavioral and personality questions'),
        ('Design Interviews', 'UI/UX and design thinking questions'),
        ('Data Science Interviews', 'Statistics, ML, and data manipulation questions'),
        ('Product Management', 'Product strategy and execution questions')
    ]
    
    cursor.executemany('INSERT INTO interview_categories (name, description) VALUES (?, ?)', interview_categories)
    
    # Insert sample career paths
    career_paths = [
        ('Full Stack Developer', 
         'Develop both frontend and backend components of web applications.', 
         json.dumps({'JavaScript': 4, 'HTML/CSS': 3, 'Python': 3, 'SQL': 3, 'React': 3}),
         json.dumps([
             {'title': 'The Web Developer Bootcamp', 'url': 'https://www.udemy.com/course/the-web-developer-bootcamp/'},
             {'title': 'Full Stack Open', 'url': 'https://fullstackopen.com/en/'},
             {'title': 'The Odin Project', 'url': 'https://www.theodinproject.com/'}
         ]),
         '₹6,00,000 - ₹15,00,000',
         'High growth in startups and established companies'
        ),
        ('Data Scientist', 
         'Analyze and interpret complex data to help organizations make better decisions.', 
         json.dumps({'Python': 4, 'Statistics': 4, 'Machine Learning': 3, 'SQL': 3, 'Data Visualization': 3}),
         json.dumps([
             {'title': 'Data Science A-Z', 'url': 'https://www.udemy.com/course/datascience/'},
             {'title': 'IBM Data Science Professional Certificate', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science'},
             {'title': 'DataCamp', 'url': 'https://www.datacamp.com/'}
         ]),
         '₹8,00,000 - ₹20,00,000',
         'High demand across industries'
        ),
        ('UI/UX Designer', 
         'Design user interfaces and experiences for digital products.', 
         json.dumps({'Figma': 4, 'User Research': 3, 'Visual Design': 4, 'Prototyping': 3, 'HTML/CSS': 2}),
         json.dumps([
             {'title': 'Google UX Design Professional Certificate', 'url': 'https://www.coursera.org/professional-certificates/google-ux-design'},
             {'title': 'UI/UX Design Specialization', 'url': 'https://www.coursera.org/specializations/ui-ux-design'},
             {'title': 'Interaction Design Foundation', 'url': 'https://www.interaction-design.org/'}
         ]),
         '₹5,00,000 - ₹15,00,000',
         'Growing demand in product companies'
        ),
        ('DevOps Engineer', 
         'Implement and manage continuous integration and delivery pipelines.', 
         json.dumps({'Linux': 4, 'Docker': 4, 'Cloud Services': 3, 'Git': 3, 'Jenkins': 3}),
         json.dumps([
             {'title': 'DevOps Engineering Course', 'url': 'https://www.udemy.com/course/devops-engineering-on-aws/'},
             {'title': 'Docker and Kubernetes', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/'},
             {'title': 'AWS DevOps Engineer Professional', 'url': 'https://aws.amazon.com/certification/devops-engineer-professional/'}
         ]),
         '₹8,00,000 - ₹25,00,000',
         'High demand across tech companies'
        ),
        ('Product Manager', 
         'Oversee the development and strategy of digital products.', 
         json.dumps({'Product Strategy': 4, 'User Research': 3, 'Data Analysis': 3, 'Communication': 4, 'Technical Knowledge': 3}),
         json.dumps([
             {'title': 'Product Management Fundamentals', 'url': 'https://www.udemy.com/course/product-management-fundamentals/'},
             {'title': 'Become a Product Manager', 'url': 'https://www.udemy.com/course/become-a-product-manager-learn-the-skills-get-a-job/'},
             {'title': 'Product School', 'url': 'https://productschool.com/'}
         ]),
         '₹10,00,000 - ₹30,00,000',
         'Leadership role with high impact'
        )
    ]
    
    cursor.executemany('''
        INSERT INTO career_paths (title, description, required_skills, learning_resources, average_salary, growth_potential)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', career_paths)
    
    # Insert interview questions
    technical_questions = [
        (1, 'What is the difference between let, const, and var in JavaScript?', 'Let and const are block-scoped, while var is function-scoped. Const cannot be reassigned.', 2),
        (1, 'Explain the concept of closures in JavaScript.', 'A closure is the combination of a function and the lexical environment within which that function was declared.', 3),
        (1, 'What is the time complexity of quicksort in worst case?', 'O(n²) in the worst case when the pivot is always the smallest or largest element.', 3),
        (1, 'Explain the Box Model in CSS.', 'The CSS box model describes the rectangular boxes that are generated for elements in the document tree and laid out according to the visual formatting model.', 2),
        (1, 'What are the four main HTTP methods?', 'GET, POST, PUT, DELETE', 1)
    ]
    
    hr_questions = [
        (2, 'Tell me about yourself.', 'Focus on relevant professional experience, skills, and career goals.', 1),
        (2, 'Why do you want to work for our company?', 'Research the company and align your values and career goals with their mission.', 2),
        (2, 'Describe a time when you faced a challenge at work and how you overcame it.', 'Use the STAR method: Situation, Task, Action, Result.', 2),
        (2, 'Where do you see yourself in 5 years?', 'Show ambition while being realistic about career growth within the company.', 1),
        (2, 'What are your strengths and weaknesses?', 'Be honest about strengths with examples. For weaknesses, show self-awareness and improvement steps.', 2)
    ]
    
    design_questions = [
        (3, 'Walk me through your design process.', 'Explain research, ideation, prototyping, testing, and iteration phases.', 2),
        (3, 'How do you prioritize user needs in your designs?', 'Discuss user research methods, personas, and how you balance business goals with user needs.', 3),
        (3, 'Explain the difference between UX and UI design.', 'UX focuses on the user\'s journey and experience, while UI focuses on the visual and interactive elements.', 1),
        (3, 'How do you handle feedback on your designs?', 'Explain how you collect, evaluate, and incorporate feedback to improve designs.', 2),
        (3, 'Describe a project where you had to make design compromises.', 'Explain the constraints, your process, and how you found the best solution given limitations.', 3)
    ]
    
    ds_questions = [
        (4, 'Explain the difference between supervised and unsupervised learning.', 'Supervised learning uses labeled data for prediction, while unsupervised learning finds patterns in unlabeled data.', 2),
        (4, 'How would you handle missing data in a dataset?', 'Discuss methods like deletion, imputation with mean/median/mode, or advanced techniques like KNN or regression imputation.', 3),
        (4, 'Explain the bias-variance tradeoff.', 'The tradeoff between a model\'s ability to minimize bias and variance, which impacts its ability to generalize to new data.', 3),
        (4, 'What is the difference between correlation and causation?', 'Correlation indicates a relationship between variables, while causation indicates that one variable directly affects another.', 2),
        (4, 'How would you evaluate a classification model?', 'Discuss metrics like accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrix.', 3)
    ]
    
    product_questions = [
        (5, 'How do you prioritize features for a product?', 'Discuss frameworks like RICE (Reach, Impact, Confidence, Effort) or MoSCoW (Must have, Should have, Could have, Won\'t have).', 3),
        (5, 'How do you measure the success of a product?', 'Discuss KPIs like user growth, retention, engagement, revenue, and customer satisfaction.', 2),
        (5, 'Describe how you would launch a new feature.', 'Cover research, planning, development, testing, go-to-market strategy, and post-launch analysis.', 3),
        (5, 'How do you incorporate user feedback into product development?', 'Discuss methods to collect, analyze, and prioritize feedback and how to translate it into product decisions.', 2),
        (5, 'How would you explain technical concepts to non-technical stakeholders?', 'Focus on using simple language, analogies, visuals, and focusing on impact rather than implementation details.', 2)
    ]
    
    all_questions = technical_questions + hr_questions + design_questions + ds_questions + product_questions
    
    cursor.executemany('''
        INSERT INTO interview_questions (category_id, question, sample_answer, difficulty_level)
        VALUES (?, ?, ?, ?)
    ''', all_questions)
    
    # Insert sample job listings
    companies = ['TCS', 'Infosys', 'Wipro', 'HCL', 'Tech Mahindra', 'Cognizant', 'Accenture', 
                'Microsoft', 'Google', 'Amazon', 'Flipkart', 'Swiggy', 'Zomato', 'Paytm', 'Ola', 'Uber', 'Razorpay']
    
    job_titles = ['Software Engineer', 'Data Scientist', 'Product Manager', 'UI/UX Designer', 
                 'DevOps Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
                 'ML Engineer', 'Data Analyst', 'Business Analyst', 'QA Engineer', 'Android Developer',
                 'iOS Developer', 'Cloud Engineer']
    
    locations = ['Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Mumbai', 'Delhi NCR', 'Kolkata', 'Remote']
    
    experience_levels = ['Entry Level', '1-3 years', '3-5 years', '5-8 years', '8+ years']
    
    job_types = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Remote']
    
    salary_ranges = [
        '₹3-5 LPA', '₹5-8 LPA', '₹8-12 LPA', '₹12-18 LPA', '₹18-25 LPA', '₹25-40 LPA', '₹40+ LPA'
    ]
    
    # Generate some realistic job listings
    job_listings = []
    now = datetime.now()
    
    for i in range(50):  # Generate 50 job listings
        company = random.choice(companies)
        title = random.choice(job_titles)
        location = random.choice(locations)
        experience = random.choice(experience_levels)
        job_type = random.choice(job_types)
        salary = random.choice(salary_ranges)
        
        # Generate a random date within the last 30 days
        days_ago = random.randint(0, 30)
        post_date = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        description = f"We are looking for a {title} to join our team at {company}. This is a {job_type} position based in {location}."
        
        if 'Software' in title or 'Developer' in title:
            description += " The ideal candidate will have strong programming skills and experience with modern frameworks."
        elif 'Data' in title:
            description += " You should have strong analytical skills and experience with data processing tools."
        elif 'Product' in title:
            description += " You will work closely with engineering and design teams to define product strategy."
        elif 'Design' in title:
            description += " You should have a strong portfolio demonstrating UI/UX design skills."
        
        url = f"https://example.com/jobs/{company.lower().replace(' ', '-')}-{title.lower().replace(' ', '-')}"
        
        job_listings.append((company, title, description, location, salary, experience, job_type, url, post_date))
    
    cursor.executemany('''
        INSERT INTO job_listings (company_name, job_title, description, location, salary_range, 
                                 experience_level, job_type, url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', job_listings)
    
    # Add job skills
    programming_skills = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Ruby', 'PHP', 'Swift', 'Kotlin']
    frontend_skills = ['React', 'Angular', 'Vue.js', 'HTML/CSS', 'TypeScript', 'Redux', 'Webpack']
    backend_skills = ['Node.js', 'Django', 'Flask', 'Spring Boot', 'Express.js', 'Ruby on Rails', 'Laravel']
    data_skills = ['SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Hadoop', 'Spark']
    cloud_skills = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins']
    design_skills = ['Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'UI Design', 'UX Research']
    
    # Map job titles to relevant skill sets
    job_skills_map = {
        'Software Engineer': programming_skills + backend_skills + data_skills,
        'Frontend Developer': frontend_skills + ['JavaScript', 'HTML/CSS'],
        'Backend Developer': backend_skills + programming_skills + data_skills,
        'Full Stack Developer': frontend_skills + backend_skills + data_skills,
        'DevOps Engineer': cloud_skills + ['Linux', 'Bash', 'Python'],
        'Data Scientist': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'TensorFlow', 'PyTorch'],
        'ML Engineer': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Deep Learning'],
        'Data Analyst': ['SQL', 'Excel', 'Tableau', 'Power BI', 'Python', 'R'],
        'UI/UX Designer': design_skills,
        'Product Manager': ['Product Strategy', 'User Research', 'Agile', 'JIRA', 'Product Roadmapping'],
        'Business Analyst': ['SQL', 'Excel', 'Requirements Gathering', 'Process Modeling', 'Data Analysis'],
        'QA Engineer': ['Selenium', 'TestNG', 'JUnit', 'Cypress', 'Manual Testing', 'Automated Testing'],
        'Android Developer': ['Kotlin', 'Java', 'Android SDK', 'Firebase', 'RESTful APIs'],
        'iOS Developer': ['Swift', 'Objective-C', 'iOS SDK', 'Xcode', 'CoreData'],
        'Cloud Engineer': cloud_skills
    }
    
    job_skills = []
    
    # Get all job listings
    cursor.execute('SELECT id, job_title FROM job_listings')
    jobs = cursor.fetchall()
    
    for job_id, job_title in jobs:
        # Get relevant skills for this job title
        relevant_skills = job_skills_map.get(job_title, programming_skills)
        
        # Select 3-7 random skills for this job
        num_skills = random.randint(3, 7)
        selected_skills = random.sample(relevant_skills, min(num_skills, len(relevant_skills)))
        
        for skill in selected_skills:
            job_skills.append((job_id, skill))
    
    cursor.executemany('INSERT INTO job_skills (job_id, skill_name) VALUES (?, ?)', job_skills)
    
    # Insert sample user
    sample_user = ('Demo Student', 'demo@example.com', generate_password_hash('password'), 
                  'ABC Engineering College', '3rd Year', 'Computer Science student interested in web development and AI.',
                  None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    cursor.execute('''
        INSERT INTO users (name, email, password, college, year_of_study, bio, profile_pic, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_user)
    
    # Get the user id
    user_id = cursor.lastrowid
    
    # Add some skills for the sample user
    user_skills = [
        (user_id, 'Python', 3),
        (user_id, 'JavaScript', 2),
        (user_id, 'HTML/CSS', 4),
        (user_id, 'React', 1),
        (user_id, 'SQL', 2)
    ]
    
    cursor.executemany('INSERT INTO user_skills (user_id, skill_name, proficiency_level) VALUES (?, ?, ?)', user_skills)
    
    # Add career interests
    career_interests = [
        (user_id, 1, 5),  # Full Stack Developer - high interest
        (user_id, 2, 3),  # Data Scientist - medium interest
        (user_id, 3, 4)   # UI/UX Designer - high interest
    ]
    
    cursor.executemany('INSERT INTO user_career_interests (user_id, career_path_id, interest_level) VALUES (?, ?, ?)', career_interests)
    
    # Add learning resources
    learning_resources = [
        ('The Complete Web Developer in 2023', 'Course', 'https://www.udemy.com/course/the-complete-web-developer/', 
         'Comprehensive course covering HTML, CSS, JavaScript, Node.js, and more', 4.7, 1),
        ('Python for Everybody', 'Course', 'https://www.coursera.org/specializations/python', 
         'Learn Python programming and basic data analysis', 4.8, 1),
        ('React - The Complete Guide', 'Course', 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 
         'Dive into React, Redux, React Hooks, and more', 4.6, 1),
        ('SQL Basics for Beginners', 'Tutorial', 'https://www.w3schools.com/sql/', 
         'Learn fundamental SQL concepts and commands', 4.5, 1),
        ('Machine Learning A-Z', 'Course', 'https://www.udemy.com/course/machinelearning/', 
         'Learn to create Machine Learning Algorithms', 4.5, 2),
        ('Design Thinking Specialization', 'Course', 'https://www.coursera.org/specializations/design-thinking-innovation', 
         'Learn the design thinking process and apply it to real-world challenges', 4.6, 2)
    ]
    
    cursor.executemany('''
        INSERT INTO learning_resources (title, resource_type, url, description, rating, skill_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', learning_resources)
