import streamlit as st
from pymongo import MongoClient
from web3 import Web3
import json
import os
import hashlib
import io
from datetime import datetime
import pandas as pd
from landing import fetch_user_data  # Import the function to fetch user data

UPLOAD_DIR = "uploaded_files"
QR_CODE_DIR = "qr_codes"  # Directory to store QR codes
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Blockchain and MongoDB Configuration
infura_url = "https://sepolia.infura.io/v3/48cb49733a1446978ac6b86326b3a314"
web3 = Web3(Web3.HTTPProvider(infura_url))

with open("https://github.com/Anidipta/Omi-Chain/blob/main/institute/SmartContractABI.json", "r") as abi_file:  # ABI JSON file
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
def get_transaction_hash(wallet_address, role ):
    # MongoDB query setup for all transactions by default
    if role == 'institute':
        query = {}

        # Fetch transactions from MongoDB
        transactions = list(credentials_collection.find(query))
        if transactions:
            # Display transaction hashes in a list
            st.write("Transaction Hashes:")
            st.write(transactions)
        else:
            st.write("No transactions found for the given filters.")
    else:
        credentials = fetch_credentials_by_address(wallet_address)

        if not credentials:
            st.warning("No records found for this wallet address.")
            return

        # Step 2: Fetch all transactions with the same wallet address
        query = {"wallet_address": wallet_address}
        transactions = list(credentials_collection.find(query))

        if transactions:
            # Display transaction hashes for the wallet address
            st.write("Transaction Hashes:")
            for transaction in transactions:
                st.write(transaction) 
        else:
            st.warning("No transactions found for this wallet address.")

        


# Function to generate a hash for a file
def generate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Function to generate a QR code for the file
def generate_qr_code(file_path):
    # QR code will encode the file path (you can modify it to a URL if the file is hosted elsewhere)
    qr = qrcode.make(file_path)
    
    # Save the QR code to a file in the QR_CODE_DIR
    qr_code_path = os.path.join(QR_CODE_DIR, f"{os.path.basename(file_path)}_qr.png")
    qr.save(qr_code_path)
    
    return qr_code_path

# Function to issue credentials and handle file uploads
def issue_credential_ui(m):
    st.subheader("Issue New Credential")
    user_role, detail = fetch_user_data(m)  # Get user role from session

    # Ensure only institutes can issue credentials
    if user_role != "institute":
        st.error("Only an institute can issue credentials.")
        return

    with st.form("issue_form"):
        # Step 1: Wallet Address Input
        wallet_address = st.text_input("Student Wallet Address")
        student_name = ""
        student_email = ""

        # If the wallet address is provided, search for details in MongoDB
        if wallet_address:
            result = credentials_collection.find_one({"wallet_address": wallet_address})
            if result:
                # Auto-fill student name and email if found
                student_name = result.get("student_name", "")
                student_email = result.get("student_email", "")
                st.text_input("Student Name", value=student_name, disabled=True)
                st.text_input("Student Email", value=student_email, disabled=True)
            else:
                # If no record found, ask for name and email
                student_name = st.text_input("Student Name")
                student_email = st.text_input("Student Email")
                st.warning("No record found for the given wallet address. Please enter the details.")

        # Step 2: Course Input
        course = st.text_input("Course")

        # Step 3: File Upload
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "jpg", "png", "docx", "txt"])
        
        submitted = st.form_submit_button("Issue Credential")
        if submitted and uploaded_file:
            # Save the uploaded file locally
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Generate file hash
            file_hash = generate_file_hash(file_path)

            # Save credential and file details in MongoDB
            credential_id = int(datetime.now().timestamp())  # Generate a unique credential ID
            credentials_collection.insert_one({
                "credential_id": credential_id,
                "student_name": student_name,
                "student_email": student_email,
                "course": course,
                "wallet_address": wallet_address,
                "file_hash": file_hash,
                "file_path": file_path,
                "transaction_hash": file_hash,  # You can use file hash as a transaction hash
                "issue_date": datetime.now().isoformat(),
                "status": "active"
            })

            st.success(f"Credential issued successfully! Transaction Hash: {file_hash}")
            
            
# ---------------------------- Revoke Credential UI ---------------------------- #
def revoke_credential_ui(m):
    st.subheader("Revoke Credential")
    user_role, detail = fetch_user_data(m)

    # Ensure only institutes can revoke credentials
    if user_role != "institute":
        st.error("Only an institute can revoke credentials.")
        return

    student_email = st.text_input("Enter Student Email")
    reason = st.text_input("Reason for Revocation")
    
    if st.button("Revoke All"):
        # Find all credentials associated with the email
        credentials = list(credentials_collection.find({"student_email": student_email}))
        if not credentials:
            st.warning("No credentials found for the provided email.")
            return

        # Display credentials in a list or table format
        st.write(f"**Found {len(credentials)} credential(s) for the email `{student_email}`:**")
        for index, cred in enumerate(credentials, start=1):
            st.write(f"**Credential {index}:**")
            st.json({
                "Credential ID": cred["credential_id"],
                "Student Name": cred["student_name"],
                "Course": cred["course"],
                "Issue Date": cred["issue_date"],
                "Status": cred.get("status", "active"),
                "Wallet Address": cred["wallet_address"],
                "Transaction Hash": cred.get("transaction_hash", "N/A")
            })

        # Revoke all credentials
        result = credentials_collection.update_many(
            {"student_email": student_email},
            {"$set": {"status": "revoked", "revoked_reason": reason}}
        )

        st.success(f"Successfully revoked {result.modified_count} credential(s).")

        # Display confirmation of revoked credentials
        st.write("**Revoked Credentials:**")
        for index, cred in enumerate(credentials, start=1):
            cred["status"] = "revoked"
            cred["revoked_reason"] = reason
            st.write(f"**Credential {index}:**")
            st.json(cred)


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
def fetch_credentials_by_address(wallet_address):
    return list(credentials_collection.find({"wallet_address": wallet_address}))

# Function to monitor and display credentials
def monitor_credentials_ui(role, m):
    if role == 'institute':
        
        st.subheader("Share Your Credentials")
        st.write("Feature to share your credentials securely.")
        credentials = fetch_credentials()
        df = pd.DataFrame(credentials)
        df.drop(columns=["_id"], inplace=True)
        st.dataframe(df)
        csv_data = df.to_csv(index=False)
        if st.download_button(
                    label="Export to CSV",
                    data=csv_data,
                    file_name="credentials_data.csv",
                    mime="text/csv"
                ):
            st.success("CSV file is ready for download!")

    else:
        # Step 1: Fetch credentials for the given wallet address (m)
        credentials = fetch_credentials_by_address(m)

        if not credentials:
            st.warning("No records found for this wallet address.")
            return

        # Step 2: Display each credential in a dropdown (without download option)
        for credential in credentials:
            # Display details for each credential
            st.subheader(f"Credential")

            # Show credential details
            st.write(f"Course: {credential['course']}")
            st.write(f"Issue Date: {credential['issue_date']}")
            st.write(f"Status: {credential['status']}")
            st.write(f"Transaction Hash: {credential['transaction_hash']}")
            st.write("---")
                
# ---------------------------- Core Functions ---------------------------- #
def issue_credential(student_name, student_email, course, wallet_address):
    credential_id = int(datetime.now().timestamp())
    try:
        nonce = web3.eth.get_transaction_count(admin_wallet_address)
        txn = contract.functions.issueCredential(credential_id, wallet_address, course).build_transaction({
            'chainId': 11155111,
            'gas': 22030,
            'gasPrice': web3.eth.gas_price,
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
