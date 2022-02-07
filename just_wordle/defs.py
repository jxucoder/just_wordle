CSS = """<style>
    table {
      width: 100%;
    }
    td {
      width: 20.%;
      position: relative;
    }
    td:after {
      content: '';
      display: block;
      margin-top: 100%;
    }
    td .mention {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background: #f2d56b;
    }
    td .hit {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background: #5cd173;
    }
    td .miss {
      position: absolute;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background: #b3acab;
    }
    div {
      text-align: center;
    }
</style>"""

GREEN_SQUARE = '🟩'
GREY_SQUARE = '⬜'
YELLOW_SQUARE = '🟨'

COLORED_SQUARE_MAPPING = {
    'miss': GREY_SQUARE,
    'hit': GREEN_SQUARE,
    'mention': YELLOW_SQUARE,
}

LENGTH_TO_FONT_SIZE_MAPPING = {
    1: 7,
    2: 7,
    3: 7,
    4: 7,
    5: 7,
    6: 7,
    7: 7,
    8: 6,
    9: 5,
    10: 5,
    11: 5,
    12: 4
}