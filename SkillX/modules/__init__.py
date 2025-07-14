"""
SkillX Modules Package
"""
from .auth import (
    login_user, register_user, logout_user, is_authenticated, 
    get_current_user, require_login
)

from .user import (
    get_user_by_id, get_user_by_email, create_user, 
    update_user_profile, get_user_skills, update_user_skills,
    get_user_profile_completion
)

from .skills import (
    get_all_skill_categories, get_skills_by_category,
    get_user_skills, get_user_skills_dict, update_user_skills,
    get_trending_skills, get_skill_gap_analysis,
    get_learning_resources_for_skills
)

from .careers import (
    get_all_career_paths, get_career_path_by_id,
    get_user_career_interests, set_user_career_interest,
    get_recommended_career_paths, get_learning_resources_for_career,
    get_career_roadmap, get_career_job_outlook
)

from .jobs import (
    get_all_job_listings, get_job_by_id, search_jobs,
    filter_jobs_by_skill, get_trending_job_roles, get_trending_skills,
    get_job_salary_trends, get_location_wise_jobs, get_job_type_distribution,
    get_remote_work_trends, get_recommended_jobs_for_user
)

from .interviews import (
    get_interview_categories, get_category_by_id,
    get_interview_questions, get_question_by_id,
    get_user_interview_history, start_mock_interview,
    save_interview_results, get_interview_results,
    get_interview_tips, evaluate_answer
)

from .resume import (
    allowed_file, save_resume, analyze_resume,
    save_resume_feedback, get_resume_feedback,
    get_resume_tips, get_resume_templates
)

# Export all modules
__all__ = [
    'auth', 'user', 'skills', 'careers', 'jobs', 'interviews', 'resume'
]