import streamlit as st
from defs import CSS
from enum import Enum
import SessionState
from google.oauth2 import service_account
from google.cloud import bigquery
import uuid
from defs import COLORED_SQUARE_MAPPING
import os
import json
from datetime import datetime


URL = "https://justwordle.com/"


def run_query(client, query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return rows


session_state = SessionState.get(answer="", tries=[], name="", social_media_link="", hint='', win=False)
query_params = st.experimental_get_query_params()
wordle_key = query_params["wordle_key"][0] if "wordle_key" in query_params else None
leaderboard = query_params["leaderboard"][0] if "leaderboard" in query_params else None


class LetterStatus(Enum):
    miss = "miss"
    mention = "mention"
    hit = "hit"

def get_classes(input_word):
    classes = [LetterStatus.miss] * len(input_word)
    for i, letter in enumerate(input_word):
        if letter in session_state.answer:
            classes[i] = LetterStatus.mention
    for i, letter in enumerate(input_word):
        if letter == session_state.answer[i]:
            classes[i] = LetterStatus.hit
    return classes

def create_guess_table(classes, word_try):
    cells = [f"<td><div class='{classes[i].value}' style='font-size:7vmin'>{word_try[i]}</div></td>" for i in range(len(word_try))]
    all_cells_string = "".join(cells)
    return f"""
            <table>
              <tr>
                {all_cells_string}
              </tr>
            </table>
            """

def add_word(container, input_word):
    if not input_word.isalpha():
        st.warning("English Letter only.")
    else:
        input_word = input_word.upper()
        global session_state
        if len(session_state.tries) > 0 and input_word == session_state.tries[-1]:
            pass
        else:
            session_state.tries.append(input_word)

    squares_matrix = []
    words_matrix = []
    for word_try in session_state.tries:
        words_matrix.append(word_try)
        classes = get_classes(word_try)
        squares_matrix.append("".join([COLORED_SQUARE_MAPPING[c.value] for c in classes]))
        container.write(create_guess_table(classes, word_try), unsafe_allow_html=True)
    squares_matrix_text = "\n".join(squares_matrix)
    words_matrix_text = ", ".join(words_matrix)
    st.code(squares_matrix_text)
    if set(classes) == set([LetterStatus.hit]):
        session_state.win = True
        with st.form("my_form"):
            st.write("Congratulations! You won!")
            record_name = st.text_input("name/alias to display in leaderboard")
            record_social_link = st.text_input("social media link to share (optional)")
            st.write(f"Check leaderboard({URL}?wordle_key={wordle_key}&leaderboard=true)")
            submitted = st.form_submit_button("Submit to leaderboard")
            if submitted:
                print("submitted")
                if not record_name.isidentifier():
                    st.warning("The name/alias can only have English letters")
                else:
                    client = create_client()
                    rows_to_insert = [
                        {"wordle_key": wordle_key,
                         "name": record_name,
                         "social_media_link": record_social_link,
                         "win_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                         "word_status": squares_matrix_text,
                         "word_guess": words_matrix_text},
                    ]
                    dataset_ref = client.dataset('wordles')
                    table_ref = dataset_ref.table('tries')
                    errors = client.insert_rows_json(table_ref, rows_to_insert)  # Make an API request.
                    if errors == []:
                        print("New rows have been added.")
                    else:
                        print(errors)

def validate_guess_and_refresh(guess):
    if guess:
        if len(guess) == len(session_state.answer):
            add_word(c, guess)
        else:
            st.warning(f"Please enter a word of length {len(session_state.answer)}")

def create_client():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    )
    client = bigquery.Client(credentials=credentials)
    return client

st.title("Just Wordle")
st.write(CSS, unsafe_allow_html=True)

if wordle_key and leaderboard == "true":
    # case 0: leaderboard
    client = create_client()
    rows = run_query(client, f"SELECT * FROM `openwordle.wordles.tries` "
                             f"where wordle_key='{wordle_key}' "
                             f"ORDER BY win_time ASC "
                             f"limit 10 ")
    for idx, row in enumerate(rows):
        name = row['name']
        social_media_link = row['social_media_link']
        word_guess = row['word_guess']
        word_status = row['word_status']
        st.write("[name](social_media_link)")
        st.write(word_guess)
        st.write(word_status)
        st.write('----')

elif wordle_key and session_state.answer == "":
    # case 1: test take initialization
    client = create_client()
    rows = run_query(client, f"SELECT * FROM `openwordle.wordles.wordles` where wordle_key='{wordle_key}'")
    if len(rows) == 0:
        st.warning("We couldn't find a wordle associated with this URL.")
        st.write(f"Visit [Just Wordle]({URL}) to create a wordle of your own.")
    else:
        record = rows[0]
        session_state.answer = record['answer']
        session_state.name = record['name']
        session_state.social_media_link = record['link']
        session_state.hint = record['hint']
        st.write(f"by [{session_state.name}]({session_state.social_media_link})")
        st.write(f"**Creator's hint**: {session_state.hint}")
        c = st.container()
        guess = st.text_input(f'Enter your guess (length {len(session_state.answer)})')
        validate_guess_and_refresh(guess)

elif wordle_key and session_state.answer:
    # case 2: test taker after first try
    st.write(f"by [{session_state.name}]({session_state.social_media_link})")
    st.write(f"**Creator's hint**: {session_state.hint}")
    c = st.container()
    guess = st.text_input(f'Enter your guess (length {len(session_state.answer)})')
    validate_guess_and_refresh(guess)

else:
    # case 3: create your own wordle
    st.subheader("Create your own wordle")
    word_from_form = st.text_input("Word")
    name_from_form = st.text_input("Your name/alias (lower case and numbers only)")
    hint_from_form = st.text_input("Hint")
    social_from_form = st.text_input("Social Media link (optional)")
    btn = st.button("Create Wordle")
    if btn:
        if not word_from_form.isalpha():
            st.warning("The word can only have English letters")
        if not (name_from_form.isidentifier() and name_from_form.islower()):
            st.warning("The name/alias can only have lower case English letters or numbers")
        else:
            client = create_client()
            uuid_rand = uuid.uuid4().hex[:8]
            rows_to_insert = [
                {"wordle_key": uuid_rand,
                 "answer": word_from_form.upper(),
                 "name": name_from_form.lower(),
                 "hint": hint_from_form,
                 "link": social_from_form},
            ]
            dataset_ref = client.dataset('wordles')
            table_ref = dataset_ref.table('wordles')

            errors = client.insert_rows_json(table_ref, rows_to_insert)  # Make an API request.
            if errors == []:
                print("New rows have been added.")
            else:
                print(errors)
            st.text_area("", value=f'Hi I created a Wordle at https://justwordle.com/?wordle_key={uuid_rand}. '
                            f'Can you solve it?')
