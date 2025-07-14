"""
SkillX Configuration Settings
"""
import os
from datetime import datetime

# Application settings
APP_NAME = "SkillX"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Driven Career Path Navigator for Tier-2/Tier-3 College Students"

# Flask settings
SECRET_KEY = "skillx_hackathon_secret_key"  # In production, use a strong random key
DEBUG = True  # Set to False in production
TESTING = False

# Database settings
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skillx.db')

# File upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'}

# Session settings
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# Career categories
CAREER_CATEGORIES = [
    "Web Development",
    "Mobile Development",
    "Data Science",
    "DevOps",
    "UI/UX Design",
    "Cloud Computing",
    "Cybersecurity",
    "Machine Learning",
    "Product Management"
]

# Template context processors
def template_context_processors():
    """Global template context processors"""
    return {
        'app_name': APP_NAME,
        'app_version': APP_VERSION,
        'now': datetime.now(),
        'current_year': datetime.now().year,
        'career_categories': CAREER_CATEGORIES
    }

# Configure application
def configure_app(app):
    """Configure Flask application"""
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    app.config['TESTING'] = TESTING
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['DB_PATH'] = DB_PATH
    
    # Register context processors
    @app.context_processor
    def inject_context():
        return template_context_processors()
    
    # Create required directories
    create_required_directories()
    
    return app

def create_required_directories():
    """Create required directories if they don't exist"""
    # Create static directories
    os.makedirs(os.path.join('static', 'css'), exist_ok=True)
    os.makedirs(os.path.join('static', 'js'), exist_ok=True)
    os.makedirs(os.path.join('static', 'img'), exist_ok=True)
    
    # Create upload directories
    os.makedirs(os.path.join('static', 'uploads', 'resumes'), exist_ok=True)
    os.makedirs(os.path.join('static', 'uploads', 'profile_pics'), exist_ok=True)
    
    # Create templates directory if it doesn't exist (unlikely to be needed)
    os.makedirs('templates', exist_ok=True)

def allowed_file(filename, allowed_extensions=None):
    """Check if a file has an allowed extension"""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
        
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Create a default styles.css file if it doesn't exist
def create_default_css():
    """Create a default styles.css file if it doesn't exist"""
    css_path = os.path.join('static', 'css', 'styles.css')
    
    if not os.path.exists(css_path):
        default_css = """/* SkillX Custom Styles */

/* Global Styles */
:root {
    --primary-color: #4e73df;
    --secondary-color: #858796;
    --success-color: #1cc88a;
    --info-color: #36b9cc;
    --warning-color: #f6c23e;
    --danger-color: #e74a3b;
    --light-color: #f8f9fc;
    --dark-color: #5a5c69;
}

body {
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: #f8f9fc;
}

/* Custom Card Styling */
.card {
    border-radius: 0.5rem;
    transition: all 0.2s ease-in-out;
}

.card-header {
    border-top-left-radius: 0.5rem !important;
    border-top-right-radius: 0.5rem !important;
}

.card-body {
    border-bottom-left-radius: 0.5rem;
    border-bottom-right-radius: 0.5rem;
}

/* Button Styling */
.btn {
    border-radius: 0.375rem;
    font-weight: 600;
    transition: all 0.2s;
}

.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-primary:hover {
    background-color: #3a5fc9;
    border-color: #3a5fc9;
}

/* Navbar Styling */
.navbar-dark.bg-primary {
    background-color: var(--primary-color) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar-brand {
    font-weight: 700;
    font-size: 1.5rem;
}

.nav-link {
    font-weight: 600;
    padding: 0.6rem 1rem !important;
}

/* Footer Styling */
footer {
    background-color: #4e73df;
    color: white;
}

footer a {
    color: rgba(255,255,255,0.8);
    text-decoration: none;
}

footer a:hover {
    color: white;
    text-decoration: none;
}
"""
        
        with open(css_path, 'w') as f:
            f.write(default_css)
        
        print(f"Created default styles.css at {css_path}")

# Create default JavaScript file if it doesn't exist
def create_default_js():
    """Create a default main.js file if it doesn't exist"""
    js_path = os.path.join('static', 'js', 'main.js')
    
    if not os.path.exists(js_path):
        default_js = """/**
 * SkillX - Main JavaScript File
 */

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize any popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    console.log('SkillX JavaScript initialized successfully!');
});
"""
        
        with open(js_path, 'w') as f:
            f.write(default_js)
        
        print(f"Created default main.js at {js_path}")

# Initialize the application
def init_app():
    """Initialize the application - create directories and default files"""
    create_required_directories()
    create_default_css()
    create_default_js()
    
    return True