from idlelib.configdialog import font_sample_text

import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
# import streamlit.components.v1 as components
def main():
    st.title('Category Generator')

    randomize = st.button('Randomize')
    member_list = ['Alvaro','Elijah','Favier','Raffy']

    object = ''
    emotion = ''
    action = ''
    setting = ''
    word_count = 0
    due_date = dt.date.today()

    if randomize:
        st.session_state.message = "Update"
        np.random.shuffle(member_list)
        object = member_list[0]
        emotion = member_list[1]
        action = member_list[2]
        setting = member_list[3]

        word_count = np.random.randint(1,6)*500
        weeks_to_add = dt.timedelta(weeks=word_count/500)
        days_to_add = dt.timedelta(days=1)

        due_date = dt.date.today() + weeks_to_add + days_to_add

    st.write('Object / Noun: {}'.format(object), font = 'Helvetica 16 bold')

    st.write('Emotion: {}'.format(emotion))

    st.write('Action / Verb: {}'.format(action))

    st.write('Setting / Location: {}'.format(setting))

    st.write(f"Word Count = {word_count} and it is due {due_date}")








if __name__ == '__main__':
    main()