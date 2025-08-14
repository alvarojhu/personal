import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_icon = '🌌')

# Initialization
columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories = ['object','emotion','action','setting']
password = 'Toto'
import gspread
from google.oauth2 import service_account

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-e61ccb85d72c.json'  # Upload this to your app directory
SHEET_NAME = 'data'
WORKSHEET_NAME_GEN = 'generated'  # Usually Sheet1 unless renamed
WORKSHEET_NAME_CHOSE = 'chosen'

# determining environment
try:
    # pull either prod or staging
    ENV = st.secrets['env']['APP_ENV']
except Exception:
    # if local development, use local
    ENV = 'dev'

# Auth and connect
@st.cache_resource
def connect_to_gsheet(worksheet_name):
    if ENV == 'dev':
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
        )
    else:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
        )
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(worksheet_name)

sheet_gen = connect_to_gsheet(WORKSHEET_NAME_GEN)
sheet_chose = connect_to_gsheet(WORKSHEET_NAME_CHOSE)

data_gen = sheet_gen.get_all_records()
data_chose = sheet_chose.get_all_records()

categories_df = pd.DataFrame(data_gen)[columns_to_get]
selected_df = pd.DataFrame(data_chose)

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


if "save_word" not in st.session_state:
    st.session_state.save_word = False

# building dataframes
joined = categories_df.join(selected_df, lsuffix = '_category', rsuffix = '_selected', on = 'upload_number')

max_upload_number = joined["upload_number_category"].max()
max_upload_date = joined["upload_date_category"].max()

max_data = joined[joined["upload_number_category"] == max_upload_number]
# adding a row to the sheet if it doesn't exist
if max_upload_number not in (selected_df.upload_number):
    # selected_df.loc[max_upload_number] = {"upload_number": max_upload_number, 'upload_date': max_upload_date}
    new_row = {"upload_number": max_upload_number, 'upload_date': max_upload_date}

    sheet_chose.append_row([str(value) for value in new_row.values()])
# building app
st.header('Category Input Page')

st.subheader("Use this page to add the word you've selected for your category")

cats_for_dropdown = []
for category in categories:
    if max_data.loc[max_upload_number, '{}_selected'.format(category)] == '':
        cats_for_dropdown.append(category)

cat_selection = st.selectbox(options = [x.capitalize() for x in cats_for_dropdown], label = 'Category',
                             index = None, placeholder = 'Only Available Categories will Appear')
st.session_state.cat = cat_selection

# if all(pd.notna([max_data.loc[max_upload_number,'object_selected'],max_data.loc[max_upload_number,'emotion_selected'],
#     max_data.loc[max_upload_number,'action_selected'],max_data.loc[max_upload_number,'setting_selected']])):
if max_data.loc[max_upload_number,'object_selected'] != '' and max_data.loc[max_upload_number,'emotion_selected'] != ''\
   and max_data.loc[max_upload_number,'action_selected'] != '' and max_data.loc[max_upload_number,'setting_selected'] != '':

    st.write("All Categories have been selected. Check the 'Current Story' tab to see what everyone chose")

if cat_selection:
    max_category = max_data.loc[max_upload_number,'{}_selected'.format(cat_selection.lower())]
    if max_category != '':
        st.info('Your selection already has a word! Select a different one.')
    else:
        word_selection = st.text_input(label = 'Chosen Word')
        if st.button('Save Word'):
            st.session_state.save_word = True
        if st.session_state.save_word:
            user_pass = st.text_input('Enter Password')
            if user_pass == '':
                pass
            elif user_pass == password:
                records = sheet_chose.get_all_records()
                for i, row in enumerate(records, start=2):  # start=2 to match actual row number (skip header)
                    if row["upload_number"] == max_upload_number:
                        update_col = get_col_number(sheet_chose, cat_selection.lower())
                        sheet_chose.update_cell(i, update_col, word_selection)

                st.write('Word Saved! Check the "Current Story" tab once everyone is done submitting their word.')
                st.session_state.save_word = False
                st.rerun()
            else:
                st.write('Incorrect Password. Try Again')



