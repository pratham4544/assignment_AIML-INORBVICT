import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Configuration ---
GITHUB_USERNAME = 'pratham4544' # Your GitHub username

# Set page config for wider layout and a nice title
st.set_page_config(
    page_title="Pratham - Developer Portfolio",
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    /* Main styling for the Streamlit app */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Profile picture styling */
    .profile-pic {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 5px solid white;
        margin: 0 auto 2rem;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60px;
        color: #667eea;
        font-weight: bold;
    }
    
    .header-title {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    /* General card styling */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #eee;
    }
    
    /* Project card specific styling */
    .project-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .project-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 25px rgba(0,0,0,0.15);
    }
    
    /* Skill tags styling */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    /* Technology tags for projects */
    .tech-tag {
        display: inline-block;
        background: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    
    /* Statistics section styling */
    .stat-container {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin: 0.5rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Custom button styling */
    .custom-button {
        background: #667eea !important;
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none !important;
        display: inline-block;
        margin: 0.2rem;
        font-weight: 500;
        transition: background 0.3s ease;
        border: none;
    }
    .custom-button:hover {
        background: #5a67d8 !important;
        color: white !important;
        text-decoration: none !important;
    }
    
    /* Social links styling */
    .social-links {
        text-align: center;
        margin-top: 1rem;
    }
    
    .social-link {
        display: inline-block;
        margin: 0 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.2);
        color: white !important;
        text-decoration: none !important;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.3);
        transition: background 0.3s ease;
    }
    .social-link:hover {
        background: rgba(255,255,255,0.4);
        color: white !important;
        text-decoration: none !important;
    }
    
    /* Contact info styling */
    .contact-info {
        font-size: 1.05rem;
        margin-top: 2rem;
    }
    
    .contact-info p {
        margin-bottom: 0.8rem;
    }
    
    .contact-info a {
        color: #667eea !important;
        text-decoration: none !important;
    }
    
    .contact-info a:hover {
        text-decoration: underline !important;
    }
    
    /* Hide Streamlit branding and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# --- Function to fetch GitHub data with caching ---
@st.cache_data(ttl=3600)
def fetch_github_data(username):
    """
    Fetches user profile and repository data from GitHub API.
    """
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"

    try:
        user_response = requests.get(user_url)
        user_response.raise_for_status()
        user_data = user_response.json()

        repos_response = requests.get(repos_url)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        return user_data, repos_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from GitHub: {e}. Please check your internet connection or the username.")
        return None, []

# --- Load GitHub Data ---
user_data, repos_data = None, []
with st.spinner("Fetching your data from GitHub..."):
    user_data, repos_data = fetch_github_data(GITHUB_USERNAME)

# Handle cases where GitHub data cannot be fetched
if not user_data:
    st.error(f"Could not load portfolio. Please ensure the GitHub username '{GITHUB_USERNAME}' is correct and you have an internet connection.")
    st.stop()

# --- Process Data for Portfolio Sections ---
def get_processed_portfolio_data(user_data, repos_data):
    """Processes raw GitHub data into a structured format for the portfolio."""
    
    # Extract languages and count their occurrences
    language_counts = {}
    for repo in repos_data:
        if repo['language']:
            language_counts[repo['language']] = language_counts.get(repo['language'], 0) + 1

    # Convert language counts to percentages for the pie chart
    total_languages_counted = sum(language_counts.values())
    language_percentages = {
        lang: (count / total_languages_counted * 100)
        for lang, count in language_counts.items()
    } if total_languages_counted > 0 else {}

    # Map GitHub repo data to project card format
    projects_list = []
    for repo in repos_data:
        projects_list.append({
            "name": repo['name'],
            "description": repo['description'] if repo['description'] else "No description provided.",
            "technologies": [repo['language']] if repo['language'] else [],
            "github_url": repo['html_url'],
            "demo_url": repo['homepage'] if repo['homepage'] else repo['html_url'],
            "stars": repo['stargazers_count']
        })
    
    # Sort projects by stars in descending order
    projects_list.sort(key=lambda x: x['stars'], reverse=True)

    return {
        "name": user_data.get('name', user_data.get('login', 'Pratham')),
        "title": "Full Stack Developer & Software Engineer",
        "bio": user_data.get('bio', """Hello! I'm Pratham, a passionate software developer with a love for creating 
                 innovative solutions and building amazing user experiences. I specialize in 
                 full-stack development and enjoy working with modern technologies to bring ideas to life."""),
        "email": "prathameshshete609@gmail.com",
        "github": user_data.get('html_url', f"https://github.com/{GITHUB_USERNAME}"),
        "linkedin": "https://www.linkedin.com/in/prathameshshete/",
        "mobile": "9970939341",
        "profile_pic_url": user_data.get('avatar_url', 'https://placehold.co/150x150/cbd5e1/4b5563?text=P'),
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "Streamlit", 
            "FastAPI", "MongoDB", "PostgreSQL", "Docker", "AWS", 
            "Machine Learning", "Data Science", "Git", "CI/CD"
        ],
        "projects": projects_list,
        "stats": {
            "repositories": user_data.get('public_repos', 0),
            "contributions": user_data.get('followers', 0),
            "languages": len(language_counts),
            "years_coding": 3
        },
        "language_percentages": language_percentages
    }

portfolio_data = get_processed_portfolio_data(user_data, repos_data)

# --- Header Section ---
def create_header(data):
    """Creates the header section with profile pic, name, title, and social links."""
    # Center everything using a single column and HTML/CSS
    st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <img src="{data['profile_pic_url']}" alt="Profile Picture" class="profile-pic" style="margin-bottom: 1.5rem;" />
            <div class="header-title">{data['name']}</div>
            <div class="header-subtitle">{data['title']}</div>
            <div class="social-links">
                <a href="{data['github']}" class="social-link" target="_blank">🔗 GitHub</a>
                <a href="{data['linkedin']}" class="social-link" target="_blank">💼 LinkedIn</a>
                <a href="mailto:{data['email']}" class="social-link" target="_blank">📧 Email</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

# --- About Me Section ---
def create_about_section(data):
    """Creates the About Me section with bio and skills."""
    st.markdown("## 👨‍💻 About Me")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <p style="font-size: 1.1rem; line-height: 1.8; color: #555;">
                {data['bio']}
            </p>
            <br>
            <p style="font-size: 1.1rem; line-height: 1.8; color: #555;">
                When I'm not coding, you can find me exploring new technologies, contributing to 
                open-source projects, or sharing my knowledge with the developer community.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛠️ Skills & Technologies")
        skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in data['skills']])
        st.markdown(f'<div class="card">{skills_html}</div>', unsafe_allow_html=True)

# --- GitHub Statistics Section ---
def create_stats_section(data):
    """Creates the GitHub statistics section."""
    st.markdown("## 📊 GitHub Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats_display = [
        (col1, data['stats']['repositories'], "Public Repositories", "📁"),
        (col2, data['stats']['contributions'], "Followers (Proxy)", "👥"),
        (col3, data['stats']['languages'], "Languages Used", "🔤"),
        (col4, data['stats']['years_coding'], "Years Coding", "⏱️")
    ]
    
    for col, number, label, icon in stats_display:
        with col:
            st.markdown(f"""
            <div class="stat-container">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="stat-number">{number}{'+' if label == 'Years Coding' else ''}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

# --- Project Cards Section ---
def create_projects_section(data):
    """Creates the projects section with dynamic project cards."""
    st.markdown("## 🚀 Featured Projects")
    
    if not data['projects']:
        st.info("No public repositories found for this GitHub user.")
        return

    # Create project cards in a two-column grid
    for i in range(0, len(data['projects']), 2):
        col1, col2 = st.columns(2)
        
        for j, col in enumerate([col1, col2]):
            if i + j < len(data['projects']):
                project = data['projects'][i + j]
                
                # Dynamically create tech tags
                tech_tags = "".join([f'<span class="tech-tag">{tech}</span>' for tech in project['technologies']])
                if not project['technologies']:
                    tech_tags = '<span class="tech-tag">General</span>'

                with col:
                    st.markdown(f"""
                    <div class="project-card">
                        <h3 style="color: #2c3e50; margin-bottom: 0.75rem;">
                            {project['name']} 
                            <span style="color: #ffd700; font-size: 0.85rem; margin-left: 0.5rem;">⭐ {project['stars']}</span>
                        </h3>
                        <p style="color: #666; margin-bottom: 1rem; line-height: 1.6; font-size: 0.95rem;">
                            {project['description']}
                        </p>
                        <div style="margin-bottom: 1rem;">
                            {tech_tags}
                        </div>
                        <div>
                            <a href="{project['github_url']}" class="custom-button" target="_blank" style="margin-right: 0.5rem;">
                                🔗 View Code
                            </a>
                            <a href="{project['demo_url']}" class="custom-button" target="_blank">
                                🚀 Live Demo
                            </a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# --- Activity Chart  ---
def create_activity_chart():
    """
    Creates a sample contribution activity chart.
    """
    st.markdown("## 📈 Development Activity")
    
    # Generate sample data for contribution activity
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    contributions = [max(0, int((abs(hash(str(date)) % 20) - 8) * (1 + (date.month % 3) * 0.5))) for date in dates]
    
    df = pd.DataFrame({
        'date': dates,
        'contributions': contributions
    })
    
    fig = px.area(df, x='date', y='contributions', 
                  title='Contribution Activity Over Time ',
                  labels={'contributions': 'Daily Contributions', 'date': 'Date'},
                  color_discrete_sequence=['#667eea'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333'),
        xaxis_showgrid=False,
        yaxis_showgrid=True,
        yaxis_gridcolor='#e0e0e0',
        hovermode="x unified"
    )
    fig.update_traces(mode='lines', line_width=2, fill='tozeroy', opacity=0.8)
    
    st.plotly_chart(fig, use_container_width=True)

# --- Technology Proficiency  ---
def create_technology_proficiency_chart():
    """
    Creates a sample bar chart for technology proficiency.
    """
    st.markdown("### 📊 Technology Proficiency ")
    
    tech_data = {
        'Python': 95, 'JavaScript': 85, 'React': 80, 'Node.js': 75,
        'Streamlit': 90, 'MongoDB': 70, 'Docker': 65, 'AWS': 60
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(tech_data.keys()),
            y=list(tech_data.values()),
            marker_color=['#667eea', '#764ba2', '#667eea', '#764ba2', '#667eea', '#764ba2', '#667eea', '#764ba2']
        )
    ])
    
    fig.update_layout(
        title="Technology Proficiency ",
        xaxis_title="Technologies",
        yaxis_title="Proficiency Level (%)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333'),
        yaxis_range=[0,100]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- Languages Used in Projects (Dynamic Data) ---
def create_languages_pie_chart(language_percentages):
    """Creates a pie chart showing the distribution of languages used in projects."""
    if not language_percentages:
        st.info("No language data available from repositories to generate the chart.")
        return

    languages = list(language_percentages.keys())
    percentages = list(language_percentages.values())
    
    fig = px.pie(values=percentages, names=languages, 
                 title="Languages Used in Projects",
                 color_discrete_sequence=px.colors.sequential.Purp_r)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#333'))
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# --- Projects by Category  ---
def create_projects_by_category_chart():
    """
    Creates a sample bar chart for projects by category.
    """
    st.markdown("### 📂 Categorization of My Projects ")
    project_types = ['Web Apps', 'APIs', 'ML Projects', 'Data Analysis', 'Mobile']
    project_counts = [8, 6, 5, 4, 2]
    
    fig = px.bar(x=project_types, y=project_counts,
                title="Projects by Category ",
                color=project_counts,
                color_continuous_scale=['#667eea', '#764ba2'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#333'),
        xaxis_title="Category",
        yaxis_title="Number of Projects"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Contact Section ---
def create_contact_section(data):
    """Creates the contact section with contact info and a form."""
    st.markdown("## 📬 Get In Touch")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Let's Connect!")
        st.markdown("""
        I'm always interested in hearing about new opportunities and interesting projects. 
        Whether you want to discuss a potential collaboration or just say hello, feel free to reach out!
        """)
        
        # Using Streamlit's native markdown for contact info
        st.markdown("#### Contact Information")
        st.markdown(f"**📧 Email:** {data['email']}")
        st.markdown(f"**🔗 GitHub:** [github.com/{GITHUB_USERNAME}]({data['github']})")
        st.markdown(f"**💼 LinkedIn:** [LinkedIn Profile]({data['linkedin']})")
        st.markdown(f"**📱 Mobile:** {data['mobile']}")
    
    with col2:
        st.markdown("### Send me a message")
        with st.form("contact_form"):
            name = st.text_input("Your Name", placeholder="John Doe")
            email = st.text_input("Your Email", placeholder="john.doe@example.com")
            message = st.text_area("Your Message", height=100, placeholder="Type your message here...")
            
            submitted = st.form_submit_button("Send Message", use_container_width=True)
            
            if submitted:
                if name and email and message:
                    st.success("Thank you for your message! I'll get back to you soon. 🚀")
                else:
                    st.error("Please fill in all fields.")

# --- Favourite Projects Section ---
def create_favourite_projects_section():
    """Creates a section to showcase personal favourite projects with links."""
    st.markdown("## 🌟 My Favourite Projects")
    st.markdown("Here are some of my most exciting and innovative projects that showcase my expertise in AI, NLP, and web development:")

    # List your favourite projects here
    favourite_projects = [
        {
            "name": "Chat with Indian Freedom Fighters 🇮🇳",
            "description": "An educational AI application that brings Indian freedom fighters to life through interactive conversations. Users can chat with historical figures and learn about India's independence struggle in an engaging way.",
            "technologies": ["Python", "Streamlit", "Historical AI", "Educational Tech"],
            "demo_url": "https://chat-with-indian-freedom-fighters.streamlit.app/",
            "features": ["Historical figure simulation", "Educational content", "Interactive learning"]
        },
        {
            "name": "Chat with Gita 🕉️",
            "description": "An interactive AI-powered chatbot that allows users to have meaningful conversations with the wisdom of the Bhagavad Gita. Built using advanced NLP techniques and Streamlit for an intuitive user experience.",
            "technologies": ["Python", "Streamlit", "NLP", "AI", "RAG"],
            "demo_url": "https://chat-with-gita.streamlit.app/",
            "features": ["Interactive chat interface", "Contextual responses", "Ancient wisdom accessibility"]
        },
        {
            "name": "Bulk Email Sender 📧",
            "description": "A powerful bulk email automation tool with advanced features like personalization, scheduling, and analytics. Perfect for marketing campaigns and newsletter distribution with a user-friendly interface.",
            "technologies": ["Python", "Streamlit", "SMTP", "Email APIs", "Automation"],
            "demo_url": "https://bulk-email-sender.streamlit.app/",
            "features": ["Bulk email sending", "Template customization", "Analytics dashboard"]
        },
        {
            "name": "RAG Evaluator 🔍",
            "description": "A comprehensive evaluation framework for Retrieval-Augmented Generation (RAG) systems. This tool helps assess the performance, accuracy, and effectiveness of RAG implementations with detailed metrics and analysis.",
            "technologies": ["Python", "Streamlit", "RAG", "ML Evaluation", "NLP"],
            "demo_url": "https://rag-evaluator.streamlit.app/",
            "features": ["Performance metrics", "Accuracy assessment", "Comparative analysis"]
        },
        {
            "name": "Multi-LLM Summarization Tool 📝",
            "description": "An advanced text summarization application powered by Large Language Models. Capable of processing long documents and generating concise, accurate summaries while preserving key information and context.",
            "technologies": ["Python", "Streamlit", "LLM", "Text Processing", "AI"],
            "demo_url": "https://summarization-llm-0.streamlit.app/",
            "features": ["Multi-document summarization", "Customizable length", "Context preservation"]
        }
    ]

    # Create project cards in a grid layout
    for i, project in enumerate(favourite_projects):
        # Create alternating layout for visual appeal
        if i % 2 == 0:
            col1, col2 = st.columns([2, 1])
            main_col, side_col = col1, col2
        else:
            col1, col2 = st.columns([1, 2])
            main_col, side_col = col2, col1
        
        with main_col:
            # Technology tags
            tech_tags = "".join([f'<span class="tech-tag">{tech}</span>' for tech in project['technologies']])
            
            st.markdown(f"""
            <div class="project-card">
                <h3 style="color: #2c3e50; margin-bottom: 0.75rem;">
                    {project['name']}
                    <span style="color: #667eea; font-size: 0.7rem; margin-left: 0.5rem;">✨ FEATURED</span>
                </h3>
                <p style="color: #666; margin-bottom: 1rem; line-height: 1.6; font-size: 0.95rem;">
                    {project['description']}
                </p>
                <div style="margin-bottom: 1rem;">
                    {tech_tags}
                </div>
                <div style="margin-bottom: 1rem;">
                    <a href="{project['demo_url']}" class="custom-button" target="_blank" style="margin-right: 0.5rem;">
                        🚀 Try Live Demo
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with side_col:
            st.markdown("#### Key Features:")
            for feature in project['features']:
                st.markdown(f"• {feature}")
            st.markdown("---")

    # Add a call-to-action section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-top: 2rem;">
        <h3 style="color: white; margin-bottom: 1rem;">🚀 Interested in collaborating?</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1.5rem; opacity: 0.9;">
            I'm always excited to work on innovative projects and explore new technologies. 
            Let's build something amazing together!
        </p>
        <a href="mailto:prathameshshete609@gmail.com" style="background: rgba(255,255,255,0.2); color: white; padding: 0.8rem 2rem; border-radius: 25px; text-decoration: none; font-weight: bold; border: 2px solid rgba(255,255,255,0.3);">
            📧 Let's Connect
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- Main Application Logic ---
def main():
    
    # Header
    create_header(portfolio_data)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👨‍💻 About", 
        "🌟 Favourites",   # Favourites tab moved to second position
        "🚀 Projects", 
        "📈 Analytics", 
        "📬 Contact"
    ])
    
    with tab1:
        create_about_section(portfolio_data)
    
    with tab2:
        create_favourite_projects_section()  # Show favourite projects here
    
    with tab3:
        create_projects_section(portfolio_data)
    
    with tab4:
        create_activity_chart()
        col1, col2 = st.columns(2)
        with col1:
            create_languages_pie_chart(portfolio_data['language_percentages'])
        with col2:
            create_projects_by_category_chart()
    
    with tab5:
        create_contact_section(portfolio_data)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Built with ❤️ using Streamlit | © {datetime.now().year} {portfolio_data['name']}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()