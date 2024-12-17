import streamlit as st
from pymongo import MongoClient
from web3 import Web3
import json
from datetime import datetime
import pandas as pd
from landing import fetch_user_data  # Import the function to fetch user data

# Blockchain and MongoDB Configuration
infura_url = "https://sepolia.infura.io/v3/48cb49733a1446978ac6b86326b3a314"
web3 = Web3(Web3.HTTPProvider(infura_url))

with open("institute\SmartContractABI.json", "r") as abi_file:  # ABI JSON file
    contract_abi = json.load(abi_file)
contract_address = Web3.to_checksum_address("0x3DEbd84293E38591a99A8d954488168272aF687d")
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["edu_chain_verify"]
credentials_collection = db["credentials"]

# Smart Contract and Admin Wallet Configuration
admin_wallet_address = "0xee246D123f324a0aF1065B972AC398802EE63689"
private_key = "d44d90b7885b6b12a40206819dc0a9170a85283b3f17d8263ac3b66d95562ab3"

# ---------------------------- Utility Functions ---------------------------- #
def get_transaction_hash(txn):
    return web3.to_hex(txn)

# ---------------------------- Issue Credential UI ---------------------------- #
def issue_credential_ui(m):
    st.subheader("Issue New Credential")
    user_role,detail  = fetch_user_data(m)  # Get user role from session

    # Ensure only institutes can issue credentials
    if user_role != "institute":
        st.error("Only an institute can issue credentials.")
        return

    with st.form("issue_form"):
        student_name = st.text_input("Student Name")
        student_email = st.text_input("Student Email")
        course = st.text_input("Course")
        wallet_address = st.text_input("Student Wallet Address")
        submitted = st.form_submit_button("Issue Credential")
        if submitted:
            issue_credential(student_name, student_email, course, wallet_address)

# ---------------------------- Revoke Credential UI ---------------------------- #
def revoke_credential_ui(m):
    st.subheader("Revoke Credential")
    user_role,detail = fetch_user_data(m)
    
    # Ensure only institutes can revoke credentials
    if user_role != "institute":
        st.error("Only an institute can revoke credentials.")
        return

    credential_id = st.text_input("Enter Credential ID")
    reason = st.text_input("Reason for Revocation")
    if st.button("Revoke"):
        revoke_credential(credential_id, reason)

# ---------------------------- Search Credential UI ---------------------------- #
def search_credential_ui():
    st.subheader("Search Credential")
    search_query = st.text_input("Enter Student Email")
    if st.button("Search"):
        results = credentials_collection.find({
            "$or": [
                {"credential_id": search_query},
                {"student_email": search_query}
            ]
        })
        for cred in results:
            st.json(cred)

# ---------------------------- Analytics Dashboard UI ---------------------------- #
def analytics_dashboard_ui():
    st.subheader("Analytics Dashboard")
    total_credentials = credentials_collection.count_documents({})
    revoked_credentials = credentials_collection.count_documents({"status": "revoked"})
    active_credentials = total_credentials - revoked_credentials
    st.write(f"**Total Credentials:** {total_credentials}")
    st.write(f"**Active Credentials:** {active_credentials}")
    st.write(f"**Revoked Credentials:** {revoked_credentials}")

# ---------------------------- Monitor Credentials UI ---------------------------- #
def monitor_credentials_ui():
    st.subheader("Monitor All Credentials")
    credentials = fetch_credentials()
    df = pd.DataFrame(credentials)
    df.drop(columns=["_id"], inplace=True)
    st.dataframe(df)
    if st.button("Export to CSV"):
        df.to_csv("credentials_data.csv", index=False)
        st.success("Data exported successfully!")

# ---------------------------- Core Functions ---------------------------- #
def issue_credential(student_name, student_email, course, wallet_address):
    credential_id = int(datetime.now().timestamp())
    try:
        nonce = web3.eth.get_transaction_count(admin_wallet_address)
        txn = contract.functions.issueCredential(credential_id, wallet_address, course).build_transaction({
            'chainId': 11155111,
            'gas': 200000,
            'gasPrice': web3.to_wei('20', 'gwei'),
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)

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
        st.success(f"Credential issued successfully. Transaction Hash: {txn_hash}")
    except Exception as e:
        st.error(f"Error issuing credential: {e}")

def revoke_credential(credential_id, reason):
    credentials_collection.update_one({"credential_id": credential_id}, {
        "$set": {"status": "revoked", "revoked_reason": reason}
    })
    st.success("Credential revoked successfully.")

def fetch_credentials():
    return list(credentials_collection.find())
