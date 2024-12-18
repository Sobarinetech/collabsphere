import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

# Load Firebase credentials from Streamlit secrets
firebase_json = st.secrets["firebase"]["admin_json"]
database_url = st.secrets["firebase"]["database_url"]

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})

# Streamlit App Configuration
st.set_page_config(page_title="Firebase Collaboration Platform", layout="wide")
st.title("🔥 Firebase Collaboration Platform")

# Input Workspace Name
workspace_name = st.text_input("Enter workspace name:", placeholder="E.g., TeamAlpha")
if not workspace_name:
    st.warning("Please enter a workspace name.")
    st.stop()

# Shared Notes Section
st.header("📝 Collaborative Notes")
notes_ref = db.reference(f"workspaces/{workspace_name}/notes")

# Fetch existing notes
existing_notes = notes_ref.get()
if existing_notes is None:
    existing_notes = ""

# Display a text area for collaborative notes
notes = st.text_area("Shared Notes:", existing_notes, height=200)
if st.button("Save Notes"):
    notes_ref.set(notes)
    st.success("Notes saved successfully!")

# Task Management Section
st.header("✅ Task Management")
tasks_ref = db.reference(f"workspaces/{workspace_name}/tasks")

# Add a new task
task_input = st.text_input("Add a new task:", placeholder="E.g., Complete project proposal")
if st.button("Add Task"):
    task_id = tasks_ref.push({"task": task_input, "status": "Pending"})
    st.success("Task added successfully!")

# Display existing tasks
tasks = tasks_ref.get()
if tasks:
    for task_id, task_data in tasks.items():
        col1, col2 = st.columns([6, 2])
        col1.write(f"{task_data['task']} (Status: {task_data['status']})")
        if col2.button("Mark Complete", key=task_id):
            tasks_ref.child(task_id).update({"status": "Completed"})
            st.experimental_rerun()

# Footer
st.write("---")
st.write("Built with Streamlit and Firebase")
