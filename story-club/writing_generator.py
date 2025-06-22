import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
# import streamlit.components.v1 as components
def main():
    st.title('Interstellar Story Club Category Generator')

    odds_500 = 0.1
    odds_1000 = 0.3
    odds_1500 = 0.3
    odds_2000 = 0.2
    odds_2500 = 0.05
    odds_3000 = 0.05

    st.info(f'Odds of story length are {odds_500*100}% for 500 words, {odds_1000*100}% each for 1000 and '
            f'1500, {odds_2000*100}% for 2000 words, and {odds_2500*100}% each for 2500 and 3000 words. '
            'There are 5 Days assigned per 100 words of story selected. ')

    randomize = st.button('Randomize')
    member_list = ['Alvaro','Elijah','Favier','Raffy']

    image = 'gifs/tars.gif'

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

        rand = np.random.random()
        if rand < odds_500:
            word_count = 500
            image = 'gifs/blackhole.gif'
        elif rand >= odds_500 and rand < odds_500 + odds_1000:
            word_count = 1000
            image = 'gifs/necessary.gif'
        elif rand >= odds_500 + odds_1000 and rand < odds_500 + odds_1000 + odds_1500:
            word_count = 1500
            image = 'gifs/yes.gif'
        elif rand >= odds_500 + odds_1000 + odds_1500 and rand < odds_500 + odds_1000 + odds_1500 + odds_2000:
            word_count = 2000
            image = 'gifs/humor.gif'
        elif rand >= odds_500 + odds_1000 + odds_1500 + odds_2000 and rand < odds_500 + odds_1000 + odds_1500 + odds_2000 + odds_2500:
            word_count = 2500
            image = 'gifs/interstellar-cost.gif'
        else:
            word_count = 3000
            image = 'gifs/crying.gif'

        days_to_add = dt.timedelta(days=(word_count/100)+1)

        due_date = dt.date.today() + days_to_add

    st.write('Object / Noun: {}'.format(object), font = 'Helvetica 16 bold')

    st.write('Emotion: {}'.format(emotion))

    st.write('Action / Verb: {}'.format(action))

    st.write('Setting / Location: {}'.format(setting))

    st.write(f"Word Count = {word_count} and it is due {due_date}")

    st.image(image)
if __name__ == '__main__':
    main()