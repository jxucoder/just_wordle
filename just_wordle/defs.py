CSS = """<style>
    table {
      width: 90%;
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