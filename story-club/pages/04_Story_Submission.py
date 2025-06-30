import streamlit as st
import os
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-05ab670db57d.json'  # Upload this to your app directory
FOLDER_ID = '1zZtfu-f6EyD93gTUOhNgY2K7ofYEOPaU'  # The ID of the shared Google Drive folder

@st.cache_resource
def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

# Streamlit UI
st.title("📄 Upload Your Story Anonymously Here")

uploaded_file = st.file_uploader("Choose a file to upload")

if uploaded_file:
    st.success(f"File `{uploaded_file.name}` ready to upload.")
    if st.button("Upload to Google Drive"):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_file_path = tmp_file.name

        try:
            service = get_drive_service()
            file_metadata = {
                'name': uploaded_file.name,
                'parents': [FOLDER_ID]
            }
            media = MediaFileUpload(temp_file_path, resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            st.success(f"Upload successful! File ID: {file.get('id')}")
        except Exception as e:
            st.error(f"Upload failed: {e}")

