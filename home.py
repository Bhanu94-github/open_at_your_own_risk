import streamlit as st

st.set_page_config(page_title="Growthmate Infotech", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
            color: #e0e1dd;
        }

        /* Navigation */
        .nav-container {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem;
        }

        .nav-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-logo img {
            height: 50px;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
        }

        .nav-links a {
            color: #e0e1dd;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #00d4ff;
        }

        /* Hero Section */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 6rem 2rem;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
            animation: rotate 20s linear infinite;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .hero-content {
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }

        .hero-title {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(45deg, #00d4ff, #0077b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); }
            to { text-shadow: 0 0 20px rgba(0, 212, 255, 0.8); }
        }

        /* Sections */
        .section {
            padding: 5rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .section-title {
            font-size: 2.5rem;
            margin-bottom: 3rem;
            text-align: center;
            color: #00d4ff;
        }

        /* Features Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 212, 255, 0.1);
        }

        .feature-card:hover {
            transform: translateY(-10px);
            border-color: #00d4ff;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
        }

        /* AI Modules */
        .module-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 212, 255, 0.1);
        }

        .module-card:hover {
            transform: translateY(-10px);
            border-color: #00d4ff;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
        }

        /* Contact Form */
        .contact-form {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            border: 1px solid rgba(0, 212, 255, 0.1);
        }

        .contact-form input,
        .contact-form textarea {
            width: 100%;
            padding: 0.8rem;
            margin-bottom: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 0.5rem;
            color: #e0e1dd;
        }

        /* Launch Button */
        .launch-button {
            background: linear-gradient(45deg, #00d4ff, #0077b6);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 2rem;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
            animation: pulse 2s infinite;
        }

        .launch-button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 212, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0); }
        }

        /* Hamburger Menu */
        .hamburger {
            display: none;
            flex-direction: column;
            gap: 6px;
            cursor: pointer;
            padding: 10px;
        }

        .hamburger span {
            width: 30px;
            height: 3px;
            background: #e0e1dd;
            transition: all 0.3s ease;
        }

        @media (max-width: 768px) {
            .hamburger {
                display: flex;
            }

            .nav-links {
                display: none;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 1rem;
                flex-direction: column;
                text-align: center;
            }

            .nav-links.active {
                display: flex;
            }

            .hero-title {
                font-size: 2.5rem;
            }
        }
    </style>

    <div class="nav-container">
        <div class="nav-content">
            <div class="nav-logo">
                <img src="https://growthmateinfotech.in/growthmate/assets/img/logo1.png" alt="Growthmate Infotech">
            </div>
            <div class="hamburger" onclick="toggleMenu()">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#about">About</a>
                <a href="#vision">Vision</a>
                <a href="#mission">Mission</a>
                <a href="#features">Features</a>
                <a href="#ai-modules">AI Modules</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
    </div>

    <section class="hero" id="home">
        <div class="hero-content">
            <h1 class="hero-title">Welcome to Growthmate Infotech</h1>
            <p>Empowering businesses through innovative AI solutions</p>
            <a href="/app" class="launch-button">Launch Platform</a>
        </div>
    </section>

    <section class="section" id="about">
        <h2 class="section-title">About Us</h2>
        <p>Growthmate Infotech is a leading provider of AI-powered solutions, helping businesses transform and grow in the digital age.</p>
    </section>

    <section class="section" id="vision">
        <h2 class="section-title">Our Vision</h2>
        <p>To revolutionize the way businesses operate through cutting-edge AI technology and innovative solutions.</p>
    </section>

    <section class="section" id="mission">
        <h2 class="section-title">Our Mission</h2>
        <p>To provide accessible, efficient, and powerful AI tools that drive business growth and success.</p>
    </section>

    <section class="section" id="features">
        <h2 class="section-title">Why Choose Growthmate</h2>
        <div class="features-grid">
            <div class="feature-card">
                <h3>Innovation</h3>
                <p>Cutting-edge AI solutions</p>
            </div>
            <div class="feature-card">
                <h3>Expertise</h3>
                <p>Industry-leading professionals</p>
            </div>
            <div class="feature-card">
                <h3>Support</h3>
                <p>24/7 dedicated assistance</p>
            </div>
        </div>
    </section>

    <section class="section" id="ai-modules">
        <h2 class="section-title">AI Modules</h2>
        <div class="features-grid">
            <div class="module-card">
                <h3>Text-to-Text</h3>
                <p>Advanced natural language processing</p>
            </div>
            <div class="module-card">
                <h3>Voice-to-Voice</h3>
                <p>Real-time voice interaction</p>
            </div>
            <div class="module-card">
                <h3>Face-to-Face</h3>
                <p>Coming soon: AI-powered video interactions</p>
            </div>
        </div>
    </section>

    <section class="section" id="contact">
        <h2 class="section-title">Contact Us</h2>
        <div class="contact-form">
            <input type="text" placeholder="Name">
            <input type="email" placeholder="Email">
            <textarea placeholder="Message" rows="5"></textarea>
            <button class="launch-button">Send Message</button>
        </div>
    </section>

    <script>
        function toggleMenu() {
            document.querySelector('.nav-links').classList.toggle('active');
        }

        // Smooth scroll for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Launch button redirect
        document.querySelector('.launch-button').addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/app';
        });
    </script>
""", unsafe_allow_html=True)