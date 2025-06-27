import streamlit as st
import pandas as pd
from pathlib import Path

# Initialization
parent_folder = Path(__file__).parent.parent
columns_to_get = ['upload_number','upload_date','object','action','emotion','setting','word_count','due_date']
categories_df = pd.read_csv(parent_folder / 'data/story_categories.csv')[columns_to_get]
selected_df = pd.read_csv(parent_folder / 'data/selected.csv', index_col=0)
categories = ['object','emotion','action','setting']
password = 'Toto'

if "save_word" not in st.session_state:
    st.session_state.save_word = False

# building dataframes
joined = categories_df.join(selected_df, lsuffix = '_category', rsuffix = '_selected', on = 'upload_number')

max_upload_number = joined["upload_number_category"].max()
max_upload_date = joined["upload_date_category"].max()

max_data = joined[joined["upload_number_category"] == max_upload_number]

if max_upload_number not in (selected_df.upload_number):
    selected_df.loc[max_upload_number] = {"upload_number": max_upload_number, 'upload_date': max_upload_date}
# building app
st.header('Category Input Page')

st.subheader("Use this page to add the word you've selected for your category")

cats_for_dropdown = []
for category in categories:
    if pd.isna(max_data.loc[max_upload_number, '{}_selected'.format(category)]):
        cats_for_dropdown.append(category)

cat_selection = st.selectbox(options = [x.capitalize() for x in cats_for_dropdown], label = 'Category',
                             index = None, placeholder = 'Only Available Categories will Appear')
st.session_state.cat = cat_selection

if all(pd.notna([max_data.loc[max_upload_number,'object_selected'],max_data.loc[max_upload_number,'emotion_selected'],
    max_data.loc[max_upload_number,'action_selected'],max_data.loc[max_upload_number,'setting_selected']])):

    st.write("All Categories have been selected. Check the 'Current Story' tab to see what everyone chose")

if cat_selection:
    max_category = max_data.loc[max_upload_number,'{}_selected'.format(cat_selection.lower())]
    if pd.notna(max_category):
        st.info('Your selection already has a word! Select a different one.')
    else:
        word_selection = st.text_input(label = 'Chosen Word')
        selected_df.loc[max_upload_number,'{}'.format(cat_selection.lower())] = word_selection

        if st.button('Save Word'):
            st.session_state.save_word = True
        if st.session_state.save_word:
            user_pass = st.text_input('Enter Password')
            if user_pass == '':
                pass
            elif user_pass == password:
                selected_df.to_csv(parent_folder / 'data/selected.csv')
                st.write('Word Saved! Check the "Current Story" tab once everyone is done submitting their word.')
                st.session_state.save_word = False
            else:
                st.write('Incorrect Password. Try Again')



