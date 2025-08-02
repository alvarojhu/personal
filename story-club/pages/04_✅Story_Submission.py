import streamlit as st
import os
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import base64
import pickle

st.set_page_config(page_icon = '🌌')

if "submit_story" not in st.session_state:
    st.session_state.submit_story = False
password = 'Toto'

# Set up credentials and Drive API
# SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-e61ccb85d72c.json'  # No longer using service account
FOLDER_ID = '1zZtfu-f6EyD93gTUOhNgY2K7ofYEOPaU'  # The ID of the shared Google Drive folder

# pull in access token for personal upload
token_bytes = base64.b64decode(st.secrets["drive_oauth"]['credentials'])
creds = pickle.loads(token_bytes)

# previously used for service account upload
# @st.cache_resource
# def get_drive_service():
#     # Uncomment for Local Development
#     # creds = service_account.Credentials.from_service_account_file(
#     #     SERVICE_ACCOUNT_FILE,
#     #     scopes=['https://www.googleapis.com/auth/drive']
#     # )
#     # Uncomment for Deployed
#     creds = service_account.Credentials.from_service_account_info(
#         st.secrets["gcp_service_account"],
#         scopes=['https://www.googleapis.com/auth/drive']
#     )
#
#     return build('drive', 'v3', credentials=creds)

# Streamlit UI
st.title("Upload Your Story Anonymously Here")

st.header("You're finally ready to submit your Story!")

url = 'https://drive.google.com/drive/u/1/folders/1zZtfu-f6EyD93gTUOhNgY2K7ofYEOPaU'

st.markdown(f"You can view all story submissions [here]({url})", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a file to upload")

if uploaded_file:
    st.success(f"File `{uploaded_file.name}` ready to upload.")
    if st.button("Upload to Google Drive"):
        st.session_state.submit_story = True
    if st.session_state.submit_story:
        user_pass = st.text_input('Enter Password')
        if user_pass == '':
            pass
        elif user_pass == password:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_file_path = tmp_file.name

            try:
                service = build('drive', 'v3', credentials=creds)
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
        else:
            st.write('Incorrect Password. Try Again')


