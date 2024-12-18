import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import tempfile

# Streamlit App Configuration
st.set_page_config(page_title="Firebase JSON Upload", layout="wide")
st.title("🔥 Firebase Integration with JSON Upload")

# Upload JSON File
st.header("📂 Upload Firebase Credentials")
uploaded_file = st.file_uploader("Upload your Firebase service account JSON file:", type="json")

if uploaded_file:
    # Save uploaded JSON file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_name = temp_file.name

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred = credentials.Certificate(temp_file_name)
        firebase_admin.initialize_app(cred, {
            "databaseURL": st.text_input("Enter your Firebase Database URL:", placeholder="https://your-database-url.firebaseio.com")
        })

    st.success("Firebase initialized successfully!")

    # Workspace Name Input
    workspace_name = st.text_input("Enter workspace name:", placeholder="E.g., TeamAlpha")
    if not workspace_name:
        st.warning("Please enter a workspace name.")
        st.stop()

    # Shared Notes Section
    st.header("📝 Collaborative Notes")
    notes_ref = db.reference(f"workspaces/{workspace_name}/notes")

    # Display existing notes
    existing_notes = notes_ref.get() or ""
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
        tasks_ref.push({"task": task_input, "status": "Pending"})
        st.success("Task added successfully!")

    # Display existing tasks
    tasks = tasks_ref.get() or {}
    for task_id, task_data in tasks.items():
        col1, col2 = st.columns([6, 2])
        col1.write(f"{task_data['task']} (Status: {task_data['status']})")
        if col2.button("Mark Complete", key=task_id):
            tasks_ref.child(task_id).update({"status": "Completed"})
            st.experimental_rerun()

    # Footer
    st.write("---")
    st.write("Built with Streamlit and Firebase")
else:
    st.info("Please upload your Firebase service account JSON file to proceed.")
