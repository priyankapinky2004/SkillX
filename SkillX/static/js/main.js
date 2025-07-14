/**
 * SkillX - Main JavaScript File
 */

// DOM Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initTooltips();
    
    // Initialize any popovers
    initPopovers();
    
    // Add fade-in animation to main content
    addPageTransitions();
    
    // Set current year in the footer
    setFooterYear();
    
    // Initialize any page-specific components
    initPageComponents();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Add page transitions
 */
function addPageTransitions() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
}

/**
 * Set current year in the footer
 */
function setFooterYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });
}

/**
 * Initialize page-specific components based on the current page
 */
function initPageComponents() {
    // Identify current page by the URL path
    const currentPath = window.location.pathname;
    
    // Handle specific pages
    if (currentPath.includes('/skill-assessment')) {
        initSkillAssessment();
    } else if (currentPath.includes('/career-paths')) {
        initCareerPaths();
    } else if (currentPath.includes('/job-trends')) {
        initJobTrends();
    } else if (currentPath.includes('/mock-interview')) {
        initMockInterview();
    } else if (currentPath.includes('/resume-review')) {
        initResumeReview();
    }
}

/**
 * Skill Assessment page initialization
 */
function initSkillAssessment() {
    // Get all skill level containers
    const skillContainers = document.querySelectorAll('.skill-level-container');
    
    // Add click event handlers to each container
    skillContainers.forEach(container => {
        const skillName = container.dataset.skillName;
        const hiddenInput = document.getElementById(skillName);
        const buttons = container.querySelectorAll('.skill-level-btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', function() {
                // Clear active state from all buttons in this container
                buttons.forEach(b => b.classList.remove('active'));
                
                // Set active state on clicked button
                this.classList.add('active');
                
                // Update hidden input value
                hiddenInput.value = this.dataset.level;
            });
        });
    });
}

/**
 * Career Paths page initialization
 */
function initCareerPaths() {
    // Initialize any career path specific functionality
    console.log('Career Paths page initialized');
}

/**
 * Job Trends page initialization
 */
function initJobTrends() {
    // Initialize job search and filtering
    const searchInput = document.getElementById('jobSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', searchJobs);
    }
}

/**
 * Mock Interview page initialization
 */
function initMockInterview() {
    // Initialize mock interview functionality
    console.log('Mock Interview page initialized');
}

/**
 * Resume Review page initialization
 */
function initResumeReview() {
    // Initialize resume review functionality
    console.log('Resume Review page initialized');
}

/**
 * Job search functionality
 */
function searchJobs() {
    const searchInput = document.getElementById('jobSearchInput').value.toLowerCase();
    const jobItems = document.querySelectorAll('.job-item');
    let visibleJobs = 0;
    
    jobItems.forEach(item => {
        const title = item.querySelector('h5').textContent.toLowerCase();
        const company = item.querySelector('.text-muted').textContent.toLowerCase();
        
        if (title.includes(searchInput) || company.includes(searchInput)) {
            item.style.display = '';
            visibleJobs++;
        } else {
            item.style.display = 'none';
        }
    });
    
    // Show/hide no jobs message
    const noJobsMessage = document.getElementById('noJobsMessage');
    if (noJobsMessage) {
        noJobsMessage.style.display = visibleJobs === 0 ? 'block' : 'none';
    }
}

/**
 * Filter jobs by role
 */
function filterJobs(role) {
    const jobItems = document.querySelectorAll('.job-item');
    let visibleJobs = 0;
    
    jobItems.forEach(item => {
        const title = item.querySelector('h5').textContent;
        
        if (title === role) {
            item.style.display = '';
            visibleJobs++;
        } else {
            item.style.display = 'none';
        }
    });
    
    // Show/hide no jobs message
    const noJobsMessage = document.getElementById('noJobsMessage');
    if (noJobsMessage) {
        noJobsMessage.style.display = visibleJobs === 0 ? 'block' : 'none';
    }
    
    // Update search input
    const searchInput = document.getElementById('jobSearchInput');
    if (searchInput) {
        searchInput.value = role;
    }
}

/**
 * Reset job filters
 */
function resetFilters() {
    const jobItems = document.querySelectorAll('.job-item');
    jobItems.forEach(item => {
        item.style.display = '';
    });
    
    const searchInput = document.getElementById('jobSearchInput');
    if (searchInput) {
        searchInput.value = '';
    }
    
    const noJobsMessage = document.getElementById('noJobsMessage');
    if (noJobsMessage) {
        noJobsMessage.style.display = 'none';
    }
}

/**
 * Show animated status message
 */
function showStatusMessage(message, type = 'success') {
    // Create status message container
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-4`;
    messageDiv.setAttribute('role', 'alert');
    messageDiv.style.zIndex = '9999';
    messageDiv.style.maxWidth = '80%';
    
    // Add message content
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}