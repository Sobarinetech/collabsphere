import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import random

# Firebase Configuration
cred = credentials.Certificate("path/to/firebase-credentials.json")  # Replace with your Firebase credentials
firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-database.firebaseio.com'})

# Streamlit App Configuration
st.set_page_config(page_title="CollabSphere", layout="wide")
st.title("\U0001F91D CollabSphere: Real-Time Collaboration Platform")

# User Login
username = st.text_input("Enter your pseudonym:", placeholder="E.g., CreativeSoul123")
if not username:
    st.warning("Please enter a pseudonym to proceed.")
    st.stop()

workspace = st.text_input("Enter or create a workspace name:", placeholder="E.g., TeamAlpha")
if not workspace:
    st.warning("Please provide a workspace name.")
    st.stop()

st.info(f"Welcome, {username}! You are in workspace: {workspace}")

# Firebase Database References
workspace_ref = db.reference(f"workspaces/{workspace}")
chat_ref = workspace_ref.child("chats")
notes_ref = workspace_ref.child("notes")
tasks_ref = workspace_ref.child("tasks")
leaderboard_ref = workspace_ref.child("leaderboard")

# Real-Time Chat
st.subheader("\U0001F4AC Real-Time Chat")
chat_input = st.text_input("Send a message:")
if st.button("Send"):
    chat_ref.push({"username": username, "message": chat_input, "timestamp": str(datetime.now())})

# Display Chat Messages
st.markdown("### Chat Messages:")
chat_data = chat_ref.get()
if chat_data:
    for msg in chat_data.values():
        st.write(f"**{msg['username']}**: {msg['message']} (_{msg['timestamp']}_)")

# Real-Time Shared Notes
st.subheader("\U0001F4DD Collaborative Notes")
notes = notes_ref.get() or ""
updated_notes = st.text_area("Shared Notes:", notes, height=200)
if updated_notes != notes:
    notes_ref.set(updated_notes)

# Task Management
st.subheader("\U00002705 Task Management")
new_task = st.text_input("Add a task:")
if st.button("Add Task"):
    tasks_ref.push({"task": new_task, "status": "Pending", "assigned": username})

st.markdown("### Tasks:")
tasks = tasks_ref.get()
if tasks:
    for task_id, task in tasks.items():
        col1, col2, col3 = st.columns([6, 2, 2])
        col1.write(f"{task['task']} (Assigned: {task['assigned']})")
        col2.write(task['status'])
        if col3.button("Mark Complete", key=task_id):
            tasks_ref.child(task_id).update({"status": "Completed"})

# Leaderboard
st.subheader("\U0001F3C6 Leaderboard")
leaderboard = leaderboard_ref.get() or {}
leaderboard[username] = leaderboard.get(username, 0) + random.randint(1, 5)
leaderboard_ref.set(leaderboard)

st.markdown("### Points:")
for user, points in sorted(leaderboard.items(), key=lambda x: x[1], reverse=True):
    st.write(f"{user}: {points} points")

# File Sharing
st.subheader("\U0001F4C4 File Sharing")
uploaded_files = st.file_uploader("Upload files:", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        file_data = file.read()
        workspace_ref.child("files").push({"filename": file.name, "data": file_data.decode()})
        st.success(f"Uploaded: {file.name}")

# Display Shared Files
st.markdown("### Shared Files:")
shared_files = workspace_ref.child("files").get()
if shared_files:
    for file in shared_files.values():
        st.write(f"**{file['filename']}**")
