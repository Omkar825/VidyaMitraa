from streamlit_chat import message
import logging
from datetime import datetime, timedelta
import base64
import uuid
import random
import requests
from io import BytesIO
from PIL import Image
import altair as alt
import time
import matplotlib.pyplot as plt
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import streamlit as st
import tracemalloc
tracemalloc.start()


# Configure logging
logging.basicConfig(
    filename='recommendation_system.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

# Configure page
st.set_page_config(
    page_title="EduPathfinder",
    page_icon="📚",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}

.content-box {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.skill-tag {
    display: inline-block;
    background-color: #e9ecef;
    padding: 5px 10px;
    margin: 2px;
    border-radius: 15px;
    font-size: 0.9em;
}

/* Content Management Styles */
.content-card {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    margin: 10px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    border-left: 4px solid #4CAF50;
    transition: transform 0.2s;
}

.content-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.content-card h3 {
    color: #2C3E50;
    margin-bottom: 10px;
}

.content-card p {
    color: #34495E;
    margin: 8px 0;
}

.version-badge {
    display: inline-block;
    background-color: #17A2B8;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-left: 8px;
}

.status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-left: 8px;
}

.status-approved {
    background-color: #28A745;
    color: white;
}

.status-pending {
    background-color: #FFC107;
    color: black;
}

.status-rejected {
    background-color: #DC3545;
    color: white;
}

.rating-stars {
    color: #FFD700;
    font-size: 1.2em;
}

.tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 10px 0;
}

.content-tag {
    background-color: #6C757D;
    color: white;
    padding: 3px 10px;
    border-radius: 15px;
    font-size: 0.8em;
}

.content-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.content-button {
    padding: 5px 15px;
        border-radius: 5px;
    border: none;
    cursor: pointer;
    font-size: 0.9em;
    transition: background-color 0.2s;
}

.view-button {
    background-color: #007BFF;
    color: white;
}

.rate-button {
    background-color: #FFC107;
    color: black;
}

.version-button {
    background-color: #17A2B8;
    color: white;
}

.moderate-button {
    background-color: #28A745;
    color: white;
}

.design-skill {
    background-color: #FF6B6B;
}

.technical-skill {
    background-color: #4ECDC4;
}

.soft-skill {
    background-color: #45B7D1;
}

.tool-skill {
    background-color: #96CEB4;
    }
    
    /* Existing styles */
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    
    /* Chat container styles */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    
    .chat-message-user, .chat-message-assistant {
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        max-width: 80%;
    }
    
    .chat-message-user {
        background-color: #e3f2fd;
        margin-left: auto;
        margin-right: 0;
    }
    
    .chat-message-assistant {
        background-color: #f5f5f5;
        margin-right: auto;
        margin-left: 0;
    }
    
    /* Suggestion button styles */
    .suggestion-button {
        margin: 0.25rem 0;
        padding: 0.5rem;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .suggestion-button:hover {
        background-color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Load more comprehensive course data


@st.cache_data
def load_course_data():
    # In a production environment, this would come from a database
    courses_data = {
        'course_id': range(1, 21),
        'title': [
            'Introduction to Python Programming',
            'Data Structures and Algorithms',
            'Web Development Fundamentals',
            'Machine Learning Basics',
            'Database Management Systems',
            'Software Engineering Principles',
            'Artificial Intelligence',
            'Cloud Computing',
            'Cybersecurity Fundamentals',
            'Mobile App Development',
            'Advanced Data Science',
            'DevOps Engineering',
            'Blockchain Development',
            'UI/UX Design Principles',
            'Natural Language Processing',
            'Computer Vision Fundamentals',
            'Quantum Computing Basics',
            'Internet of Things (IoT)',
            'Game Development Foundations',
            'Augmented Reality Applications'
        ],
        'description': [
            'Learn the fundamentals of Python programming language with hands-on exercises.',
            'Master essential data structures and algorithms for efficient problem-solving.',
            'Build responsive websites using HTML, CSS, and JavaScript.',
            'Introduction to machine learning concepts, algorithms, and applications.',
            'Design and manage relational databases with SQL.',
            'Learn software development lifecycle and best practices in engineering.',
            'Explore AI concepts, machine learning, and neural networks.',
            'Master cloud infrastructure, services, and deployment models.',
            'Learn essential cybersecurity concepts, threats, and defenses.',
            'Develop cross-platform mobile applications using modern frameworks.',
            'Advanced techniques in data manipulation, visualization, and predictive modeling.',
            'Implement continuous integration and deployment workflows.',
            'Learn blockchain technology and smart contract development.',
            'Master the principles of user experience and interface design.',
            'Build systems that can understand and process human language.',
            'Develop applications that can interpret and understand visual information.',
            'Introduction to quantum computing principles and algorithms.',
            'Connect and control devices in the Internet of Things ecosystem.',
            'Create interactive games using modern game engines.',
            'Develop applications that blend digital content with the real world.'
        ],
        'difficulty': [
            'Beginner', 'Intermediate', 'Beginner', 'Intermediate', 'Intermediate',
            'Intermediate', 'Advanced', 'Intermediate', 'Beginner', 'Intermediate',
            'Advanced', 'Advanced', 'Advanced', 'Intermediate', 'Advanced',
            'Advanced', 'Advanced', 'Intermediate', 'Intermediate', 'Advanced'
        ],
        'category': [
            'Programming', 'Computer Science', 'Web Development', 'Data Science',
            'Database', 'Software Engineering', 'AI/ML', 'Cloud', 'Security', 'Mobile Development',
            'Data Science', 'DevOps', 'Blockchain', 'Design', 'AI/ML',
            'AI/ML', 'Quantum Computing', 'IoT', 'Game Development', 'AR/VR'
        ],
        'duration_weeks': [
            4, 8, 6, 10, 6, 12, 14, 8, 5, 10,
            12, 8, 10, 6, 12, 10, 14, 8, 10, 12
        ],
        'skills_gained': [
            ['Python', 'Programming Fundamentals', 'Problem Solving'],
            ['Algorithms', 'Data Structures', 'Computational Thinking'],
            ['HTML', 'CSS', 'JavaScript', 'Responsive Design'],
            ['Machine Learning', 'Python', 'Data Analysis'],
            ['SQL', 'Database Design', 'Data Modeling'],
            ['Agile', 'Git', 'Testing', 'Project Management'],
            ['Neural Networks', 'Deep Learning', 'Python'],
            ['AWS', 'Azure', 'Virtualization', 'Containers'],
            ['Network Security', 'Encryption', 'Vulnerability Assessment'],
            ['iOS', 'Android', 'React Native', 'Flutter'],
            ['Advanced Statistics', 'BigData', 'Visualization', 'MLOps'],
            ['CI/CD', 'Docker', 'Kubernetes', 'Infrastructure as Code'],
            ['Smart Contracts', 'Ethereum', 'Solidity', 'Web3'],
            ['Wireframing', 'Prototyping', 'User Research', 'Usability Testing'],
            ['NLP', 'BERT', 'Transformers', 'Language Models'],
            ['OpenCV', 'CNNs', 'Image Processing', 'Object Detection'],
            ['Qubits', 'Quantum Gates', 'Quantum Algorithms'],
            ['Sensors', 'Embedded Systems', 'MQTT', 'Edge Computing'],
            ['Unity', 'Unreal Engine', '3D Modeling', 'Game Physics'],
            ['ARKit', 'ARCore', '3D Rendering', 'Spatial Computing']
        ],
        'prerequisites': [
            ['None'],
            ['Introduction to Programming'],
            ['Basic HTML/CSS Knowledge'],
            ['Python Programming', 'Basic Statistics'],
            ['Basic Computer Skills'],
            ['Programming Experience', 'Version Control'],
            ['Machine Learning Basics', 'Advanced Mathematics'],
            ['Networking Fundamentals', 'Basic Programming'],
            ['Basic Networking Knowledge'],
            ['Object-Oriented Programming'],
            ['Machine Learning Basics', 'Python Programming'],
            ['Linux Administration', 'Programming Experience'],
            ['Web Development', 'Cryptography Basics'],
            ['Graphic Design Basics'],
            ['Machine Learning', 'Python Programming'],
            ['Machine Learning', 'Linear Algebra'],
            ['Advanced Physics', 'Linear Algebra'],
            ['Basic Electronics', 'Programming Experience'],
            ['Programming Experience', '3D Graphics Basics'],
            ['Mobile Development', '3D Graphics']
        ],
        'rating': [
            4.7, 4.5, 4.8, 4.6, 4.3, 4.5, 4.9, 4.4, 4.7, 4.5,
            4.8, 4.6, 4.7, 4.5, 4.8, 4.9, 4.6, 4.3, 4.7, 4.8
        ],
        'career_relevance': [
            ['Software Developer', 'Data Analyst', 'QA Engineer'],
            ['Software Engineer', 'Backend Developer', 'Research Scientist'],
            ['Front-end Developer', 'Web Designer', 'UI Developer'],
            ['Data Scientist', 'Machine Learning Engineer', 'Research Analyst'],
            ['Database Administrator', 'Data Architect', 'Backend Developer'],
            ['Project Manager', 'Software Engineer', 'Product Manager'],
            ['AI Researcher', 'Machine Learning Engineer', 'Data Scientist'],
            ['Cloud Architect', 'DevOps Engineer', 'Solutions Architect'],
            ['Security Analyst', 'Penetration Tester', 'Security Engineer'],
            ['Mobile Developer', 'App Designer', 'UI/UX Developer'],
            ['Senior Data Scientist', 'AI Specialist', 'Research Scientist'],
            ['DevOps Engineer', 'Site Reliability Engineer', 'Cloud Architect'],
            ['Blockchain Developer', 'Smart Contract Engineer', 'Crypto Specialist'],
            ['UX Designer', 'Product Designer', 'UI Developer'],
            ['NLP Engineer', 'AI Researcher', 'Data Scientist'],
            ['Computer Vision Engineer', 'AI Researcher', 'Robotics Engineer'],
            ['Quantum Researcher', 'Quantum Software Engineer', 'Physicist'],
            ['IoT Engineer', 'Embedded Systems Developer', 'Solutions Architect'],
            ['Game Developer', 'Game Designer', '3D Modeler'],
            ['AR Developer', 'VR Engineer', 'Unity Developer']
        ]
    }
    return pd.DataFrame(courses_data)


courses_df = load_course_data()

# Add a new dataset for learning resources


@st.cache_data
def load_learning_resources():
    # In production, this would come from a database
    resources_data = {
        'course_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10,
                      11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20],
        'resource_type': ['Video', 'Tutorial', 'Video', 'Documentation', 'Video', 'Practice',
                          'Video', 'Dataset', 'Video', 'Documentation', 'Video', 'Tutorial',
                          'Video', 'Research', 'Video', 'Documentation', 'Video', 'Practice',
                          'Video', 'Tutorial', 'Video', 'Dataset', 'Video', 'Documentation',
                          'Video', 'Tutorial', 'Video', 'Tool', 'Video', 'Research',
                          'Video', 'Dataset', 'Video', 'Research', 'Video', 'Tutorial',
                          'Video', 'Engine', 'Video', 'Tutorial'],
        'title': ['Python for Beginners - Full Course', 'Interactive Python Tutorial',
                  'Data Structures and Algorithms in Python', 'Python Algorithm Documentation',
                  'HTML, CSS, JavaScript Crash Course', 'Frontend Mentor - Coding Challenges',
                  'Machine Learning Course by Andrew Ng', 'Kaggle Datasets for ML Practice',
                  'SQL Tutorial for Beginners', 'MySQL Official Documentation',
                  'Software Engineering Best Practices', 'Agile Development Tutorial',
                  'Artificial Intelligence Full Course', 'AI Research Papers Collection',
                  'AWS Certified Cloud Practitioner Training', 'AWS Documentation',
                  'Cybersecurity Fundamentals Course', 'Hack The Box - Security Challenges',
                  'iOS & Android App Development', 'Flutter Documentation',
                  'Advanced Data Science with Python', 'UCI Machine Learning Repository',
                  'DevOps CI/CD Pipeline Tutorial', 'Docker Documentation',
                  'Blockchain and Cryptocurrency Fundamentals', 'Ethereum Development Tutorial',
                  'UI/UX Design Principles Masterclass', 'Figma Design Tool',
                  'Natural Language Processing with TensorFlow', 'Latest NLP Research Papers',
                  'Computer Vision with Python OpenCV', 'Image Datasets for CV',
                  'Introduction to Quantum Computing', 'Quantum Computing Research',
                  'IoT Projects with Raspberry Pi and Arduino', 'Arduino Documentation',
                  'Unity Game Development Tutorial', 'Unreal Engine Documentation',
                  'AR Development with Unity', 'ARCore Documentation'],
        'url': ['https://www.youtube.com/watch?v=_uQrJ0TkZlc', 'https://www.learnpython.org/',
                'https://www.youtube.com/watch?v=B31LgI4Y4DQ', 'https://docs.python.org/3/tutorial/datastructures.html',
                'https://www.youtube.com/watch?v=mU6anWqZJcc', 'https://www.frontendmentor.io/',
                'https://www.youtube.com/watch?v=jGwO_UgTS7I', 'https://www.kaggle.com/datasets',
                'https://www.youtube.com/watch?v=HXV3zeQKqGY', 'https://dev.mysql.com/doc/',
                'https://www.youtube.com/watch?v=9vJRopau0g0', 'https://www.atlassian.com/agile/tutorials',
                'https://www.youtube.com/watch?v=JMUxmLyrhSk', 'https://arxiv.org/list/cs.AI/recent',
                'https://www.youtube.com/watch?v=3hLmDS179YE', 'https://docs.aws.amazon.com/',
                'https://www.youtube.com/watch?v=fNzpcB7ODxQ', 'https://www.hackthebox.com/',
                'https://www.youtube.com/watch?v=F9UC9DY-vIU', 'https://flutter.dev/docs',
                'https://www.youtube.com/watch?v=ua-CiDNNj30', 'https://archive.ics.uci.edu/ml/index.php',
                'https://www.youtube.com/watch?v=Y-XW9m8qOis', 'https://docs.docker.com/',
                'https://www.youtube.com/watch?v=SSo_EIwHSd4', 'https://ethereum.org/en/developers/docs/',
                'https://www.youtube.com/watch?v=c9Wg6Cb_YlU', 'https://www.figma.com/',
                'https://www.youtube.com/watch?v=fM4qTMfCoak', 'https://aclanthology.org/',
                'https://www.youtube.com/watch?v=oXlwWbU8l2o', 'https://www.cvlibs.net/datasets/kitti/',
                'https://www.youtube.com/watch?v=F_Riqjdh2oM', 'https://arxiv.org/list/quant-ph/recent',
                'https://www.youtube.com/watch?v=_AtP7au_Q9w', 'https://www.arduino.cc/en/main/docs',
                'https://www.youtube.com/watch?v=gB1F9G0JXOo', 'https://docs.unrealengine.com/',
                'https://www.youtube.com/watch?v=MjHsUiBTPOY', 'https://developers.google.com/ar/develop']
    }
    return pd.DataFrame(resources_data)


# Load resources data
learning_resources_df = load_learning_resources()

# Define learning style characteristics for more personalized recommendations
learning_styles_characteristics = {
    "Visual": {
        "description": "You learn best through visual aids like diagrams, charts, and videos.",
        "preferred_methods": [
            "Video tutorials and online courses",
            "Interactive infographics and data visualizations",
            "Mind mapping tools and concept maps",
            "Visual note-taking and sketchnoting",
            "Educational animations and simulations"
        ],
        "study_tips": [
            "Use color-coding in notes to organize information",
            "Convert text to diagrams or flowcharts",
            "Create visual flashcards with images",
            "Draw mind maps for complex topics",
            "Watch educational videos and animations"
        ],
        "recommended_resources": [
            {
                "name": "Coursera Video Courses",
                "url": "https://www.coursera.org",
                "description": "High-quality video courses from top universities"
            },
            {
                "name": "Khan Academy",
                "url": "https://www.khanacademy.org",
                "description": "Visual explanations and interactive exercises"
            },
            {
                "name": "Miro Mind Mapping",
                "url": "https://miro.com",
                "description": "Create interactive mind maps and visual diagrams"
            },
            {
                "name": "Canva Infographic Maker",
                "url": "https://www.canva.com/create/infographics",
                "description": "Design your own visual study materials"
            },
            {
                "name": "YouTube EDU",
                "url": "https://www.youtube.com/education",
                "description": "Educational video content across all subjects"
            },
            {
                "name": "Lucidchart",
                "url": "https://www.lucidchart.com/pages/education",
                "description": "Create diagrams, flowcharts, and visual documentation"
            },
            {
                "name": "Visual Learning Resources",
                "url": "https://www.mindtools.com/pages/article/visual-study-aids.htm",
                "description": "Tips and techniques for visual learners"
            }
        ],
        "tools": [
            {
                "name": "XMind",
                "url": "https://www.xmind.net",
                "type": "Mind Mapping Software"
            },
            {
                "name": "Draw.io",
                "url": "https://app.diagrams.net",
                "type": "Diagram Creation Tool"
            },
            {
                "name": "Coggle",
                "url": "https://coggle.it",
                "type": "Collaborative Mind Mapping"
            },
            {
                "name": "Prezi",
                "url": "https://prezi.com",
                "type": "Visual Presentation Tool"
            }
        ],
        "learning_platforms": [
            {
                "name": "Udacity",
                "url": "https://www.udacity.com",
                "focus": "Tech-focused visual learning"
            },
            {
                "name": "Skillshare",
                "url": "https://www.skillshare.com",
                "focus": "Creative visual courses"
            },
            {
                "name": "LinkedIn Learning",
                "url": "https://www.linkedin.com/learning",
                "focus": "Professional skill development with visual content"
            }
        ]
    },
    "Auditory": {
        "description": "You learn best through listening and speaking.",
        "preferred_methods": ["Lectures", "Group discussions", "Audio recordings", "Reading aloud"],
        "study_tips": [
            "Record and playback lectures",
            "Participate in study groups",
            "Explain concepts out loud",
            "Use music or rhythmic mnemonics"
        ]
    },
    "Reading/Writing": {
        "description": "You learn best through reading and writing text.",
        "preferred_methods": ["Textbooks", "Note-taking", "Written assignments", "Research papers"],
        "study_tips": [
            "Take detailed notes",
            "Rewrite key concepts in your own words",
            "Create lists and summaries",
            "Read textbooks and articles"
        ]
    },
    "Kinesthetic": {
        "description": "You learn best through hands-on activities and physical experiences.",
        "preferred_methods": ["Practical exercises", "Labs", "Role-playing", "Field trips"],
        "study_tips": [
            "Apply concepts to real-world scenarios",
            "Use physical manipulatives when possible",
            "Take breaks for movement",
            "Create models or act out processes"
        ]
    }
}

# User session management


def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'profile' not in st.session_state:
        st.session_state.profile = {
            'interests': [],
            'learning_style': '',
            'career_goal': '',
            'completed_courses': [],
            'profile_picture': None,
            'skills_assessment': {},
            'milestones': [],
            'progress': {}
        }
    if 'recommended_courses' not in st.session_state:
        st.session_state.recommended_courses = []
    if 'completed_courses' not in st.session_state:
        st.session_state.completed_courses = []
    if 'milestones' not in st.session_state:
        st.session_state.milestones = []


init_session_state()

# Enhanced recommendation function using both Gemini API and collaborative filtering


def get_personalized_recommendations(interests, learning_style, career_goal, experience_level='Beginner'):
    logging.info("Generating recommendations for user")
    logging.debug(
        f"User profile - Interests: {interests}, Learning Style: {learning_style}, Career Goal: {career_goal}, Experience Level: {experience_level}")

    # Step 1: Use Gemini API for content-based filtering
    prompt = f"""
    You are an advanced educational recommendation system. Based on the following student profile:
    - Interests: {interests}
    - Learning Style: {learning_style}
    - Career Goal: {career_goal}
    - Experience Level: {experience_level}
    
    I need you to analyze the following courses and rank them in order of relevance for this student.
    Consider the following factors:
    1. Core skills alignment with interests and career goals
    2. UI/UX design principles if relevant to their interests or career
    3. Visual and interactive learning components for {learning_style} learners
    4. Progressive skill development path from {experience_level} level
    5. Complementary skills that enhance their primary focus
    
    For UI/UX related interests or careers, prioritize:
    - Design thinking and user research
    - Visual design and prototyping tools
    - User interface development
    - Interaction design principles
    - Usability testing methods
    
    Return ONLY a comma-separated list of course IDs in order of most to least recommended, with no additional text.
    
    Course data:
    {courses_df[['course_id', 'title', 'description', 'difficulty', 'category', 'skills_gained', 'prerequisites', 'career_relevance']].to_string()}
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        logging.debug(f"AI response: {response_text}")

        # Extract course IDs from the response
        ai_recommended_courses = []
        for item in response_text.replace(',', ' ').split():
            if item.isdigit() and int(item) in courses_df['course_id'].values:
                ai_recommended_courses.append(int(item))

        logging.info(f"AI recommended courses: {ai_recommended_courses}")

        # Step 2: Enhanced filtering for UI/UX focus
        ui_ux_keywords = ['ui', 'ux', 'design',
                          'user experience', 'user interface', 'usability']
        is_ui_ux_focused = any(keyword in interests.lower() or keyword in career_goal.lower()
                               for keyword in ui_ux_keywords)

        # Initialize ui_ux_courses
        ui_ux_courses = []

        if is_ui_ux_focused:
            logging.info("User is UI/UX focused")
            # Get UI/UX related courses
            for course_id in courses_df['course_id'].values:
                course = courses_df[courses_df['course_id']
                                    == course_id].iloc[0]

                # Check if course is UI/UX related
                is_ui_ux_course = (
                    any(keyword in course['title'].lower() for keyword in ui_ux_keywords) or
                    any(keyword in course['description'].lower() for keyword in ui_ux_keywords) or
                    any(any(keyword in skill.lower() for keyword in ui_ux_keywords)
                        for skill in course['skills_gained']) or
                    any(any(keyword in career.lower() for keyword in ui_ux_keywords)
                        for career in course['career_relevance'])
                )

                if is_ui_ux_course:
                    ui_ux_courses.append(course_id)

        logging.info(f"UI/UX related courses: {ui_ux_courses}")

        # Blend recommendations
        final_recommendations = []

        # First, include UI/UX courses from AI recommendations
        for course_id in ai_recommended_courses:
            if course_id in ui_ux_courses and course_id not in final_recommendations:
                final_recommendations.append(course_id)

        # Then, add remaining UI/UX courses not in AI recommendations
        for course_id in ui_ux_courses:
            if course_id not in final_recommendations:
                final_recommendations.append(course_id)

        # Finally, add remaining AI recommendations
        for course_id in ai_recommended_courses:
            if course_id not in final_recommendations:
                final_recommendations.append(course_id)

        logging.info(f"Final recommendations: {final_recommendations}")

        # Get top 8 recommendations
        return final_recommendations[:8]

    except Exception as e:
        logging.error(f"Error generating recommendations: {str(e)}")
        st.error(f"Error generating recommendations: {str(e)}")
        # Fallback to basic filtering
        return courses_df.sort_values('rating', ascending=False)['course_id'].tolist()[:8]

# Update course explanation to include UI/UX specific insights


def get_course_explanation(course, interests, learning_style, career_goal):
    ui_ux_keywords = ['ui', 'ux', 'design',
                      'user experience', 'user interface', 'usability']
    is_ui_ux_focused = any(keyword in interests.lower() or keyword in career_goal.lower()
                           for keyword in ui_ux_keywords)

    if is_ui_ux_focused:
        prompt = f"""
        Explain in 2-3 sentences why the course "{course['title']}" ({course['category']}, {course['difficulty']}) 
        would be beneficial for a UI/UX focused student with:
        - Interests: {interests}
        - Learning Style: {learning_style}
        - Career Goal: {career_goal}

        Focus on:
        1. How this course enhances UI/UX design skills
        2. The visual and interactive learning aspects
        3. Career applications in design and user experience
        """
    else:
        prompt = f"""
        Explain in 2-3 sentences why the course "{course['title']}" ({course['category']}, {course['difficulty']}) 
        would be beneficial for a student with:
        - Interests: {interests}
        - Learning Style: {learning_style}
        - Career Goal: {career_goal}
        
        Focus on how this course aligns with their goals and learning preferences.
        """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback explanation
        return f"This {course['difficulty']} level course in {course['category']} provides valuable skills in {', '.join(course['skills_gained'][:3])} which align with your interests and career goals."

# Function to generate a learning path visualization


def generate_learning_path_visualization(recommended_course_ids):
    if not recommended_course_ids:
        return None

    courses = [courses_df[courses_df['course_id'] == id].iloc[0]
               for id in recommended_course_ids]

    # Prepare data for visualization
    timeline_data = []
    current_week = 0

    for i, course in enumerate(courses):
        start_week = current_week
        end_week = current_week + course['duration_weeks']

        timeline_data.append({
            'Course': course['title'],
            'Category': course['category'],
            'Start': start_week,
            'End': end_week,
            'Difficulty': course['difficulty'],
            'Order': i + 1
        })

        # Add a small gap between courses
        current_week = end_week + 1

    timeline_df = pd.DataFrame(timeline_data)

    # Create the Altair chart
    chart = alt.Chart(timeline_df).mark_bar().encode(
        x=alt.X('Start:Q', title='Week'),
        x2=alt.X2('End:Q'),
        y=alt.Y('Course:N', sort=alt.EncodingSortField(
            field='Order', order='descending'), title=None),
        color=alt.Color('Category:N', legend=alt.Legend(
            title="Course Category")),
        tooltip=['Course', 'Category', 'Difficulty', 'Start', 'End']
    ).properties(
        title='Your Learning Path Timeline',
        width=700,
        height=300
    ).configure_axisY(
        labelLimit=200
    )

    return chart

# Function to generate a skill development chart


def generate_skill_chart(recommended_course_ids):
    if not recommended_course_ids:
        return None

    courses = [courses_df[courses_df['course_id'] == id].iloc[0]
               for id in recommended_course_ids]

    # Extract all skills and categorize them
    skill_categories = {
        'Technical': [],
        'Design': [],
        'Soft Skills': [],
        'Tools': []
    }

    # Define skill categorization rules
    design_keywords = ['design', 'ui', 'ux', 'user', 'interface',
                       'experience', 'wireframe', 'prototype', 'usability']
    soft_skills_keywords = ['management', 'agile', 'communication',
                            'planning', 'research', 'analysis', 'testing']
    tools_keywords = ['git', 'docker', 'aws', 'azure',
                      'figma', 'sketch', 'adobe', 'kubernetes', 'jenkins']

    all_skills = {}
    for course in courses:
        for skill in course['skills_gained']:
            skill_lower = skill.lower()

            # Categorize the skill
            if any(keyword in skill_lower for keyword in design_keywords):
                category = 'Design'
            elif any(keyword in skill_lower for keyword in soft_skills_keywords):
                category = 'Soft Skills'
            elif any(keyword in skill_lower for keyword in tools_keywords):
                category = 'Tools'
            else:
                category = 'Technical'

            # Add to the appropriate category with count
            if skill in all_skills:
                all_skills[skill]['count'] += 1
            else:
                all_skills[skill] = {
                    'count': 1,
                    'category': category
                }

    # Convert to dataframe for visualization
    skill_data = []
    for skill, data in all_skills.items():
        skill_data.append({
            'Skill': skill,
            'Count': data['count'],
            'Category': data['category']
        })

    skill_df = pd.DataFrame(skill_data)

    # Sort by count within each category
    skill_df = skill_df.sort_values(
        ['Category', 'Count'], ascending=[True, False])

    # Create a more engaging visualization
    chart = alt.Chart(skill_df).mark_bar().encode(
        x=alt.X('Count:Q', title='Frequency in Your Learning Path'),
        y=alt.Y('Skill:N',
                sort=alt.EncodingSortField(field='Count', order='descending'),
                title=None),
        color=alt.Color('Category:N',
                        scale=alt.Scale(
                            domain=['Technical', 'Design',
                                    'Soft Skills', 'Tools'],
                            range=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                        ),
                        legend=alt.Legend(title="Skill Category")),
        tooltip=['Skill', 'Category', 'Count']
    ).properties(
        title={
            "text": "Skills You'll Gain in Your Journey",
            "subtitle": "Hover over bars for details"
        },
        width=350,
        height=400
    ).configure_title(
        fontSize=16,
        anchor='start'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_legend(
        labelFontSize=12,
        titleFontSize=14
    )

    return chart

# Update display_course_with_resources to show skills in a more organized way


def display_course_with_resources(course, i, explanation):
    # Get resources for this course
    course_resources = learning_resources_df[learning_resources_df['course_id']
                                             == course['course_id']]

    with st.container():
        st.markdown(f"""
        <div class="course-card">
            <h3>{i}. {course['title']}</h3>
            <p><strong>Difficulty:</strong> {course['difficulty']} | <strong>Category:</strong> {course['category']} | <strong>Duration:</strong> {course['duration_weeks']} weeks</p>
            <p>{course['description']}</p>
            <div class="highlight">
                <p><strong>Why this is recommended for you:</strong> {explanation}</p>
            </div>
            <p><strong>Skills you'll gain:</strong></p>
        """, unsafe_allow_html=True)

        # Categorize skills
        design_skills = []
        technical_skills = []
        soft_skills = []
        tool_skills = []

        design_keywords = ['design', 'ui', 'ux', 'user', 'interface',
                           'experience', 'wireframe', 'prototype', 'usability']
        soft_skills_keywords = [
            'management', 'agile', 'communication', 'planning', 'research', 'analysis', 'testing']
        tools_keywords = ['git', 'docker', 'aws', 'azure',
                          'figma', 'sketch', 'adobe', 'kubernetes', 'jenkins']

        for skill in course['skills_gained']:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in design_keywords):
                design_skills.append(skill)
            elif any(keyword in skill_lower for keyword in soft_skills_keywords):
                soft_skills.append(skill)
            elif any(keyword in skill_lower for keyword in tools_keywords):
                tool_skills.append(skill)
            else:
                technical_skills.append(skill)

        # Display skills by category
        if design_skills:
            st.markdown('<p><strong>🎨 Design Skills:</strong></p>',
                        unsafe_allow_html=True)
            for skill in design_skills:
                st.markdown(
                    f'<span class="skill-tag design-skill">{skill}</span>', unsafe_allow_html=True)

        if technical_skills:
            st.markdown('<p><strong>💻 Technical Skills:</strong></p>',
                        unsafe_allow_html=True)
            for skill in technical_skills:
                st.markdown(
                    f'<span class="skill-tag technical-skill">{skill}</span>', unsafe_allow_html=True)

        if soft_skills:
            st.markdown('<p><strong>🤝 Soft Skills:</strong></p>',
                        unsafe_allow_html=True)
            for skill in soft_skills:
                st.markdown(
                    f'<span class="skill-tag soft-skill">{skill}</span>', unsafe_allow_html=True)

        if tool_skills:
            st.markdown('<p><strong>🛠️ Tools:</strong></p>',
                        unsafe_allow_html=True)
            for skill in tool_skills:
                st.markdown(
                    f'<span class="skill-tag tool-skill">{skill}</span>', unsafe_allow_html=True)

        # Rest of the function remains the same
        # Display prerequisites
        if course['prerequisites'] and course['prerequisites'][0] != 'None':
            st.markdown("<p><strong>Prerequisites:</strong></p>",
                        unsafe_allow_html=True)
            for prereq in course['prerequisites']:
                st.markdown(f"- {prereq}")

        # Display career relevance
        st.markdown("<p><strong>Career Relevance:</strong></p>",
                    unsafe_allow_html=True)
        for career in course['career_relevance']:
            st.markdown(f"- {career}")

        # Display learning resources
        if not course_resources.empty:
            st.markdown("<p><strong>Learning Resources:</strong></p>",
                        unsafe_allow_html=True)
            for _, resource in course_resources.iterrows():
                st.markdown(
                    f"- [{resource['resource_type']}] [{resource['title']}]({resource['url']})")

        # Add Assessment Tools section
        st.markdown("<h4>📝 Assessment Tools</h4>", unsafe_allow_html=True)

        assessment_tabs = st.tabs(
            ["🎯 Quiz", "💻 Coding Challenges", "🚀 Projects", "📊 Progress"])

        with assessment_tabs[0]:
            st.markdown("### Course Quiz")
            quiz = get_course_quiz(course)

            if 'quiz_responses' not in st.session_state:
                st.session_state.quiz_responses = {}

            quiz_key = f"quiz_{course['course_id']}"
            if quiz_key not in st.session_state.quiz_responses:
                st.session_state.quiz_responses[quiz_key] = {}

            for idx, q in enumerate(quiz['questions']):
                st.markdown(f"**Question {idx + 1}:** {q['question']}")
                response = st.radio(
                    f"Select your answer for question {idx + 1}:",
                    q['options'],
                    key=f"quiz_{course['course_id']}_{idx}"
                )

                # Store response
                st.session_state.quiz_responses[quiz_key][idx] = q['options'].index(
                    response)

                # Check answer if submitted
                if st.button(f"Check Answer {idx + 1}", key=f"check_{course['course_id']}_{idx}"):
                    if q['options'].index(response) == q['correct']:
                        st.success("Correct! 🎉")
                    else:
                        st.error(
                            f"Incorrect. The correct answer is: {q['options'][q['correct']]}")

        with assessment_tabs[1]:
            st.markdown("### Coding Challenges")
            challenges = get_coding_challenges(course)

            for challenge in challenges:
                with st.expander(f"📝 {challenge['title']} ({challenge['difficulty']})"):
                    st.markdown(f"**Description:** {challenge['description']}")
                    st.markdown("**Template:**")
                    st.code(challenge['template'], language='python')

                    # Code editor
                    user_code = st.text_area(
                        "Your Solution:",
                        value=challenge['template'],
                        height=200,
                        key=f"code_{course['course_id']}_{challenge['title']}"
                    )

                    # Test cases
                    st.markdown("**Test Cases:**")
                    for test in challenge['test_cases']:
                        st.markdown(
                            f"Input: `{test['input']}` → Expected Output: `{test['output']}`")

                    if st.button("Run Tests", key=f"test_{course['course_id']}_{challenge['title']}"):
                        st.info("Running tests... (This is a simulation)")
                        st.success("All test cases passed! 🎉")

        with assessment_tabs[2]:
            st.markdown("### Project Suggestions")
            projects = get_project_suggestions(course)

            for project in projects:
                with st.expander(f"🚀 {project['title']} ({project['difficulty']})"):
                    st.markdown(f"**Description:** {project['description']}")

                    st.markdown("**Requirements:**")
                    for req in project['requirements']:
                        st.markdown(f"- {req}")

                    st.markdown("**Helpful Resources:**")
                    for resource in project['resources']:
                        st.markdown(f"- {resource}")

                    st.markdown(
                        f"**Estimated Time:** {project['estimated_hours']} hours")

                    # Project tracking
                    if st.button("Start Project", key=f"start_{course['course_id']}_{project['title']}"):
                        st.success("Project added to your tracking list! 📋")

        with assessment_tabs[3]:
            st.markdown("### Progress Assessment")
            progress = get_progress_assessment(course)

            # Skills checklist
            st.markdown("**Skills Checklist:**")
            for skill in progress['skills_checklist']:
                st.checkbox(
                    skill['skill'], key=f"skill_{course['course_id']}_{skill['skill']}")

            # Milestones
            st.markdown("**Course Milestones:**")
            for milestone in progress['milestones']:
                with st.expander(f"📍 {milestone['name']}"):
                    st.markdown(milestone['description'])
                    st.markdown("**Completion Criteria:**")
                    for criteria in milestone['completion_criteria']:
                        st.checkbox(
                            criteria, key=f"milestone_{course['course_id']}_{criteria}")

            # Overall progress
            st.markdown("**Completion Requirements:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Quizzes", f"{progress['completion_requirements']['quizzes_passed']}/{progress['completion_requirements']['required_quizzes']}")
            with col2:
                st.metric(
                    "Challenges", f"{progress['completion_requirements']['challenges_completed']}/{progress['completion_requirements']['required_challenges']}")
            with col3:
                st.metric(
                    "Projects", f"{progress['completion_requirements']['projects_submitted']}/{progress['completion_requirements']['required_projects']}")

        st.markdown("</div>", unsafe_allow_html=True)

# Add this function before display_learning_style_resources


def get_automatic_visual_resources(interests, career_goal):
    """Generate automatic visual learning resources based on interests and career goals"""
    # Define tech-specific visual learning platforms
    tech_specific_resources = {
        "Machine Learning": [
            {
                "name": "3Blue1Brown",
                "url": "https://www.3blue1brown.com/topics/machine-learning",
                "description": "Visual explanations of machine learning concepts with animations"
            },
            {
                "name": "Google AI Visual Learning",
                "url": "https://ai.google/education/",
                "description": "Interactive visualizations for AI/ML concepts"
            }
        ],
        "Web Development": [
            {
                "name": "Frontend Masters",
                "url": "https://frontendmasters.com",
                "description": "Visual courses for web development with live coding"
            },
            {
                "name": "CSS-Tricks",
                "url": "https://css-tricks.com",
                "description": "Visual guides and examples for web design"
            }
        ],
        "Data Science": [
            {
                "name": "D3.js Gallery",
                "url": "https://observablehq.com/@d3/gallery",
                "description": "Interactive data visualization examples"
            },
            {
                "name": "Tableau Public",
                "url": "https://public.tableau.com/gallery",
                "description": "Visual analytics and data storytelling"
            }
        ],
        "Cybersecurity": [
            {
                "name": "HackTheBox Academy",
                "url": "https://academy.hackthebox.com",
                "description": "Interactive cybersecurity visualization labs"
            },
            {
                "name": "Security Visualization Lab",
                "url": "https://secviz.org",
                "description": "Visual analysis of security data"
            }
        ],
        "Cloud Computing": [
            {
                "name": "AWS Architecture Center",
                "url": "https://aws.amazon.com/architecture",
                "description": "Visual cloud architecture diagrams"
            },
            {
                "name": "Azure Architecture Center",
                "url": "https://docs.microsoft.com/azure/architecture",
                "description": "Visual guides for cloud solutions"
            }
        ]
    }

    # Career-specific visual tools
    career_specific_tools = {
        "Data Scientist": [
            {
                "name": "Plotly",
                "url": "https://plotly.com/python/",
                "description": "Interactive visualization library for data science"
            },
            {
                "name": "Power BI",
                "url": "https://powerbi.microsoft.com/learning/",
                "description": "Visual analytics training"
            }
        ],
        "Software Engineer": [
            {
                "name": "System Design Primer",
                "url": "https://github.com/donnemartin/system-design-primer",
                "description": "Visual guides to system design"
            },
            {
                "name": "Visual Studio Code Guides",
                "url": "https://code.visualstudio.com/docs",
                "description": "Interactive coding environment tutorials"
            }
        ],
        "Cloud Architect": [
            {
                "name": "Cloud Architecture Patterns",
                "url": "https://docs.microsoft.com/azure/architecture/patterns/",
                "description": "Visual patterns for cloud design"
            }
        ]
    }

    suggested_resources = []

    # Add interest-based resources
    if interests:
        for topic in tech_specific_resources.keys():
            if topic.lower() in interests.lower():
                suggested_resources.extend(tech_specific_resources[topic])

    # Add career-based resources
    if career_goal:
        for career in career_specific_tools.keys():
            if career.lower() in career_goal.lower():
                suggested_resources.extend(career_specific_tools[career])

    return suggested_resources

# Add this function to generate note templates


def get_note_templates(topic):
    """Generate topic-specific note templates"""
    templates = {
        "Machine Learning": {
            "concept_template": """
            # Machine Learning Concept Note Template
            
            ## Concept Name: [Fill in]
            
            ### Key Components:
            - Algorithm Type: 
            - Use Cases:
            - Mathematical Foundation:
            
            ### Visual Representation:
            [ ] Draw or paste diagram here
            
            ### Code Example:
            ```python
            # Add code implementation
            ```
            
            ### Real-world Applications:
            1. 
            2. 
            3.
            
            ### Common Pitfalls:
            - 
            -
            
            ### Practice Exercises:
            1. 
            2.
            """
        },
        "Web Development": {
            "concept_template": """
            # Web Development Component Note Template
            
            ## Component/Feature: [Fill in]
            
            ### Structure:
            ```html
            <!-- HTML Structure -->
            ```
            
            ### Styling:
            ```css
            /* CSS Styles */
            ```
            
            ### Functionality:
            ```javascript
            // JavaScript Code
            ```
            
            ### Visual Design:
            [ ] Add wireframe/mockup
            
            ### Responsive Considerations:
            - Mobile:
            - Tablet:
            - Desktop:
            
            ### Accessibility Notes:
            - 
            -
            """
        },
        "Data Science": {
            "concept_template": """
            # Data Analysis Note Template
            
            ## Dataset: [Fill in]
            
            ### Data Overview:
            - Source:
            - Size:
            - Features:
            
            ### Visualization Plan:
            [ ] Add planned visualizations
            
            ### Analysis Steps:
            1. Data Cleaning:
            2. Feature Engineering:
            3. Model Selection:
            
            ### Results:
            - Key Findings:
            - Metrics:
            - Visualizations:
            
            ### Conclusions:
            - 
            -
            """
        }
    }
    return templates.get(topic, {
        "concept_template": """
        # General Study Note Template
        
        ## Topic: [Fill in]
        
        ### Key Concepts:
        1. 
        2. 
        3.
        
        ### Visual Elements:
        [ ] Add diagrams/images
        
        ### Examples:
        1. 
        2.
        
        ### Practice Questions:
        1. 
        2.
        
        ### Resources:
        - 
        -
        """
    })

# Update the display_learning_style_resources function


def display_learning_style_resources(learning_style):
    if learning_style in learning_styles_characteristics:
        style_info = learning_styles_characteristics[learning_style]

        st.markdown(f"""
        <div class="info-box">
            <h3>{learning_style} Learning Resources</h3>
            <p>{style_info['description']}</p>
        """, unsafe_allow_html=True)

        # If it's a visual learner and we have interests/career goals, show automatic suggestions
        if learning_style == "Visual" and 'profile' in st.session_state:
            interests = st.session_state.profile.get('interests', '')
            career_goal = st.session_state.profile.get('career_goal', '')

            if interests or career_goal:
                auto_resources = get_automatic_visual_resources(
                    interests, career_goal)
                if auto_resources:
                    st.markdown(
                        "<h4>🎯 Personalized Visual Resources</h4>", unsafe_allow_html=True)
                    st.markdown(
                        "<p>Based on your interests and career goals:</p>", unsafe_allow_html=True)

                    # Display automatic resources in a grid
                    cols = st.columns(2)
                    for i, resource in enumerate(auto_resources):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                                <h5>{resource['name']}</h5>
                                <p style='font-size: 0.9em;'>{resource['description']}</p>
                                <a href='{resource['url']}' target='_blank'>Access Resource</a>
                            </div>
                            """, unsafe_allow_html=True)

        st.markdown("<h4>🎯 Recommended Learning Platforms</h4>",
                    unsafe_allow_html=True)

        # Display learning platforms in a grid
        cols = st.columns(3)
        for i, platform in enumerate(style_info.get('learning_platforms', [])):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                    <h5>{platform['name']}</h5>
                    <p style='font-size: 0.9em;'>{platform['focus']}</p>
                    <a href='{platform['url']}' target='_blank'>Visit Platform</a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<h4>🛠️ Recommended Tools</h4>", unsafe_allow_html=True)

        # Display tools in a grid
        cols = st.columns(2)
        for i, tool in enumerate(style_info.get('tools', [])):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                    <h5>{tool['name']}</h5>
                    <p style='font-size: 0.9em;'>{tool['type']}</p>
                    <a href='{tool['url']}' target='_blank'>Try Tool</a>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<h4>📚 Additional Learning Resources</h4>",
                    unsafe_allow_html=True)

        # Display resources in an organized list
        for resource in style_info.get('recommended_resources', []):
            st.markdown(f"""
            <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                <h5>{resource['name']}</h5>
                <p style='font-size: 0.9em;'>{resource['description']}</p>
                <a href='{resource['url']}' target='_blank'>Access Resource</a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h4>💡 Study Tips</h4>", unsafe_allow_html=True)
        for tip in style_info['study_tips']:
            st.markdown(f"- {tip}")

        if learning_style == "Visual":
            st.markdown("<h4>📝 Interactive Note-Taking Tools</h4>",
                        unsafe_allow_html=True)

            # Add note-taking template selector
            selected_topic = st.selectbox(
                "Select topic for note template:",
                ["General", "Machine Learning", "Web Development", "Data Science"],
                key="note_template_selector"
            )

            # Get template for selected topic
            template = get_note_templates(selected_topic)["concept_template"]

            # Create tabs for different note-taking features
            note_tabs = st.tabs(
                ["📒 Note Template", "✏️ Sketch Pad", "🔄 Flash Cards"])

            with note_tabs[0]:
                st.markdown("### 📝 Smart Note Template")
                st.markdown(
                    "Use this template to create structured visual notes:")

                # Add copy button for template
                if st.button("📋 Copy Template to Clipboard"):
                    st.code(template, language="markdown")
                    st.success(
                        "Template copied! Paste it into your favorite note-taking app.")

                # Show preview
                st.markdown("### Preview:")
                st.markdown(template)

            with note_tabs[1]:
                st.markdown("### ✏️ Quick Sketch Pad")
                st.markdown("""
                Use this space to quickly sketch concepts or create diagrams:
                
                1. Open [Excalidraw](https://excalidraw.com/) in a new tab for quick sketches
                2. Open [Draw.io](https://app.diagrams.net/) for detailed diagrams
                3. Open [Miro](https://miro.com) for collaborative visual boards
                """)

                # Add quick sketch tools
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                        <h5>Quick Sketch</h5>
                        <a href='https://excalidraw.com/' target='_blank'>Open Excalidraw</a>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div style='padding: 10px; border: 1px solid #ce93d8; border-radius: 5px; margin: 5px;'>
                        <h5>Detailed Diagrams</h5>
                        <a href='https://app.diagrams.net/' target='_blank'>Open Draw.io</a>
                    </div>
                    """, unsafe_allow_html=True)

            with note_tabs[2]:
                st.markdown("### 🔄 Visual Flash Cards")
                st.markdown("Create visual flash cards for active recall:")

                # Add flash card creator
                term = st.text_input("Term/Concept:")
                visual_url = st.text_input("Image URL (optional):")
                definition = st.text_area("Definition/Explanation:")

                if st.button("Add Flash Card"):
                    if term and definition:
                        if 'flash_cards' not in st.session_state:
                            st.session_state.flash_cards = []

                        st.session_state.flash_cards.append({
                            'term': term,
                            'visual_url': visual_url,
                            'definition': definition
                        })
                        st.success("Flash card added!")

                # Display existing flash cards
                if 'flash_cards' in st.session_state and st.session_state.flash_cards:
                    st.markdown("### Your Flash Cards:")
                    for i, card in enumerate(st.session_state.flash_cards):
                        with st.expander(f"Card {i+1}: {card['term']}"):
                            if card['visual_url']:
                                st.image(card['visual_url'])
                            st.markdown(card['definition'])

            # Add practice exercises section
            st.markdown("<h4>🎯 Practice Exercises</h4>",
                        unsafe_allow_html=True)
            practice_tabs = st.tabs(
                ["📊 Visualization Practice", "🧩 Interactive Exercises", "📝 Concept Mapping"])

            with practice_tabs[0]:
                st.markdown("""
                ### 📊 Visualization Practice
                Practice creating visual representations:
                
                1. [Observable](https://observablehq.com/) - Practice data visualization
                2. [CodePen](https://codepen.io/) - Practice web design visualization
                3. [Kaggle Notebooks](https://www.kaggle.com/notebooks) - Practice data science visualization
                """)

            with practice_tabs[1]:
                st.markdown("""
                ### 🧩 Interactive Exercises
                Try these interactive learning exercises:
                
                1. [LeetCode Visualizer](https://leetcode.com/) - Algorithm visualization
                2. [Visualgo](https://visualgo.net/) - Data structure visualization
                3. [Regex Visualizer](https://regexr.com/) - Regular expression visualization
                """)

            with practice_tabs[2]:
                st.markdown("""
                ### 📝 Concept Mapping Exercise
                Create visual concept maps:
                
                1. [Coggle](https://coggle.it) - Collaborative mind mapping
                2. [MindMeister](https://www.mindmeister.com/) - Online mind mapping
                3. [Bubbl.us](https://bubbl.us/) - Simple concept mapping
                """)

        st.markdown("</div>", unsafe_allow_html=True)

# Add new functions for enhanced profile features


def load_profile_picture(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        encoded = base64.b64encode(bytes_data).decode()
        return f"data:image/png;base64,{encoded}"
    return None


def get_skills_assessment_questions():
    return {
        "Programming": [
            {
                "question": "How comfortable are you with Python programming?",
                "options": ["Beginner", "Intermediate", "Advanced"]
            },
            {
                "question": "Have you worked with web development technologies?",
                "options": ["No Experience", "Basic Knowledge", "Experienced"]
            }
        ],
        "Data Science": [
            {
                "question": "How familiar are you with machine learning concepts?",
                "options": ["Beginner", "Intermediate", "Advanced"]
            },
            {
                "question": "Have you worked with data visualization tools?",
                "options": ["No Experience", "Basic Knowledge", "Experienced"]
            }
        ],
        "Cloud Computing": [
            {
                "question": "How experienced are you with cloud platforms?",
                "options": ["Beginner", "Intermediate", "Advanced"]
            },
            {
                "question": "Have you deployed applications to the cloud?",
                "options": ["No Experience", "Basic Knowledge", "Experienced"]
            }
        ]
    }


def calculate_skill_level(responses):
    skill_levels = {
        "No Experience": 0,
        "Beginner": 1,
        "Basic Knowledge": 1,
        "Intermediate": 2,
        "Advanced": 3,
        "Experienced": 3
    }

    total_score = sum(skill_levels[response] for response in responses)
    avg_score = total_score / len(responses)

    if avg_score < 1:
        return "Beginner"
    elif avg_score < 2:
        return "Intermediate"
    else:
        return "Advanced"


def update_progress_and_milestones():
    if not st.session_state.recommended_courses:
        return

    total_courses = len(st.session_state.recommended_courses)
    completed_courses = len(st.session_state.completed_courses)
    progress_percentage = (completed_courses / total_courses) * 100

    # Update progress
    st.session_state.profile['progress'] = {
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'progress_percentage': progress_percentage
    }

    # Check and award milestones
    milestones = [
        {'name': '🌱 Learning Journey Begins', 'requirement': 1},
        {'name': '🌿 Making Progress', 'requirement': 3},
        {'name': '🌲 Halfway There', 'requirement': total_courses // 2},
        {'name': '🎓 Course Champion', 'requirement': total_courses}
    ]

    current_milestones = []
    for milestone in milestones:
        if completed_courses >= milestone['requirement']:
            if milestone not in st.session_state.milestones:
                st.session_state.milestones.append(milestone)
            current_milestones.append(milestone)

    st.session_state.profile['milestones'] = current_milestones

# Add new functions for assessment tools


def get_course_quiz(course):
    """Generate quiz questions for a course"""
    quizzes = {
        'Introduction to Python Programming': {
            'questions': [
                {
                    'question': 'What is a variable in Python?',
                    'options': [
                        'A container for storing data values',
                        'A function that performs calculations',
                        'A loop statement',
                        'A conditional statement'
                    ],
                    'correct': 0
                },
                {
                    'question': 'Which of the following is a valid Python list?',
                    'options': [
                        '{1, 2, 3}',
                        '[1, 2, 3]',
                        '(1, 2, 3)',
                        '<1, 2, 3>'
                    ],
                    'correct': 1
                }
            ]
        },
        'Data Structures and Algorithms': {
            'questions': [
                {
                    'question': 'What is the time complexity of binary search?',
                    'options': [
                        'O(n)',
                        'O(n^2)',
                        'O(log n)',
                        'O(1)'
                    ],
                    'correct': 2
                },
                {
                    'question': 'Which data structure follows LIFO principle?',
                    'options': [
                        'Queue',
                        'Stack',
                        'Linked List',
                        'Tree'
                    ],
                    'correct': 1
                }
            ]
        }
    }
    return quizzes.get(course['title'], {
        'questions': [
            {
                'question': f"What is the main focus of {course['title']}?",
                'options': [
                    course['description'],
                    'Understanding basic concepts',
                    'Practical applications',
                    'Theory and fundamentals'
                ],
                'correct': 0
            }
        ]
    })


def get_coding_challenges(course):
    """Generate coding challenges for a course"""
    challenges = {
        'Introduction to Python Programming': [
            {
                'title': 'FizzBuzz Implementation',
                'description': 'Write a program that prints numbers from 1 to 100. For multiples of 3, print "Fizz", for multiples of 5, print "Buzz", and for multiples of both, print "FizzBuzz".',
                'difficulty': 'Easy',
                'template': '''def fizzbuzz():
    # Your code here
    pass''',
                'test_cases': [
                    {'input': '15', 'output': 'FizzBuzz'},
                    {'input': '3', 'output': 'Fizz'},
                    {'input': '5', 'output': 'Buzz'}
                ]
            }
        ],
        'Data Structures and Algorithms': [
            {
                'title': 'Binary Search Implementation',
                'description': 'Implement binary search algorithm to find a target element in a sorted array.',
                'difficulty': 'Medium',
                'template': '''def binary_search(arr, target):
    # Your code here
    pass''',
                'test_cases': [
                    {'input': '[1,2,3,4,5], 3', 'output': '2'},
                    {'input': '[1,2,3,4,5], 6', 'output': '-1'}
                ]
            }
        ]
    }
    return challenges.get(course['title'], [
        {
            'title': f"Basic {course['category']} Challenge",
            'description': f"Create a simple program demonstrating core concepts of {course['title']}",
            'difficulty': 'Medium',
            'template': '# Your code here',
            'test_cases': [
                {'input': 'sample input', 'output': 'expected output'}
            ]
        }
    ])


def get_project_suggestions(course):
    """Generate project suggestions for a course"""
    projects = {
        'Introduction to Python Programming': [
            {
                'title': 'Task Manager Application',
                'description': 'Build a command-line task manager that allows users to create, update, and delete tasks.',
                'requirements': [
                    'CRUD operations for tasks',
                    'Data persistence using files',
                    'Command-line interface',
                    'Task prioritization'
                ],
                'resources': [
                    'Python File I/O documentation',
                    'Command-line argument parsing tutorial'
                ],
                'difficulty': 'Beginner',
                'estimated_hours': 10
            },
            {
                'title': 'Weather Data Analyzer',
                'description': 'Create a program that fetches and analyzes weather data from a public API.',
                'requirements': [
                    'API integration',
                    'Data processing',
                    'Statistical analysis',
                    'Data visualization'
                ],
                'resources': [
                    'Weather API documentation',
                    'Python requests library tutorial',
                    'Matplotlib documentation'
                ],
                'difficulty': 'Intermediate',
                'estimated_hours': 15
            }
        ],
        'Web Development Fundamentals': [
            {
                'title': 'Personal Portfolio Website',
                'description': 'Build a responsive portfolio website showcasing your projects and skills.',
                'requirements': [
                    'Responsive design',
                    'Multiple pages/sections',
                    'Contact form',
                    'Project gallery'
                ],
                'resources': [
                    'HTML5 documentation',
                    'CSS Grid tutorial',
                    'JavaScript DOM manipulation guide'
                ],
                'difficulty': 'Beginner',
                'estimated_hours': 20
            }
        ]
    }

    # Generate generic projects if course-specific ones are not available
    default_projects = [
        {
            'title': f"{course['title']} Portfolio Project",
            'description': f"Create a comprehensive project showcasing the skills learned in {course['title']}",
            'requirements': [
                'Implementation of core concepts',
                'Documentation',
                'Testing',
                'Presentation'
            ],
            'resources': [
                f"{course['category']} documentation",
                'Best practices guide',
                'Testing frameworks'
            ],
            'difficulty': course['difficulty'],
            'estimated_hours': 20
        }
    ]

    return projects.get(course['title'], default_projects)


def get_progress_assessment(course):
    """Generate progress assessment criteria for a course"""
    return {
        'skills_checklist': [
            {'skill': skill, 'mastered': False} for skill in course['skills_gained']
        ],
        'milestones': [
            {
                'name': 'Fundamentals',
                'description': f"Understanding basic concepts of {course['title']}",
                'completion_criteria': [
                    'Complete introduction modules',
                    'Pass basic concept quiz',
                    'Complete first coding challenge'
                ]
            },
            {
                'name': 'Practical Application',
                'description': 'Applying concepts to real-world problems',
                'completion_criteria': [
                    'Complete hands-on exercises',
                    'Submit working project',
                    'Pass practical assessment'
                ]
            },
            {
                'name': 'Advanced Mastery',
                'description': 'Demonstrating advanced understanding',
                'completion_criteria': [
                    'Complete advanced modules',
                    'Create complex project',
                    'Pass final assessment'
                ]
            }
        ],
        'completion_requirements': {
            'quizzes_passed': 0,
            'challenges_completed': 0,
            'projects_submitted': 0,
            'required_quizzes': 3,
            'required_challenges': 2,
            'required_projects': 1
        }
    }

# User-generated content and content management system


@st.cache_data
def load_user_content():
    # In production, this would come from a database
    user_content_data = {
        'content_id': range(1, 5),
        'user_id': ['user1', 'user2', 'user3', 'user4'],
        'content_type': ['tutorial', 'project', 'resource', 'tutorial'],
        'title': [
            'Python Data Visualization Guide',
            'Machine Learning Project Portfolio',
            'Web Development Resources Collection',
            'Data Structures Implementation Guide'
        ],
        'description': [
            'A comprehensive guide to data visualization in Python using various libraries.',
            'Collection of ML projects with source code and documentation.',
            'Curated list of web development resources and tools.',
            'Step-by-step guide to implementing common data structures.'
        ],
        'content': [
            'content/tutorials/python_viz_guide.md',
            'content/projects/ml_portfolio.md',
            'content/resources/webdev_collection.md',
            'content/tutorials/ds_guide.md'
        ],
        'tags': [
            ['python', 'visualization', 'data-science'],
            ['machine-learning', 'portfolio', 'projects'],
            ['web-development', 'resources', 'tools'],
            ['data-structures', 'algorithms', 'python']
        ],
        'created_at': ['2024-03-15', '2024-03-14', '2024-03-13', '2024-03-12'],
        'updated_at': ['2024-03-15', '2024-03-14', '2024-03-13', '2024-03-12'],
        'version': [1, 1, 1, 1],
        'status': ['approved', 'pending', 'approved', 'approved'],
        'rating': [4.5, 0, 4.8, 4.2],
        'votes': [10, 0, 15, 8]
    }
    return pd.DataFrame(user_content_data)


@st.cache_data
def load_content_versions():
    # In production, this would come from a database
    version_data = {
        'version_id': range(1, 5),
        'content_id': [1, 1, 2, 3],
        'version_number': [1, 2, 1, 1],
        'changes': [
            'Initial version',
            'Updated visualization examples',
            'Initial version',
            'Initial version'
        ],
        'content_path': [
            'content/tutorials/python_viz_guide_v1.md',
            'content/tutorials/python_viz_guide_v2.md',
            'content/projects/ml_portfolio_v1.md',
            'content/resources/webdev_collection_v1.md'
        ],
        'created_at': ['2024-03-15', '2024-03-16', '2024-03-14', '2024-03-13'],
        'created_by': ['user1', 'user1', 'user2', 'user3']
    }
    return pd.DataFrame(version_data)


@st.cache_data
def load_content_ratings():
    # In production, this would come from a database
    ratings_data = {
        'rating_id': range(1, 11),
        'content_id': [1, 1, 1, 3, 3, 3, 3, 4, 4, 4],
        'user_id': ['user2', 'user3', 'user4', 'user1', 'user2', 'user4', 'user5', 'user1', 'user2', 'user3'],
        'rating': [4, 5, 4.5, 5, 4.5, 5, 4.5, 4, 4.5, 4],
        'comment': [
            'Very helpful guide!',
            'Great examples',
            'Well explained',
            'Excellent collection',
            'Very useful',
            'Comprehensive list',
            'Good resources',
            'Clear explanations',
            'Helpful implementation',
            'Good guide'
        ],
        'created_at': ['2024-03-15'] * 10
    }
    return pd.DataFrame(ratings_data)


def submit_user_content(title, description, content_type, content, tags):
    """Submit new user-generated content for moderation"""
    # In production, this would add to the database
    if 'user_content' not in st.session_state:
        st.session_state.user_content = load_user_content()

    new_content = {
        'content_id': max(st.session_state.user_content['content_id']) + 1,
        'user_id': 'current_user',  # In production, get from auth system
        'content_type': content_type,
        'title': title,
        'description': description,
        'content': content,
        'tags': tags,
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d'),
        'version': 1,
        'status': 'pending',
        'rating': 0,
        'votes': 0
    }

    st.session_state.user_content = pd.concat([
        st.session_state.user_content,
        pd.DataFrame([new_content])
    ], ignore_index=True)

    return new_content['content_id']


def submit_content_rating(content_id, rating, comment):
    """Submit a rating for user-generated content"""
    # In production, this would add to the database
    if 'content_ratings' not in st.session_state:
        st.session_state.content_ratings = load_content_ratings()

    new_rating = {
        'rating_id': max(st.session_state.content_ratings['rating_id']) + 1,
        'content_id': content_id,
        'user_id': 'current_user',  # In production, get from auth system
        'rating': rating,
        'comment': comment,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }

    st.session_state.content_ratings = pd.concat([
        st.session_state.content_ratings,
        pd.DataFrame([new_rating])
    ], ignore_index=True)

    # Update average rating in user_content
    content_ratings = st.session_state.content_ratings[
        st.session_state.content_ratings['content_id'] == content_id
    ]
    avg_rating = content_ratings['rating'].mean()
    votes = len(content_ratings)

    st.session_state.user_content.loc[
        st.session_state.user_content['content_id'] == content_id,
        ['rating', 'votes']
    ] = [avg_rating, votes]


def moderate_content(content_id, action):
    """Moderate user-generated content (approve/reject)"""
    # In production, this would update the database
    if action not in ['approve', 'reject']:
        raise ValueError("Action must be 'approve' or 'reject'")

    st.session_state.user_content.loc[
        st.session_state.user_content['content_id'] == content_id,
        'status'
    ] = 'approved' if action == 'approve' else 'rejected'


def create_content_version(content_id, content, changes):
    """Create a new version of user-generated content"""
    # In production, this would add to the database
    if 'content_versions' not in st.session_state:
        st.session_state.content_versions = load_content_versions()

    current_versions = st.session_state.content_versions[
        st.session_state.content_versions['content_id'] == content_id
    ]
    new_version_number = max(
        current_versions['version_number']) + 1 if len(current_versions) > 0 else 1

    new_version = {
        'version_id': max(st.session_state.content_versions['version_id']) + 1,
        'content_id': content_id,
        'version_number': new_version_number,
        'changes': changes,
        'content_path': f"content/{content_id}/v{new_version_number}.md",
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'created_by': 'current_user'  # In production, get from auth system
    }

    st.session_state.content_versions = pd.concat([
        st.session_state.content_versions,
        pd.DataFrame([new_version])
    ], ignore_index=True)

    # Update version in user_content
    st.session_state.user_content.loc[
        st.session_state.user_content['content_id'] == content_id,
        ['version', 'updated_at']
    ] = [new_version_number, datetime.now().strftime('%Y-%m-%d')]

    return new_version['version_id']


def calculate_learning_metrics(user_id):
    """Calculate detailed learning metrics for the user"""
    if 'completed_courses' not in st.session_state:
        return None

    metrics = {
        'total_courses': len(st.session_state.recommended_courses),
        'completed_courses': len(st.session_state.completed_courses),
        'total_skills': len(set([skill for course_id in st.session_state.recommended_courses
                                 for skill in courses_df[courses_df['course_id'] == course_id].iloc[0]['skills_gained']])),
        'learning_streak': calculate_streak(),
        'achievements': get_user_achievements(),
        'estimated_hours': sum([courses_df[courses_df['course_id'] == id].iloc[0]['duration_weeks'] * 10
                                for id in st.session_state.completed_courses])
    }

    # Calculate progress percentage
    if metrics['total_courses'] > 0:
        metrics['progress_percentage'] = (
            metrics['completed_courses'] / metrics['total_courses']) * 100
    else:
        metrics['progress_percentage'] = 0

    return metrics


def get_user_achievements():
    """Get user's earned achievements"""
    achievements = []
    completed_courses = len(st.session_state.completed_courses)

    # Course completion achievements
    if completed_courses >= 1:
        achievements.append({
            'name': 'First Step',
            'description': 'Completed your first course',
            'icon': '🎯'
        })
    if completed_courses >= 5:
        achievements.append({
            'name': 'Quick Learner',
            'description': 'Completed 5 courses',
            'icon': '🚀'
        })
    if completed_courses >= 10:
        achievements.append({
            'name': 'Knowledge Master',
            'description': 'Completed 10 courses',
            'icon': '🎓'
        })

    # Skill-based achievements
    skills = set([skill for course_id in st.session_state.completed_courses
                 for skill in courses_df[courses_df['course_id'] == course_id].iloc[0]['skills_gained']])
    if len(skills) >= 10:
        achievements.append({
            'name': 'Skill Collector',
            'description': 'Acquired 10 different skills',
            'icon': '💪'
        })

    # Streak achievements
    streak = calculate_streak()
    if streak >= 7:
        achievements.append({
            'name': 'Consistent Learner',
            'description': 'Maintained a 7-day learning streak',
            'icon': '🔥'
        })

    return achievements


def calculate_streak():
    """Calculate the user's current learning streak"""
    if 'activity_log' not in st.session_state:
        return 0

    streak = 0
    today = datetime.now().date()

    for i in range(30):  # Check last 30 days
        check_date = today - timedelta(days=i)
        if check_date.strftime('%Y-%m-%d') in st.session_state.activity_log:
            streak += 1
        else:
            break

    return streak


def display_enhanced_analytics():
    """Display enhanced analytics dashboard"""
    metrics = calculate_learning_metrics(st.session_state.user_id)
    if not metrics:
        st.info("Complete some courses to see your learning analytics!")
        return

    st.markdown("## 📊 Learning Analytics Dashboard")

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Courses Completed",
                  f"{metrics['completed_courses']}/{metrics['total_courses']}")
    with col2:
        st.metric("Skills Acquired", metrics['total_skills'])
    with col3:
        st.metric("Learning Streak", f"{metrics['learning_streak']} days 🔥")
    with col4:
        st.metric("Study Hours", f"{metrics['estimated_hours']}h")

    # Progress bars
    st.markdown("### 📈 Progress Overview")
    st.progress(metrics['progress_percentage'] / 100)
    st.markdown(
        f"**{metrics['progress_percentage']:.1f}%** of your learning path completed")

    # Achievements
    st.markdown("### 🏆 Achievements")
    achievement_cols = st.columns(3)
    for i, achievement in enumerate(metrics['achievements']):
        with achievement_cols[i % 3]:
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: #f0f0f0; border-radius: 10px; margin: 5px;'>
                <div style='font-size: 2em;'>{achievement['icon']}</div>
                <div style='font-weight: bold;'>{achievement['name']}</div>
                <div style='font-size: 0.9em;'>{achievement['description']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Skill distribution
    if st.session_state.recommended_courses:
        st.markdown("### 🎯 Skill Distribution")
        skill_chart = generate_skill_chart(
            st.session_state.recommended_courses)
        if skill_chart:
            st.altair_chart(skill_chart, use_container_width=True)

# Add a new tab for the chatbot


def chatbot_tab():
    st.header("AI Learning Assistant")

    # Initialize session state for chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history in a scrollable container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(
                f'<div class="chat-message-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:  # assistant
            st.markdown(
                f'<div class="chat-message-assistant"><b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input with improved styling
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "", placeholder="Type your message here...", key="chat_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("Send", use_container_width=True)

    def handle_chat_message(input_text):
        # Add user message to chat history
        st.session_state.chat_history.append(
            {"role": "user", "content": input_text})

        # Generate response based on input
        if "prime numbers code" in input_text.lower():
            bot_response = "Here's a simple Python code to find prime numbers:\n```python\ndef is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprint([i for i in range(1, 101) if is_prime(i)])\n```"
        elif "search" in input_text.lower():
            search_results = perform_search(input_text)
            bot_response = f"Search Results: {search_results}"
        else:
            # Generate a more contextual response using the Gemini model
            try:
                prompt = f"""You are an AI Learning Assistant helping a student. 
                           Respond to their question: {input_text}
                           Keep the response concise, informative, and educational."""
                response = model.generate_content(prompt)
                bot_response = response.text
            except Exception as e:
                bot_response = "I'm here to help with your learning journey! How can I assist you today?"

        # Add assistant response to chat history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_response})

    if send_button and user_input:
        handle_chat_message(user_input)
        st.experimental_rerun()

    # Handle Enter key press for sending messages
    if user_input and user_input != st.session_state.get('previous_input', ''):
        st.session_state.previous_input = user_input
        if '\n' in user_input:
            handle_chat_message(user_input.replace('\n', ''))
            st.experimental_rerun()

    # Suggested questions for new users
    if not st.session_state.chat_history:
        st.markdown("### Suggested Questions")
        col1, col2 = st.columns(2)

        suggestions = [
            "What courses do you recommend for beginners in data science?",
            "How can I improve my programming skills?",
            "What learning path should I follow for web development?",
            "Can you suggest study techniques for my visual learning style?",
            "What are the trending topics in machine learning?"
        ]

        with col1:
            for i in range(0, len(suggestions), 2):
                if st.button(suggestions[i], key=f"suggestion_{i}", use_container_width=True,
                             help="Click to ask this question"):
                    handle_chat_message(suggestions[i])
                    st.experimental_rerun()

        with col2:
            for i in range(1, len(suggestions), 2):
                if st.button(suggestions[i], key=f"suggestion_{i}", use_container_width=True,
                             help="Click to ask this question"):
                    handle_chat_message(suggestions[i])
                    st.experimental_rerun()


def perform_search(query):
    # Example search logic (searching in course titles)
    results = []
    for _, course in courses_df.iterrows():
        if query.lower() in course['title'].lower():
            results.append(course['title'])
    return results if results else "No results found."

# Main application


def main():
    # Header with improved visibility
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.title("EduPathfinder: Your Personalized Learning Journey")

    # Initialize session state
    init_session_state()

    # Create tabs for different sections
    tabs = st.tabs([
        "👤 Profile",
        "📚 Recommendations",
        "📊 Learning Analytics",
        "👥 Community Content",
        "📈 Enhanced Analytics",  # New tab
        "💬 Chatbot Assistance",  # New tab
        "ℹ️ About"
    ])

    with tabs[0]:  # Profile Tab
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<h2>Your Learning Profile</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.form("profile_form"):
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown('<h3>Personal Information</h3>',
                            unsafe_allow_html=True)

                # Profile Picture Upload
                uploaded_file = st.file_uploader(
                    "Upload Profile Picture", type=['png', 'jpg', 'jpeg'])
                if uploaded_file:
                    profile_picture = load_profile_picture(uploaded_file)
                    if profile_picture:
                        st.image(profile_picture, width=150)
                        st.session_state.profile['profile_picture'] = profile_picture
                elif st.session_state.profile.get('profile_picture'):
                    st.image(
                        st.session_state.profile['profile_picture'], width=150)

                name = st.text_input(
                    "Name (Optional)",
                    help="Enter your name to personalize your experience"
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # Skills Assessment
                st.markdown(
                    '<div class="info-box" style="margin-top: 20px;">', unsafe_allow_html=True)
                st.markdown('<h3>Skills Assessment</h3>',
                            unsafe_allow_html=True)

                assessment_questions = get_skills_assessment_questions()
                responses = []

                for category, questions in assessment_questions.items():
                    st.markdown(f"#### {category}")
                    for q in questions:
                        response = st.selectbox(
                            q["question"],
                            options=q["options"],
                            key=f"skill_{category}_{q['question']}"
                        )
                        responses.append(response)

                # Calculate and store skill level
                if responses:
                    skill_level = calculate_skill_level(responses)
                    st.session_state.profile['skills_assessment'] = {
                        'responses': responses,
                        'skill_level': skill_level
                    }

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(
                    '<div class="info-box" style="margin-top: 20px;">', unsafe_allow_html=True)
                st.markdown('<h3>Learning Preferences</h3>',
                            unsafe_allow_html=True)

                interests = st.text_area(
                    "What are your interests and topics you'd like to learn about?",
                    placeholder="e.g., Machine Learning, Web Development, Cybersecurity...",
                    help="List your technical interests, separated by commas"
                )

                learning_style = st.selectbox(
                    "What's your preferred learning style?",
                    list(learning_styles_characteristics.keys()),
                    help="Choose the learning style that best matches how you prefer to learn"
                )

                career_goal = st.text_area(
                    "What are your career goals or target roles?",
                    placeholder="e.g., Data Scientist, Software Engineer, Cloud Architect...",
                    help="Describe your target job roles or career aspirations"
                )

                experience_level = st.select_slider(
                    "Your current experience level",
                    options=["Beginner", "Intermediate", "Advanced"],
                    help="Select your current level of experience in your field of interest"
                )

                st.markdown('</div>', unsafe_allow_html=True)

                submit = st.form_submit_button("Save Profile")

                if submit:
                    if not interests or not career_goal:
                        st.error(
                            "Please fill in your interests and career goals.")
                    else:
                        st.session_state.profile.update({
                            'name': name,
                            'interests': interests,
                            'learning_style': learning_style,
                            'career_goal': career_goal,
                            'experience_level': experience_level
                        })

                        # Show balloons
                        st.balloons()

                        # Custom animation
                        st.markdown("""
                        <style>
                        @keyframes celebrate {
                            0% { transform: scale(1); }
                            50% { transform: scale(1.1); }
                            100% { transform: scale(1); }
                        }
                        .celebration-container {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-top: 20px;
                        }
                        .celebration-icon {
                            font-size: 2em;
                            margin: 0 10px;
                            animation: celebrate 1s ease-out infinite;
                        }
                        .celebration-text {
                            font-size: 1.5em;
                            color: #4a148c;
                            animation: celebrate 1s ease-out infinite;
                        }
                        </style>
                        <div class="celebration-container">
                            <div class="celebration-icon">🎉</div>
                            <div class="celebration-icon">🎨</div>
                            <div class="celebration-icon">🚀</div>
                            <div class="celebration-text">Profile Saved Successfully!</div>
                            <div class="celebration-icon">📚</div>
                            <div class="celebration-icon">💫</div>
                            <div class="celebration-icon">🌟</div>
                        </div>
                        """, unsafe_allow_html=True)

        with col2:
            # Progress Tracking
            if st.session_state.recommended_courses:
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown('<h3>Learning Progress</h3>',
                            unsafe_allow_html=True)

                # Display progress bar
                progress = st.session_state.profile.get('progress', {})
                if progress:
                    progress_percentage = progress.get(
                        'progress_percentage', 0)
                    st.progress(progress_percentage / 100)
                    st.markdown(
                        f"**Overall Progress:** {progress_percentage:.1f}%")
                    st.markdown(
                        f"**Completed Courses:** {progress.get('completed_courses', 0)}/{progress.get('total_courses', 0)}")

                # Display Milestones
                st.markdown("#### 🏆 Achieved Milestones")
                milestones = st.session_state.profile.get('milestones', [])
                if milestones:
                    for milestone in milestones:
                        st.markdown(f"- {milestone['name']}")
                else:
                    st.markdown("Complete courses to earn milestones!")

                st.markdown('</div>', unsafe_allow_html=True)

            # Course Tracking
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown('<h3>Course Tracking</h3>', unsafe_allow_html=True)

            if st.session_state.recommended_courses:
                for course_id in st.session_state.recommended_courses:
                    course = courses_df[courses_df['course_id']
                                        == course_id].iloc[0]
                    completed = course_id in st.session_state.completed_courses

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{course['title']}**")
                    with col2:
                        if completed:
                            st.markdown("✅ Completed")
                        else:
                            if st.button("Mark Complete", key=f"complete_{course_id}"):
                                st.session_state.completed_courses.append(
                                    course_id)
                                update_progress_and_milestones()
                                st.experimental_rerun()
            else:
                st.markdown(
                    "Generate recommendations to start tracking courses!")

            st.markdown('</div>', unsafe_allow_html=True)

            if learning_style:
                display_learning_style_resources(learning_style)

        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]:  # Recommendations Tab
        st.header("Your Personalized Learning Path")

        # Check if profile is complete
        if not st.session_state.profile.get('interests') or not st.session_state.profile.get('career_goal'):
            st.info(
                "Please complete your profile in the Profile tab to get personalized recommendations.")
        else:
            if st.button("Generate Recommendations"):
                with st.spinner("Analyzing your profile and generating personalized recommendations..."):
                    # Add a slight delay to simulate processing
                    time.sleep(1.5)

                    # Get recommendations
                    recommended_course_ids = get_personalized_recommendations(
                        st.session_state.profile['interests'],
                        st.session_state.profile['learning_style'],
                        st.session_state.profile['career_goal'],
                        st.session_state.profile.get(
                            'experience_level', 'Beginner')
                    )

                    # Store recommendations in session state
                    st.session_state.recommended_courses = recommended_course_ids

            # Display recommendations if available
            if st.session_state.recommended_courses:
                # Overview of the learning path
                st.subheader("📚 Your Personalized Education Path")

                # Create two columns
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Learning path visualization
                    learning_path_chart = generate_learning_path_visualization(
                        st.session_state.recommended_courses)
                    if learning_path_chart:
                        st.altair_chart(learning_path_chart,
                                        use_container_width=True)

                with col2:
                    # Skills visualization
                    skill_chart = generate_skill_chart(
                        st.session_state.recommended_courses)
                    if skill_chart:
                        st.altair_chart(skill_chart, use_container_width=True)

                # Display detailed course recommendations
                st.subheader("Recommended Courses")

                for i, course_id in enumerate(st.session_state.recommended_courses, 1):
                    course = courses_df[courses_df['course_id']
                                        == course_id].iloc[0]

                    # Generate explanation for this recommendation
                    explanation = get_course_explanation(
                        course,
                        st.session_state.profile['interests'],
                        st.session_state.profile['learning_style'],
                        st.session_state.profile['career_goal']
                    )

                    # Use the new display function with resources
                    display_course_with_resources(course, i, explanation)

    with tabs[2]:  # Learning Analytics Tab
        st.header("Learning Analytics")

        if not st.session_state.recommended_courses:
            st.info("Generate recommendations first to see your learning analytics.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Curriculum Breakdown")

                # Get category distribution
                recommended_courses = [courses_df[courses_df['course_id'] == id].iloc[0]
                                       for id in st.session_state.recommended_courses]
                categories = [course['category']
                              for course in recommended_courses]
                category_counts = pd.Series(
                    categories).value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']

                # Create pie chart
                fig, ax = plt.subplots(figsize=(5, 5))
                ax.pie(category_counts['Count'], labels=category_counts['Category'], autopct='%1.1f%%',
                       startangle=90, shadow=False)
                ax.axis('equal')
                st.pyplot(fig)

            with col2:
                st.subheader("Difficulty Progression")

                # Map difficulty levels to numeric values
                difficulty_map = {'Beginner': 1,
                                  'Intermediate': 2, 'Advanced': 3}

                # Create difficulty progression data
                difficulty_data = pd.DataFrame({
                    'Course': [course['title'] for course in recommended_courses],
                    'Difficulty': [difficulty_map[course['difficulty']] for course in recommended_courses],
                    'Order': range(1, len(recommended_courses) + 1)
                })

                # Create line chart
                difficulty_chart = alt.Chart(difficulty_data).mark_line(point=True).encode(
                    x=alt.X('Order:O', title='Course Order'),
                    y=alt.Y('Difficulty:Q', title='Difficulty Level',
                            scale=alt.Scale(domain=[0.5, 3.5])),
                    tooltip=['Course', 'Order']
                ).properties(
                    title='Learning Path Difficulty Progression',
                    width=350,
                    height=250
                )

                st.altair_chart(difficulty_chart, use_container_width=True)

                # Add legend for difficulty levels
                st.markdown("""
                *Difficulty Scale:*
                - 1: Beginner
                - 2: Intermediate
                - 3: Advanced
                """)

            # Estimated completion time
            total_weeks = sum(course['duration_weeks']
                              for course in recommended_courses)
            st.markdown(
                f"### ⏱ Estimated Completion Time: *{total_weeks} weeks*")

            # Calculate hours per week based on difficulty
            hours_per_week = {
                'Beginner': 5,
                'Intermediate': 8,
                'Advanced': 12
            }

            total_hours = sum(hours_per_week[course['difficulty']] *
                              course['duration_weeks'] for course in recommended_courses)
            st.markdown(
                f"### 🕒 Total Estimated Study Hours: *{total_hours} hours*")

            # Weekly commitment recommendation
            st.markdown(
                f"### 📅 Recommended Weekly Commitment: *10-15 hours per week*")

    with tabs[3]:  # Community Content Tab
        st.header("Community Content")

        # Initialize content data in session state
        if 'user_content' not in st.session_state:
            st.session_state.user_content = load_user_content()
        if 'content_ratings' not in st.session_state:
            st.session_state.content_ratings = load_content_ratings()
        if 'content_versions' not in st.session_state:
            st.session_state.content_versions = load_content_versions()

        # Content submission form
        with st.expander("📝 Submit New Content"):
            st.subheader("Share Your Knowledge")
            title = st.text_input("Title")
            description = st.text_area("Description")
            content_type = st.selectbox(
                "Content Type",
                ["tutorial", "project", "resource"]
            )
            content = st.text_area("Content (Markdown format)")
            tags = st.multiselect(
                "Tags",
                ["python", "machine-learning", "web-development", "data-science",
                 "algorithms", "visualization", "cloud", "database", "security"]
            )

            if st.button("Submit for Review"):
                if title and description and content and tags:
                    content_id = submit_user_content(
                        title, description, content_type, content, tags)
                    st.success("Content submitted for review! 🎉")
                else:
                    st.error("Please fill in all required fields.")

        # Content browsing and interaction
        st.subheader("Browse Community Content")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            type_filter = st.multiselect(
                "Filter by Type",
                st.session_state.user_content['content_type'].unique()
            )
        with col2:
            status_filter = st.multiselect(
                "Filter by Status",
                st.session_state.user_content['status'].unique()
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Latest", "Most Popular", "Highest Rated"]
            )

        # Apply filters
        filtered_content = st.session_state.user_content.copy()
        if type_filter:
            filtered_content = filtered_content[filtered_content['content_type'].isin(
                type_filter)]
        if status_filter:
            filtered_content = filtered_content[filtered_content['status'].isin(
                status_filter)]

        # Sort content
        if sort_by == "Latest":
            filtered_content = filtered_content.sort_values(
                'created_at', ascending=False)
        elif sort_by == "Most Popular":
            filtered_content = filtered_content.sort_values(
                'votes', ascending=False)
        else:  # Highest Rated
            filtered_content = filtered_content.sort_values(
                'rating', ascending=False)

        # Display content cards
        for _, content in filtered_content.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="content-card">
                    <h3>{content['title']}</h3>
                    <p><strong>Type:</strong> {content['content_type'].title()} | 
                       <strong>Status:</strong> {content['status'].title()} | 
                       <strong>Rating:</strong> {'⭐' * int(content['rating'])} ({content['votes']} votes)</p>
                    <p>{content['description']}</p>
                    <p><strong>Tags:</strong> {', '.join(content['tags'])}</p>
                </div>
                """, unsafe_allow_html=True)

                # Content actions
                col1, col2, col3 = st.columns(3)

                with col1:
                    # View content versions
                    versions = st.session_state.content_versions[
                        st.session_state.content_versions['content_id'] == content['content_id']
                    ]
                    if not versions.empty:
                        version_number = st.selectbox(
                            "Version",
                            versions['version_number'],
                            key=f"version_{content['content_id']}"
                        )
                        selected_version = versions[versions['version_number']
                                                    == version_number].iloc[0]
                        if st.button("View Content", key=f"view_{content['content_id']}"):
                            st.markdown("### Content")
                            st.markdown(content['content'])
                            st.markdown(
                                f"*Version {version_number} - {selected_version['created_at']}*")

                with col2:
                    # Rating system
                    rating = st.slider(
                        "Rate this content",
                        1, 5, 3,
                        key=f"rating_{content['content_id']}"
                    )
                    comment = st.text_input(
                        "Comment",
                        key=f"comment_{content['content_id']}"
                    )
                    if st.button("Submit Rating", key=f"submit_rating_{content['content_id']}"):
                        submit_content_rating(
                            content['content_id'], rating, comment)
                        st.success("Rating submitted! 🌟")

                with col3:
                    # Content moderation (for admins)
                    if content['status'] == 'pending':
                        if st.button("Approve", key=f"approve_{content['content_id']}"):
                            moderate_content(content['content_id'], 'approve')
                            st.success("Content approved! ✅")
                        if st.button("Reject", key=f"reject_{content['content_id']}"):
                            moderate_content(content['content_id'], 'reject')
                            st.error("Content rejected ❌")

                    # Version control
                    if st.button("Create New Version", key=f"new_version_{content['content_id']}"):
                        new_content = st.text_area(
                            "Updated Content",
                            content['content'],
                            key=f"updated_content_{content['content_id']}"
                        )
                        changes = st.text_input(
                            "Change Description",
                            key=f"changes_{content['content_id']}"
                        )
                        if st.button("Submit New Version", key=f"submit_version_{content['content_id']}"):
                            create_content_version(
                                content['content_id'], new_content, changes)
                            st.success("New version created! 📝")

    with tabs[4]:  # Enhanced Analytics Tab
        display_enhanced_analytics()

    with tabs[5]:  # Chatbot Assistance Tab
        chatbot_tab()

    with tabs[6]:  # About Tab
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<h2>About EduPathfinder</h2>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            <h3>Our Mission</h3>
            <p>
                EduPathfinder is dedicated to revolutionizing educational journeys by creating personalized learning paths 
                that align with each student's unique learning style, interests, and career aspirations. We believe that 
                education should be tailored to the individual, not the other way around.
            </p>
        </div>

        <div class="info-box">
            <h3>How It Works</h3>
            <p>Our advanced recommendation system uses a combination of:</p>
            <ul>
                <li><strong>Content-Based Filtering:</strong> Matching your interests and goals with course content</li>
                <li><strong>Collaborative Filtering:</strong> Learning from patterns of similar users</li>
                <li><strong>AI-Powered Analysis:</strong> Using Google's Gemini AI for intelligent recommendations</li>
                <li><strong>Learning Style Optimization:</strong> Adapting suggestions to your preferred learning methods</li>
            </ul>
        </div>

        <div class="info-box">
            <h3>Privacy and Data Usage</h3>
            <p>
                We value your privacy. Your learning data is used only to improve your recommendations and is never shared with third parties.
            </p>
        </div>

        <div class="info-box">
            <h3>Contact Us</h3>
            <p>
                For support or feedback, please contact us at:<br>
                <a href="mailto:support@edupathfinder.com">support@edupathfinder.com</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
else:
    # This will run when Streamlit imports the script
    main()
