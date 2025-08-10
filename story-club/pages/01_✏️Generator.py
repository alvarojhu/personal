import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import random
import base64
from pathlib import Path
import gspread
from google.oauth2 import service_account

st.set_page_config(page_icon = '🌌')

# Initializing values
parent_folder = Path(__file__).parent.parent
columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories = ['object','emotion','action','setting']
password = 'Toto'

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-e61ccb85d72c.json'  # Upload this to your app directory
SHEET_NAME = 'data'
WORKSHEET_NAME_GEN = 'generated'  # Usually Sheet1 unless renamed
WORKSHEET_NAME_READY = 'readyup'
WORKSHEET_NAME_MEMBERS = 'members'

# Auth and connect
@st.cache_resource
def connect_to_gsheet(worksheet_name):
    # Uncomment for Local Development
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    )
    # Uncomment for Deployed
    # creds = service_account.Credentials.from_service_account_info(
    #     st.secrets["gcp_service_account"],
    #     scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    # )
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(worksheet_name)

def get_image_download_link(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<img src="data:image/gif;base64,{b64}" width="400">'

def shuffle_avoiding_fixed_points(prev, members):
    """Return a shuffled version of `prev` where
       no element remains in the same index."""
    while True:
        new = members  # copy
        random.shuffle(new)
        if all(a != b for a, b in zip(new, prev)):
            return new

def get_col_number(sheet, column_name, header_row=1):
    """
    Return 1‑based column number that matches `column_name`.
    Raises KeyError if not found.
    """
    headers = sheet.row_values(header_row)          # list of header strings
    try:
        # `.index` is 0‑based → add 1 for Sheets’ 1‑based columns
        return headers.index(column_name) + 1
    except ValueError:
        raise KeyError(f"Column '{column_name}' not found in header row")

# Connecting to Google Sheet
sheet_gen = connect_to_gsheet(WORKSHEET_NAME_GEN)
sheet_ready = connect_to_gsheet(WORKSHEET_NAME_READY)
sheet_members = connect_to_gsheet(WORKSHEET_NAME_MEMBERS)

# Read as DataFrame
generated_data = sheet_gen.get_all_records()
categories_df = pd.DataFrame(generated_data)[columns_to_get]

data_ready = sheet_ready.get_all_records()
ready_df = pd.DataFrame(data_ready)

data_members = sheet_members.get_all_records()
members_df = pd.DataFrame(data_members)

member_list = list(members_df['member'].values)

max_upload = categories_df.upload_number.max()
max_due_date = dt.datetime.strptime(categories_df.loc[max_upload,'due_date'], "%Y-%m-%d").date()
today = dt.date.today()
days_left = max_due_date - today

# summing flags
sum_flags = 0
for member in member_list:
    sum_flags += ready_df.loc[0, member]

def main():
    if (days_left.days < 0) and (sum_flags<len(member_list)):
        # initializing variables
        if "ready" not in st.session_state:
            st.session_state.ready = False

        st.header('Ready Up to Get Started on your Next Story!')
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if sum_flags >= 1:
                st.header('🚩')
            else:
                st.write('❌')
        with c2:
            if sum_flags >= 2:
                st.header('🚩')
            else:
                st.write('❌')
        with c3:
            if sum_flags >= 3:
                st.header('🚩')
            else:
                st.write('❌')
        with c4:
            if sum_flags >= 4:
                st.header('🚩')
            else:
                st.write('❌')
        member_select = st.selectbox(options = member_list, label = 'Ready Up')
        if st.button("I'm Ready"):
            st.session_state.ready = True
        if st.session_state.ready:
            user_pass = st.text_input('Enter Password')
            if user_pass == '':
                pass
            elif user_pass == password:
                update_col = get_col_number(sheet_ready, member_select)
                sheet_ready.update_cell(2, update_col, 1)
                st.write(f'Thanks for Readying Up {member_select}')
                st.session_state.ready = False # reset session state
                st.rerun() # re-run the page so that the flag pops up
            else:
                st.write('Incorrect Password. Try Again')
    elif days_left.days > 0:
        # if there's a new story generated and the due date hasn't come yet
        st.title("Current Story in Progress. View Current Story Tab for Details")
        # Reset the flags to 0 if a new story was generated
        for member in member_list:
            update_col = get_col_number(sheet_ready, member)
            sheet_ready.update_cell(2, update_col, 0)
    else:
        # initializing variables
        if "click_save" not in st.session_state:
            st.session_state.click_save = False

        st.title("Generate Your Story")

        # setting the story length odds
        odds_500 = 0.1
        odds_1000 = 0.2
        odds_1500 = 0.35
        odds_2000 = 0.2
        odds_2500 = 0.1
        odds_3000 = 0.05

        with st.expander('Story Length Odds'):
            st.info(f'Odds of story length are {odds_500*100}% for 500 words, {odds_1000*100}% for 1000,  '
                    f'{odds_1500*100}% for 1500, {odds_2000*100}% for 2000 words, {odds_2500*100}% for 2500, and {odds_3000*100}% for 3000 words. '
                    'There are 5 Days assigned per 100 words of story selected. ')

        image = 'gifs/tars.gif'

        # setting the chosen categories to blank if randomize hasn't been hit yet
        if 'object' not in st.session_state:
            for category in categories:
                st.session_state[category] = ''
            st.session_state.word_count = 0
            st.session_state.due_date = dt.date.today()

        if st.button('Randomize'):

            st.session_state.message = "Update"

            # gets the previous list of categories and who chose them, so that the new list doesn't repeat
            prev = []
            for category in categories:
                prev.append(categories_df.loc[max_upload, category])

            new_list = shuffle_avoiding_fixed_points(prev, member_list)

            # sets the session states for each category to the chosen member
            for category, i in zip(categories, np.arange(0,len(new_list))):
                st.session_state[category] = new_list[i]

            # sets the word_count session state depending on what random number has been generated
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

            # calculated the due date based on the word length
            days_to_add = dt.timedelta(days=(st.session_state.word_count/100)+1)

            due_date = dt.date.today() + days_to_add
            st.session_state.due_date = due_date

        c1,c2 = st.columns(2)
        with (c1):

            # printing categories and who is selecting (or nothing)
            st.write('Object / Noun: {}'.format(st.session_state.object))

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
                    new_row = {'upload_number':max_upload+1,'upload_date': dt.date.today(), 'object': st.session_state.object,
                               'action': st.session_state.action, 'emotion': st.session_state.emotion,
                               'setting': st.session_state.setting, 'word_count': st.session_state.word_count,
                               'due_date':st.session_state.due_date}
                    try:
                        sheet_gen.append_row([str(value) for value in new_row.values()])
                        st.write('Categories Saved! Check the Current Story tab to see how long you have left.')
                        st.session_state.click_save = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add row: {e}")

                else:
                    st.write('Incorrect Password. Try Again')
        with c2:
            st.markdown(get_image_download_link(parent_folder / image), unsafe_allow_html=True)

if __name__ == '__main__':
    main()