import streamlit as st
import whisper
from groq import Groq
from gtts import gTTS
from pydub import AudioSegment
from audiorecorder import audiorecorder
import tempfile
import os
import time
import base64
import pymongo
import pdfplumber
import docx
from io import BytesIO
import uuid
import gc

def main():
    if "student_username" not in st.session_state or not st.session_state.student_username:
        st.error("⚠️ You must be logged in to access the dashboard.")
        return

    # Initialize dependencies
    try:
        gc.collect()  # Free up memory before loading model
        whisper_model = whisper.load_model("tiny")
    except RuntimeError as e:
        st.error(f"⚠️ Failed to load Whisper model due to memory issues: {e}. Please close other applications and try again.")
        return
    groq_client = Groq(api_key="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")
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["instructor"]
    responses_collection = db["voice_responses"]

    username = st.session_state.student_username

    # Fetch user data
    user = db["access_students"].find_one({"username": username})
    if not user:
        st.error("User not found. Please log in again.")
        return

    # Initialize session state
    st.session_state.setdefault("exam_started", False)
    st.session_state.setdefault("resume_file", None)
    st.session_state.setdefault("show_summary", False)
    for key, default in {
        "step": 0,
        "questions": [],
        "responses": [],
        "phase": "ready",
        "spoken": False,
        "session_id": str(uuid.uuid4()),
        "audio_data": None,
        "skills": None,
        "reset_message": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Ensure questions is always a list
    if st.session_state.questions is None:
        st.session_state.questions = []

    # Button styling and animations
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            margin-top: 10px;
            transition: all 0.3s ease;
        }
        .reset-button>button {
            background-color: #ff4d4d;
            color: white;
            border: none;
        }
        .reset-button>button:hover {
            transform: scale(1.05);
            background-color: #cc0000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .submit-button>button {
            background-color: #4CAF50;
            color: white;
            border: none;
        }
        .submit-button>button:hover {
            transform: scale(1.05);
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        </style>
    """, unsafe_allow_html=True)

    # Tab switch detection
    st.components.v1.html(
        """
        <script>
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
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
        for key, default in {
            "exam_started": False,
            "resume_file": None,
            "show_summary": False,
            "step": 0,
            "questions": [],
            "responses": [],
            "phase": "ready",
            "spoken": False,
            "session_id": str(uuid.uuid4()),
            "audio_data": None,
            "skills": None,
            "reset_message": None
        }.items():
            st.session_state[key] = default
        st.success("⚠️ Exam ended due to tab switch. You can start a new exam.")
        st.rerun()

    def set_background():
        st.markdown(
            """
            <style>
            .stApp {
                background-image: url("br");
                background-size: 100% 100%;
                background-attachment: fixed;
                background-repeat: no-repeat;
                background-position: center;
            }
            </style>
            """, unsafe_allow_html=True)

    def branded_ui():
        st.markdown("""
            <div style='text-align: center; padding: 10px; background-color: rgba(0,0,0,0.5); color: white; border-radius: 12px; margin-bottom: 20px;'>
                <h2>🎙️ AI Voice & Code Interview Bot</h2>
            </div>
            """, unsafe_allow_html=True)

    def show_logo():
        st.markdown("""
            <div style='text-align: center;'>
                <img src='https://growthmateinfotech.in/growthmate/assets/img/logo1.png' width='100'>
            </div>
            """, unsafe_allow_html=True)

    def dark_mode_toggle():
        if st.checkbox("🌙 Dark Mode"):
            st.markdown("""
                <style>
                body, .stApp {
                    color: white;
                    background-color: #1e1e1e;
                }
                </style>
                """, unsafe_allow_html=True)

    def extract_resume_text(resume_file):
        try:
            if resume_file.name.endswith(".pdf"):
                with pdfplumber.open(resume_file) as pdf:
                    return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            elif resume_file.name.endswith(".docx"):
                doc = docx.Document(resume_file)
                return "\n".join([para.text for para in doc.paragraphs])
            elif resume_file.name.endswith(".txt"):
                return resume_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"❌ Failed to parse resume: {e}")
        return ""

    def extract_skills(text):
        return ["Python", "SQL", "Machine Learning"]

    def chat_with_groq(user_input, skill, resume_text, is_question=True):
        try:
            prompt = "Ask a professional interview question" if is_question else "Give feedback for the following answer"
            messages = [
                {"role": "system", "content": f"You are an AI interviewer. {prompt} related to this skill: {skill}."},
                {"role": "system", "content": f"Resume:\n{resume_text}"},
                {"role": "user", "content": user_input}
            ]
            res = groq_client.chat.completions.create(model="llama3-8b-8192", messages=messages)
            return res.choices[0].message.content
        except Exception as e:
            return f"Error fetching response: {e}"

    def speak(text):
        tts = gTTS(text)
        tts.save("temp.mp3")
        with open("temp.mp3", "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        st.markdown(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
        os.remove("temp.mp3")

    def calculate_performance_rating(responses):
        positive_keywords = ["good", "excellent", "well done", "correct", "strong", "accurate"]
        negative_keywords = ["needs improvement", "incorrect", "lacking", "weak", "incomplete"]
        total_score = 0
        feedback_summary = []
        for r in responses:
            feedback = r["feedback"].lower()
            score = 5  # Base score per response
            for word in positive_keywords:
                if word in feedback:
                    score += 1
            for word in negative_keywords:
                if word in feedback:
                    score -= 1
            score = max(0, min(10, score))  # Clamp score between 0 and 10
            total_score += score
            feedback_summary.append(f"Skill: {r['skill']}, Score: {score}/10")
        overall_score = round(total_score / len(responses), 1) if responses else 0
        stars = "⭐" * int(overall_score // 2) + ("½" if overall_score % 2 else "")
        return {
            "score": overall_score,
            "stars": stars,
            "summary": "\n".join(feedback_summary)
        }

    # UI setup
    set_background()
    dark_mode_toggle()
    branded_ui()
    show_logo()

    if st.session_state.show_summary:
        st.success("✅ Interview completed!")
        rating = calculate_performance_rating(st.session_state.responses)
        st.markdown(f"**Overall Performance Rating: {rating['score']}/10 {rating['stars']}**")
        st.text_area("📊 Performance Summary:", value=rating['summary'], height=150)
        return

    if not st.session_state.exam_started:
        resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
        if resume_file:
            st.session_state.resume_file = resume_file
            if st.button("✅ Start Voice-to-Voice Interview"):
                st.session_state.exam_started = True
                resume_text = extract_resume_text(st.session_state.resume_file)
                if not resume_text:
                    st.error("⚠️ Failed to process resume. Please upload a valid file.")
                    st.session_state.exam_started = False
                    st.session_state.resume_file = None
                    return
                st.session_state.skills = extract_skills(resume_text)
                if not st.session_state.skills:
                    st.error("⚠️ No skills extracted from resume. Please upload a valid resume.")
                    st.session_state.exam_started = False
                    st.session_state.resume_file = None
                    return
    else:
        if st.session_state.resume_file is None or st.session_state.skills is None:
            st.error("⚠️ Resume file or skills lost. Please upload again.")
            st.session_state.exam_started = False
            st.session_state.resume_file = None
            st.session_state.skills = None
            return

        skills = st.session_state.skills
        resume_text = extract_resume_text(st.session_state.resume_file)

        if st.session_state.step < len(skills):
            current_skill = skills[st.session_state.step]
            st.subheader(f"🔍 Skill {st.session_state.step + 1}/{len(skills)}: {current_skill}")

            if st.session_state.step >= len(st.session_state.questions):
                with st.spinner("Generating question..."):
                    question = chat_with_groq("Give me an interview question", current_skill, resume_text, True)
                    st.session_state.questions.append(question)
                    st.session_state.phase = "ready"
                    st.session_state.spoken = False

            question = st.session_state.questions[st.session_state.step]
            st.write(f"🤖 Question: {question}")

            if st.session_state.phase == "ready" and not st.session_state.spoken:
                speak(question)
                st.session_state.spoken = True

            input_mode = st.selectbox("🛠️ Choose how you'd like to answer:", ["Voice", "Code"], key=f"mode_{st.session_state.step}")

            if st.session_state.phase == "ready":
                if input_mode == "Voice":
                    st.markdown("🎙️ Record your answer below:")
                    audio_data = audiorecorder("Start Recording", "Stop Recording")
                    if audio_data:
                        st.session_state.audio_data = audio_data
                        st.session_state.reset_message = None
                        audio_bytes_io = BytesIO()
                        audio_data.export(audio_bytes_io, format="wav")
                        audio_bytes = audio_bytes_io.getvalue()
                        st.audio(audio_bytes, format="audio/wav")

                    if st.session_state.reset_message:
                        st.success(st.session_state.reset_message)

                    if st.session_state.audio_data:
                        if st.button("🔄 Reset Recording", key=f"reset_{st.session_state.step}", help="Clear the current recording and start over", type="primary", use_container_width=True):
                            st.session_state.audio_data = None
                            st.session_state.phase = "ready"
                            st.session_state.reset_message = "Recording cleared! Please record again."
                            # No rerun; let conditional rendering handle UI update
                        if st.button("✅ Submit Answer", key=f"submit_answer_{st.session_state.step}", help="Submit your recording for transcription and feedback", type="primary", use_container_width=True):
                            audio_bytes_io = BytesIO()
                            st.session_state.audio_data.export(audio_bytes_io, format="wav")
                            audio_bytes = audio_bytes_io.getvalue()
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                                f.write(audio_bytes)
                                f.flush()
                                audio_path = f.name

                            with st.spinner("Transcribing audio..."):
                                transcribed_text = whisper_model.transcribe(audio_path)["text"]
                            st.success(f"🗣️ You said: {transcribed_text}")
                            with st.spinner("Generating feedback..."):
                                feedback = chat_with_groq(transcribed_text, current_skill, resume_text, is_question=False)
                            st.text_area("💬 Feedback:", value=feedback, height=120)
                            speak(feedback)

                            response_data = {
                                "username": username,
                                "session_id": st.session_state.session_id,
                                "skill": current_skill,
                                "question": question,
                                "response_text": transcribed_text,
                                "feedback": feedback,
                                "mode": "voice"
                            }
                            responses_collection.insert_one(response_data)
                            st.session_state.responses.append(response_data)
                            os.remove(audio_path)
                            st.session_state.audio_data = None
                            st.session_state.phase = "answered"
                            st.session_state.reset_message = None

                elif input_mode == "Code":
                    code_answer = st.text_area("💻 Write your code below:", height=200, key=f"code_{st.session_state.step}")
                    if st.button("✅ Submit Answer", key=f"submit_answer_{st.session_state.step}", help="Submit your code for feedback", type="primary", use_container_width=True):
                        with st.spinner("Generating feedback..."):
                            feedback = chat_with_groq(code_answer, current_skill, resume_text, is_question=False)
                        st.text_area("💬 Feedback:", value=feedback, height=120)
                        speak(feedback)
                        response_data = {
                            "username": username,
                            "session_id": st.session_state.session_id,
                            "skill": current_skill,
                            "question": question,
                            "response_text": code_answer,
                            "feedback": feedback,
                            "timestamp": time.time(),
                            "mode": "code"
                        }
                        responses_collection.insert_one(response_data)
                        st.session_state.responses.append(response_data)
                        st.session_state.phase = "answered"

            if st.session_state.phase == "answered":
                if st.session_state.step < len(skills) - 1:
                    if st.button("➡️ Next Question", key=f"next_{st.session_state.step}", type="primary", use_container_width=True):
                        st.session_state.step += 1
                        st.session_state.phase = "ready"
                        st.session_state.spoken = False
                        st.session_state.reset_message = None
                        st.rerun()
                else:
                    if st.button("✅ Submit", key="final_submit", type="primary", use_container_width=True):
                        st.session_state.show_summary = True
                        rating = calculate_performance_rating(st.session_state.responses)
                        responses_collection.update_one(
                            {"session_id": st.session_state.session_id, "username": username},
                            {"$set": {"performance_rating": rating}},
                            upsert=True
                        )
                        # No rerun; let show_summary take over
        else:
            st.session_state.show_summary = True
            rating = calculate_performance_rating(st.session_state.responses)
            responses_collection.update_one(
                {"session_id": st.session_state.session_id, "username": username},
                {"$set": {"performance_rating": rating}},
                upsert=True
            )
            # No rerun; let show_summary take over