import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt

parent_folder = Path(__file__).parent.parent
columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories_df = pd.read_csv(parent_folder / 'data/story_categories.csv')[columns_to_get]
selected_df = pd.read_csv(parent_folder / 'data/selected.csv', index_col=0)
categories = ['object','emotion','action','setting']

today = dt.date.today()

joined = categories_df.join(selected_df, lsuffix = '_category', rsuffix = '_selected', on = 'upload_number')

max_upload_number = joined["upload_number_category"].max()

max_data = joined[joined["upload_number_category"] == max_upload_number]

max_due_date = dt.datetime.strptime(max_data.loc[max_upload_number, 'due_date'], "%Y-%m-%d").date()
days_left = max_due_date - today

st.header(f'You have {days_left.days} days left to write your story!')

st.subheader(f'Your story is due {max_data.loc[max_upload_number, 'due_date']}')

if pd.isna(max_data.loc[max_upload_number,'object_selected']) or pd.isna(max_data.loc[max_upload_number,'emotion_selected'] or
         pd.isna(max_data.loc[max_upload_number,'action_selected']) or pd.isna(max_data.loc[max_upload_number,'setting_selected'])):
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






