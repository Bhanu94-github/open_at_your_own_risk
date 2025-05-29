import streamlit as st
from utils import db
from datetime import datetime
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
import bcrypt

# Gmail SMTP credentials
GMAIL_ADDRESS = "palivelabhanuprakash99@gmail.com"
GMAIL_APP_PASSWORD = "ywgvvgplhdgwwewc"

# Inject responsive CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;600&family=Inter:wght@300;400&display=swap');
    .stApp {
        background: linear-gradient(135deg, #121212 0%, #1e1e2e 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }
    .stSubheader, h3 {
        font-family: 'Exo 2', sans-serif;
        color: #00d4ff;
        text-shadow: 0 0 8px rgba(0, 212, 255, ^^0.5);
        animation: fadeIn 0.8s ease-in;
        text-align: center;
    }
    input[type="text"], input[type="password"], textarea {
        background-color: #2a2a2a !important;
        color: #000000 !important;
        border: 1px solid #00d4ff;
        border-radius: 8px;
        padding: 10px;
        width: 100%;
        transition: border-color 0.3s ease;
        animation: slideIn 0.6s ease-in;
        box-sizing: border-box;
    }
    input::placeholder, textarea::placeholder {
        color: #d9d9d9 !important;
    }
    input:focus, textarea:focus {
        border-color: #00f0ff;
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
    }
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #0077b6);
        color: #ffffff !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-family: 'Exo 2', sans-serif;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        animation: slideIn 0.6s ease-in, pulse 2s infinite;
        display: block;
        width: 100%;
        max-width: 300px;
        margin: 15px auto;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(45deg, #0077b6, #00d4ff);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.8);
    }
    .reset-button > button {
        background: linear-gradient(45deg, #ff4d4d, #b30000);
        box-shadow: 0 0 10px rgba(255, 77, 77, 0.5);
    }
    .reset-button > button:hover {
        background: linear-gradient(45deg, #b30000, #ff4d4d);
        box-shadow: 0 0 15px rgba(255, 77, 77, 0.8);
    }
    .stSuccess, .stError, .stWarning {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #00d4ff;
        color: #e0e0e0 !important;
        animation: slideIn 0.5s ease-in;
        margin-top: 15px;
    }
    .stError, .stWarning {
        border-color: #ff4d4d;
    }
    .form-container {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 30px 25px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        width: 90%;
        max-width: 500px;
        margin: 40px auto;
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 10px rgba(0, 212, 255, 0.5); }
        50% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.8); }
    }
    @media (max-width: 1024px) {
        .form-container {
            width: 95%;
            padding: 25px 20px;
        }
        .stButton > button {
            font-size: 15px;
            padding: 10px 22px;
        }
    }
    @media (max-width: 768px) {
        .form-container {
            width: 96%;
            padding: 20px 15px;
            color: #f0f0f0 !important;
        }
        .stSubheader, h3 {
            font-size: 22px;
            color: #f0f0f0 !important;
            text-shadow: 0 0 4px rgba(0, 212, 255, 0.3);
        }
        input[type="text"], input[type="password"], textarea {
            color: #000000 !important;
        }
        input::placeholder, textarea::placeholder {
            color: #f0f0f0 !important;
        }
        .stSuccess, .stError, .stWarning {
            color: #f0f0f0 !important;
            text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
        }
        .stButton > button {
            color: #f0f0f0 !important;
            font-size: 14px;
            padding: 10px 18px;
        }
    }
    @media (max-width: 480px) {
        .form-container {
            padding: 15px 10px;
        }
        .stSubheader, h3 {
            font-size: 20px;
        }
        input[type="text"], input[type="password"], textarea {
            font-size: 15px;
        }
        .stButton > button {
            font-size: 13px;
            padding: 8px 16px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# MongoDB collections
reg_col = db["student_registrations"]
access_col = db["access_students"]

# Common passwords to block
COMMON_PASSWORDS = [
    "password123", "qwerty123", "admin123", "12345678", "welcome123",
    "password1", "abc123", "letmein", "test123", "changeme"
]

def validate_password(password, username, email):
    errors = []
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must include at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        errors.append("Password must include at least one lowercase letter.")
    if not re.search(r'\d', password):
        errors.append("Password must include at least one digit.")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Password must include at least one special character.")
    if username.lower() in password.lower() or email.lower() in password.lower():
        errors.append("Password cannot contain your username or email.")
    if password.lower() in [p.lower() for p in COMMON_PASSWORDS]:
        errors.append("Password is too common and not allowed.")
    return errors

def send_email_verification_code(to_email, otp):
    try:
        message = MIMEMultipart()
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = "Email Verification OTP"
        body = f"Your OTP for registration is {otp}"
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, message.as_string())
        return True
    except Exception as e:
        st.error(f"❌ Failed to send OTP: {str(e)}")
        return False

def student_login():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader("🔐 Student Login")
    username = st.text_input("Username", key="stu_login_user")
    password = st.text_input("Password", type="password", key="stu_login_pass")
    if st.button("Login", key="stu_login_btn"):
        user = access_col.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            access_col.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.utcnow(), "is_logged_in": True}}
            )
            st.session_state.student_logged_in = True
            st.session_state.student_username = username
            st.success(f"✅ Welcome {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials or not approved yet.")
    st.markdown('</div>', unsafe_allow_html=True)

def student_register():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    if "email_otp_sent" not in st.session_state:
        st.session_state.email_otp_sent = False
        st.session_state.email_otp = None
        st.session_state.registration_data = None
        st.session_state.email_otp_attempts = 0
    if not st.session_state.email_otp_sent:
        st.subheader("📝 Student Registration")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number", help="Enter as +91xxxxxxxxxx")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = "student"
        if st.button("Send OTP"):
            if not all([name, email, phone, username, password, confirm_password]):
                st.warning("⚠️ Please fill in all fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                password_errors = validate_password(password, username, email)
                if password_errors:
                    for error in password_errors:
                        st.error(f"❌ {error}")
                elif reg_col.find_one({"email": email}):
                    st.error("❌ Email already registered.")
                elif reg_col.find_one({"username": username}):
                    st.error("❌ Username already taken.")
                else:
                    try:
                        valid = validate_email(email, check_deliverability=True)
                        email = valid.normalized
                    except EmailNotValidError as e:
                        st.error(f"❌ Invalid email: {str(e)}")
                        return
                    otp = str(random.randint(100000, 999999))
                    if send_email_verification_code(email, otp):
                        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        st.session_state.email_otp = otp
                        st.session_state.email_otp_sent = True
                        st.session_state.registration_data = {
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "username": username,
                            "password": hashed_password,
                            "role": role
                        }
                        st.session_state.email_otp_attempts = 0
                        st.success(f"✅ OTP sent to {email}")
                        st.rerun()
    else:
        st.subheader("🔐 Verify Email")
        otp_input = st.text_input("Enter OTP", key="email_otp_input")
        if st.button("Verify OTP"):
            if st.session_state.email_otp_attempts >= 3:
                st.error("❌ Maximum OTP attempts reached. Please try again.")
                st.session_state.email_otp_sent = False
                st.session_state.email_otp = None
                st.session_state.registration_data = None
                st.session_state.email_otp_attempts = 0
                st.rerun()
            elif otp_input == st.session_state.email_otp:
                reg_col.insert_one(st.session_state.registration_data)
                st.success("✅ Registration successful! Await admin approval.")
                st.balloons()
                st.session_state.email_otp_sent = False
                st.session_state.email_otp = None
                st.session_state.registration_data = None
                st.session_state.email_otp_attempts = 0
                st.rerun()
            else:
                st.session_state.email_otp_attempts += 1
                st.error(f"❌ Invalid OTP. {3 - st.session_state.email_otp_attempts} attempts remaining.")
    st.markdown('</div>', unsafe_allow_html=True)

def student_forgot_password():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.subheader("🔄 Reset Password")
    username = st.text_input("Enter your username", key="forgot_user")
    new_password = st.text_input("New Password", type="password", key="forgot_pass")
    confirm_new = st.text_input("Confirm New Password", type="password", key="forgot_conf")
    if st.button("Reset Password", key="reset_btn", help="Reset your password"):
        user = access_col.find_one({"username": username})
        if not user:
            st.error("❌ Username not found or not approved.")
        elif new_password != confirm_new:
            st.error("❌ Passwords do not match.")
        else:
            # Optional: Apply same password validation
            """
            password_errors = validate_password(new_password, username, user.get("email", ""))
            if password_errors:
                for error in password_errors:
                    st.error(f"❌ {error}")
                return
            """
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            access_col.update_one(
                {"username": username},
                {"$set": {"password": hashed_password}}
            )
            st.success("✅ Password reset successfully.")
            st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)