import streamlit as st
import sqlite3
from pymongo import MongoClient
from web3 import Web3
import json
from datetime import datetime
#from institute.app1 import analytics_dashboard_ui

# Blockchain and MongoDB Configuration
infura_url = "https://sepolia.infura.io/v3/48cb49733a1446978ac6b86326b3a314"
web3 = Web3(Web3.HTTPProvider(infura_url))

with open("institute/SmartContractABI.json", "r") as abi_file:  # ABI JSON file
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

# Fetch User Role and Details
def fetch_user_data(metamask_address):
    try:
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, email, institute FROM students WHERE metamask_account = ?", (metamask_address,))
            student_result = cursor.fetchone()
            if student_result:
                return "student", {"name": student_result[0], "email": student_result[1], "institute": student_result[2]}
            
            cursor.execute("SELECT institute_name FROM institutes WHERE metamask_account = ?", (metamask_address,))
            institute_result = cursor.fetchone()
            if institute_result:
                return "institute", {"institute_name": institute_result[0]}
            
            return None, None
    except Exception as e:
        st.error(f"Database error: {e}")
        return None, None

def institute_dashboard(institute_details):
    
    st.title("Institute Dashboard")
    st.write(f"**Institute Name:** {institute_details['institute_name']}")
    st.subheader("Analytics Dashboard")
    total_credentials = credentials_collection.count_documents({})
    revoked_credentials = credentials_collection.count_documents({"status": "revoked"})
    active_credentials = total_credentials - revoked_credentials
    st.write(f"**Total Credentials:** {total_credentials}")
    st.write(f"**Active Credentials:** {active_credentials}")
    st.write(f"**Revoked Credentials:** {revoked_credentials}")
  
def student_dashboard(student_details):
    
    st.title("My Credentials")
    st.write(f"**Name:** {student_details['name']}")
    st.write(f"**Email:** {student_details['email']}")
    st.write(f"**Institute:** {student_details['institute']}") 
    

def landing(m):
    role, details = fetch_user_data(m)
    if role == "student":
            student_dashboard(details)
    else:
            institute_dashboard(details)
