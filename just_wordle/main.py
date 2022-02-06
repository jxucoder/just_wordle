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
URL = "https://justwordle.com/"

def run_query(client, query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows


session_state = SessionState.get(answer="", tries=[], name="", social_media_link="")
query_params = st.experimental_get_query_params()
wordle_key = query_params["wordle_key"][0] if "wordle_key" in query_params else None


class LetterStatus(Enum):
    miss = "miss"
    mention = "mention"
    hit = "hit"


def get_classes(input_word):
    assert len(input_word) == len(session_state.answer)
    classes = [LetterStatus.miss] * len(input_word)
    for i, letter in enumerate(input_word):
        if letter in session_state.answer:
            classes[i] = LetterStatus.mention
    for i, letter in enumerate(input_word):
        if letter == session_state.answer[i]:
            classes[i] = LetterStatus.hit
    return classes


def add_word(input_word):
    if not input_word.isalpha():
        st.warning("English Letter only.")
    else:
        input_word = input_word.upper()
        global session_state
        session_state.tries.append(input_word)

    squares_matrix = []

    for word_try in session_state.tries:
        classes = get_classes(word_try)
        squares_matrix.append("".join([COLORED_SQUARE_MAPPING[c.value] for c in classes]))
        cells = [f"<td><div class='{classes[i].value}'>{word_try[i]}</div></td>" for i in range(len(word_try))]
        all_cells_string = "".join(cells)
        c.write(f"""
        <table style="width:40; font-size:60px;">
          <tr>
            {all_cells_string}
          </tr>
        </table>
        """, unsafe_allow_html=True)
    squares_matrix_text = "\n".join(squares_matrix)
    st.code(squares_matrix_text)


st.title("Just Wordle")
st.write(CSS, unsafe_allow_html=True)

if wordle_key and session_state.answer == "":
    # create API client.
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    )
    client = bigquery.Client(credentials=credentials)
    rows = run_query(client, f"SELECT * FROM `openwordle.wordles.wordles` where wordle_key='{wordle_key}'")
    if len(rows) == 0:
        st.warning("We couldn't find a wordle associated with this URL.")
        st.write(f"Visit [Just Wordle]({URL}) to create a wordle of your own.")
    else:
        record = rows[0]
        session_state.answer = record['answer']
        session_state.name = record['name']
        session_state.social_media_link = record['link']
        st.write(f"by [{session_state.name}]({session_state.social_media_link})")
        c = st.container()
        guess = st.text_input('Enter your guess')
        if guess:
            add_word(guess)

elif wordle_key and session_state.answer:
    st.write(f"by [{session_state.name}]({session_state.social_media_link})")
    c = st.container()
    guess = st.text_input('Enter your guess')
    if guess:
        add_word(guess)

else:
    st.subheader("Create your own wordle")
    word_from_form = st.text_input("Word")
    name_from_form = st.text_input("Your name")
    social_from_form = st.text_input("Social Media link")
    btn = st.button("Create Wordle")
    if btn:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
        )
        client = bigquery.Client(credentials=credentials)
        uuid_rand = uuid.uuid4().hex
        rows_to_insert = [
            {"wordle_key": uuid_rand,
             "answer": word_from_form,
             "name": name_from_form,
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







