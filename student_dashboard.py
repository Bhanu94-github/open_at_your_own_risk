import streamlit as st
import uuid
from utils import db
from datetime import datetime
from ai_assessment import main as ai_assessment_main
from voice import main as voice_main
from instructor_panel import log_token_history

def student_dashboard():
    # --- LOGIN CHECK ---
    if "student_username" not in st.session_state or not st.session_state.student_username:
        st.error("⚠ You must be logged in to access the dashboard.")
        return

    username = st.session_state.student_username

    # --- FETCH USER DATA ---
    user = db["access_students"].find_one({"username": username})
    if not user:
        st.error("User not found. Please log in again.")
        return

    # --- DEFAULT STATE INIT ---
    st.session_state.setdefault("exam_active", False)
    st.session_state.setdefault("selected_module", None)

    # --- TAB SWITCH DETECTION ---
    if st.session_state.exam_active:
        st.components.v1.html(
            """
            <script>
            document.addEventListener('visibilitychange', function() {
                if (document.hidden) {
                    // Trigger a form submission to end the exam
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '';
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'end_exam';
                    input.value = 'true';
                    form.appendChild(input);
                    document.body.appendChild(form);
                    form.submit();
                }
            });
            </script>
            """,
            height=0
        )
        if st.session_state.get("end_exam"):
            st.session_state.exam_active = False
            st.session_state.selected_module = None
            # Clear ai_assessment session state to ensure fresh exam
            for key in ["page", "selected_skill", "difficulty", "questions", "index", "score", "responses", "session_id"]:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.session_id = str(uuid.uuid4())
            st.success("⚠ Exam ended due to tab switch. You can start a new exam.")
            st.rerun()

    # --- SIDEBAR ---
    st.sidebar.title("📚 Navigation")
    page = "Home"  # Default page

    if st.session_state.exam_active:
        st.sidebar.markdown("🔒 Sidebar locked during exam. Submit exam to unlock.")
    else:
        page = st.sidebar.radio("Go to", ["Home", "AI Module", "AI Module Info", "Logout"], key="nav_radio")

        if page == "AI Module":
            st.sidebar.markdown("### Select AI Module")
            ai_module = st.sidebar.radio(
                "Choose an AI Module",
                options=["Text-to-Text", "Voice-to-Voice", "Face-to-Face"],
                key="ai_module_radio"
            )

            if st.sidebar.button("Start Exam"):
                token_key = ai_module.replace("-", "_")
                tokens_left = user.get("ai_tokens", {}).get(token_key, 0)

                if tokens_left > 0:
                    result = db["access_students"].update_one(
                        {"username": username, f"ai_tokens.{token_key}": {"$gt": 0}},
                        {"$inc": {f"ai_tokens.{token_key}": -1}}
                    )

                    if result.modified_count == 1:
                        log_token_history(username, token_key, -1, datetime.now())
                        st.session_state.exam_active = True
                        st.session_state.selected_module = token_key
                        # Reset ai_assessment session state for fresh exam
                        for key in ["page", "selected_skill", "difficulty", "questions", "index", "score", "responses", "session_id"]:
                            if key in st.session_state:
                                st.session_state[key] = None
                        st.session_state.session_id = str(uuid.uuid4())
                        st.session_state.page = "upload"  # Ensure ai_assessment starts at upload page
                        st.success(f"✅ Launched {ai_module} exam! Tokens left: {tokens_left - 1}")
                        st.rerun()
                    else:
                        st.error("Token deduction failed or no tokens left.")
                else:
                    st.error(f"❌ You have no {ai_module} tokens left.")

    # --- EXAM MODE ---
    if st.session_state.exam_active:
        module = st.session_state.selected_module.replace("_", "-")
        st.markdown(f'<h2 style="text-align:center;">📝 {module} Exam</h2>', unsafe_allow_html=True)

        if st.session_state.selected_module == "Text_to_Text":
            ai_assessment_main()
        elif st.session_state.selected_module == "Voice_to_Voice":
            voice_main()
        elif st.session_state.selected_module == "Face_to_Face":
            st.info("Face-to-Face AI module coming soon!")

        if st.button("Submit Exam"):
            st.session_state.exam_active = False
            st.session_state.selected_module = None
            # Clear ai_assessment session state to ensure fresh exam next time
            for key in ["page", "selected_skill", "difficulty", "questions", "index", "score", "responses", "session_id"]:
                if key in st.session_state:
                    st.session_state[key] = None
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.page = "Home"  # Redirect to Home page
            st.success("✅ Exam submitted successfully!")
            st.rerun()

    # --- HOME PAGE ---
    elif page == "Home":
        st.markdown('<h2 style="text-align:center;">🎓 Welcome to Your Dashboard</h2>', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align:center; color:#444;">💡 Your Token Balances</h4>', unsafe_allow_html=True)

        # CSS for token cards
        st.markdown("""
            <style>
            .token-card {
                background: #ffffff;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                width: 100%;
                min-height: 140px;
                margin: 10px 0;
                box-sizing: border-box;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .token-card h3 {
                font-size: 22px;
                margin: 0 0 10px 0;
                color: #333;
            }
            .token-card p {
                font-size: 28px;
                margin: 0;
                color: #000000;
                text-shadow: 0 0 4px rgba(0, 212, 255, 0.5);
            }
            @media (max-width: 768px) {
                .token-card {
                    min-height: 120px;
                    padding: 15px;
                }
                .token-card h3 {
                    font-size: 20px;
                }
                .token-card p {
                    font-size: 24px;
                }
            }
            @media (max-width: 480px) {
                .token-card {
                    min-height: 100px;
                    padding: 10px;
                }
                .token-card h3 {
                    font-size: 18px;
                }
                .token-card p {
                    font-size: 22px;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        # Three-column layout for token cards
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'''
                <div class="token-card" style="background:#F8D7DA;">
                    <h3>📝 Text-to-Text Tokens</h3>
                    <p>{user.get("ai_tokens", {}).get("Text_to_Text", 0)}</p>
                </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown(f'''
                <div class="token-card" style="background:#D4EDDA;">
                    <h3>🎤 Voice-to-Voice Tokens</h3>
                    <p>{user.get("ai_tokens", {}).get("Voice_to_Voice", 0)}</p>
                </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
                <div class="token-card" style="background:#FFF3CD;">
                    <h3>👥 Face-to-Face Tokens</h3>
                    <p>{user.get("ai_tokens", {}).get("Face_to_Face", 0)}</p>
                </div>
            ''', unsafe_allow_html=True)

    # --- MODULE INFO ---
    elif page == "AI Module Info":
        st.markdown('<h2 style="text-align:center;">🤖 AI Module Information</h2>', unsafe_allow_html=True)
        st.write("""
        Welcome to the AI Module Info page!  
        - *Text-to-Text*: Convert or generate text using advanced NLP models.  
        - *Voice-to-Voice*: Transform or synthesize voice interactions.  
        - *Face-to-Face*: (Coming soon) Interactive face recognition and communication.  
        """)

    # --- LOGOUT ---
    elif page == "Logout":
        if st.button("Logout"):
            st.session_state.clear()
            st.success("👋 You have been logged out.")
            st.rerun()