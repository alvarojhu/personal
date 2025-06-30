import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
import gspread
from google.oauth2 import service_account

columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories = ['object','emotion','action','setting']

# Set up credentials and Drive API
SERVICE_ACCOUNT_FILE = 'psyched-axle-269916-e61ccb85d72c.json'  # Upload this to your app directory
SHEET_NAME = 'data'
WORKSHEET_NAME_GEN = 'generated'  # Usually Sheet1 unless renamed
WORKSHEET_NAME_CHOSE = 'chosen'

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

sheet_gen = connect_to_gsheet(WORKSHEET_NAME_GEN)
sheet_chose = connect_to_gsheet(WORKSHEET_NAME_CHOSE)

data_gen = sheet_gen.get_all_records()
data_chose = sheet_chose.get_all_records()

categories_df = pd.DataFrame(data_gen)[columns_to_get]
selected_df = pd.DataFrame(data_chose)

today = dt.date.today()

joined = categories_df.join(selected_df, lsuffix = '_category', rsuffix = '_selected', on = 'upload_number')

max_upload_number = joined["upload_number_category"].max()

max_data = joined[joined["upload_number_category"] == max_upload_number]

max_due_date = dt.datetime.strptime(max_data.loc[max_upload_number, 'due_date'], "%Y-%m-%d").date()
days_left = max_due_date - today

st.header(f'You have {days_left.days} days left to write your story!')
st.subheader(f'Your story is due {max_data.loc[max_upload_number, 'due_date']}')

if max_data.loc[max_upload_number,'object_selected'] == '' or max_data.loc[max_upload_number,'emotion_selected'] == ''\
         or max_data.loc[max_upload_number,'action_selected'] == '' or max_data.loc[max_upload_number,'setting_selected'] == '':
    st.write("Not everyone has chosen words for their selected Category. Please return when that is done!")
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






