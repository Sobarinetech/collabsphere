import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Initialize Streamlit App
st.set_page_config(page_title="Collaboration Platform", layout="wide")
st.title("🌟 Real-Time Collaboration Platform with Firebase")

# Firebase Initialization
if not firebase_admin._apps:  # Ensure Firebase is initialized only once
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred, {
        "databaseURL": st.secrets["firebase"]["database_url"]
    })

# Database Reference
db_ref = db.reference("/collaboration")

# User Login
username = st.text_input("Enter your pseudonym to join:", placeholder="E.g., Creator123")
if not username:
    st.warning("Please enter a pseudonym to proceed.")
    st.stop()

st.success(f"Welcome, {username}! You can start collaborating in real time.")

# Workspace Selection
workspace = st.text_input("Enter or create a workspace name:", placeholder="E.g., TeamAlpha")
if not workspace:
    st.warning("Please provide a workspace name.")
    st.stop()

st.info(f"You are working in the workspace: {workspace}")

# Workspace Database Reference
workspace_ref = db_ref.child(workspace)

# Collaborative Notes Section
st.subheader("📝 Collaborative Notes")
notes = workspace_ref.child("notes").get() or ""
updated_notes = st.text_area("Shared Notes", value=notes, height=300)
if st.button("Save Notes"):
    workspace_ref.child("notes").set(updated_notes)
    st.success("Notes updated!")

# Task Management Section
st.subheader("✅ Task Management")
tasks = workspace_ref.child("tasks").get() or {}

# Display Tasks
for task_id, task_info in tasks.items():
    col1, col2, col3 = st.columns([6, 2, 2])
    col1.write(f"{task_info['task']} (Assigned to: {task_info['assigned']})")
    col2.write(task_info['status'])
    if col3.button("Mark Complete", key=f"complete_{task_id}"):
        task_info["status"] = "Completed"
        workspace_ref.child("tasks").child(task_id).set(task_info)
        st.experimental_rerun()

# Add New Task
new_task = st.text_input("Add a new task:", placeholder="E.g., Complete project proposal")
if st.button("Add Task"):
    task_id = workspace_ref.child("tasks").push({
        "task": new_task,
        "status": "Pending",
        "assigned": username
    }).key
    st.success("Task added!")
    st.experimental_rerun()

# Leaderboard Section
st.subheader("🏆 Leaderboard")
leaderboard = workspace_ref.child("leaderboard").get() or {}
leaderboard[username] = leaderboard.get(username, 0) + 10
workspace_ref.child("leaderboard").set(leaderboard)

sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
for rank, (user, points) in enumerate(sorted_leaderboard, start=1):
    st.write(f"{rank}. {user}: {points} points")

# File Sharing Section
st.subheader("📂 File Sharing")
uploaded_files = st.file_uploader("Upload files for the workspace:", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        file_path = f"files/{workspace}/{file.name}"
        workspace_ref.child("files").push({"filename": file.name, "content": file.getvalue().decode()})
        st.success(f"File uploaded: {file.name}")
