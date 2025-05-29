import streamlit as st
import os
from pymongo import MongoClient
import bcrypt

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["instructor"]
access_students = db["access_students"]

# -------------------- Page Config --------------------
st.set_page_config(page_title="GrowthMate AI Platform", layout="wide")

# -------------------- Imports --------------------
try:
    from student_dashboard import student_dashboard
    from instructor_panel import instructor_dashboard
    from admin_panel import admin_panel
    from student_panel import student_login, student_register, student_forgot_password
    from ai_assessment import main as ai_assessment_main
    from voice import main as voice_main
except Exception as e:
    st.error(f"Import error: {e}")

# Check if accessing through landing page
if 'from_landing' not in st.session_state:
    # Serve the landing page
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, 'index.html')
    
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            landing_page = f.read()
            st.markdown(landing_page, unsafe_allow_html=True)
            st.stop()
    else:
        st.session_state.from_landing = True

# -------------------- Session State Initialization --------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False
if "instructor_logged_in" not in st.session_state:
    st.session_state.instructor_logged_in = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "selected_panel" not in st.session_state:
    st.session_state.selected_panel = None

# -------------------- CSS Styling --------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400&family=Orbitron:wght@700&display=swap');
        .stApp {
            height: 100vh;
        }
        [data-page="welcome"] .stApp {
            background: url("https://i.gifer.com/Ax9R.gif") center/cover;
        }
        [data-page="main"] .stApp {
            background: none !important;
            background-image: none !important;
            background: linear-gradient(to right, #1e3c72, #2a5298) !important;
            position: relative;
            overflow: hidden;
        }
        [data-page="main"] .stApp::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                transparent,
                transparent 20px,
                rgba(0, 247, 255, 0.1) 20px,
                rgba(0, 247, 255, 0.1) 22px
            ),
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 20px,
                rgba(0, 247, 255, 0.1) 20px,
                rgba(0, 247, 255, 0.1) 22px
            );
            opacity: 0.3;
            animation: gridPulse 5s infinite;
        }
        @keyframes gridPulse {
            0% { opacity: 0.3; }
            50% { opacity: 0.5; }
            100% { opacity: 0.3; }
        }
        .welcome-container {
            display: none;
        }
        [data-page="welcome"] .welcome-container {
            display: block;
        }
        [data-page="welcome"] .main-container {
            display: none;
        }
        .centered-launch {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            width: 100%;
            max-width: 300px;
            text-align: center;
        }
        .stButton.launch-button > button {
            background: linear-gradient(to right, #00f7ff, #ff00ff);
            color: white !important;
            font-size: 20px;
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.7), 0 0 30px rgba(255, 0, 255, 0.5);
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Orbitron', sans-serif;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            margin: 0 auto;
            width: 100%;
            max-width: 200px;
            position: relative;
            overflow: hidden;
        }
        .stButton.launch-button > button:hover {
            background: linear-gradient(to right, #ff00ff, #00f7ff);
            transform: scale(1.05) rotate(2deg);
            box-shadow: 0 0 30px rgba(0, 247, 255, 1), 0 0 40px rgba(255, 0, 255, 0.8);
        }
        .stButton.launch-button > button::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            transition: left 0.3s ease;
        }
        .stButton.launch-button > button:hover::after {
            left: 100%;
        }
        .welcome-container h1, .welcome-container h4 {
            text-shadow: 0 0 10px #00f7ff, 0 0 20px #ff00ff;
            text-align: center;
            color: white;
            font-family: 'Orbitron', sans-serif;
        }
        .glass-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.3), 0 0 30px rgba(255, 0, 255, 0.2);
            border: 1px solid rgba(0, 247, 255, 0.5);
            margin-top: 30px;
            animation: slideIn 0.5s ease-in-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main-title {
            text-align: center;
            font-size: 48px;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 0 0 15px #00f7ff, 0 0 25px #ff00ff;
            font-family: 'Orbitron', sans-serif;
        }
        .subtitle {
            text-align: center;
            font-size: 22px;
            color: #00f7ff;
            text-shadow: 0 0 10px #00f7ff;
            margin-top: -10px;
            font-family: 'Inter', sans-serif;
        }
        .section-title {
            text-align: center;
            font-size: 28px;
            color: #39ff14;
            text-shadow: 0 0 10px #39ff14;
            margin-top: 30px;
            margin-bottom: 10px;
            font-family: 'Orbitron', sans-serif;
        }
        .stButton.panel-button > button {
            background: linear-gradient(45deg, #00f7ff, #ff00ff);
            color: white !important;
            font-weight: 600;
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            border: 2px solid #00f7ff;
            box-shadow: 0 0 15px rgba(0, 247, 255, 0.7);
            transition: all 0.3s ease;
            font-family: 'Orbitron', sans-serif;
            position: relative;
            overflow: hidden;
            animation: pulse 2s infinite;
        }
        .stButton.panel-button > button:hover {
            background: linear-gradient(45deg, #ff00ff, #00f7ff);
            transform: scale(1.1) rotate(3deg);
            box-shadow: 0 0 25px rgba(255, 0, 255, 1), 0 0 35px rgba(0, 247, 255, 0.8);
            border-color: #ff00ff;
        }
        .stButton.panel-button > button::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.3);
            transition: left 0.4s ease;
        }
        .stButton.panel-button > button:hover::after {
            left: 100%;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 15px rgba(0, 247, 255, 0.7); }
            50% { box-shadow: 0 0 25px rgba(0, 247, 255, 1); }
            100% { box-shadow: 0 0 15px rgba(0, 247, 255, 0.7); }
        }
        .stRadio > div {
            color: #00f7ff;
            font-family: 'Inter', sans-serif;
        }
        .student-panel-radio .stRadio > label > div {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid #00f7ff;
            border-radius: 8px;
            padding: 8px 16px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .student-panel-radio .stRadio > label > div:hover {
            background: rgba(0, 247, 255, 0.2);
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(0, 247, 255, 0.7);
        }
        .student-panel-radio .stRadio > label > input:checked + div {
            background: linear-gradient(45deg, #00f7ff, #ff00ff);
            border-color: #ff00ff;
            color: white;
            box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        }
        .panel-info {
            margin-top: 30px;
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 12px;
            color: #00f7ff;
            box-shadow: 0 0 15px rgba(0, 247, 255, 0.3);
            border: 1px solid rgba(0, 247, 255, 0.5);
        }
        @media (max-width: 768px) {
            .welcome-container h1 {
                font-size: 28px;
            }
            .welcome-container h4 {
                font-size: 18px;
            }
            .stButton.launch-button > button {
                font-size: 16px;
                padding: 12px 24px;
                max-width: 180px;
            }
            .centered-launch {
                bottom: 20px;
                max-width: 250px;
            }
            .main-title {
                font-size: 36px;
            }
            .subtitle {
                font-size: 18px;
            }
            .section-title {
                font-size: 22px;
            }
            .glass-container {
                padding: 1.5rem;
            }
            .stButton.panel-button > button {
                padding: 0.6rem 1rem;
                font-size: 14px;
            }
            .student-panel-radio .stRadio > label > div {
                padding: 6px 12px;
                font-size: 14px;
            }
        }
        @media (max-width: 480px) {
            .welcome-container h1 {
                font-size: 24px;
            }
            .welcome-container h4 {
                font-size: 16px;
            }
            .stButton.launch-button > button {
                font-size: 14px;
                padding: 10px 20px;
                max-width: 160px;
            }
            .centered-launch {
                bottom: 15px;
                max-width: 200px;
            }
            .main-title {
                font-size: 28px;
            }
            .subtitle {
                font-size: 16px;
            }
            .section-title {
                font-size: 20px;
            }
            .glass-container {
                padding: 1rem;
            }
            .stButton.panel-button > button {
                padding: 0.5rem 0.8rem;
                font-size: 12px;
            }
            .student-panel-radio .stRadio > label > div {
                padding: 5px 10px;
                font-size: 12px;
            }
        }
    </style>
    <link rel="preload" href="https://i.gifer.com/Ax9R.gif" as="image">
""", unsafe_allow_html=True)

# -------------------- Functions --------------------
def logout_all_panels():
    st.session_state.student_logged_in = False
    st.session_state.instructor_logged_in = False
    st.session_state.admin_logged_in = False

def student_dashboard_with_modules():
    st.markdown("<h4 style='color:#39ff14;'>🎓 Student Dashboard</h4>", unsafe_allow_html=True)
    module = st.radio("Select Module", ["Text-to-Text", "Voice-to-Voice", "Face-to-Face"], horizontal=True)
    if module == "Text-to-Text":
        st.success("Redirecting to AI Assessment Module...")
        ai_assessment_main()
    elif module == "Voice-to-Voice":
        st.success("Redirecting to Voice Module...")
        voice_main()
    elif module == "Face-to-Face":
        st.warning("🚧 Face-to-Face Module is Coming Soon!")

def main_app():
    if st.session_state.get("student_logged_in"):
        student_dashboard()
        return
    elif st.session_state.get("instructor_logged_in"):
        instructor_dashboard()
        return
    elif st.session_state.get("admin_logged_in"):
        admin_panel()
        return
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>📚 GrowthMate AI Platform</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Empowering Students, Instructors, and Admins — All in One Place</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 10px; border-color: #00f7ff;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔍 Choose Your Panel</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎓 Student Panel", key="student_panel", help="Access student features", type="primary", use_container_width=True):
            logout_all_panels()
            st.session_state.selected_panel = None if st.session_state.selected_panel == "student" else "student"
    with col2:
        if st.button("👨‍🏫 Instructor Panel", key="instructor_panel", help="Access instructor features", use_container_width=True):
            logout_all_panels()
            st.session_state.selected_panel = None if st.session_state.selected_panel == "instructor" else "instructor"
    with col3:
        if st.button("🛡️ Admin Panel", key="admin_panel", help="Access admin features", use_container_width=True):
            logout_all_panels()
            st.session_state.selected_panel = None if st.session_state.selected_panel == "admin" else "admin"
    panel = st.session_state.get("selected_panel")
    if panel:
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        if panel == "student":
            st.markdown("<h4 style='color:#39ff14;'>🎓 Student Access</h4>", unsafe_allow_html=True)
            st.markdown('<div class="student-panel-radio">', unsafe_allow_html=True)
            nav = st.radio("Select Action", ["Login", "Register", "Forgot Password"], horizontal=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if nav == "Login":
                student_login()
            elif nav == "Register":
                student_register()
            elif nav == "Forgot Password":
                student_forgot_password()
            st.markdown("""
                <div class='panel-info'>
                    <h5>👨‍🎓 Student Panel Overview</h5>
                    <ul>
                        <li>Register or login to access skill-based learning modules.</li>
                        <li>Track course progress, certificates and more.</li>
                        <li>Reset your password easily if forget it.</li>
                        <li>After login, access Text, Voice, or Face-to-Face assessment modules.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        elif panel == "instructor":
            st.markdown("<h4 style='color:#00f7ff;'>👨‍🏫 Instructor Access</h4>", unsafe_allow_html=True)
            instructor_dashboard()
            st.markdown("""
                <div class='panel-info'>
                    <h5>🧑‍🏫 Instructor Panel Overview</h5>
                    <ul>
                        <li>Upload new courses and manage content easily.</li>
                        <li>Engage with student questions and feedback.</li>
                        <li>Track enrolled students and performance.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        elif panel == "admin":
            st.markdown("<h4 style='color:#ff00ff;'>🛡️ Admin Access</h4>", unsafe_allow_html=True)
            admin_panel()
            st.markdown("""
                <div class='panel-info'>
                    <h5>🛡️ Admin Panel Overview</h5>
                    <ul>
                        <li>Manage platform users including students and instructors.</li>
                        <li>Monitor activity logs and ensure compliance.</li>
                        <li>Perform platform-wide configuration and analysis.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Main Logic --------------------
with st.container():
    st.markdown(f'<div data-page="{st.session_state.page}">', unsafe_allow_html=True)
    if st.session_state.page == "welcome":
        st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
        st.markdown("<h1>Welcome to the Growthmate AI Platform</h1>", unsafe_allow_html=True)
        st.markdown("<h4>Your journey begins here</h4>", unsafe_allow_html=True)
        st.markdown('<div class="centered-launch">', unsafe_allow_html=True)
        if st.button("🚀 Launch", key="launch_button", help="Launch the platform", type="primary"):
            with st.spinner("Launching..."):
                st.session_state.page = "main"
                st.write("Debug: Transition to main page")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        main_app()