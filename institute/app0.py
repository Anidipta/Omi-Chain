import streamlit as st
from pymongo import MongoClient
from web3 import Web3
import pandas as pd
import json
import os
from datetime import datetime

# ---------------------------- Configurations ---------------------------- #
# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/" 
client = MongoClient(MONGO_URI)
db = client["edu_chain_verify"]
credentials_collection = db["credentials"]

# Blockchain Configuration
infura_url = "https://sepolia.infura.io/v3/48cb49733a1446978ac6b86326b3a314"  # Replace with your Infura URL
web3 = Web3(Web3.HTTPProvider(infura_url))



# Smart Contract ABI and Address
with open("SmartContractABI.json", "r") as abi_file:  # ABI JSON file
    contract_abi = json.load(abi_file)
contract_address = Web3.to_checksum_address("0x3DEbd84293E38591a99A8d954488168272aF687d")
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Admin Wallet Configuration
admin_wallet_address = "0xee246D123f324a0aF1065B972AC398802EE63689"   # Replace with wallet address
private_key = "d44d90b7885b6b12a40206819dc0a9170a85283b3f17d8263ac3b66d95562ab3" # Load admin private key securely

# ---------------------------- Authentication ---------------------------- #
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def admin_login():
    st.sidebar.subheader("Admin Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin123":  # Replace with secure checks
            st.session_state.authenticated = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

def logout():
    st.session_state.authenticated = False
    st.sidebar.info("Logged out successfully.")

# ---------------------------- Utility Functions ---------------------------- #
def get_transaction_hash(txn):
    return web3.to_hex(txn)

def fetch_credentials():
    return list(credentials_collection.find())

# ---------------------------- Credential Features ---------------------------- #
def issue_credential(student_name, student_email, course, wallet_address):
    credential_id = int(datetime.now().timestamp())  # Use timestamp as uint256
    try:
        # Print out details for debugging
        print("Credential ID:", credential_id)
        print("Wallet Address:", wallet_address)
        print("Course:", course)

        # Blockchain Interaction
        nonce = web3.eth.get_transaction_count(admin_wallet_address)
        print("Nonce:", nonce)
        
        # Prepare the transaction
        txn = contract.functions.issueCredential(credential_id, wallet_address, course).build_transaction({
            'chainId': 11155111,
            'gas': 200000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce
        })
        
        # Print transaction details
        print("Transaction:", txn)
        
        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        
        # Print signed transaction details
        print("Signed Transaction:", signed_txn)
        print("Signed Transaction Type:", type(signed_txn))
        
        # Try sending the transaction
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Save to MongoDB
        credentials_collection.insert_one({
            "credential_id": credential_id,
            "student_name": student_name,
            "student_email": student_email,
            "course": course,
            "issue_date": datetime.now().isoformat(),
            "status": "active",
            "wallet_address": wallet_address,
            "transaction_hash": get_transaction_hash(txn_hash),
            "revoked_reason": None
        })
        st.success(f"Credential issued successfully. Transaction Hash: {get_transaction_hash(txn_hash)}")
    except Exception as e:
        st.error(f"Error issuing credential: {str(e)}")
        # Print the full traceback for more detailed debugging
        import traceback
        traceback.print_exc()

# Revoke Credential
def revoke_credential(credential_id, reason):
    credential = credentials_collection.find_one({"credential_id": credential_id})
    if not credential:
        st.error("Credential not found.")
        return
    try:
        # Smart Contract Interaction
        nonce = web3.eth.get_transaction_count(admin_wallet_address)
        txn = contract.functions.revokeCredential(credential_id).build_transaction({
            'chainId': 11155111,
            'gas': 200000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(signed_txn)
        
        # Update MongoDB
        credentials_collection.update_one(
            {"credential_id": credential_id},
            {"$set": {"status": "revoked", "revoked_reason": reason}}
        )
        st.success(f"Credential revoked successfully. Transaction Hash: {get_transaction_hash(txn_hash)}")
    except Exception as e:
        st.error(f"Error revoking credential: {e}")

# ---------------------------- Streamlit UI ---------------------------- #
if not st.session_state.authenticated:
    admin_login()
else:
    st.sidebar.button("Logout", on_click=logout)
    st.title("EduChainVerify - Institutional Dashboard")

    menu = ["Issue Credential", "Revoke Credential", "Search Credential", "Analytics Dashboard", "Monitor Credentials"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Issue Credential":
        st.subheader("Issue New Credential")
        with st.form("issue_form"):
            student_name = st.text_input("Student Name")
            student_email = st.text_input("Student Email")
            course = st.text_input("Course")
            wallet_address = st.text_input("Student Wallet Address")
            submitted = st.form_submit_button("Issue Credential")
            if submitted:
                issue_credential(student_name, student_email, course, wallet_address)

    elif choice == "Revoke Credential":
        st.subheader("Revoke Credential")
        credential_id = st.text_input("Enter Credential ID")
        reason = st.text_input("Reason for Revocation")
        if st.button("Revoke"):
            revoke_credential(credential_id, reason)

    elif choice == "Search Credential":
        st.subheader("Search Credential")
        search_query = st.text_input("Enter Credential ID or Student Email")
        if st.button("Search"):
            results = credentials_collection.find({
                "$or": [
                    {"credential_id": search_query},
                    {"student_email": search_query}
                ]
            })
            for cred in results:
                st.json(cred)

    elif choice == "Analytics Dashboard":
        st.subheader("Analytics Dashboard")
        total_credentials = credentials_collection.count_documents({})
        revoked_credentials = credentials_collection.count_documents({"status": "revoked"})
        active_credentials = total_credentials - revoked_credentials
        st.write(f"**Total Credentials:** {total_credentials}")
        st.write(f"**Active Credentials:** {active_credentials}")
        st.write(f"**Revoked Credentials:** {revoked_credentials}")

    elif choice == "Monitor Credentials":
        st.subheader("Monitor All Credentials")
        credentials = fetch_credentials()
        df = pd.DataFrame(credentials)
        df.drop(columns=["_id"], inplace=True)
        st.dataframe(df)
        if st.button("Export to CSV"):
            df.to_csv("credentials_data.csv", index=False)
            st.success("Data exported successfully!")