import streamlit as st

st.set_page_config(page_title="Welcome", layout="wide")

st.markdown("""
    <style>
        .stApp {
            height: 100vh;
            background: url("https://i.gifer.com/Ax9R.gif");
            background-size: cover;
            background-position: center;
        }

        .centered-launch {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
        }

        .launch-button {
            background: linear-gradient(to right, #6e8efb, #a777e3);
            color: white;
            font-size: 20px;
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            box-shadow: 0px 0px 18px rgba(167, 119, 227, 0.7);
            cursor: pointer;
            transition: all 0.3s ease-in-out;
        }

        .launch-button:hover {
            background: linear-gradient(to right, #4f46e5, #7c3aed);
            transform: scale(1.05);
        }

        h1, h4 {
            text-shadow: 2px 2px 5px #000;
            text-align: center;
            color: white;
        }
    </style>

    <h1>Welcome to the Growthmate AI Platform</h1>
    <h4>Your journey begins here</h4>

    <div class="centered-launch">
        <button class="launch-button" onclick="window.location.href='/app.py'">🚀 Launch</button>
    </div>
""", unsafe_allow_html=True)

