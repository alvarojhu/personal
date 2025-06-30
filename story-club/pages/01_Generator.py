import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import base64
from pathlib import Path
import gspread
from google.oauth2 import service_account

# Initializing values
parent_folder = Path(__file__).parent.parent
columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories = ['object','emotion','action','setting']
password = 'Toto'

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-05ab670db57d.json'  # Upload this to your app directory
SHEET_NAME = 'data'
WORKSHEET_NAME = 'generated'  # Usually Sheet1 unless renamed

# Auth and connect
@st.cache_resource
def connect_to_gsheet():
    # Uncomment for Local Development
    # creds = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE,
    #     scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    # )
    # Uncomment for Deployed
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(WORKSHEET_NAME)

sheet = connect_to_gsheet()

# Read as DataFrame
data = sheet.get_all_records()
categories_df = pd.DataFrame(data)[columns_to_get]

st.table(categories_df)

if "click_save" not in st.session_state:
    st.session_state.click_save = False

def get_image_download_link(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<img src="data:image/gif;base64,{b64}" width="400">'

def main():
    st.title("Interstellar Writer's Club Category Generator")

    odds_500 = 0.1
    odds_1000 = 0.3
    odds_1500 = 0.3
    odds_2000 = 0.2
    odds_2500 = 0.05
    odds_3000 = 0.05

    with st.expander('Story Length Odds'):
        st.info(f'Odds of story length are {odds_500*100}% for 500 words, {odds_1000*100}% each for 1000 and '
                f'1500, {odds_2000*100}% for 2000 words, and {odds_2500*100}% each for 2500 and 3000 words. '
                'There are 5 Days assigned per 100 words of story selected. ')

    member_list = ['Alvaro', 'Elijah', 'Favier', 'Raffy']

    image = 'gifs/tars.gif'

    if 'object' not in st.session_state:
        for category in categories:
            st.session_state[category] = ''
        st.session_state.word_count = 0
        st.session_state.due_date = dt.date.today()

    if st.button('Randomize'):

        st.session_state.message = "Update"
        np.random.shuffle(member_list)

        for category, i in zip(categories, np.arange(0,len(member_list))):
            st.session_state[category] = member_list[i]

        rand = np.random.random()
        if rand < odds_500:
            st.session_state.word_count = 500
            image = 'gifs/blackhole.gif'
        elif rand >= odds_500 and rand < odds_500 + odds_1000:
            st.session_state.word_count = 1000
            image = 'gifs/necessary.gif'
        elif rand >= odds_500 + odds_1000 and rand < odds_500 + odds_1000 + odds_1500:
            st.session_state.word_count = 1500
            image = 'gifs/yes.gif'
        elif rand >= odds_500 + odds_1000 + odds_1500 and rand < odds_500 + odds_1000 + odds_1500 + odds_2000:
            st.session_state.word_count = 2000
            image = 'gifs/humor.gif'
        elif rand >= odds_500 + odds_1000 + odds_1500 + odds_2000 and rand < odds_500 + odds_1000 + odds_1500 + odds_2000 + odds_2500:
            st.session_state.word_count = 2500
            image = 'gifs/interstellar-cost.gif'
        else:
            st.session_state.word_count = 3000
            image = 'gifs/crying.gif'

        days_to_add = dt.timedelta(days=(st.session_state.word_count/100)+1)

        due_date = dt.date.today() + days_to_add
        st.session_state.due_date = due_date

    c1,c2 = st.columns(2)
    with (c1):

        st.write('Object / Noun: {}'.format(st.session_state.object), font = 'Helvetica 16 bold')

        st.write('Emotion: {}'.format(st.session_state.emotion))

        st.write('Action / Verb: {}'.format(st.session_state.action))

        st.write('Setting / Location: {}'.format(st.session_state.setting))

        st.write(f"Word Count = {st.session_state.word_count} and it is due {st.session_state.due_date}")

        st.warning('WARNING! Do not click "Save Categories" unless you are ready for the next story')
        if st.button('Save Categories'):
            st.session_state.click_save = True

        if st.session_state.click_save:
            user_pass = st.text_input('Enter Password')
            if user_pass == '':
                pass
            elif user_pass == password:
                max_upload = categories_df.upload_number.max()
                new_row = {'upload_number':max_upload+1,'upload_date': dt.date.today(), 'object': st.session_state.object,
                           'action': st.session_state.action, 'emotion': st.session_state.emotion,
                           'setting': st.session_state.setting, 'word_count': st.session_state.word_count,
                           'due_date':st.session_state.due_date}
                try:
                    sheet.append_row([str(value) for value in new_row.values()])
                    st.write('Categories Saved! Check the Current Story tab to see how long you have left.')
                    st.session_state.click_save = False
                except Exception as e:
                    st.error(f"Failed to add row: {e}")

            else:
                st.write('Incorrect Password. Try Again')
    with c2:
        st.markdown(get_image_download_link(parent_folder / image), unsafe_allow_html=True)
if __name__ == '__main__':
    main()