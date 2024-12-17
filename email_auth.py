
import os
import random
import re
import smtplib
import socket
import redis
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Retrieve environment variables from .env file
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_PASS = os.getenv("UPSTASH_REDIS_REST_TOKEN")

# Connect to Redis (Upstash)
r = redis.StrictRedis.from_url(UPSTASH_REDIS_URL, password=UPSTASH_REDIS_PASS)

def is_valid_email(email):
    """
    Validate email address using regex
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def generate_otp(length=6):
    """
    Generate a random OTP of specified length
    
    Args:
        length (int, optional): Length of OTP. Defaults to 6.
    
    Returns:
        str: Generated OTP
    """
    return str(random.randint(10 ** (length - 1), (10 ** length) - 1))

def set_otp(email, otp):
    """
    Store OTP in Redis with expiration
    
    Args:
        email (str): User's email
        otp (str): Generated OTP
    """
    expiration_time = int(os.getenv("OTP_EXPIRATION", 600))  # Default 10 minutes
    r.setex(f"otp:{email}", expiration_time, otp)

def get_otp(email):
    """
    Retrieve stored OTP for an email
    
    Args:
        email (str): User's email
    
    Returns:
        str or None: Stored OTP or None if not found
    """
    otp = r.get(f"otp:{email}")
    return otp.decode("utf-8") if otp else None

def send_otp_email(email):
    """
    Send OTP to user's email
    
    Args:
        email (str): Recipient's email address
    
    Returns:
        str or None: Generated OTP or None if sending fails
    """
    # Validate email first
    if not is_valid_email(email):
        st.error("Invalid email address")
        return None

    otp = generate_otp()
    try:
        # Store OTP in Redis
        set_otp(email, otp)

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = 'Your OTP for Authentication'

        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
          <h2>OTP Verification</h2>
          <p>Your One-Time Password (OTP) is:</p>
          <h3 style="background-color: #f0f0f0; padding: 10px; text-align: center; letter-spacing: 5px;">{otp}</h3>
          <p>This OTP will expire in 10 minutes. Do not share it with anyone.</p>
        </div>
        """
        msg.attach(MIMEText(body, 'html'))

        # Setup the server and send email with increased timeout
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USER, SMTP_PASS)  # Login with the email credentials
            server.sendmail(SMTP_FROM_EMAIL, email, msg.as_string())  # Send the email

        return otp  # Return the OTP for comparison
    except socket.timeout:
        st.error("Connection to SMTP server timed out. Please check your network connection.")
        return None
    except smtplib.SMTPException as e:
        st.error(f"SMTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error sending OTP: {e}")
        return None

def verify_otp(email, otp):
    """
    Verify the OTP for a given email
    
    Args:
        email (str): User's email
        otp (str): OTP to verify
    
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    stored_otp = get_otp(email)
    if stored_otp is None:
        return False  # OTP not found or expired
    return stored_otp == otp

def main():
    """
    Main Streamlit application for OTP Authentication
    """
    st.title("Secure OTP Authentication")

    # Email input
    email = st.text_input("Enter your email:", key="email_input")

    # OTP Generation Section
    if email:
        if st.button("Generate OTP"):
            # Send OTP email and store it in Redis
            otp = send_otp_email(email)
            if otp:
                st.session_state.otp = otp  # Store the OTP in session state for later comparison
                st.success(f"OTP sent to {email}. Please check your inbox.")

    # OTP Verification Section
    user_otp = st.text_input("Enter OTP", key="otp_input")

    if user_otp and st.button("Verify OTP"):
        # Verify OTP
        if verify_otp(email, user_otp):
            st.success("OTP verified successfully!")
            # You can add additional actions post-verification here
        else:
            st.error("Invalid OTP. Please try again.")

if __name__ == "__main__":
    main()
