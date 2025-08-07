import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
import gspread
from google.oauth2 import service_account

st.set_page_config(page_icon = '🌌')

columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories = ['object','emotion','action','setting']

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-e61ccb85d72c.json'  # Upload this to your app directory
SHEET_NAME = 'data'
WORKSHEET_NAME_GEN = 'generated'  # Usually Sheet1 unless renamed
WORKSHEET_NAME_CHOSE = 'chosen'
WORKSHEET_NAME_READY = 'readyup'

# Auth and connect
@st.cache_resource
def connect_to_gsheet(worksheet_name):
    # Uncomment for Local Development
    # creds = service_account.Credentials.from_service_account_file(
    #     SERVICE_ACCOUNT_FILE,
    #     scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    # )
    # Uncomment for Deployed
    creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[ "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
        )
    gc = gspread.authorize(creds)
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(worksheet_name)

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

# Importing and saving Google Sheets
sheet_gen = connect_to_gsheet(WORKSHEET_NAME_GEN)
sheet_chose = connect_to_gsheet(WORKSHEET_NAME_CHOSE)
sheet_ready = connect_to_gsheet(WORKSHEET_NAME_READY)

data_gen = sheet_gen.get_all_records()
data_chose = sheet_chose.get_all_records()
data_ready = sheet_ready.get_all_records()

categories_df = pd.DataFrame(data_gen)[columns_to_get]
selected_df = pd.DataFrame(data_chose)
ready_df = pd.DataFrame(data_ready)

today = dt.date.today()

joined = categories_df.join(selected_df, lsuffix = '_category', rsuffix = '_selected', on = 'upload_number')

# Getting data for the latest story
max_upload_number = joined["upload_number_category"].max()
max_upload_date = joined["upload_date_category"].max()

max_data = joined[joined["upload_number_category"] == max_upload_number]

max_due_date = dt.datetime.strptime(max_data.loc[max_upload_number, 'due_date'], "%Y-%m-%d").date()
days_left = max_due_date - today

# add a row to selected_df if it doesn't exist yet
if max_upload_number not in (selected_df.upload_number):
    # selected_df.loc[max_upload_number] = {"upload_number": max_upload_number, 'upload_date': max_upload_date}
    new_row = {"upload_number": max_upload_number, 'upload_date': max_upload_date}

    sheet_chose.append_row([str(value) for value in new_row.values()])

if days_left.days >= 0:
    st.header(f'You have {days_left.days} days left to write your story!')
    st.subheader(f'Your story is due {max_data.loc[max_upload_number, 'due_date']} and '
                 f'should be between {round(max_data.loc[max_upload_number, 'word_count']-max_data.loc[max_upload_number, 'word_count']/10)} and'
                 f' {round(max_data.loc[max_upload_number, 'word_count']+max_data.loc[max_upload_number, 'word_count']/10)} words long')

    if max_data.loc[max_upload_number,'object_selected'] == '' or max_data.loc[max_upload_number,'emotion_selected'] == ''\
             or max_data.loc[max_upload_number,'action_selected'] == '' or max_data.loc[max_upload_number,'setting_selected'] == '':
        st.write("Not everyone has chosen words for their selected Category. Please return when that is done!")
        st.write('For this story:')
        for category in categories:
            st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{} is choosing in the {} category".format(max_data.loc[max_upload_number, f'{category}_category'],
                                                         category.capitalize()))
    elif pd.isna(max_data.loc[max_upload_number,'object_selected']) or pd.isna(max_data.loc[max_upload_number,'emotion_selected'])\
             or pd.isna(max_data.loc[max_upload_number,'action_selected']) or pd.isna(max_data.loc[max_upload_number,'setting_selected']):
        st.write("Not everyone has chosen words for their selected Category. Please return when that is done!")
        st.write('For this story:')
        for category in categories:
            st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{} is choosing in the {} category".format(max_data.loc[max_upload_number, f'{category}_category'],
                                                         category.capitalize()))
    else:
        for category in categories:
            st.write('{} chose {} in the {} category'.format(max_data.loc[max_upload_number,f'{category}_category'],
                                                             max_data.loc[max_upload_number,f'{category}_selected'].capitalize(),
                                                             category.capitalize()))


    with st.expander('Click to Show Previous Choices'):
        prev_df = pd.DataFrame()
        prev_df['upload_number'] = joined['upload_number']
        prev_df['due_date'] = joined['due_date']
        prev_df['word_count'] = joined['word_count']

        for category in categories:
            prev_df[category] = joined[f'{category}_category'].astype(str) + " : " + joined[f'{category}_selected'].astype(str)

        st.table(prev_df[prev_df['upload_number'] != max_upload_number])
else:
    st.header("Ready Up to get started on your next story!")
    member_list = [x for x in ready_df.columns if x != 'story_end']
    member_count = len(member_list)
    sum_flags = 0
    for member in member_list:
        sum_flags += ready_df.loc[0, member]

    # Reset the ready flags ONLY if the last due date is after the last time it was reset (to prevent resetting mid story),
    # the due date is already past, and if all flags are 1
    if (ready_df.loc[0, 'story_end'] < max_data.loc[max_upload_number, 'due_date']) & \
        (days_left.days < 0) & (member_count == sum_flags):
        for member in member_list:
            update_col = get_col_number(sheet_ready, member)
            sheet_ready.update_cell(2, update_col, 0)
        update_col = get_col_number(sheet_ready, 'story_end')
        sheet_ready.update_cell(2, update_col, str(dt.date.today()))






