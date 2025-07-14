# SkillX - AI-Driven Career Path Navigator

SkillX is an AI-powered career guidance platform designed specifically for students from tier-2 and tier-3 colleges. The platform helps students assess their skills, discover suitable career paths, stay updated with job market trends, and prepare for job applications through mock interviews and resume reviews.

## Features

- **Skill Assessment**: Evaluate your proficiency in various technical and soft skills
- **Career Path Recommendations**: Get personalized career path suggestions based on your skills and interests
- **Job Market Trends**: Stay updated with in-demand skills and job opportunities
- **Mock Interviews**: Practice with AI-powered interview simulations tailored to specific roles
- **Resume Review**: Get AI-powered feedback on your resume to increase your chances of getting noticed

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python with Flask framework
- **Database**: SQLite (for simplicity in hackathon setting)
- **Deployment**: Gunicorn for production deployment

## Project Structure

```
SkillX/
├── README.md
├── requirements.txt
├── app.py                # Main application file
├── config.py             # Configuration settings
├── db_setup.py           # Database setup script
├── static/
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── styles.css    # Custom CSS
│   ├── js/
│   │   ├── bootstrap.bundle.min.js
│   │   ├── jquery.min.js
│   │   └── main.js       # Custom JavaScript
│   └── img/              # Image assets
│       ├── logo.svg
│       └── careers/
├── templates/            # HTML templates
└── modules/              # Application modules
    ├── __init__.py
    ├── auth.py
    ├── user.py
    ├── skills.py
    ├── careers.py
    ├── jobs.py
    ├── interviews.py
    └── resume.py
```

## Installation & Setup

### Prerequisites

- Python 3.7+ installed
- pip package manager

### Installation Steps

1. Clone the repository (for hackathon, download the project files)

2. Create a virtual environment

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment

   ```bash
   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

4. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

5. Run the database setup script

   ```bash
   python db_setup.py
   ```

6. Run the application

   ```bash
   python app.py
   ```

7. Open a web browser and navigate to `http://localhost:5000`

## Deployment

For a hackathon demo, you can deploy the application using the following methods:

### Option 1: Deploy to Heroku

1. Create a Procfile in the root directory

   ```
   web: gunicorn app:app
   ```

2. Add a runtime.txt file

   ```
   python-3.9.13
   ```

3. Create a Heroku app and deploy
   ```bash
   heroku create skillx-demo
   git push heroku main
   ```

### Option 2: Deploy to PythonAnywhere

1. Create a PythonAnywhere account
2. Upload the project files
3. Set up a web app with Flask
4. Configure the virtual environment and install dependencies

### Option 3: Deploy to a local server for demo

1. Set up the application on your laptop
2. Use ngrok to create a temporary public URL
   ```bash
   ngrok http 5000
   ```

## Demo Access

For the hackathon demo, the application includes a pre-configured demo account:

- **Email**: demo@example.com
- **Password**: password

## Future Enhancements

- Integration with real job APIs (LinkedIn, Naukri, Internshala)
- Advanced skill recommendation algorithm using machine learning
- Personalized learning path generation
- Mentor matching with industry professionals
- Analytics dashboard for educational institutions

## Contributors

- Your Name
- Team Members (if applicable)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
