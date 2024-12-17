import streamlit as st
from PIL import Image
import sqlite3
from home import home
from landing import landing, fetch_user_data
from institute.app1 import get_transaction_hash,issue_credential_ui,revoke_credential_ui,search_credential_ui,analytics_dashboard_ui,monitor_credentials_ui,issue_credential,revoke_credential,fetch_credentials
#from email_auth import is_valid_email, send_otp_email, verify_otp

# Set up Streamlit page config
st.set_page_config(page_title="OmiChain - Home", page_icon=":guardsman:", layout="wide")

# Session state for user tracking
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "address" not in st.session_state:
    st.session_state.address = None
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Default page

# Function to save data to the database
def save_data(role, name, email, inst, acc):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    if role == "Student":
        cursor.execute(''' 
        INSERT INTO students (name, email, institute, metamask_account)
        VALUES (?, ?, ?, ?)
        ''', (name, email, inst, acc))
    elif role == "Institute":
        cursor.execute(''' 
        INSERT INTO institutes (institute_name, metamask_account)
        VALUES (?, ?)
        ''', (inst, acc))

    conn.commit()
    conn.close()

# Function to check if Metamask Account exists
def check_metamask_account(acc):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE metamask_account = ?", (acc,))
    student = cursor.fetchone()
    cursor.execute("SELECT * FROM institutes WHERE metamask_account = ?", (acc,))
    institute = cursor.fetchone()
    conn.close()
    return student, institute

# Sidebar: Login/Signup at Top
st.sidebar.title("OmiChain")

# Login and Signup Buttons Side by Side
if not st.session_state.logged_in:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Login", key="login_btn"):
            st.session_state.page = "Login"
    with col2:
        if st.button("Sign Up", key="signup_btn"):
            st.session_state.page = "Signup"

# Login Section
if st.session_state.page == "Login" and not st.session_state.logged_in:
    st.sidebar.subheader("Login")
    metamask_acc = st.sidebar.text_input("Metamask Account Address", key="login_acc")
    if st.sidebar.button("Proceed to Login", key="login_submit"):
        if not metamask_acc or len(metamask_acc) != 42:
            st.sidebar.warning("Please enter a valid Metamask Account Address.")
        else:
            student, institute = check_metamask_account(metamask_acc)
            if student:
                st.session_state.logged_in = True
                st.session_state.role = "Student"
                st.session_state.address = metamask_acc
                st.success("Logged in as Student.")
                st.session_state.page = "Home"
            elif institute:
                st.session_state.logged_in = True
                st.session_state.role = "Institute"
                st.session_state.address = metamask_acc
                st.success("Logged in as Institute.")
                st.session_state.page = "Home"
            else:
                st.sidebar.warning("Account not found. Please Sign Up.")

# Signup Section

if st.session_state.page == "Signup" and not st.session_state.logged_in:
    st.sidebar.subheader("Sign Up")
    
    # Step 1: Role and Basic Information
    role = st.sidebar.selectbox("Select Role", ["Student", "Institute"], key="signup_role")
    
    # Create placeholders for different input fields
    if role == "Student":
        name = st.sidebar.text_input("Full Name")
        email = st.sidebar.text_input("Email")
        inst = st.sidebar.selectbox("Select Institute", ["HITK", "NITD"], key="signup_institute")
        acc = st.sidebar.text_input("Metamask Account Address")
    elif role == "Institute":
        inst = st.sidebar.text_input("Institute Name")
        email = st.sidebar.text_input("Email")
        acc = st.sidebar.text_input("Metamask Account Address")
    
    # OTP Verification Section
    if st.sidebar.button("Send OTP", key="send_otp"):
        # Validate email before sending OTP
        if not email:
            st.sidebar.warning("Please enter an email address.")
        elif not is_valid_email(email):
            st.sidebar.warning("Please enter a valid email address.")
        else:
            # Send OTP and store in session state
            otp = send_otp_email(email)
            if otp:
                st.session_state.signup_email = email
                st.session_state.expected_otp = otp
                st.sidebar.success("OTP sent to your email. Please check your inbox.")
    
    # OTP Input and Verification
    if hasattr(st.session_state, 'expected_otp'):
        user_otp = st.sidebar.text_input("Enter OTP", key="otp_input")
        
        if st.sidebar.button("Verify OTP", key="verify_otp"):
            # Check if OTP is correct
            if verify_otp(st.session_state.signup_email, user_otp):
                # OTP Verified, proceed with account creation
                if not acc or len(acc) != 42:
                    st.sidebar.warning("Please enter a valid Metamask Account Address.")
                else:
                    # Save data to database
                    save_data(role, 
                              name if role == "Student" else None, 
                              st.session_state.signup_email, 
                              inst, 
                              acc)
                    
                    # Clear OTP-related session state
                    del st.session_state.expected_otp
                    del st.session_state.signup_email
                    
                    st.sidebar.success(f"Account created as {role}. Please log in.")
                    st.session_state.page = "Login"
            else:
                st.sidebar.error("Invalid OTP. Please try again.")


# Sidebar: Navigation Buttons when logged in
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.role}")
    if st.sidebar.button("Home", key="home_btn"):
        st.session_state.page = "Home"
    if st.sidebar.button("Manage Credentials", key="cred_btn"):
        st.session_state.page = "Manage Credentials"
    if st.sidebar.button("Account", key="account_btn"):
        st.session_state.page = "Account"
    if st.sidebar.button("Blockchain Wallet", key="wallet_btn"):
        st.session_state.page = "Blockchain Wallet"
    if st.sidebar.button("Share Credentials", key="share_btn"):
        st.session_state.page = "Share Credentials"

# Main Content
if not st.session_state.logged_in:
    if st.session_state.page == "Home":
        home()
    else:
        st.warning("Please log in to access this section.")
else:
    if st.session_state.page == "Home":
        landing(st.session_state.address)
    elif st.session_state.page == "Manage Credentials":
        st.subheader("Manage Credentials")
        st.write("Issue, search, and revoke credentials.")
        col1, col2, col3 = st.columns(3)

        with col1:
            issue_credential = st.button("🔑 Issue Credential")
        with col2:
            search_credential = st.button("🔍 Search Credential")
        with col3:
            revoke_credential = st.button("❌ Revoke Credential")

        if issue_credential:
            st.session_state.action = "issue"
        elif search_credential:
            st.session_state.action = "search"
        elif revoke_credential:
            st.session_state.action = "revoke"
        action=""
        if 'action' in st.session_state:
            action = st.session_state.action
                
        if action == "issue":
            issue_credential_ui(st.session_state.address)
        elif action == "search":
            search_credential_ui()
        elif action == "revoke":
            revoke_credential_ui(st.session_state.address)
           
                
    elif st.session_state.page == "Account":
        st.subheader("Account Details")
        role,institute_details= fetch_user_data(st.session_state.address)
        if role == 'institute':
            st.markdown("""
                <style>
                    
                    .account-header {
                        font-size: 1.5em;
                        color: #0073e6;
                        margin-bottom: 10px;
                        font-weight: bold;
                    }
                    .account-info {
                        font-size: 1.1em;
                        margin-bottom: 5px;
                        color: #333;
                    }
                    .account-info strong {
                        color: #0073e6;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="account-section">', unsafe_allow_html=True)
            st.write(f"**Institute Name:** {institute_details['institute_name']}", unsafe_allow_html=True)
            st.write(f"Account information for: **{st.session_state.address}**", unsafe_allow_html=True)

            role, institute_details = fetch_user_data(st.session_state.address)
            if role == "Institute" and institute_details:
                st.markdown(f'<p class="account-header">Institute Details:</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="account-info"><strong>Institute Name:</strong> {institute_details["institute_name"]}</p>', unsafe_allow_html=True)
        else:
                st.markdown("""
                    <style>
                        .account-header {
                            font-size: 1.5em;
                            color: #0073e6;
                            margin-bottom: 10px;
                            font-weight: bold;
                        }
                        .account-info {
                            font-size: 1.1em;
                            margin-bottom: 5px;
                            color: #ffffff;
                        }
                        .account-info strong {
                            color: #0073e6;
                        }
                    </style>
                """, unsafe_allow_html=True)

                # Display the student's details
                st.markdown('<div class="account-section">', unsafe_allow_html=True)
                st.markdown(f'<p class="account-info"><strong>Name:</strong> {institute_details["name"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="account-info"><strong>Email:</strong> {institute_details["email"]}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="account-info"><strong>Institute:</strong> {institute_details["institute"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
        logout_button = st.button("Logout", key="logout_btn", help="Click to logout and clear current address")

        if logout_button:
            # Clear session state variables for logout
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.address = None
            st.session_state.page = "Home"  
            st.success("You have been logged out successfully.")
            
            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        
    elif st.session_state.page == "Blockchain Wallet":
        st.subheader("Blockchain Wallet")
        st.write(f"Access your blockchain wallet linked to {st.session_state.address}")
        role,details= fetch_user_data(st.session_state.address)
        get_transaction_hash(st.session_state.address, role)
    elif st.session_state.page == "Share Credentials":
        role,details= fetch_user_data(st.session_state.address)
        monitor_credentials_ui(role,st.session_state.address)
