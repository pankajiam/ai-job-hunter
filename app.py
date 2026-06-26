# app.py - Main Streamlit Application
import streamlit as st
import pandas as pd
# plotly removed for compatibility
import os
import json
from datetime import datetime

# Import our custom modules
from database.db import get_connection, create_tables
from modules.resume_parser import extract_text_from_pdf, save_uploaded_file
from modules.ats_analyzer import analyze_resume
from modules.job_search import search_jobs_jsearch
from modules.matcher import match_resume_to_job
from modules.email_generator import generate_cold_email
from modules.smtp_sender import send_email
from modules.career_coach import generate_career_roadmap

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Hunter Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on startup
create_tables()

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🎯 AI Job Hunter Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-powered job search companion for students & freshers</div>', unsafe_allow_html=True)
st.divider()

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
    st.title("Navigation")
    
    page = st.radio("Go to:", [
        "📄 Resume Analyzer",
        "🔍 Job Search",
        "🎯 Resume Matcher",
        "✉️ Email Generator",
        "📊 Application Tracker",
        "🎓 Career Coach"
    ])
    
    st.divider()
    st.markdown("**💡 Quick Tips**")
    st.info("Upload your resume first to unlock all features!")

# Store resume text in session state so it persists across pages
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "ats_result" not in st.session_state:
    st.session_state.ats_result = None
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: RESUME ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
if page == "📄 Resume Analyzer":
    st.header("📄 Resume Analyzer & ATS Scorer")
    st.write("Upload your resume PDF to get an ATS score, skill analysis, and improvement tips.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])
        candidate_name = st.text_input("Your Name", placeholder="e.g., Rahul Sharma")
        
        if uploaded_file and candidate_name:
            if st.button("🔍 Analyze My Resume", type="primary", use_container_width=True):
                with st.spinner("Reading your resume... please wait..."):
                    # Save and extract text
                    file_path = save_uploaded_file(uploaded_file)
                    resume_text = extract_text_from_pdf(file_path)
                    
                    # Store in session state
                    st.session_state.resume_text = resume_text
                    st.session_state.candidate_name = candidate_name
                    
                    # Analyze with AI
                    with st.spinner("AI is analyzing your resume..."):
                        result = analyze_resume(resume_text)
                        st.session_state.ats_result = result
                    
                    # Save to database
                    conn = get_connection()
                    conn.execute(
                        "INSERT INTO resumes (filename, content, ats_score) VALUES (?, ?, ?)",
                        (uploaded_file.name, resume_text, result.get("ats_score", 0))
                    )
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Resume analyzed successfully!")
    
    # Show results
    if st.session_state.ats_result:
        result = st.session_state.ats_result
        
        with col2:
            # ATS Score with big visual
            score = result.get("ats_score", 0)
            if score >= 75:
                score_color = "🟢"
                score_label = "Excellent!"
            elif score >= 50:
                score_color = "🟡"
                score_label = "Good, can improve"
            else:
                score_color = "🔴"
                score_label = "Needs improvement"
            
            st.metric(
                label="ATS Score",
                value=f"{score}/100",
                delta=score_label
            )
            
            # Progress bar
            st.progress(score / 100)
        
        st.divider()
        
        # Three columns for details
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.subheader("✅ Skills Found")
            for skill in result.get("skills_found", []):
                st.markdown(f"• {skill}")
        
        with c2:
            st.subheader("❌ Missing Keywords")
            for kw in result.get("missing_keywords", []):
                st.markdown(f"• {kw}")
        
        with c3:
            st.subheader("💡 Suggestions")
            for i, sug in enumerate(result.get("suggestions", []), 1):
                st.markdown(f"{i}. {sug}")
        
        st.divider()
        st.subheader("📝 AI-Generated Professional Summary")
        st.info(result.get("summary", ""))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: JOB SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Job Search":
    st.header("🔍 Job Search")
    st.write("Search for jobs by role and location.")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        role = st.text_input("Job Role", placeholder="e.g., Data Scientist, Python Developer")
    with col2:
        location = st.text_input("Location", placeholder="e.g., Bangalore, Remote India")
    with col3:
        st.write("")  # spacing
        st.write("")  # spacing
        search_btn = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_btn and role:
        with st.spinner(f"Searching for {role} jobs in {location}..."):
            jobs = search_jobs_jsearch(role, location)
        
        if jobs:
            st.success(f"Found {len(jobs)} jobs!")
            
            # Save jobs to database
            conn = get_connection()
            for job in jobs:
                conn.execute(
                    "INSERT INTO jobs (title, company, location, description, url, source) VALUES (?,?,?,?,?,?)",
                    (job["title"], job["company"], job["location"], job["description"], job["url"], job["source"])
                )
            conn.commit()
            conn.close()
            
            # Display as cards
            for i, job in enumerate(jobs):
                with st.expander(f"💼 {job['title']} at {job['company']} — {job['location']}"):
                    st.write(f"**📍 Location:** {job['location']}")
                    st.write(f"**🏢 Company:** {job['company']}")
                    st.write(f"**📄 Description:**")
                    st.write(job['description'])
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.link_button("🔗 Apply Now", job['url'])
                    with col_b:
                        # Quick apply tracker
                        if st.button(f"✅ Mark as Applied", key=f"apply_{i}"):
                            conn = get_connection()
                            conn.execute(
                                "INSERT INTO applications (job_title, company, status) VALUES (?,?,?)",
                                (job['title'], job['company'], 'Applied')
                            )
                            conn.commit()
                            conn.close()
                            st.success("Added to Application Tracker!")
        else:
            st.warning("No jobs found. Try a different role or location.")
    
    # Note about API
    st.divider()
    with st.expander("ℹ️ How to get real job listings?"):
        st.write("""
        Currently showing demo jobs. To get real job listings:
        1. Go to **rapidapi.com** and create a free account
        2. Search for **JSearch API** and subscribe (free tier available)
        3. Copy your API key
        4. Add to your `.env` file: `RAPIDAPI_KEY=your_key_here`
        5. Restart the app
        """)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: RESUME MATCHER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Resume Matcher":
    st.header("🎯 Resume-to-Job Matcher")
    st.write("Paste a job description to see how well your resume matches it.")
    
    if not st.session_state.resume_text:
        st.warning("⚠️ Please go to **Resume Analyzer** first and upload your resume!")
    else:
        st.success(f"✅ Resume loaded for: {st.session_state.candidate_name}")
        
        job_description = st.text_area(
            "Paste the Job Description here:",
            height=200,
            placeholder="Copy and paste the full job description from LinkedIn/Naukri..."
        )
        
        if st.button("🎯 Match My Resume", type="primary") and job_description:
            with st.spinner("AI is comparing your resume with the job..."):
                result = match_resume_to_job(st.session_state.resume_text, job_description)
            
            # Display results
            score = result.get("match_score", 0)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Match Score", f"{score}%")
                st.progress(score / 100)
                
                if score >= 70:
                    st.success("🎉 Great match! Apply confidently.")
                elif score >= 40:
                    st.warning("📝 Decent match. Improve a few skills first.")
                else:
                    st.error("❌ Low match. Consider upskilling before applying.")
            
            with col2:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("✅ Matching Skills")
                    for skill in result.get("matching_skills", []):
                        st.markdown(f"✅ {skill}")
                with c2:
                    st.subheader("❌ Missing Skills")
                    for skill in result.get("missing_skills", []):
                        st.markdown(f"❌ {skill}")
            
            st.divider()
            st.subheader("💡 How to Improve Your Resume for This Job")
            st.info(result.get("recommendation", ""))

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: EMAIL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✉️ Email Generator":
    st.header("✉️ Cold Email & LinkedIn Message Generator")
    st.write("Generate personalized outreach emails to recruiters.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Your Name", value=st.session_state.candidate_name)
        job_title = st.text_input("Job Title you're applying for", placeholder="e.g., Data Analyst")
        company = st.text_input("Company Name", placeholder="e.g., Google, TCS, Startup")
        recruiter = st.text_input("Recruiter Name (optional)", placeholder="e.g., Priya Sharma")
    
    with col2:
        summary = st.text_area(
            "Brief About Yourself",
            height=150,
            placeholder="e.g., Final year B.Tech student with skills in Python, ML, and data analysis. Built 3 projects on GitHub."
        )
    
    if st.button("✨ Generate Email & Messages", type="primary"):
        if name and job_title and company and summary:
            with st.spinner("AI is writing your emails..."):
                result = generate_cold_email(name, summary, job_title, company, recruiter or "Hiring Manager")
            
            # Show results in tabs
            tab1, tab2, tab3 = st.tabs(["📧 Cold Email", "💼 LinkedIn Message", "🔄 Follow-up Email"])
            
            with tab1:
                st.subheader("Subject:")
                st.code(result.get("cold_email_subject", ""))
                st.subheader("Email Body:")
                st.text_area("", value=result.get("cold_email_body", ""), height=250, key="cold_email")
                
                # Send email option
                st.divider()
                to_email = st.text_input("Send this email to:", placeholder="recruiter@company.com", key="send_cold")
                if st.button("📤 Send Email Now", key="send_cold_btn"):
                    with st.spinner("Sending..."):
                        status = send_email(to_email, result["cold_email_subject"], result["cold_email_body"])
                    if status["success"]:
                        st.success(status["message"])
                        # Log to DB
                        conn = get_connection()
                        conn.execute(
                            "INSERT INTO emails_sent (recipient, subject, body, status) VALUES (?,?,?,?)",
                            (to_email, result["cold_email_subject"], result["cold_email_body"], "Sent")
                        )
                        conn.commit()
                        conn.close()
                    else:
                        st.error(status["message"])
            
            with tab2:
                st.subheader("LinkedIn Connection Request Message:")
                st.text_area("", value=result.get("linkedin_message", ""), height=100, key="linkedin_msg")
                st.info("👆 Copy this and paste it when sending a LinkedIn connection request!")
            
            with tab3:
                st.subheader("Subject:")
                st.code(result.get("followup_email_subject", ""))
                st.subheader("Follow-up Email Body:")
                st.text_area("", value=result.get("followup_email_body", ""), height=200, key="followup_email")
        else:
            st.warning("Please fill all fields!")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: APPLICATION TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Application Tracker":
    st.header("📊 Application Tracker Dashboard")
    
    # Add new application
    with st.expander("➕ Add New Application"):
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input("Job Title")
            new_company = st.text_input("Company")
        with col2:
            new_status = st.selectbox("Status", ["Applied", "Interview Scheduled", "Rejected", "Offer Received"])
            new_notes = st.text_input("Notes (optional)")
        
        if st.button("Add Application"):
            if new_title and new_company:
                conn = get_connection()
                conn.execute(
                    "INSERT INTO applications (job_title, company, status, notes) VALUES (?,?,?,?)",
                    (new_title, new_company, new_status, new_notes)
                )
                conn.commit()
                conn.close()
                st.success("✅ Application added!")
                st.rerun()
    
    # Load all applications
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM applications ORDER BY applied_at DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No applications tracked yet. Search for jobs and click 'Mark as Applied'!")
    else:
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applied", len(df))
        with col2:
            interviews = len(df[df['status'] == 'Interview Scheduled'])
            st.metric("Interviews", interviews)
        with col3:
            rejected = len(df[df['status'] == 'Rejected'])
            st.metric("Rejected", rejected)
        with col4:
            offers = len(df[df['status'] == 'Offer Received'])
            st.metric("Offers 🎉", offers)
        
        st.divider()
        
        # Pie chart
        if len(df) > 0:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
           st.bar_chart(status_counts.set_index('Status'))
        # Application table
        st.subheader("All Applications")
        
        # Allow status update
        for idx, row in df.iterrows():
            with st.expander(f"💼 {row['job_title']} at {row['company']} — {row['status']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Applied on:** {row['applied_at']}")
                    st.write(f"**Notes:** {row['notes'] or 'None'}")
                with col_b:
                    new_s = st.selectbox(
                        "Update Status:", 
                        ["Applied", "Interview Scheduled", "Rejected", "Offer Received"],
                        index=["Applied", "Interview Scheduled", "Rejected", "Offer Received"].index(row['status']),
                        key=f"status_{row['id']}"
                    )
                    if st.button("Update", key=f"update_{row['id']}"):
                        conn = get_connection()
                        conn.execute("UPDATE applications SET status=? WHERE id=?", (new_s, row['id']))
                        conn.commit()
                        conn.close()
                        st.success("Status updated!")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6: CAREER COACH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎓 Career Coach":
    st.header("🎓 AI Career Coach")
    st.write("Get a personalized learning roadmap, project ideas, and interview prep guide.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_role = st.text_input(
            "What role do you want to achieve?",
            placeholder="e.g., Machine Learning Engineer, Full Stack Developer, Data Analyst"
        )
    
    with col2:
        current_skills = st.text_area(
            "What skills do you currently have?",
            height=100,
            placeholder="e.g., Python basics, some SQL, built 1 project in college"
        )
    
    if st.button("🚀 Generate My Career Roadmap", type="primary"):
        if target_role and current_skills:
            with st.spinner("AI Career Coach is creating your personalized roadmap..."):
                result = generate_career_roadmap(target_role, current_skills)
            
            # Timeline
            st.success(f"⏱️ Estimated time to job-ready: **{result.get('timeline', '3-6 months')}**")
            
            # Motivational message
            st.info(f"💪 {result.get('motivational_message', '')}")
            
            st.divider()
            
            # Four sections
            tab1, tab2, tab3, tab4 = st.tabs(["📚 Learning Roadmap", "🔨 Project Ideas", "🎤 Interview Prep", "⚡ Skill Gaps"])
            
            with tab1:
                st.subheader("Your Step-by-Step Learning Roadmap")
                for step in result.get("learning_roadmap", []):
                    if isinstance(step, dict):
                        with st.expander(f"📖 {step.get('step', 'Step')} ({step.get('duration', '')})"):
                            resources = step.get('resources', [])
                            if isinstance(resources, list):
                                for r in resources:
                                    st.markdown(f"• {r}")
                            else:
                                st.write(resources)
                    else:
                        st.markdown(f"• {step}")
            
            with tab2:
                st.subheader("Portfolio Projects to Build")
                for i, project in enumerate(result.get("recommended_projects", []), 1):
                    st.markdown(f"**{i}.** {project}")
            
            with tab3:
                st.subheader("Interview Topics & Questions")
                for i, topic in enumerate(result.get("interview_prep", []), 1):
                    st.markdown(f"**Q{i}.** {topic}")
            
            with tab4:
                st.subheader("Skills You Need to Learn")
                for skill in result.get("skill_gaps", []):
                    st.markdown(f"❌ {skill}")
        else:
            st.warning("Please fill in both fields!")