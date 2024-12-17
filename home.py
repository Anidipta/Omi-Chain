import streamlit as st 
from PIL import Image

def home():
    st.markdown("""
        <style>
            body {
                background-color: #2b2b2b;
                color: white;
                font-family: 'Arial', sans-serif;
            }
            .container {
                text-align: center;
                margin-top: 50px;
            }
            .logo {
                width: 300px;
                height: auto;
                transition: transform 1s ease, opacity 1s ease;
            }
            .logo:hover {
                transform: scale(1.1);
                opacity: 0.8;
            }
            .selectbox {
                margin-top: 20px;
                font-size: 18px;
                padding: 10px;
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 5px;
            }
            .sidebar-title {
                font-size: 24px;
                color: #ffd700;
            }
            .sidebar-content {
                color: white;
                font-size: 15px;
                padding:10px;
            }
            .sidebar-emoji {
                font-size: 28px;
                margin-right: 10px;
            }
            .sidebar-header {
                font-size: 20px;
                color: #f2f2f2;
                font-weight: bold;
                margin-bottom: 15px;
            }
            .overview-header {
                font-size: 26px;
                font-weight: bold;
                margin-top: 30px;
                color: #ffd700;
                transition: color 0.5s ease;
            }
            .overview-content {
                font-size: 18px;
                color: #f2f2f2;
                margin-bottom: 20px;
                transition: color 0.5s ease;
            }
            .overview-content:hover {
                color: #ffd700;
            }
            .tech-stack {
                font-size: 18px;
                margin-top: 20px;
                background-color: #333;
                padding: 10px;
                border-radius: 5px;
            }
            .tech-stack h3 {
                color: #ffd700;
            }
            .key-features {
                margin-top: 20px;
            }
            .key-features li {
                color: #f2f2f2;
                font-size: 18px;
            }
        </style>
    """, unsafe_allow_html=True)


    # Main content
    st.title("EduChainVerify")
    st.subheader("Empowering Education through Blockchain")

    img_path = "logo.webp"
    img = Image.open(img_path)
    st.image(img, caption="EduChainVerify Logo", use_column_width=True)

    # Overview Section
    st.markdown("<h3 class='overview-header'>Overview</h3>", unsafe_allow_html=True)
    st.markdown("<div class='overview-content'>"
                    "*EduChainVerify* is a decentralized platform designed for secure storage and verification of academic credentials. It enhances the integrity, accessibility, and efficiency of credential verification while empowering students with ownership of their academic records."
                    "</div>", unsafe_allow_html=True)

    # Key Features Section
    st.markdown("<h3 class='overview-header'>Key Features</h3>", unsafe_allow_html=True)
    st.markdown("<ul class='key-features'>"
                    "<li><strong>Decentralized Storage</strong>: Tamper-proof and immutable records of credentials.</li>"
                    "<li><strong>User Empowerment</strong>: Students access and share credentials via a secure digital wallet.</li>"
                    "<li><strong>Streamlined Verification</strong>: Instant verification through QR codes linked to blockchain entries.</li>"
                    "<li><strong>Global Accessibility</strong>: Easy cross-border verification of qualifications.</li>"
                    "<li><strong>Cost-Effective Operations</strong>: Automated processes reduce administrative costs.</li>"
                    "</ul>", unsafe_allow_html=True)

    # Tech Stack Section
    st.markdown("<h3 class='overview-header'>Tech Stack</h3>", unsafe_allow_html=True)
    st.markdown("<div class='tech-stack'>"
                "<h5>Blockchain Platform</h5> Ethereum or Hyperledger for secure data storage. <br>"
                "<br></br>"
                "<h5>Smart Contracts</h5> Solidity for automated credential issuance and verification. <br>"
                "<br></br>"
                "<h5>Frontend Framework</h5> Streamlit (Python) for a user-friendly interface. <br>"
                "<br></br>"
                "<h5>Backend Framework</h5> Flask (Python) for server-side logic. <br>"
                "<br></br>"
                "<h5>Database</h5> IPFS (InterPlanetary File System) for storing credential data off-chain. <br>"
                "<br></br>"
                "<h5>Authentication</h5> OAuth 2.0 for secure user authentication. <br>"
                "</div>", unsafe_allow_html=True)