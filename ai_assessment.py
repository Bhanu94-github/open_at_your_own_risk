import streamlit as st
import spacy
import PyPDF2
import docx
import uuid
import pymongo
import random
from db_utils import get_all_questions

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
results_collection = client["instructor"]["results"]

# spaCy model
nlp = spacy.load("en_core_web_sm")
ALL_SKILLS = ["python", "sql", "java", "javascript", "html", "css", "c++", "mongodb"]

# Custom CSS for futuristic UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
        color: #e0e1dd;
        font-family: 'Roboto', sans-serif;
    }

    h1, .stTitle {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        animation: fadeIn 1s ease-in;
    }

    .stSubheader {
        color: #778da9;
        font-family: 'Roboto', sans-serif;
    }

    .skill-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: transform 0.3s ease;
        animation: slideIn 0.5s ease-in;
    }

    .skill-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }

    .stButton>button {
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-family: 'Orbitron', sans-serif;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-in;
        width: 100%;
        max-width: 300px;
        margin: 10px auto;
        display: block;
    }

    .take-assessment>button {
        background: linear-gradient(45deg, #00d4ff, #0077b6);
        color: white;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }

    .take-assessment>button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
        background: linear-gradient(45deg, #0077b6, #00d4ff);
    }

    .start-assessment>button {
        background: linear-gradient(45deg, #ff6b6b, #ff3f3f);
        color: white;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
    }

    .start-assessment>button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 20px rgba(255, 107, 107, 0.8);
        background: linear-gradient(45deg, #ff3f3f, #ff6b6b);
    }

    .prev-button>button {
        background: linear-gradient(45deg, #778da9, #415a77);
        color: white;
    }

    .prev-button>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(119, 141, 169, 0.8);
    }

    .next-button>button {
        background: linear-gradient(45deg, #00ff87, #00b894);
        color: white;
    }

    .next-button>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 135, 0.8);
    }

    .submit-button>button {
        background: linear-gradient(45deg, #ffd60a, #ffaa00);
        color: #1b263b;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(255, 214, 10, 0.5);
    }

    .submit-button>button:hover {
        transform: scale(1.1);
        box-shadow: 0 0 20px rgba(255, 214, 10, 0.8);
        background: linear-gradient(45deg, #ffaa00, #ffd60a);
    }

    .stRadio, .stTextArea, .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        animation: fadeIn 0.7s ease-in;
    }

    .stSuccess, .stWarning {
        border-radius: 10px;
        padding: 15px;
        animation: slideIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    @keyframes slideIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .stButton>button {
            font-size: 14px;
            padding: 10px 20px;
            max-width: 100%;
        }
        h1, .stTitle {
            font-size: 24px;
        }
        .stSubheader {
            font-size: 18px;
        }
        .skill-container {
            padding: 10px;
        }
    }

    @media (max-width: 480px) {
        .stButton>button {
            font-size: 12px;
            padding: 8px 16px;
        }
        h1, .stTitle {
            font-size: 20px;
        }
        .stSubheader {
            font-size: 16px;
        }
        .stRadio, .stTextArea, .stFileUploader {
            padding: 10px;
        }
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    for key, default in {
        "page": "upload",
        "selected_skill": None,
        "difficulty": None,
        "questions": [],
        "index": 0,
        "score": 0,
        "responses": [],
        "session_id": str(uuid.uuid4()),
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Helper function to extract text from resume
    def extract_text_from_resume(uploaded_file):
        text = ""
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text

    # Helper function to extract skills
    def extract_skills(text):
        doc = nlp(text.lower())
        return list({token.text for token in doc if token.text in ALL_SKILLS})

    # Main logic
    if st.session_state.page == "upload":
        st.title("📄 Resume Skill Extractor & Assessment")

        uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt", "docx"])
        if uploaded_file:
            text = extract_text_from_resume(uploaded_file)
            extracted_skills = extract_skills(text)

            if extracted_skills:
                st.success("Skills found in resume:")
                for skill in extracted_skills:
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"<div class='skill-container'>{skill.title()}</div>", unsafe_allow_html=True)
                    if col2.button(f"Take Assessment: {skill}", key=f"take_{skill}", type="primary", help=f"Start the {skill} assessment"):
                        st.session_state.selected_skill = skill
                        st.session_state.page = "assessment"
                        st.rerun()
            else:
                st.warning("No predefined skills found in your resume.")

    elif st.session_state.page == "assessment":
        skill = st.session_state.selected_skill
        st.title(f"🧠 {skill.title()} Skill Assessment")

        if st.session_state.difficulty is None:
            difficulty = st.radio("Choose difficulty level:", ["easy", "medium", "hard"], key=f"q_{st.session_state.index}")
            if st.button("Start Assessment", key="start_assessment", type="primary", help="Begin the assessment"):
                all_questions = get_all_questions(skill, difficulty)
                if len(all_questions) < 15:
                    st.error("Insufficient questions for this skill and difficulty level.")
                    st.session_state.page = "upload"
                    st.rerun()

                st.session_state.questions = random.sample(all_questions, 15)
                random.shuffle(st.session_state.questions)
                st.session_state.index = 0
                st.session_state.score = 0
                st.session_state.responses = []
                st.session_state.difficulty = difficulty
                st.session_state.page = "exam"
                st.rerun()

    elif st.session_state.page == "exam" and st.session_state.index < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.index]
        q_num = st.session_state.index + 1
        st.markdown(f"<div class='skill-container'><strong>Question {q_num}:</strong> {question['question']}</div>", unsafe_allow_html=True)

        if question["type"] == "coding":
            for key in ["constraints", "input", "output", "explanation"]:
                if key in question:
                    st.markdown(f"<div class='skill-container'><strong>{key.replace('_', ' ').title()}:</strong> {question[key]}</div>", unsafe_allow_html=True)

        if question["type"] in ["mcqs", "blanks"] and "options" in question:
            answer = st.radio("Options:", question["options"], index=None, key=f"q_{st.session_state.index}")
        else:
            answer = st.text_area("Your answer:", key=f"q_{st.session_state.index}")

        if len(st.session_state.responses) <= st.session_state.index:
            st.session_state.responses.append({"selected": ""})

        st.session_state.responses[st.session_state.index].update({
            "question": question["question"],
            "type": question["type"],
            "selected": answer,
            "correct": question.get("answer")
        })

        col1, col2, col3 = st.columns([1, 1, 2])
        if col1.button("⬅ Previous", key=f"prev_{st.session_state.index}", disabled=st.session_state.index == 0, type="primary", help="Go to previous question"):
            st.session_state.index -= 1
            st.rerun()

        if col2.button("➡ Next", key=f"next_{st.session_state.index}", disabled=st.session_state.index == len(st.session_state.questions) - 1, type="primary", help="Go to next question"):
            st.session_state.index += 1
            st.rerun()

        if st.session_state.index == len(st.session_state.questions) - 1:
            if col3.button("✅ Submit", key="submit_exam", type="primary", help="Submit your assessment"):
                st.session_state.page = "submit"
                st.rerun()

    elif st.session_state.page == "submit":
        score = 0
        invalid_questions = 0
        for resp in st.session_state.responses:
            if (resp["selected"] and isinstance(resp["selected"], str) and
                    resp["correct"] and isinstance(resp["correct"], str)):
                if resp["selected"].strip().lower() == resp["correct"].strip().lower():
                    score += 1
            else:
                invalid_questions += 1

        if invalid_questions > 0:
            st.warning(f"{invalid_questions} questions had invalid or missing answers and were not scored.")

        st.session_state.score = score

        results_collection.insert_one({
            "session_id": st.session_state.session_id,
            "username": st.session_state.student_username,
            "score": score,
            "skill": st.session_state.selected_skill,
            "difficulty": st.session_state.difficulty,
            "score": st.session_state.score,
            "total": len(st.session_state.questions),
            "responses": st.session_state.responses
        })

        st.subheader("🎉 Assessment Completed!")
        st.success(f"✅ Submitted successfully! Score: {st.session_state.score} / {len(st.session_state.questions)}")
        st.balloons()

