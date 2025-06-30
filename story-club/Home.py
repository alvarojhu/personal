import streamlit as st
from pathlib import Path
import base64

parent_folder = Path(__file__).parent

def get_image_download_link(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<img src="data:image/gif;base64,{b64}" width="100%">'

def main():
    st.header("Welcome to the Interstellar Writer's Guild Homepage")

    st.subheader('Select a tab to get started.')

    st.write('Select **Generator** to randomize the next story entry')
    st.write('Select **Current Story** to see when the current story is due and words were chosen for the categories')
    st.write('Select **Category Input** to add your word once you are ready')
    st.write('Select **Story Submission** to submit your Story')

    image = 'gifs/large_blackhole.gif'
    st.markdown(get_image_download_link(parent_folder / image), unsafe_allow_html=True)

if __name__ == '__main__':
    main()